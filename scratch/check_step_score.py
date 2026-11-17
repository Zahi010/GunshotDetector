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

# Monkey-patch step to print input score!
orig_step = det10.fsm.step
def debug_step(score, crest_db, time_s, acoustics=None, operating_mode=None):
    res = orig_step(score, crest_db, time_s, acoustics, operating_mode)
    if res[1] is not None:
        print(f"DEBUG_STEP TRIGGERED! score={score}, crest={crest_db}, time={time_s}")
    return res

det10.fsm.step = debug_step
det10.evaluate_waveform(audio, sr)

