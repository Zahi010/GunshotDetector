import sys, os
sys.path.insert(0, 'E:/gunshot/gunshot')
os.chdir('E:/gunshot/gunshot')
import soundfile as sf
from experiments.detector_improvement_v4.model_detector_improvement_v4 import DetectorImprovementV4

v4 = DetectorImprovementV4(profile='balanced')
fpath = 'data/phase12_independent_test/negatives/phase12_negative_esc50_glass_breaking_3-203377-A-39.wav'
y, sr = sf.read(fpath)
res = v4.evaluate_waveform(y)
for k, v in res.items():
    print(f"{k}: {v}")
