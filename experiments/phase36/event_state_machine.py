"""
Phase 36 Explicit Event State Machine
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
This experimental acoustic machine-learning software is uncertified and must never
be deployed for autonomous emergency dispatch, tactical police response,
active-shooter alerting, automated evacuation, building lockdown, or life-critical
physical security. Safe recorded audio playback only; no live-fire testing.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
import numpy as np


class EventState(str, Enum):
    IDLE = "IDLE"
    CANDIDATE = "CANDIDATE"
    CONFIRMED = "CONFIRMED"
    COOLDOWN = "COOLDOWN"


class TransitionReason(str, Enum):
    INITIALIZE = "INITIALIZE"
    IDLE_NO_QUALIFY = "IDLE_NO_QUALIFY"
    CANDIDATE_INITIATED = "CANDIDATE_INITIATED"
    IMMEDIATE_HIGH_CONFIDENCE = "IMMEDIATE_HIGH_CONFIDENCE"
    CANDIDATE_CONTINUED = "CANDIDATE_CONTINUED"
    MULTI_WINDOW_CONFIRMED = "MULTI_WINDOW_CONFIRMED"
    CANDIDATE_DISCARDED_BELOW_BASE = "CANDIDATE_DISCARDED_BELOW_BASE"
    CANDIDATE_DISCARDED_GAP = "CANDIDATE_DISCARDED_GAP"
    CANDIDATE_DISCARDED_AT_EOF = "CANDIDATE_DISCARDED_AT_EOF"
    CONFIRMED_CONTINUED = "CONFIRMED_CONTINUED"
    EVENT_DECAYED_BELOW_OFF = "EVENT_DECAYED_BELOW_OFF"
    EVENT_TERMINATED_STREAM_GAP = "EVENT_TERMINATED_STREAM_GAP"
    CONFIRMED_FLUSHED_AT_EOF = "CONFIRMED_FLUSHED_AT_EOF"
    COOLDOWN_ACTIVE = "COOLDOWN_ACTIVE"
    COOLDOWN_REFRACTORY_BLOCKED = "COOLDOWN_REFRACTORY_BLOCKED"
    COOLDOWN_EXPIRED = "COOLDOWN_EXPIRED"
    STREAM_BOUNDARY_RESET = "STREAM_BOUNDARY_RESET"


class EventStateMachine:
    """
    Deterministic 4-State Event Management Engine:
    IDLE -> CANDIDATE -> CONFIRMED -> COOLDOWN -> IDLE

    Guarantees:
    1. Temporal continuity enforced on candidates (gap <= max_hop_gap_s).
    2. Unconfirmed candidates strictly discarded upon continuity break or decay.
    3. Stale candidates purged across recording boundaries via reset().
    4. End-of-file (EOF) never promotes unconfirmed candidates.
    5. Cooldown refractory window is independent of candidate accumulation.
    6. All state transitions logged with timestamps and explicit reasons.
    """

    def __init__(
        self,
        threshold_base: float = 0.75,
        threshold_high: float = 0.88,
        threshold_off: float = 0.48,
        confirm_windows: int = 2,
        cooldown_secs: float = 2.0,
        max_hop_gap_s: float = 0.60,
        min_crest_factor_db: float = 8.8,
        single_win_min_crest_db: float = 12.0,
        allow_short_clip_exception: bool = True
    ):
        self.threshold_base = threshold_base
        self.threshold_high = threshold_high
        self.threshold_off = threshold_off
        self.confirm_windows = confirm_windows
        self.cooldown_secs = cooldown_secs
        self.max_hop_gap_s = max_hop_gap_s
        self.min_crest_factor_db = min_crest_factor_db
        self.single_win_min_crest_db = single_win_min_crest_db
        self.allow_short_clip_exception = allow_short_clip_exception

        # State storage
        self.state: EventState = EventState.IDLE
        self.cooldown_until: float = -1.0
        self.candidate_windows: List[Dict[str, Any]] = []
        self.confirmed_windows: List[Dict[str, Any]] = []
        self.last_window_time: Optional[float] = None
        self.transition_log: List[Dict[str, Any]] = []
        self.transition_counter: int = 0
        self.events_emitted: List[Dict[str, Any]] = []

    def reset(self) -> None:
        """Deterministic reset for stream or recording boundary."""
        self._record_transition(
            self.state,
            EventState.IDLE,
            TransitionReason.STREAM_BOUNDARY_RESET,
            timestamp_s=self.last_window_time or 0.0,
            score=0.0
        )
        self.state = EventState.IDLE
        self.cooldown_until = -1.0
        self.candidate_windows = []
        self.confirmed_windows = []
        self.last_window_time = None

    def _record_transition(
        self,
        prev_state: EventState,
        new_state: EventState,
        reason: TransitionReason,
        timestamp_s: float,
        score: float,
        raw_score: Optional[float] = None,
        window_start_s: Optional[float] = None,
        window_end_s: Optional[float] = None
    ) -> None:
        self.transition_counter += 1
        self.transition_log.append({
            "transition_id": self.transition_counter,
            "timestamp_s": round(timestamp_s, 4),
            "previous_state": prev_state.value,
            "new_state": new_state.value,
            "trigger_reason": reason.value,
            "score": round(score, 4),
            "raw_score": round(raw_score if raw_score is not None else score, 4),
            "window_start_s": round(window_start_s, 4) if window_start_s is not None else None,
            "window_end_s": round(window_end_s, 4) if window_end_s is not None else None,
            "candidate_count": len(self.candidate_windows),
            "confirmed_count": len(self.confirmed_windows)
        })

    def _create_event_record(self, cluster: List[Dict[str, Any]], dispatch_path: str) -> Dict[str, Any]:
        st = min(w["start_time"] for w in cluster)
        et = max(w["end_time"] for w in cluster)
        pk_win = max(cluster, key=lambda w: w.get("score", 0.0))
        pk_score = float(pk_win.get("score", 0.0))
        raw_pk = float(max(w.get("raw_score", w.get("score", 0.0)) for w in cluster))
        crest_vals = [w.get("crest_factor_db") for w in cluster if w.get("crest_factor_db") is not None]
        mean_crest = float(np.mean(crest_vals)) if crest_vals else None

        return {
            "start_time": round(st, 3),
            "end_time": round(et, 3),
            "duration_seconds": round(et - st, 3),
            "peak_time": round((pk_win["start_time"] + pk_win["end_time"]) / 2.0, 3),
            "peak_score": round(pk_score, 4),
            "raw_peak_score": round(raw_pk, 4),
            "mean_score": round(float(np.mean([w.get("score", 0.0) for w in cluster])), 4),
            "trigger_windows_count": len(cluster),
            "dispatch_path": dispatch_path,
            "crest_factor_db": round(mean_crest, 2) if mean_crest is not None else None,
            "verdict": "Gunshot-like acoustic event detected"
        }

    def process_window(
        self,
        window: Dict[str, Any],
        crest_factor_db: Optional[float] = None,
        audio_duration_sec: Optional[float] = None,
        total_windows_in_stream: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single acoustic evaluation window through the state machine.
        Returns a completed event dict if an event terminates on this window, else None.
        """
        st = float(window["start_time"])
        et = float(window["end_time"])
        score = float(window["score"])
        raw_score = float(window.get("raw_score", score))
        emitted_event = None

        has_sharp_crest = (crest_factor_db is None or crest_factor_db >= self.single_win_min_crest_db)
        
        # Single-window short clip exception check
        is_short_isolated_clip = False
        if (
            self.allow_short_clip_exception
            and audio_duration_sec is not None
            and audio_duration_sec <= 1.05
            and total_windows_in_stream == 1
        ):
            if crest_factor_db is None or crest_factor_db >= self.min_crest_factor_db:
                is_short_isolated_clip = True

        qualifies_immediate = (score >= self.threshold_high and has_sharp_crest) or (
            is_short_isolated_clip and score >= self.threshold_base
        )

        # ---------------------------------------------------------------------
        # State: COOLDOWN Check
        # ---------------------------------------------------------------------
        if self.state == EventState.COOLDOWN:
            if st >= self.cooldown_until:
                # Cooldown expired!
                self._record_transition(
                    EventState.COOLDOWN,
                    EventState.IDLE,
                    TransitionReason.COOLDOWN_EXPIRED,
                    timestamp_s=st,
                    score=score,
                    raw_score=raw_score,
                    window_start_s=st,
                    window_end_s=et
                )
                self.state = EventState.IDLE
            else:
                # Still in cooldown
                if score >= self.threshold_base:
                    self._record_transition(
                        EventState.COOLDOWN,
                        EventState.COOLDOWN,
                        TransitionReason.COOLDOWN_REFRACTORY_BLOCKED,
                        timestamp_s=st,
                        score=score,
                        raw_score=raw_score,
                        window_start_s=st,
                        window_end_s=et
                    )
                self.last_window_time = st
                return None

        # ---------------------------------------------------------------------
        # State: IDLE
        # ---------------------------------------------------------------------
        if self.state == EventState.IDLE:
            if qualifies_immediate:
                # Single-window immediate promotion
                self.confirmed_windows = [window]
                self._record_transition(
                    EventState.IDLE,
                    EventState.CONFIRMED,
                    TransitionReason.IMMEDIATE_HIGH_CONFIDENCE,
                    timestamp_s=st,
                    score=score,
                    raw_score=raw_score,
                    window_start_s=st,
                    window_end_s=et
                )
                self.state = EventState.CONFIRMED
            elif score >= self.threshold_base:
                # Initiate candidate accumulation
                self.candidate_windows = [window]
                self._record_transition(
                    EventState.IDLE,
                    EventState.CANDIDATE,
                    TransitionReason.CANDIDATE_INITIATED,
                    timestamp_s=st,
                    score=score,
                    raw_score=raw_score,
                    window_start_s=st,
                    window_end_s=et
                )
                self.state = EventState.CANDIDATE
            else:
                # Stays IDLE
                pass

        # ---------------------------------------------------------------------
        # State: CANDIDATE
        # ---------------------------------------------------------------------
        elif self.state == EventState.CANDIDATE:
            # Check temporal continuity
            time_gap = (st - self.last_window_time) if self.last_window_time is not None else 0.0
            if time_gap > self.max_hop_gap_s:
                # Continuity gap! Unconfirmed candidates discarded
                self._record_transition(
                    EventState.CANDIDATE,
                    EventState.IDLE,
                    TransitionReason.CANDIDATE_DISCARDED_GAP,
                    timestamp_s=st,
                    score=score,
                    raw_score=raw_score,
                    window_start_s=st,
                    window_end_s=et
                )
                self.candidate_windows = []
                self.state = EventState.IDLE

                # Re-evaluate current window from IDLE
                if qualifies_immediate:
                    self.confirmed_windows = [window]
                    self._record_transition(
                        EventState.IDLE,
                        EventState.CONFIRMED,
                        TransitionReason.IMMEDIATE_HIGH_CONFIDENCE,
                        timestamp_s=st,
                        score=score,
                        raw_score=raw_score,
                        window_start_s=st,
                        window_end_s=et
                    )
                    self.state = EventState.CONFIRMED
                elif score >= self.threshold_base:
                    self.candidate_windows = [window]
                    self._record_transition(
                        EventState.IDLE,
                        EventState.CANDIDATE,
                        TransitionReason.CANDIDATE_INITIATED,
                        timestamp_s=st,
                        score=score,
                        raw_score=raw_score,
                        window_start_s=st,
                        window_end_s=et
                    )
                    self.state = EventState.CANDIDATE
            else:
                # Window is continuous
                if qualifies_immediate:
                    # Immediate promotion
                    self.candidate_windows.append(window)
                    self.confirmed_windows = list(self.candidate_windows)
                    self.candidate_windows = []
                    self._record_transition(
                        EventState.CANDIDATE,
                        EventState.CONFIRMED,
                        TransitionReason.IMMEDIATE_HIGH_CONFIDENCE,
                        timestamp_s=st,
                        score=score,
                        raw_score=raw_score,
                        window_start_s=st,
                        window_end_s=et
                    )
                    self.state = EventState.CONFIRMED
                elif score >= self.threshold_base:
                    self.candidate_windows.append(window)
                    if len(self.candidate_windows) >= self.confirm_windows:
                        # Multi-window confirmation achieved!
                        self.confirmed_windows = list(self.candidate_windows)
                        self.candidate_windows = []
                        self._record_transition(
                            EventState.CANDIDATE,
                            EventState.CONFIRMED,
                            TransitionReason.MULTI_WINDOW_CONFIRMED,
                            timestamp_s=st,
                            score=score,
                            raw_score=raw_score,
                            window_start_s=st,
                            window_end_s=et
                        )
                        self.state = EventState.CONFIRMED
                    else:
                        self._record_transition(
                            EventState.CANDIDATE,
                            EventState.CANDIDATE,
                            TransitionReason.CANDIDATE_CONTINUED,
                            timestamp_s=st,
                            score=score,
                            raw_score=raw_score,
                            window_start_s=st,
                            window_end_s=et
                        )
                else:
                    # Decayed below base threshold before confirmation: discard!
                    self._record_transition(
                        EventState.CANDIDATE,
                        EventState.IDLE,
                        TransitionReason.CANDIDATE_DISCARDED_BELOW_BASE,
                        timestamp_s=st,
                        score=score,
                        raw_score=raw_score,
                        window_start_s=st,
                        window_end_s=et
                    )
                    self.candidate_windows = []
                    self.state = EventState.IDLE

        # ---------------------------------------------------------------------
        # State: CONFIRMED
        # ---------------------------------------------------------------------
        elif self.state == EventState.CONFIRMED:
            time_gap = (st - self.last_window_time) if self.last_window_time is not None else 0.0
            if time_gap > self.max_hop_gap_s:
                # Silence gap ends the sustained confirmed event
                dispatch = "single_window_high_confidence" if len(self.confirmed_windows) == 1 else "multi_window_confirmation"
                emitted_event = self._create_event_record(self.confirmed_windows, dispatch)
                self.events_emitted.append(emitted_event)
                self.cooldown_until = emitted_event["end_time"] + self.cooldown_secs

                self._record_transition(
                    EventState.CONFIRMED,
                    EventState.COOLDOWN,
                    TransitionReason.EVENT_TERMINATED_STREAM_GAP,
                    timestamp_s=st,
                    score=score,
                    raw_score=raw_score,
                    window_start_s=st,
                    window_end_s=et
                )
                self.confirmed_windows = []
                self.state = EventState.COOLDOWN

                # Check if current window after gap is during cooldown or qualifies
                if st >= self.cooldown_until:
                    self.state = EventState.IDLE
                    if qualifies_immediate:
                        self.confirmed_windows = [window]
                        self._record_transition(
                            EventState.IDLE,
                            EventState.CONFIRMED,
                            TransitionReason.IMMEDIATE_HIGH_CONFIDENCE,
                            timestamp_s=st,
                            score=score,
                            raw_score=raw_score,
                            window_start_s=st,
                            window_end_s=et
                        )
                        self.state = EventState.CONFIRMED
                    elif score >= self.threshold_base:
                        self.candidate_windows = [window]
                        self._record_transition(
                            EventState.IDLE,
                            EventState.CANDIDATE,
                            TransitionReason.CANDIDATE_INITIATED,
                            timestamp_s=st,
                            score=score,
                            raw_score=raw_score,
                            window_start_s=st,
                            window_end_s=et
                        )
                        self.state = EventState.CANDIDATE
            elif score >= self.threshold_off:
                # Event is sustained
                self.confirmed_windows.append(window)
                self._record_transition(
                    EventState.CONFIRMED,
                    EventState.CONFIRMED,
                    TransitionReason.CONFIRMED_CONTINUED,
                    timestamp_s=st,
                    score=score,
                    raw_score=raw_score,
                    window_start_s=st,
                    window_end_s=et
                )
            else:
                # Score decayed below off threshold: event ends!
                dispatch = "single_window_high_confidence" if len(self.confirmed_windows) == 1 else "multi_window_confirmation"
                emitted_event = self._create_event_record(self.confirmed_windows, dispatch)
                self.events_emitted.append(emitted_event)
                self.cooldown_until = emitted_event["end_time"] + self.cooldown_secs

                self._record_transition(
                    EventState.CONFIRMED,
                    EventState.COOLDOWN,
                    TransitionReason.EVENT_DECAYED_BELOW_OFF,
                    timestamp_s=st,
                    score=score,
                    raw_score=raw_score,
                    window_start_s=st,
                    window_end_s=et
                )
                self.confirmed_windows = []
                self.state = EventState.COOLDOWN

        self.last_window_time = st
        return emitted_event

    def step(
        self,
        window_index: int,
        start_time: float,
        end_time: float,
        score: float,
        raw_score: Optional[float] = None,
        crest_factor_db: Optional[float] = None,
        audio_duration_sec: Optional[float] = None,
        total_windows_in_stream: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Convenience step method matching unit test and streaming interface."""
        win = {
            "window_index": window_index,
            "start_time": start_time,
            "end_time": end_time,
            "score": score,
            "raw_score": raw_score if raw_score is not None else score
        }
        return self.process_window(
            win,
            crest_factor_db=crest_factor_db,
            audio_duration_sec=audio_duration_sec,
            total_windows_in_stream=total_windows_in_stream
        )

    def flush_stream(
        self,
        audio_duration_sec: Optional[float] = None,
        discard_unconfirmed: bool = True
    ) -> List[Dict[str, Any]]:
        """Convenience flush returning list of emitted events."""
        ev = self.flush()
        return [ev] if ev is not None else []

    @property
    def active_event(self) -> Optional[Dict[str, Any]]:
        if self.state == EventState.CONFIRMED and self.confirmed_windows:
            return {
                "start_time": min(w["start_time"] for w in self.confirmed_windows),
                "end_time": max(w["end_time"] for w in self.confirmed_windows),
                "confirmed": True
            }
        return None

    @property
    def cooldown_until_s(self) -> float:
        return max(0.0, self.cooldown_until)

    def flush(self) -> Optional[Dict[str, Any]]:
        """
        Handle End-of-File (EOF) or recording stream completion.
        STRICT RULE:
        - If state is CONFIRMED: emit the active confirmed event.
        - If state is CANDIDATE: DISCARD! Never promote unconfirmed candidates into alerts.
        """
        emitted_event = None
        ts = self.last_window_time or 0.0

        if self.state == EventState.CONFIRMED and self.confirmed_windows:
            dispatch = "single_window_high_confidence" if len(self.confirmed_windows) == 1 else "multi_window_confirmation"
            emitted_event = self._create_event_record(self.confirmed_windows, dispatch)
            self.events_emitted.append(emitted_event)
            self._record_transition(
                EventState.CONFIRMED,
                EventState.IDLE,
                TransitionReason.CONFIRMED_FLUSHED_AT_EOF,
                timestamp_s=ts,
                score=0.0
            )
            self.confirmed_windows = []
            self.state = EventState.IDLE
        elif self.state == EventState.CANDIDATE:
            # Strictly discard unconfirmed candidates at EOF
            self._record_transition(
                EventState.CANDIDATE,
                EventState.IDLE,
                TransitionReason.CANDIDATE_DISCARDED_AT_EOF,
                timestamp_s=ts,
                score=0.0
            )
            self.candidate_windows = []
            self.state = EventState.IDLE
        elif self.state == EventState.COOLDOWN:
            self._record_transition(
                EventState.COOLDOWN,
                EventState.IDLE,
                TransitionReason.COOLDOWN_EXPIRED,
                timestamp_s=ts,
                score=0.0
            )
            self.state = EventState.IDLE

        return emitted_event


def merge_phase36_events(
    window_results: List[Dict[str, Any]],
    threshold_base: float = 0.75,
    threshold_high: float = 0.88,
    threshold_off: float = 0.48,
    confirm_windows: int = 2,
    cooldown_secs: float = 2.0,
    max_hop_gap_s: float = 0.60,
    min_crest_factor_db: float = 8.8,
    single_win_min_crest_db: float = 12.0,
    audio_duration_sec: Optional[float] = None,
    crest_factor_db: Optional[float] = None,
    allow_short_clip_exception: bool = True
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Batch wrapper executing the deterministic Phase 36 Event State Machine
    over pre-sorted window evaluation results.
    Returns: (events_list, state_transition_log)
    """
    if not window_results:
        return [], []

    sorted_windows = sorted(window_results, key=lambda w: w["start_time"])
    fsm = EventStateMachine(
        threshold_base=threshold_base,
        threshold_high=threshold_high,
        threshold_off=threshold_off,
        confirm_windows=confirm_windows,
        cooldown_secs=cooldown_secs,
        max_hop_gap_s=max_hop_gap_s,
        min_crest_factor_db=min_crest_factor_db,
        single_win_min_crest_db=single_win_min_crest_db,
        allow_short_clip_exception=allow_short_clip_exception
    )

    tot_win = len(sorted_windows)
    for win in sorted_windows:
        fsm.process_window(
            win,
            crest_factor_db=crest_factor_db,
            audio_duration_sec=audio_duration_sec,
            total_windows_in_stream=tot_win
        )

    fsm.flush()
    return fsm.events_emitted, fsm.transition_log
