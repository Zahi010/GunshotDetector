import sys
import pathlib
import numpy as np
import soundfile as sf
import pandas as pd

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v8.model_detector_improvement_v8 import compute_physical_acoustic_features_v8

def test_broad_gunshots():
    # Check Phase 19 (46 files) and Phase 12 (47 files)
    all_files = list(pathlib.Path("e:/gunshot/gunshot/data/phase19_independent_positive").glob("**/*.wav")) + \
                list(pathlib.Path("e:/gunshot/gunshot/data/phase12_independent_test").glob("**/*.wav")) + \
                list(pathlib.Path("e:/gunshot/gunshot/data/phase15_independent_eval").glob("**/*.wav"))
    print(f"Checking {len(all_files)} broad historical gunshot/eval files...")

    violators = []
    for fpath in all_files:
        try:
            audio, sr = sf.read(str(fpath))
            if audio.ndim > 1: audio = np.mean(audio, axis=1)
            if sr != 16000:
                import librosa
                audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            audio = audio.astype(np.float32)

            win_size = 15360
            hop_size = 7680
            if len(audio) < win_size:
                y_proc = np.pad(audio, (0, win_size - len(audio)))
                n_wins = 1
            else:
                y_proc = audio
                n_wins = 1 + int((len(audio) - win_size) // hop_size)

            for w in range(n_wins):
                st = w * hop_size
                en = st + win_size
                win = y_proc[st:en]
                acoustics = compute_physical_acoustic_features_v8(win, sr=16000)
                crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
                if cent > 3300.0 and hi > 0.70 and lo < 0.01:
                    violators.append((fpath.name, cent, hi, lo))
        except Exception as e:
            pass

    print(f"Total gunshot windows matching (cent > 3300 and hi > 0.70 and lo < 0.01): {len(violators)}")
    for v in violators:
        print(v)

if __name__ == "__main__":
    test_broad_gunshots()
