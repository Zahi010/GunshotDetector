import urllib.request
import json

base_url = "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18"

# Test selection across 6 different Firing Points
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
    # Session 6: FP7
    ("FP7", "test_091", "45_cal_burst_3"),
    ("FP7", "test_094", "45_cal_single_1"),
    ("FP7", "test_097", "40_cal_burst_3"),
    ("FP7", "test_103", "9mm_burst_3")
]

print(f"Investigating {len(candidate_tests)} tests across 6 firing positions...")
total_rounds = 0

for fp, tname, desc in candidate_tests:
    s_url = f"{base_url}/{fp}/{tname}/{tname}.survey.json"
    req = urllib.request.Request(s_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            s_data = json.loads(resp.read().decode())
        rounds = s_data.get("num_rounds", 1)
        total_rounds += rounds
        print(f"[{fp}] {tname}: {s_data.get('firearm')} - Rounds: {rounds} ({desc})")
    except Exception as e:
        print(f"Error {tname}:", e)

print(f"\nTotal physical gunshot events in this candidate selection: {total_rounds}")

