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

from experiments.phase36.event_state_machine import EventStateMachine

def evaluate_integrated_v1(feats, recording_id):
    raw_scores = feats["raw_scores"]
    yamnet_scores = feats["yamnet_scores"]
    crest_db = feats["crest_factor_db"]
    dur_sec = feats["duration_seconds"]
    n_windows = len(raw_scores)

    if n_windows == 0:
        return []

    # 1. Multi-category semantic suppression
    calibrated_scores = []
    for i in range(n_windows):
        raw_s = float(raw_scores[i])
        cal_s = raw_s
        y = yamnet_scores[i]

        gun_s = max(y[YAMNET_CLASS_GUNSHOT], y[YAMNET_CLASS_MACHINE_GUN], y[YAMNET_CLASS_ARTILLERY], y[YAMNET_CLASS_CAP_GUN])
        fw_s = max(y[YAMNET_CLASS_FIREWORKS], y[YAMNET_CLASS_FIRECRACKER])
        thun_s = max(y[YAMNET_CLASS_THUNDERSTORM], y[YAMNET_CLASS_THUNDER])
        dog_s = max(y[YAMNET_CLASS_DOG], y[YAMNET_CLASS_BARK], y[YAMNET_CLASS_YIP], y[YAMNET_CLASS_CANIDAE])
        crackle_s = max(y[YAMNET_CLASS_FIRE], y[YAMNET_CLASS_CRACKLE])
        siren_s = max(y[YAMNET_CLASS_POLICE_CAR], y[YAMNET_CLASS_AMBULANCE], y[YAMNET_CLASS_FIRE_ENGINE], y[YAMNET_CLASS_SIREN], y[YAMNET_CLASS_CIVIL_DEFENSE])

        # Calibrated suppression logic
        if thun_s > 0.25 and thun_s >= gun_s * 1.5:
            cal_s *= 0.30
        elif fw_s > 0.30 and fw_s >= gun_s * 1.5 and gun_s < 0.10:
            cal_s *= 0.35
        elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
            cal_s *= 0.35
        elif crackle_s > 0.25 and crackle_s >= gun_s * 1.5:
            cal_s *= 0.35
        elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
            cal_s *= 0.30

        calibrated_scores.append(cal_s)

    # 2. State Machine: Phase 36 EventStateMachine
    fsm = EventStateMachine(
        threshold_base=0.75,
        threshold_high=0.88,
        threshold_off=0.48,
        confirm_windows=2,
        cooldown_secs=2.0,
        max_hop_gap_s=0.6,
        min_crest_factor_db=8.8,
        single_win_min_crest_db=12.0,
        allow_short_clip_exception=True
    )

    for i in range(n_windows):
        st = round(i * 0.48, 3)
        et = min(dur_sec, round(st + 0.96, 3))
        win_record = {
            "window_index": i,
            "start_time": st,
            "end_time": et,
            "raw_score": raw_scores[i],
            "score": calibrated_scores[i],
            "crest_factor_db": crest_db
        }
        fsm.process_window(
            win_record,
            crest_factor_db=crest_db,
            audio_duration_sec=dur_sec,
            total_windows_in_stream=n_windows
        )

    fsm.flush()
    return fsm.events_emitted

# Test on Positive, Fireworks, Distractors, and Continuous Streams!
pos_clips = inv[inv["evaluation_partition"] == "POSITIVE_GUNSHOT"]
fw_clips = inv[inv["is_fireworks_eval"] == True]
dist_other = inv[inv["is_distractor_eval"] == True]

pos_p14, pos_p36, pos_v1 = 0, 0, 0
dup_p14, dup_p36, dup_v1 = 0, 0, 0

for _, r in pos_clips.iterrows():
    npz = np.load(p38_cache / f"{r['recording_id']}.npz")
    feats = {
        "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
    }
    ev14 = evaluate_condition_on_features("COND1", feats, r["recording_id"])
    ev36 = evaluate_condition_on_features("COND6", feats, r["recording_id"])
    ev_v1 = evaluate_integrated_v1(feats, r["recording_id"])
    
    if len(ev14) > 0:
        pos_p14 += 1
        dup_p14 += max(0, len(ev14) - 1)
    if len(ev36) > 0:
        pos_p36 += 1
        dup_p36 += max(0, len(ev36) - 1)
    if len(ev_v1) > 0:
        pos_v1 += 1
        dup_v1 += max(0, len(ev_v1) - 1)

fw_p14, fw_p36, fw_v1 = 0, 0, 0
for _, r in fw_clips.iterrows():
    npz = np.load(p39_cache / f"{r['recording_id']}.npz")
    feats = {
        "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
    }
    if len(evaluate_condition_on_features("COND1", feats, r["recording_id"])) > 0: fw_p14 += 1
    if len(evaluate_condition_on_features("COND6", feats, r["recording_id"])) > 0: fw_p36 += 1
    if len(evaluate_integrated_v1(feats, r["recording_id"])) > 0: fw_v1 += 1

oth_p14, oth_p36, oth_v1 = 0, 0, 0
for _, r in dist_other.iterrows():
    npz = np.load(p39_cache / f"{r['recording_id']}.npz")
    feats = {
        "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
    }
    if len(evaluate_condition_on_features("COND1", feats, r["recording_id"])) > 0: oth_p14 += 1
    if len(evaluate_condition_on_features("COND6", feats, r["recording_id"])) > 0: oth_p36 += 1
    if len(evaluate_integrated_v1(feats, r["recording_id"])) > 0: oth_v1 += 1

print("\n=== SYSTEMATIC BENCHMARK COMPARISON ===")
print(f"Positive Recall (N=120): P14={pos_p14} (61.7%), P36={pos_p36} (64.2%), V1={pos_v1} ({pos_v1/120*100:.1f}%)")
print(f"Duplicate Alerts on TP: P14={dup_p14}, P36={dup_p36}, V1={dup_v1}")
print(f"Fireworks Triggers (N=100): P14={fw_p14}, P36={fw_p36}, V1={fw_v1}")
print(f"Other Distractor Triggers (N=120): P14={oth_p14}, P36={oth_p36}, V1={oth_v1}")
print(f"Total Distractor Triggers (N=220): P14={fw_p14+oth_p14}, P36={fw_p36+oth_p36}, V1={fw_v1+oth_v1}")

