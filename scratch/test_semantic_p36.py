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
YAMNET_CLASS_POLICE_CAR = 317
YAMNET_CLASS_AMBULANCE = 318
YAMNET_CLASS_FIRE_ENGINE = 319
YAMNET_CLASS_SIREN = 390
YAMNET_CLASS_CIVIL_DEFENSE = 391

def evaluate_p36_with_full_semantic_suppression(feats, recording_id):
    raw_scores = feats["raw_scores"]
    yamnet_scores = feats["yamnet_scores"]
    crest_db = feats["crest_factor_db"]
    n_wins = len(raw_scores)
    
    if n_wins == 0:
        return []
        
    calibrated_scores = []
    for i in range(n_wins):
        raw_s = float(raw_scores[i])
        cal_s = raw_s
        y = yamnet_scores[i]
        
        gun_s = max(y[YAMNET_CLASS_GUNSHOT], y[YAMNET_CLASS_MACHINE_GUN], y[YAMNET_CLASS_ARTILLERY], y[YAMNET_CLASS_CAP_GUN])
        fw_s = max(y[YAMNET_CLASS_FIREWORKS], y[YAMNET_CLASS_FIRECRACKER])
        thun_s = max(y[YAMNET_CLASS_THUNDERSTORM], y[YAMNET_CLASS_THUNDER])
        dog_s = max(y[YAMNET_CLASS_DOG], y[YAMNET_CLASS_BARK], y[YAMNET_CLASS_YIP], y[YAMNET_CLASS_CANIDAE])
        crackle_s = max(y[YAMNET_CLASS_FIRE], y[YAMNET_CLASS_CRACKLE])
        siren_s = max(y[YAMNET_CLASS_POLICE_CAR], y[YAMNET_CLASS_AMBULANCE], y[YAMNET_CLASS_FIRE_ENGINE], y[YAMNET_CLASS_SIREN], y[YAMNET_CLASS_CIVIL_DEFENSE])
        
        # Phase 14 calibrated semantic gating parameters:
        # 1. Thunder
        if thun_s > 0.25 and thun_s >= gun_s * 1.5:
            cal_s *= 0.35
        # 2. Fireworks / Firecrackers
        elif fw_s > 0.35 and fw_s >= gun_s * 2.0 and gun_s < 0.05:
            cal_s *= 0.35
        # 3. Dog / Bark
        elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
            cal_s *= 0.35
        # 4. Crackling Fire
        elif crackle_s > 0.25 and crackle_s >= gun_s * 1.5:
            cal_s *= 0.35
        # 5. Sirens
        elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
            cal_s *= 0.30
            
        calibrated_scores.append(cal_s)
        
    calibrated_scores = np.array(calibrated_scores)
    
    # Run through Phase 36's EXACT EventStateMachine rules
    from experiments.phase36.event_state_machine import EventStateMachine
    
    sm = EventStateMachine(
        threshold_base=0.75,
        threshold_high=0.88,
        threshold_off=0.48,
        min_crest_factor_db=9.5,
        single_win_min_crest_db=12.0,
        confirm_windows=2,
        cooldown_secs=2.0,
        allow_short_clip_exception=True
    )
    
    dur_sec = feats["duration_seconds"]
    alerts = []
    
    for i in range(n_wins):
        win_dict = {
            "start_time": i * 0.48,
            "end_time": i * 0.48 + 0.96,
            "score": calibrated_scores[i],
            "raw_score": raw_scores[i]
        }
        ev = sm.process_window(
            win_dict,
            crest_factor_db=crest_db,
            audio_duration_sec=dur_sec,
            total_windows_in_stream=n_wins
        )
        if ev is not None:
            alerts.append(ev)
            
    eof_ev = sm.flush()
    if eof_ev is not None:
        alerts.append(eof_ev)
        
    return alerts

# Evaluate across partitions
pos_clips = inv[inv["evaluation_partition"] == "POSITIVE_GUNSHOT"]
fw_clips = inv[inv["is_fireworks_eval"] == True]
dist_other = inv[inv["is_distractor_eval"] == True]

pos_detected = 0
for _, r in pos_clips.iterrows():
    npz = np.load(p38_cache / f"{r['recording_id']}.npz")
    feats = {
        "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
    }
    alerts = evaluate_p36_with_full_semantic_suppression(feats, r["recording_id"])
    if len(alerts) > 0:
        pos_detected += 1

fw_detected = 0
for _, r in fw_clips.iterrows():
    npz = np.load(p39_cache / f"{r['recording_id']}.npz")
    feats = {
        "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
    }
    alerts = evaluate_p36_with_full_semantic_suppression(feats, r["recording_id"])
    if len(alerts) > 0:
        fw_detected += 1

dist_detected = 0
for _, r in dist_other.iterrows():
    npz = np.load(p39_cache / f"{r['recording_id']}.npz")
    feats = {
        "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
    }
    alerts = evaluate_p36_with_full_semantic_suppression(feats, r["recording_id"])
    if len(alerts) > 0:
        dist_detected += 1

print("=== RESULTS WITH FULL SEMANTIC SUPPRESSION + PHASE 36 STATE MACHINE ===")
print(f"Positive Recall (N=120): {pos_detected} / 120 ({pos_detected/120*100:.2f}%)")
print(f"Fireworks Triggers (N=100): {fw_detected} / 100 ({fw_detected/100*100:.2f}%)")
print(f"Other Distractor Triggers (N=120): {dist_detected} / 120 ({dist_detected/120*100:.2f}%)")
