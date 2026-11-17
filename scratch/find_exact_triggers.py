import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7, EventState

v7 = DetectorImprovementV7()
p12_cont_path = 'data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav'
block_len = 16000 * 30
win_size = 15360
hop_size = 7680

for blk_idx in [20, 40, 60, 80, 100, 190, 210, 230]:
    with sf.SoundFile(p12_cont_path) as f:
        f.seek(blk_idx * block_len)
        blk = f.read(block_len, dtype='float32')
    v7.reset()
    n_wins = 1 + int((len(blk) - win_size) // hop_size)
    print(f"\n=== Block {blk_idx} Window-by-Window ===")
    for w in range(n_wins):
        win = blk[w*hop_size : w*hop_size + win_size]
        t = w * 0.48
        feat, ys, acoustics = v7.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        mode, _, _ = v7.estimator.update(rolloff, hi, mid, lo, m2l, t, w)
        raw_s = float(v7.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        supp = v7.suppression.apply_suppression(raw_s, ys, acoustics, v7.fsm.state == EventState.CONFIRMED)
        adj_s = supp["adjusted_score"]
        st, ev = v7.fsm.step(adj_s, crest, t, acoustics, mode)
        if ev is not None:
            top_y = sorted([(k, v) for k, v in ys.items() if v > 0.08], key=lambda x: x[1], reverse=True)[:3]
            print(f"  EMITTED at w={w} (t={t:.2f}s, file_t={blk_idx*30+t:.2f}s):")
            print(f"    raw={raw_s:.4f}, adj={adj_s:.4f}, crest={crest:.2f}dB, cent={cent:.1f}Hz, lo={lo:.3f}, m2l={m2l:.3f}")
            print(f"    mode={mode.value}, supp_cat={supp['category']}")
            print(f"    top YAMNet: {top_y}")

