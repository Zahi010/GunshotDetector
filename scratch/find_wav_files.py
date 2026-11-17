import urllib.request
import json
import time

base_api = "https://api.github.com/repos/ShotSpotter/research.accuracy-of-gunshot-location/contents/data/PittsburghPA_DQV_2018-12-18"

candidate_tests = [
    # Session 1: FP1
    ("FP1", "test_001", "45_cal_burst_3"),
    ("FP1", "test_004", "45_cal_single_1"),
    ("FP1", "test_007", "40_cal_burst_3"),
    ("FP1", "test_013", "9mm_burst_3"),
    # Session 2: FP2
    ("FP2", "test_019", "45_cal_burst_3"),
    ("FP2", "test_022", "45_cal_single_1"),
    ("FP2", "test_025", "40_cal_burst_3"),
    ("FP2", "test_031", "9mm_burst_3"),
    # Session 3: FP3
    ("FP3", "test_037", "45_cal_burst_3"),
    ("FP3", "test_040", "45_cal_single_1"),
    ("FP3", "test_043", "40_cal_burst_3"),
    ("FP3", "test_049", "9mm_burst_3"),
    # Session 4: FP4
    ("FP4", "test_055", "45_cal_burst_3"),
    ("FP4", "test_058", "45_cal_single_1"),
    ("FP4", "test_061", "40_cal_burst_3"),
    ("FP4", "test_067", "9mm_burst_3"),
    # Session 5: FP5
    ("FP5", "test_127", "45_cal_burst_3"),
    ("FP5", "test_130", "45_cal_single_1"),
    ("FP5", "test_133", "40_cal_burst_3"),
    ("FP5", "test_139", "9mm_burst_3"),
]

print("Querying GitHub for existing audio files in each test...")
test_audio_map = {}

for fp, tname, desc in candidate_tests:
    url = f"{base_api}/{fp}/{tname}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            files = json.loads(resp.read().decode())
        wavs = [f["name"] for f in files if f["name"].endswith(".wav")]
        test_audio_map[(fp, tname)] = wavs
        print(f"[{fp}] {tname}: found {len(wavs)} wav files: {wavs}")
    except Exception as e:
        print(f"[{fp}] {tname} Error: {e}")
    time.sleep(0.5)

print("\nSummary complete.")

