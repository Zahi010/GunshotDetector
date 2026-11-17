import sys
import soundfile as sf
import pathlib
import pandas as pd

sys.path.insert(0, "e:/gunshot/gunshot")
import scratch.run_phase51_evaluation as p51

fpath = "e:/gunshot/gunshot/data/phase8_final_eval/gunshots/mitchell_mossberg_12g_04.wav"
audio, sr = sf.read(fpath)

res_p51 = p51.evaluate_single_pass(audio, sr)
print("P51 result on mossberg 04:", res_p51)

