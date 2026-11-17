import json
import hashlib
import soundfile as sf
from pathlib import Path

raw_dir = Path("E:/gunshot/gunshot/data/phase19_independent_positive/raw")
norm_dir = Path("E:/gunshot/gunshot/data/phase19_independent_positive/normalized_16k")

tests = [
    ("FP1", "test_001", "SCP-00-BNQ-1409"),
    ("FP1", "test_004", "SCP-00-BNQ-1120"),
    ("FP1", "test_007", "SCP-00-BNQ-1635"),
    ("FP1", "test_013", "SCP-00-BNG-5567"),
    ("FP2", "test_019", "SCP-00-BNQ-0559"),
    ("FP2", "test_022", "SCP-00-BNQ-0559"),
    ("FP2", "test_025", "SCP-00-BNQ-0559"),
    ("FP2", "test_031", "SCP-00-BNQ-0559"),
    ("FP3", "test_037", "SCP-00-BNQ-2143"),
    ("FP3", "test_040", "SCP-00-BNG-5545"),
    ("FP3", "test_043", "SCP-00-BNQ-2143"),
    ("FP3", "test_049", "SCP-00-BNQ-2143"),
    ("FP4", "test_055", "SCP-00-BNQ-1651"),
    ("FP4", "test_058", "SCP-00-BNG-5606"),
    ("FP4", "test_061", "SCP-00-BNG-5573"),
    ("FP4", "test_067", "SCP-00-BNQ-1705"),
    ("FP5", "test_127", "SCP-00-BNQ-1392"),
    ("FP5", "test_130", "SCP-00-BNQ-2167"),
    ("FP5", "test_133", "SCP-00-BNQ-0933"),
    ("FP5", "test_139", "SCP-00-BNQ-1493")
]

for fp, tname, sn in tests:
    raw_wav = raw_dir / f"{tname}.audio.{sn}.wav"
    raw_json = raw_dir / f"{tname}.audio.{sn}.json"
    survey_json = raw_dir / f"{tname}.survey.json"
    norm_wav = norm_dir / f"P19-CAT-A-{fp}-{tname}.wav"
    
    with open(survey_json) as f:
        s_data = json.load(f)
    with open(raw_json) as f:
        meta_data = json.load(f)
        
    info_raw = sf.info(raw_wav)
    info_norm = sf.info(norm_wav)
    
    print(f"[{fp}] {tname}: {s_data['firearm']} | Rounds: {s_data['num_rounds']} | Sensor: {sn}")
    print(f"  Raw: {info_raw.samplerate}Hz, {info_raw.frames} samples ({info_raw.duration}s)")
    print(f"  Norm: {info_norm.samplerate}Hz, {info_norm.frames} samples ({info_norm.duration}s)")
    print(f"  Timestamp UTC: {meta_data['timestamp']}")

