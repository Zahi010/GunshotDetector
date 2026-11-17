import pandas as pd
import numpy as np
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.run_phase39_prospective_evaluation import evaluate_condition_on_features

p38_cache = REPO_ROOT / "experiments" / "phase38" / "feature_cache"
p39_cache = REPO_ROOT / "experiments" / "phase39" / "feature_cache"
p40_cache = REPO_ROOT / "experiments" / "phase40" / "feature_cache"
inv = pd.read_csv(REPO_ROOT / "experiments" / "phase41" / "phase41_recording_inventory.csv")

# Semantic class definitions
YAMNET_CLASS_GUNSHOT = 421
YAMNET_CLASS_MACHINE_GUN = 422
YAMNET_CLASS_ARTILLERY = 424
YAMNET_CLASS_CAP_GUN = 425
YAMNET_CLASS_THUNDERSTORM = 280
YAMNET_CLASS_THUNDER = 281
YAMNET_CLASS_FIREWORKS = 426
YAMNET_CLASS_FIRECRACKER = 427
YAMNET_CLASS_DOG = 69
YAMNET_CLASS_BARK = 70
YAMNET_CLASS_YIP = 75
YAMNET_CLASS_CANIDAE = 117
YAMNET_CLASS_FIRE = 292
YAMNET_CLASS_CRACKLE = 293
YAMNET_CLASS_SIREN = 390

def evaluate_improved_detector(feats, recording_id):
    raw_scores = feats["raw_scores"]
    yamnet_scores = feats["yamnet_scores"]
    crest_db = feats["crest_factor_db"]
    n_wins = len(raw_scores)
    
    if n_wins == 0:
        return []
        
    calibrated_scores = []
    # 1. Multi-category semantic suppression
    for i in range(n_wins):
        raw_s = float(raw_scores[i])
        cal_s = raw_s
        y = yamnet_scores[i]
        
        gun_s = max(y[YAMNET_CLASS_GUNSHOT], y[YAMNET_CLASS_MACHINE_GUN], y[YAMNET_CLASS_ARTILLERY], y[YAMNET_CLASS_CAP_GUN])
        fw_s = max(y[YAMNET_CLASS_FIREWORKS], y[YAMNET_CLASS_FIRECRACKER])
        thun_s = max(y[YAMNET_CLASS_THUNDERSTORM], y[YAMNET_CLASS_THUNDER])
        dog_s = max(y[YAMNET_CLASS_DOG], y[YAMNET_CLASS_BARK], y[YAMNET_CLASS_YIP], y[YAMNET_CLASS_CANIDAE])
        siren_s = y[YAMNET_CLASS_SIREN]
        
        # Fireworks attenuation
        if fw_s > 0.20 and fw_s >= gun_s * 1.5 and gun_s < 0.10:
            cal_s *= 0.35
        # Thunder attenuation
        elif thun_s > 0.25 and thun_s >= gun_s * 1.5 and gun_s < 0.10:
            cal_s *= 0.35
        # Dog bark attenuation
        elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
            cal_s *= 0.35
        # Siren attenuation
        elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
            cal_s *= 0.30
            
        calibrated_scores.append(cal_s)
        
    calibrated_scores = np.array(calibrated_scores)
    
    # 2. State Machine with Decay-Aware Confirmation
    alerts = []
    state = "IDLE" # IDLE, CANDIDATE, CONFIRMED, COOLDOWN
    cand_win = None
    cooldown_until = -1.0
    
    threshold_base = 0.75
    threshold_high = 0.88
    threshold_off = 0.48
    threshold_decay = 0.50 # Decay tail threshold
    
    for i in range(n_wins):
        t_start = i * 0.48
        t_end = t_start + 0.96
        score = calibrated_scores[i]
        
        # Cooldown check
        if state == "COOLDOWN":
            if t_start >= cooldown_until:
                state = "IDLE"
            else:
                continue
                
        if state == "IDLE":
            # Immediate high-confidence confirmation
            if score >= threshold_high and crest_db >= 12.0:
                alerts.append({"time": t_start, "score": score, "path": "single_window_immediate"})
                state = "COOLDOWN"
                cooldown_until = t_start + 2.0
            elif score >= threshold_base:
                state = "CANDIDATE"
                cand_win = {"idx": i, "time": t_start, "score": score}
                
        elif state == "CANDIDATE":
            # Strict multi-window confirmation
            if score >= threshold_base:
                alerts.append({"time": cand_win["time"], "score": max(cand_win["score"], score), "path": "multi_window_strict"})
                state = "COOLDOWN"
                cooldown_until = t_start + 2.0
                cand_win = None
            # Decay-aware confirmation: candidate had sharp crest >= 12 dB and primary >= 0.78, followed by decay >= 0.50
            elif cand_win["score"] >= 0.78 and crest_db >= 12.0 and score >= threshold_decay:
                alerts.append({"time": cand_win["time"], "score": cand_win["score"], "path": "blast_decay_confirmation"})
                state = "COOLDOWN"
                cooldown_until = t_start + 2.0
                cand_win = None
            elif score < threshold_off:
                # Sub-threshold decay reset
                state = "IDLE"
                cand_win = None
                
    # EOF handling: if candidate was an isolated sharp impulse with score >= 0.80 and crest >= 14 dB in short clip
    if state == "CANDIDATE" and cand_win is not None:
        if cand_win["score"] >= 0.80 and crest_db >= 14.0:
            alerts.append({"time": cand_win["time"], "score": cand_win["score"], "path": "isolated_impulse_eof"})
            
    return alerts

# Now test across all partitions!
pos_clips = inv[inv["evaluation_partition"] == "POSITIVE_GUNSHOT"]
fw_clips = inv[inv["is_fireworks_eval"] == True]
dist_other = inv[inv["is_distractor_eval"] == True]

p14_pos, p36_pos, imp_pos = 0, 0, 0
for _, r in pos_clips.iterrows():
    npz = np.load(p38_cache / f"{r['recording_id']}.npz")
    feats = {
        "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
    }
    if len(evaluate_condition_on_features("COND1", feats, r["recording_id"])) > 0: p14_pos += 1
    if len(evaluate_condition_on_features("COND6", feats, r["recording_id"])) > 0: p36_pos += 1
    if len(evaluate_improved_detector(feats, r["recording_id"])) > 0: imp_pos += 1

p14_fw, p36_fw, imp_fw = 0, 0, 0
for _, r in fw_clips.iterrows():
    npz = np.load(p39_cache / f"{r['recording_id']}.npz")
    feats = {
        "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
    }
    if len(evaluate_condition_on_features("COND1", feats, r["recording_id"])) > 0: p14_fw += 1
    if len(evaluate_condition_on_features("COND6", feats, r["recording_id"])) > 0: p36_fw += 1
    if len(evaluate_improved_detector(feats, r["recording_id"])) > 0: imp_fw += 1

imp_other = 0
for _, r in dist_other.iterrows():
    npz = np.load(p39_cache / f"{r['recording_id']}.npz")
    feats = {
        "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
    }
    if len(evaluate_improved_detector(feats, r["recording_id"])) > 0: imp_other += 1

print("=== EVALUATION COMPARISON ===")
print(f"Positive Recall (N=120): P14={p14_pos} ({p14_pos/120*100:.1f}%), P36={p36_pos} ({p36_pos/120*100:.1f}%), IMPROVED={imp_pos} ({imp_pos/120*100:.1f}%)")
print(f"Fireworks Triggers (N=100): P14={p14_fw}, P36={p36_fw}, IMPROVED={imp_fw}")
print(f"Other Distractor Triggers (N=120): IMPROVED={imp_other}")

