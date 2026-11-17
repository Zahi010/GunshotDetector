import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v6 = DetectorImprovementV6()
v7 = DetectorImprovementV7()
p12_cont_path = 'data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav'
block_len = 16000 * 30
with sf.SoundFile(p12_cont_path) as f:
    for blk_idx in [20, 40, 60, 80, 100, 190, 210, 230]:
        f.seek(blk_idx * block_len)
        blk = f.read(block_len, dtype='float32')
        v6.reset()
        res_v6 = v6.evaluate_waveform(blk, 16000)
        v7.reset()
        res_v7 = v7.evaluate_waveform(blk, 16000)
        print(f"=== Block {blk_idx} ===")
        print(f"  V6 ({len(res_v6['events'])} events):")
        for ev in res_v6['events']:
            print(f"    t={ev['start_time']:.2f}s, score={ev['peak_score']:.4f}, crest={ev['peak_crest_db']:.2f}dB, trigger={ev.get('trigger_type')}")
        print(f"  V7 ({len(res_v7['events'])} events):")
        for ev in res_v7['events']:
            print(f"    t={ev['start_time']:.2f}s, score={ev['peak_score']:.4f}, crest={ev['peak_crest_db']:.2f}dB, trigger={ev.get('trigger_type')}")
