import pandas as pd
import numpy as np
import pathlib
import sys

REPO = pathlib.Path(".")
if str(REPO.resolve()) not in sys.path:
    sys.path.insert(0, str(REPO.resolve()))

from scripts.run_phase39_prospective_evaluation import evaluate_condition_on_features

inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
fw_recon = pd.read_csv("experiments/phase41/phase41_fireworks_reconstruction.csv")
cache_dir = REPO / "experiments" / "phase39" / "feature_cache"

discordant = fw_recon[fw_recon["pair_status"] == "PHASE36_ONLY"].copy()

print("Tracing exact Phase 14 window scores and suppression reasons on discordant clips:")
for _, row in discordant.iterrows():
    rid = row["recording_id"]
    npz = np.load(cache_dir / f"{rid}.npz")
    feats = {
        "embeddings": npz["embeddings"],
        "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"],
        "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]),
        "sample_rate": int(npz["sample_rate"])
    }
    ev1 = evaluate_condition_on_features("COND1", feats, rid)
    print(f"\nRecording {rid}: Phase 14 events = {len(ev1)}")
    raw = npz["raw_scores"]
    yam = npz["yamnet_scores"]
    for i in range(len(raw)):
        raw_s = float(raw[i])
        gun_s = max(yam[i, 426], yam[i, 427], yam[i, 428], yam[i, 429])
        thun_s = max(yam[i, 432], yam[i, 433])
        fw_s = max(yam[i, 434], yam[i, 435])
        dog_s = max(yam[i, 74], yam[i, 75], yam[i, 76], yam[i, 77])
        crackle_s = max(yam[i, 430], yam[i, 431])
        siren_s = max(yam[i, 328], yam[i, 329], yam[i, 330], yam[i, 331], yam[i, 332])
        
        cal_s = raw_s
        supp = "none"
        if thun_s > 0.25 and thun_s >= gun_s * 1.5:
            cal_s *= 0.30
            supp = f"thunder({thun_s:.3f})"
        elif fw_s > 0.35 and fw_s >= gun_s * 2.0 and gun_s < 0.05:
            cal_s *= 0.35
            supp = f"fireworks({fw_s:.3f})"
        elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
            cal_s *= 0.35
            supp = f"dog_bark({dog_s:.3f})"
        elif crackle_s > 0.25 and crackle_s >= gun_s * 1.5:
            cal_s *= 0.35
            supp = f"crackle({crackle_s:.3f})"
        elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
            cal_s *= 0.30
            supp = f"siren({siren_s:.3f})"
            
        if raw_s >= 0.75:
            print(f"  win {i}: raw={raw_s:.4f}, supp={supp}, cal={cal_s:.4f}, gun={gun_s:.3f}, fw={fw_s:.3f}, thun={thun_s:.3f}")

