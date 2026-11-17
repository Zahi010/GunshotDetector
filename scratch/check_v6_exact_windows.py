import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6, EventState

v6 = DetectorImprovementV6()
p12_cont_path = 'data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav'
block_len = 16000 * 30
win_size = 15360
hop_size = 7680

cases = [(20, 57), (40, 32), (60, 7)]
with sf.SoundFile(p12_cont_path) as f:
    for blk_idx, w in cases:
        f.seek(blk_idx * block_len)
        blk = f.read(block_len, dtype='float32')
        v6.reset()
        for i in range(w + 1):
            win = blk[i*hop_size : i*hop_size + win_size]
            t = i * 0.48
            feat, ys, acoustics = v6.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
            mode, _, _ = v6.estimator.update(rolloff, hi, mid, lo, m2l, t, i)
            raw_s = float(v6.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
            supp = v6.suppression.apply_suppression(raw_s, ys, acoustics, v6.fsm.state == EventState.CONFIRMED)
            adj_s = supp["adjusted_score"]
            st, ev = v6.fsm.step(adj_s, crest, t, acoustics, mode)
            if i == w:
                print(f"Blk {blk_idx} w={w}: raw={raw_s:.4f}, adj={adj_s:.4f}, supp={supp['suppressed']}, cat={supp['category']}, crest={crest:.2f}dB, mode={mode.value}, st={st}, ev={ev is not None}")
