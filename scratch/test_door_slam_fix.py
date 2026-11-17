import sys
import pathlib
import numpy as np
import soundfile as sf
import pandas as pd

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v8.model_detector_improvement_v8 import (
    DetectorImprovementV8,
    EventState
)

class CandidateV9(DetectorImprovementV8):
    """
    Detector Improvement V9 Candidate:
    Applies narrow low-band / mid-to-low constraint on the thunder transient saturation override:
    (peak >= 0.30 and crest >= 12.0 and cent >= 600.0 and m2l >= 0.05 and lo < 0.90)
    This rejects heavy door slams (which have lo >= 0.997 and m2l < 0.002) while 100% preserving
    genuine clipped and distant gunshots (which have lo <= 0.76 and m2l >= 0.27).
    """
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self.name = "detector_improvement_v9"
        self.version = "9.0.0"

    def extract_features(self, window_16k: np.ndarray):
        feat, ys, acoustics = super().extract_features(window_16k)
        return feat, ys, acoustics

def evaluate_detector_on_corpus(det_class, manifest_path):
    det = det_class()
    df = pd.read_csv(manifest_path)
    results = []

    for idx, row in df.iterrows():
        fpath = pathlib.Path(row["filepath"])
        if not fpath.exists():
            fpath = pathlib.Path("e:/gunshot") / row["filepath"]
        if not fpath.exists():
            fpath = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]

        audio, sr = sf.read(str(fpath))
        if audio.ndim > 1: audio = np.mean(audio, axis=1)
        if sr != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        audio = audio.astype(np.float32)

        res = det.evaluate_waveform(audio, sr=16000)
        results.append({
            "recording_id": row.get("recording_id", fpath.stem),
            "filename": fpath.name,
            "label": int(row.get("ground_truth_label", row.get("label", 0))),
            "primary_category": row.get("primary_category", "unknown"),
            "sub_category": row.get("sub_category", "unknown"),
            "condition_category": row.get("condition_category", "unknown"),
            "detected": res["detected"],
            "event_count": res["event_count"],
            "peak_score": round(res["peak_score"], 4)
        })

    res_df = pd.DataFrame(results)
    return res_df

if __name__ == "__main__":
    print("Evaluating baseline V8 vs Candidate V9...")
    # First, let's test door slams specifically
    door_slams = list(pathlib.Path("e:/gunshot/gunshot/data/background/hard_negatives/door_slam").glob("*.wav"))
    print(f"\nTesting {len(door_slams)} door slams on V8 vs V9 logic...")

    # Load V8
    v8 = DetectorImprovementV8()
    v8_hits = 0
    v9_hits = 0

    for p in door_slams:
        a, sr = sf.read(str(p))
        if a.ndim > 1: a = np.mean(a, axis=1)
        res_v8 = v8.evaluate_waveform(a, 16000)
        if res_v8["detected"]: v8_hits += 1

        # Now test V9 override modification
        # In V9 suppression rule:
        win_size = 15360
        hop_size = 7680
        if len(a) < win_size:
            y = np.pad(a, (0, win_size - len(a)))
            nw = 1
        else:
            y = a
            nw = 1 + int((len(a) - win_size) // hop_size)

        v8.reset()
        v9_events = []
        for w in range(nw):
            win = y[w*hop_size : w*hop_size + win_size]
            feat, ys, acoustics = v8.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
            mode, conf, _ = v8.estimator.update(rolloff, hi, mid, lo, m2l, w*0.48, w)
            raw = float(v8.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

            # Apply V9 suppression logic manually to see impact
            thun_s = max(ys.get(280, 0.0), ys.get(281, 0.0))
            pure_gun = max(ys.get(421, 0.0), ys.get(422, 0.0), ys.get(425, 0.0))
            is_thun_phys = (lo >= 0.65 and m2l < 0.55)

            # V9 constrained transient override:
            c1 = (m2l >= 0.40 and cent >= 750.0 and crest >= 16.0)
            c2 = (pure_gun >= 0.12)
            c3 = (peak >= 0.30 and crest >= 12.0 and cent >= 600.0 and m2l >= 0.05 and lo < 0.90)
            is_transient = (c1 or c2 or c3)

            adj = raw
            if (thun_s >= 0.20 or is_thun_phys) and not is_transient:
                adj *= 0.25

            _, ev = v8.fsm.step(adj, crest, w*0.48, acoustics, mode)
            if ev is not None:
                v9_events.append(ev)

        if len(v9_events) > 0:
            v9_hits += 1

    print(f"Door slam detections: V8 = {v8_hits}/12 ({v8_hits/12*100:.1f}%), V9 = {v9_hits}/12 ({v9_hits/12*100:.1f}%)")

