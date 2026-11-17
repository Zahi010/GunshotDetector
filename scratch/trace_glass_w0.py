import sys
import pathlib
import pandas as pd
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v10.model_detector_improvement_v10 import DetectorImprovementV10

det10 = DetectorImprovementV10()
target = "1-88807-A-39.wav"
manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
df = pd.read_csv(manifest_path)
row = df[df["filename"] == target].iloc[0]
p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
audio, sr = sf.read(str(p), dtype="float32")

# Window 0
win = audio[:15360]
feat, ys, acoustics, m_mean = det10.extract_features(win)
crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

raw_score = float(det10.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
p_mlp, p_cb, p_lgb, p_xgb = feat[0], feat[1], feat[2], feat[3]
m_min = min(p_mlp, p_cb, p_lgb, p_xgb)
m_std = feat[7]

print(f"Base probs: MLP={p_mlp:.3f}, CB={p_cb:.3f}, LGB={p_lgb:.3f}, XGB={p_xgb:.3f}, mean={m_mean:.3f}")
print(f"Raw fusion score: {raw_score:.3f}")

# BMCC
cal_score = raw_score
if det10.consensus_cfg.get("enabled", True):
    min_prob = det10.consensus_cfg.get("min_probability_agreement", 0.65)
    mean_th = det10.consensus_cfg.get("mean_probability_threshold", 0.70)
    std_th = det10.consensus_cfg.get("max_std_threshold", 0.12)
    min_crest = det10.consensus_cfg.get("min_crest_db", 12.0)
    min_peak = det10.consensus_cfg.get("min_peak_amplitude", 0.20)
    weight = det10.consensus_cfg.get("consensus_weight", 0.70)

    if m_min >= min_prob and crest >= min_crest and peak >= min_peak:
        cal_score = max(raw_score, weight * m_mean + (1.0 - weight) * raw_score)
        print("BMCC branch 1 triggered!")
    elif m_mean >= mean_th and m_std < std_th and crest >= min_crest and peak >= min_peak:
        blend = 0.60 * m_mean + 0.40 * raw_score
        cal_score = max(raw_score, blend)
        print("BMCC branch 2 triggered!")

print(f"Cal score: {cal_score:.3f}")

supp = det10.suppression.apply_suppression(cal_score, ys, acoustics, False)
print("Suppression result:", supp)

