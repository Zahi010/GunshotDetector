import pandas as pd
import numpy as np
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from experiments.phase36.event_state_machine import EventStateMachine

p38_cache = REPO_ROOT / "experiments" / "phase38" / "feature_cache"
p39_cache = REPO_ROOT / "experiments" / "phase39" / "feature_cache"
inv = pd.read_csv(REPO_ROOT / "experiments" / "phase41" / "phase41_recording_inventory.csv")

pos_clips = inv[inv["evaluation_partition"] == "POSITIVE_GUNSHOT"]
fw_clips = inv[inv["is_fireworks_eval"] == True]
dist_other = inv[inv["is_distractor_eval"] == True]

def evaluate_with_params(feats, th_high, min_crest):
    raw_scores = feats["raw_scores"]
    yamnet_scores = feats["yamnet_scores"]
    crest_db = feats["crest_factor_db"]
    dur_sec = feats["duration_seconds"]
    n_windows = len(raw_scores)
    if n_windows == 0:
        return []
    
    cal_scores = []
    for i in range(n_windows):
        raw_s = float(raw_scores[i])
        cal_s = raw_s
        y = yamnet_scores[i]
        gun_s = max(y[421], y[422], y[424], y[425])
        fw_s = max(y[426], y[427])
        thun_s = max(y[280], y[281])
        dog_s = max(y[69], y[70], y[75], y[117])
        crackle_s = max(y[292], y[293])
        siren_s = max(y[317], y[318], y[319], y[390], y[391])

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
        cal_scores.append(cal_s)

    fsm = EventStateMachine(
        threshold_base=0.75,
        threshold_high=th_high,
        threshold_off=0.48,
        confirm_windows=2,
        cooldown_secs=2.0,
        max_hop_gap_s=0.6,
        min_crest_factor_db=8.8,
        single_win_min_crest_db=min_crest,
        allow_short_clip_exception=True
    )
    for i in range(n_windows):
        st = round(i * 0.48, 3)
        et = min(dur_sec, round(st + 0.96, 3))
        fsm.process_window({
            "window_index": i, "start_time": st, "end_time": et,
            "raw_score": raw_scores[i], "score": cal_scores[i],
            "crest_factor_db": crest_db
        }, crest_factor_db=crest_db, audio_duration_sec=dur_sec, total_windows_in_stream=n_windows)
    fsm.flush()
    return fsm.events_emitted

# Cache feature dicts in memory for ultra-fast grid search
pos_data = []
for _, r in pos_clips.iterrows():
    npz = np.load(p38_cache / f"{r['recording_id']}.npz")
    pos_data.append({
        "cid": r['recording_id'],
        "feats": {
            "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
            "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
            "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
        }
    })

fw_data = []
for _, r in fw_clips.iterrows():
    npz = np.load(p39_cache / f"{r['recording_id']}.npz")
    fw_data.append({
        "cid": r['recording_id'],
        "feats": {
            "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
            "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
            "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
        }
    })

dist_data = []
for _, r in dist_other.iterrows():
    npz = np.load(p39_cache / f"{r['recording_id']}.npz")
    dist_data.append({
        "cid": r['recording_id'],
        "feats": {
            "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
            "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
            "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
        }
    })

print(f"Loaded {len(pos_data)} pos, {len(fw_data)} fw, {len(dist_data)} dist.")
for th_high in [0.88, 0.86, 0.85, 0.84, 0.82]:
    for min_crest in [12.0, 14.0, 15.0, 16.0]:
        pos_cnt = sum(1 for item in pos_data if len(evaluate_with_params(item["feats"], th_high, min_crest)) > 0)
        fw_cnt = sum(1 for item in fw_data if len(evaluate_with_params(item["feats"], th_high, min_crest)) > 0)
        dist_cnt = sum(1 for item in dist_data if len(evaluate_with_params(item["feats"], th_high, min_crest)) > 0)
        print(f"th_high={th_high:.2f}, min_crest={min_crest:.1f} -> Pos={pos_cnt:2d}/120 ({pos_cnt/120*100:.1f}%), FW={fw_cnt:2d}/100, Dist={dist_cnt:2d}/120, TotalFP={fw_cnt+dist_cnt:2d}/220")

