"""
Prototype Evaluation for Detector Improvement V8 Candidate
Testing across:
1. Phase 12 continuous ambient (2.0 hr stream)
2. Phase 12 & Phase 15 Fireworks
3. Phase 19 Independent Field Positives (23 files)
4. Phase 15 Independent Positives (47 files)
5. Phase 12 Discrete Positives & Negatives (148 files)

RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os, sys, pathlib
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import pandas as pd
import librosa
import joblib

from experiments.detector_improvement_v6.model_detector_improvement_v6 import (
    DetectorImprovementV6,
    OperatingMode, EventState, compute_physical_acoustic_features_v6,
    GUN_CLASSES, PURE_GUN_CLASSES, BALLISTIC_CLASSES, FIREWORKS_CLASSES,
    THUNDER_CLASSES, IMPACT_CLASSES, GLASS_CLASSES, NON_TARGET_SEMANTIC_CLASSES,
    CAP_GUN_CLASS
)
from experiments.detector_improvement_v7.model_detector_improvement_v7 import (
    ConditionEstimatorV7
)

class CalibratedSemanticSuppressionV8:
    def __init__(self, cfg=None):
        self.cfg = cfg or {}

    def apply_suppression(self, raw_score, yamnet_scores, acoustics, is_confirmed=False):
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

        def _get_s(c):
            if isinstance(yamnet_scores, dict):
                return float(yamnet_scores.get(c, 0.0))
            return float(yamnet_scores[c]) if c < len(yamnet_scores) else 0.0

        pure_gun = max(_get_s(cls) for cls in PURE_GUN_CLASSES)
        bal_s = max(_get_s(cls) for cls in BALLISTIC_CLASSES)
        fw_s = max(_get_s(cls) for cls in FIREWORKS_CLASSES)
        thun_s = max(_get_s(cls) for cls in THUNDER_CLASSES)
        imp_s = max(_get_s(cls) for cls in IMPACT_CLASSES)
        glass_s = max(_get_s(cls) for cls in GLASS_CLASSES)
        cap_gun_s = _get_s(CAP_GUN_CLASS)

        # Calibrated Ballistic Shockwave override:
        # A chemical firework boom has low centroid (<500 Hz) and sub-bass dominance (m2l < 0.15).
        # A genuine ballistic shockwave / gunfire crack has mid/high frequency acoustic energy
        # (m2l >= 0.25 and cent >= 750 Hz, or cent >= 1200 Hz) OR strong pure_gun evidence.
        is_ballistic_acoustics = (m2l >= 0.25 and cent >= 750.0) or (cent >= 1200.0)
        is_ballistic_shockwave = (
            (pure_gun >= 0.20) or
            (bal_s >= 0.40 and bal_s >= fw_s * 0.85 and is_ballistic_acoustics)
        )

        adjusted_score = float(raw_score)
        suppressed = False
        category = None

        # 1. Zero-Energy Silence Gate
        if rms < 1e-4 or peak < 1e-3:
            return {"adjusted_score": 0.0, "suppressed": True, "category": "silence_gate"}

        # 2. Pyrotechnic Gating
        if fw_s >= 0.45 and not is_ballistic_shockwave:
            if fw_s / (pure_gun + 1e-4) >= 1.8:
                adjusted_score *= 0.15
                suppressed = True
                category = "fireworks_dominant"
        elif fw_s >= 0.25 and not is_ballistic_shockwave:
            if fw_s / (pure_gun + 1e-4) >= 2.2:
                adjusted_score *= 0.30
                suppressed = True
                category = "fireworks_standard"

        # 3. Glass Shatter Gating
        if not suppressed:
            if glass_s >= 0.30 and hi >= 0.25 and pure_gun < 0.20:
                adjusted_score *= 0.35
                suppressed = True
                category = "glass_shatter"

        # 4. Sub-Bass Automotive Thud & Backfire Gate
        if not suppressed:
            is_sub_bass = (lo >= 0.75 and hi < 0.008 and cent < 450.0 and pure_gun < 0.20)
            is_backfire = (
                cap_gun_s >= 0.35 and lo >= 0.70 and
                (cap_gun_s >= pure_gun * 1.5 or pure_gun < 0.20)
            )
            if is_sub_bass or is_backfire:
                adjusted_score *= 0.25
                suppressed = True
                category = "sub_bass_thud"

        # 5. Thunder Physical & Semantic Gating
        if not suppressed:
            is_thun_semantic = (thun_s >= 0.20)
            is_thun_phys = (lo >= 0.65 and m2l < 0.55)
            # A genuine gunshot with reverberation has mid-to-high frequencies (m2l >= 0.40 and cent >= 750 Hz)
            # or extreme crest factor (crest >= 16.0 dB) or pure firearm presence.
            # Environmental booms, trains, and traffic rumbles lack this mid-frequency acoustic profile.
            is_gunshot_transient = (
                (m2l >= 0.40 and cent >= 750.0 and crest >= 16.0) or
                (pure_gun >= 0.12) or
                (peak >= 0.30 and crest >= 12.0 and cent >= 600.0)
            )
            if (is_thun_semantic or is_thun_phys) and not is_gunshot_transient:
                adjusted_score *= 0.30
                suppressed = True
                category = "thunder_rumble"

        # 5. Mechanical Impact Gating
        if not suppressed:
            if imp_s >= 0.25:
                if imp_s / (pure_gun + 1e-4) >= 1.5 and pure_gun < 0.20:
                    adjusted_score *= 0.35
                    suppressed = True
                    category = "mechanical_impact"

        # 6. Ballistic Coherence Safeguard (with Saturation Protection)
        if not suppressed:
            is_saturated = (crest >= 15.0 or peak >= 0.30)
            max_pure = 0.04 if is_saturated else 0.08
            max_bal = 0.04 if is_saturated else 0.10
            if pure_gun < max_pure and bal_s < max_bal:
                adjusted_score *= 0.20
                suppressed = True
                category = "ballistic_incoherence"

        return {
            "adjusted_score": float(adjusted_score),
            "suppressed": suppressed,
            "category": category
        }


class ConditionAdaptiveFSMV8:
    def __init__(self, mode_policies):
        self.mode_policies = mode_policies
        self.state = EventState.IDLE
        self.current_event = None
        self.event_counter = 0
        self.candidate_scores = []
        self.candidate_crest_dbs = []
        self.candidate_times = []
        self.refractory_end_time = 0.0
        self.max_hop_gap_s = 0.60

    def reset(self):
        self.state = EventState.IDLE
        self.current_event = None
        self.candidate_scores = []
        self.candidate_crest_dbs = []
        self.candidate_times = []
        self.refractory_end_time = 0.0

    def get_policy_for_mode(self, mode):
        return self.mode_policies.get(mode.value, self.mode_policies["UNKNOWN"])

    def step(self, score, crest_db, time_s, acoustics=None, operating_mode=OperatingMode.UNKNOWN):
        policy = self.get_policy_for_mode(operating_mode)
        th_base = policy.get("threshold_base", 0.70)
        th_high = policy.get("threshold_high", 0.85)
        single_crest_std = policy.get("single_impulse_min_crest_db", 13.5)
        single_crest_high_conf = policy.get("single_impulse_high_conf_crest_db", 12.0)
        cooldown = policy.get("cooldown_secs", 1.50)

        cent = acoustics[7] if acoustics is not None else 1000.0
        m2l = acoustics[5] if acoustics is not None else 0.50

        # High confidence single impulse requires sharp acoustic profile
        is_high_conf_qual = (
            score >= th_high and
            crest_db >= single_crest_high_conf and
            (operating_mode == OperatingMode.DEGRADED_OCCLUDED or (m2l >= 0.35 and cent >= 750.0))
        )
        single_allowed = (crest_db >= single_crest_std) or is_high_conf_qual

        emitted_event = None

        if self.state == EventState.REFRACTORY:
            if time_s >= self.refractory_end_time:
                self.state = EventState.IDLE
            else:
                return self.state, None

        if self.state == EventState.IDLE:
            if single_allowed and score >= th_base:
                self.event_counter += 1
                self.current_event = {
                    "event_id": f"EVT_V8_{self.event_counter:04d}",
                    "start_time": time_s,
                    "end_time": time_s + 0.96,
                    "duration": 0.96,
                    "peak_score": round(score, 4),
                    "mean_score": round(score, 4),
                    "peak_crest_db": round(crest_db, 2),
                    "window_count": 1,
                    "operating_mode": operating_mode.value,
                    "trigger_type": "single_impulse_exception"
                }
                self.state = EventState.CONFIRMED
                emitted_event = dict(self.current_event)
                return self.state, emitted_event

            if score >= th_base:
                self.state = EventState.CANDIDATE
                self.candidate_scores = [score]
                self.candidate_crest_dbs = [crest_db]
                self.candidate_times = [time_s]
                return self.state, None

            return self.state, None

        if self.state == EventState.CANDIDATE:
            gap = time_s - self.candidate_times[-1]
            if gap > self.max_hop_gap_s:
                self.state = EventState.IDLE
                self.candidate_scores = []
                self.candidate_crest_dbs = []
                self.candidate_times = []
                return self.state, None

            if score >= th_base:
                self.candidate_scores.append(score)
                self.candidate_crest_dbs.append(crest_db)
                self.candidate_times.append(time_s)

                if len(self.candidate_scores) >= 2:
                    self.event_counter += 1
                    self.current_event = {
                        "event_id": f"EVT_V8_{self.event_counter:04d}",
                        "start_time": self.candidate_times[0],
                        "end_time": self.candidate_times[-1] + 0.96,
                        "duration": round((self.candidate_times[-1] + 0.96) - self.candidate_times[0], 2),
                        "peak_score": round(float(np.max(self.candidate_scores)), 4),
                        "mean_score": round(float(np.mean(self.candidate_scores)), 4),
                        "peak_crest_db": round(float(np.max(self.candidate_crest_dbs)), 2),
                        "window_count": len(self.candidate_scores),
                        "operating_mode": operating_mode.value,
                        "trigger_type": "temporal_confirmed"
                    }
                    self.state = EventState.CONFIRMED
                    emitted_event = dict(self.current_event)
                    return self.state, emitted_event

                return self.state, None

            if score < policy.get("threshold_off", 0.40):
                self.state = EventState.IDLE
                self.candidate_scores = []
                self.candidate_crest_dbs = []
                self.candidate_times = []
                return self.state, None

            return self.state, None

        if self.state == EventState.CONFIRMED:
            gap = time_s - self.current_event["end_time"]
            if score >= policy.get("threshold_off", 0.40) and gap <= 0.60:
                self.current_event["end_time"] = time_s + 0.96
                self.current_event["duration"] = round(self.current_event["end_time"] - self.current_event["start_time"], 2)
                self.current_event["peak_score"] = round(max(self.current_event["peak_score"], score), 4)
                self.current_event["peak_crest_db"] = round(max(self.current_event["peak_crest_db"], crest_db), 2)
                self.current_event["window_count"] += 1
                return self.state, None
            else:
                self.state = EventState.REFRACTORY
                self.refractory_end_time = time_s + cooldown
                self.candidate_scores = []
                self.candidate_crest_dbs = []
                self.candidate_times = []
                return self.state, None

        return self.state, None

from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

class DetectorImprovementV8(DetectorImprovementV7):
    def __init__(self, config_path="experiments/detector_improvement_v7/config_improvement_v7.json"):
        super().__init__(config_path)
        self.detector_name = "detector_improvement_v8"
        self.suppression = CalibratedSemanticSuppressionV8(self.cfg.get("suppression_rules", {}))
        # Update mode policies for V8
        v8_policies = dict(self.cfg.get("mode_policies", {}))
        v8_policies["UNKNOWN"]["single_impulse_high_conf_crest_db"] = 13.5
        v8_policies["CLEAR_NORMAL"]["single_impulse_high_conf_crest_db"] = 11.5
        v8_policies["DEGRADED_OCCLUDED"]["single_impulse_high_conf_crest_db"] = 10.0
        self.fsm = ConditionAdaptiveFSMV8(v8_policies)

print("\n--- Testing V8 Prototype ---")
v6 = DetectorImprovementV6()
v7 = DetectorImprovementV7()
v8 = DetectorImprovementV8()

# 1. Test Continuous Stream Sample Blocks (20, 40, 60, 80, 100, 190, 210, 230)
p12_cont_path = 'data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav'
block_len = 16000 * 30
blocks = [20, 40, 60, 80, 100, 190, 210, 230]

print("\n1. Continuous Ambient Sample Blocks (V6 vs V7 vs V8):")
with sf.SoundFile(p12_cont_path) as f:
    for blk_idx in blocks:
        f.seek(blk_idx * block_len)
        blk = f.read(block_len, dtype='float32')
        v6.reset(); res6 = v6.evaluate_waveform(blk, 16000)
        v7.reset(); res7 = v7.evaluate_waveform(blk, 16000)
        v8.reset(); res8 = v8.evaluate_waveform(blk, 16000)
        print(f"  Block {blk_idx:3d}: V6={len(res6['events'])} | V7={len(res7['events'])} | V8={len(res8['events'])}")
        if len(res8['events']) > 0:
            for ev in res8['events']:
                print(f"    -> V8 Alert: t={ev['start_time']:.2f}s, score={ev['peak_score']:.4f}, crest={ev['peak_crest_db']:.2f}dB, mode={ev['operating_mode']}")

# 2. Test Fireworks False Alarms (Phase 12 and Phase 15)
print("\n2. Fireworks False Alarms:")
p12_rca = pd.read_csv("experiments/detector_improvement_v4/recording_condition_analysis.csv")
p12_fw = p12_rca[(p12_rca["dataset_source"] == "phase12_independent") & (p12_rca["condition_category"].str.contains("fireworks"))]

fw_v6_p12, fw_v7_p12, fw_v8_p12 = 0, 0, 0
for _, r in p12_fw.iterrows():
    fpath = r["filepath"]
    y, sr = sf.read(fpath)
    v6.reset(); res6 = v6.evaluate_waveform(y, sr)
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    if res6["detected"]: fw_v6_p12 += 1
    if res7["detected"]: fw_v7_p12 += 1
    if res8["detected"]: fw_v8_p12 += 1
    status = f"V6={int(res6['detected'])}, V7={int(res7['detected'])}, V8={int(res8['detected'])}"
    print(f"  P12 FW {r['recording_id']}: {status}")
print(f"Phase 12 Fireworks False Alarms: V6={fw_v6_p12}/8 ({fw_v6_p12/8*100:.1f}%) | V7={fw_v7_p12}/8 ({fw_v7_p12/8*100:.1f}%) | V8={fw_v8_p12}/8 ({fw_v8_p12/8*100:.1f}%)")

p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")
p15_fw = p15_manifest[p15_manifest["event_classification"].str.contains("firework|firecracker|pyrotechnic", case=False, na=False)]
fw_v6_p15, fw_v7_p15, fw_v8_p15 = 0, 0, 0
for _, r in p15_fw.iterrows():
    fpath = r["filepath"]
    y, sr = sf.read(fpath)
    v6.reset(); res6 = v6.evaluate_waveform(y, sr)
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    if res6["detected"]: fw_v6_p15 += 1
    if res7["detected"]: fw_v7_p15 += 1
    if res8["detected"]: fw_v8_p15 += 1
print(f"Phase 15 Fireworks False Alarms: V6={fw_v6_p15}/10 ({fw_v6_p15/10*100:.1f}%) | V7={fw_v7_p15}/10 ({fw_v7_p15/10*100:.1f}%) | V8={fw_v8_p15}/10 ({fw_v8_p15/10*100:.1f}%)")

# 3. Test Phase 19 Field Positives (23 files)
print("\n3. Phase 19 Independent Field Positives:")
p19_dir = pathlib.Path("data/phase19_independent_positive/normalized_16k")
p19_files = sorted(list(p19_dir.glob("*.wav")))
p19_v6, p19_v7, p19_v8 = 0, 0, 0
for fpath in p19_files:
    y, sr = sf.read(fpath)
    v6.reset(); res6 = v6.evaluate_waveform(y, sr)
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    if res6["detected"]: p19_v6 += 1
    if res7["detected"]: p19_v7 += 1
    if res8["detected"]: p19_v8 += 1
print(f"Phase 19 Recall: V6={p19_v6}/23 ({p19_v6/23*100:.1f}%) | V7={p19_v7}/23 ({p19_v7/23*100:.1f}%) | V8={p19_v8}/23 ({p19_v8/23*100:.1f}%)")

# 4. Test Phase 15 Positives (47 files)
print("\n4. Phase 15 Independent Positives:")
p15_pos = p15_manifest[p15_manifest["ground_truth_label"] == 1]
p15_v6, p15_v7, p15_v8 = 0, 0, 0
for _, r in p15_pos.iterrows():
    fpath = r["filepath"]
    y, sr = sf.read(fpath)
    if y.ndim > 1: y = np.mean(y, axis=1)
    v6.reset(); res6 = v6.evaluate_waveform(y, sr)
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    if res6["detected"]: p15_v6 += 1
    if res7["detected"]: p15_v7 += 1
    if res8["detected"]: p15_v8 += 1
print(f"Phase 15 Positive Recall: V6={p15_v6}/47 ({p15_v6/47*100:.1f}%) | V7={p15_v7}/47 ({p15_v7/47*100:.1f}%) | V8={p15_v8}/47 ({p15_v8/47*100:.1f}%)")
