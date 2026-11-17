"""
Phase 31 Scratch Script: Build and verify model_phase17_state_reset_candidate.py
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
SRC = ROOT / "model_phase17.py"
DST = ROOT / "experiments/phase31/model_phase17_state_reset_candidate.py"

with open(SRC, "r", encoding="utf-8") as f:
    code = f.read()

# Verify frozen source hash
src_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
assert src_hash == "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819", f"Source hash mismatch: {src_hash}"

# Patch 1: offline state reset
p1_target = (
    "                elif score >= threshold_base:\n"
    "                    active_cluster.append(win)\n"
    "                    if len(active_cluster) >= confirm_windows:\n"
    "                        in_event = True\n"
    "                        had_decayed = False"
)
p1_repl = (
    "                elif score >= threshold_base:\n"
    "                    active_cluster.append(win)\n"
    "                    if len(active_cluster) >= confirm_windows:\n"
    "                        in_event = True\n"
    "                        had_decayed = False\n"
    "                else:\n"
    "                    active_cluster = []"
)

# Patch 2: offline EOF flush guard
p2_target = (
    "    if active_cluster:\n"
    "        ev_start = min(w[\"start_time\"] for w in active_cluster)"
)
p2_repl = (
    "    if in_event and active_cluster:\n"
    "        ev_start = min(w[\"start_time\"] for w in active_cluster)"
)

# Patch 3: streaming process_chunk reset
p3_target = (
    "                        elif calibrated_s >= self.detector.threshold_base:\n"
    "                            self.active_cluster.append(win_record)\n"
    "                            if len(self.active_cluster) >= self.detector.confirm_windows:\n"
    "                                self.in_event = True\n"
    "                                self.had_decayed = False\n"
    "                                alert = _create_streaming_alert_record(self.active_cluster, win_et)\n"
    "                                new_alerts.append(alert)\n"
    "                                self.detected_alerts.append(alert)\n"
    "                                self.cooldown_until = win_et + self.detector.cooldown_secs"
)
p3_repl = (
    "                        elif calibrated_s >= self.detector.threshold_base:\n"
    "                            self.active_cluster.append(win_record)\n"
    "                            if len(self.active_cluster) >= self.detector.confirm_windows:\n"
    "                                self.in_event = True\n"
    "                                self.had_decayed = False\n"
    "                                alert = _create_streaming_alert_record(self.active_cluster, win_et)\n"
    "                                new_alerts.append(alert)\n"
    "                                self.detected_alerts.append(alert)\n"
    "                                self.cooldown_until = win_et + self.detector.cooldown_secs\n"
    "                        else:\n"
    "                            self.active_cluster = []"
)

# Prepend candidate notice
candidate_notice = (
    '# =============================================================================\n'
    '# PHASE 31 EXPERIMENTAL CANDIDATE: STATE-MACHINE RESET PATCH\n'
    '# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY\n'
    '# EXPERIMENTAL ARTIFACT ONLY — DO NOT OVERWRITE FROZEN model_phase17.py OR model_phase14.py\n'
    '# Restores the missing \'else: active_cluster = []\' reset branch and guards EOF flushing.\n'
    '# =============================================================================\n'
)

assert p1_target in code, "Patch 1 target not found"
assert p2_target in code, "Patch 2 target not found"
assert p3_target in code, "Patch 3 target not found"

patched_code = candidate_notice + code
patched_code = patched_code.replace(p1_target, p1_repl, 1)
patched_code = patched_code.replace(p2_target, p2_repl, 1)
patched_code = patched_code.replace(p3_target, p3_repl, 1)

with open(DST, "w", encoding="utf-8") as f:
    f.write(patched_code)

dst_hash = hashlib.sha256(patched_code.encode("utf-8")).hexdigest()
dst_size = len(patched_code.encode("utf-8"))

print(f"Successfully generated {DST}")
print(f"Size: {dst_size} bytes")
print(f"SHA-256: {dst_hash}")
