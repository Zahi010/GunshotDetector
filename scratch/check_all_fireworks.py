import sys, os, pathlib
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import pandas as pd
from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v6 = DetectorImprovementV6()
v7 = DetectorImprovementV7()

# Check Phase 12 fireworks
p12_manifest = pd.read_csv("data/phase12_independent_test/phase12_manifest.csv")
p12_fw = p12_manifest[p12_manifest["category"] == "fireworks"]

print(f"=== Phase 12 Fireworks ({len(p12_fw)} files) ===")
for _, r in p12_fw.iterrows():
    fpath = pathlib.Path("data/phase12_independent_test") / r["relative_path"]
    y, sr = sf.read(fpath)
    v6.reset()
    res_v6 = v6.evaluate_waveform(y, sr)
    v7.reset()
    res_v7 = v7.evaluate_waveform(y, sr)
    ev6 = len(res_v6["events"])
    ev7 = len(res_v7["events"])
    status = "BOTH_OK" if (ev6==0 and ev7==0) else ("REGRESSION" if (ev6==0 and ev7>0) else "BOTH_ALERT")
    print(f"P12 {r['sample_id']}: V6={ev6} ev, V7={ev7} ev | {status}")

# Check Phase 15 fireworks
p15_manifest = pd.read_csv("data/phase15_plus_zenodo/phase15_manifest.csv")
p15_fw = p15_manifest[p15_manifest["category"] == "fireworks"]
print(f"\n=== Phase 15 Fireworks ({len(p15_fw)} files) ===")
for _, r in p15_fw.iterrows():
    fpath = pathlib.Path("data/phase15_plus_zenodo") / r["relative_path"]
    y, sr = sf.read(fpath)
    v6.reset()
    res_v6 = v6.evaluate_waveform(y, sr)
    v7.reset()
    res_v7 = v7.evaluate_waveform(y, sr)
    ev6 = len(res_v6["events"])
    ev7 = len(res_v7["events"])
    status = "BOTH_OK" if (ev6==0 and ev7==0) else ("REGRESSION" if (ev6==0 and ev7>0) else "BOTH_ALERT")
    print(f"P15 {r['sample_id']}: V6={ev6} ev, V7={ev7} ev | {status}")

