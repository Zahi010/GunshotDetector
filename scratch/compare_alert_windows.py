import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v6 = DetectorImprovementV6()
v7 = DetectorImprovementV7()
p12_cont_path = 'data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav'
block_len = 16000 * 30
win_size = 15360
hop_size = 7680

# The new alerts in V7 were at:
# Blk 20: t=27.36s
# Blk 40: t=15.36s, t=17.76s
# Blk 60: t=3.36s, t=5.76s, t=27.84s (note: t=21.12 and 26.88 in V6 disappeared or shifted)
# Blk 80: t=10.08s, t=15.84s (note: t=13.44 in V6)
# Blk 100: t=3.84s (note: t=1.44 in V6)
# Blk 190: t=26.40s
# Blk 210: t=14.40s
# Blk 230: t=2.40s, t=21.12s

targets = [
    (20, 27.36),
    (40, 15.36),
    (40, 17.76),
    (60, 3.36),
    (60, 5.76),
    (60, 27.84),
    (80, 10.08),
    (80, 15.84),
    (100, 3.84),
    (190, 26.40),
    (210, 14.40),
    (230, 2.40),
    (230, 21.12)
]

with sf.SoundFile(p12_cont_path) as f:
    for blk_idx, target_t in targets:
        f.seek(blk_idx * block_len)
        blk = f.read(block_len, dtype='float32')
        w = int(round(target_t / 0.48))
        win = blk[w*hop_size : w*hop_size + win_size]
        feat, ys, acoustics = v6.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        raw_s = float(v6.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        
        supp_v6 = v6.suppression.apply_suppression(raw_s, ys, acoustics)
        supp_v7 = v7.suppression.apply_suppression(raw_s, ys, acoustics)
        
        print(f"Blk {blk_idx} t={target_t:.2f}s (w={w}):")
        print(f"  raw={raw_s:.4f}, crest={crest:.2f}dB, cent={cent:.1f}Hz, lo={lo:.3f}, m2l={m2l:.3f}")
        print(f"  V6 supp: cat={supp_v6['category']}, factor={supp_v6['factor']:.3f}, adj={supp_v6['adjusted_score']:.4f}")
        print(f"  V7 supp: cat={supp_v7['category']}, factor={supp_v7['factor']:.3f}, adj={supp_v7['adjusted_score']:.4f}")
        top_y = sorted([(k, v) for k, v in ys.items() if v > 0.08], key=lambda x: x[1], reverse=True)[:4]
        print(f"  Top YAMNet: {top_y}")

