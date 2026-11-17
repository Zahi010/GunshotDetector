import urllib.request
import json

base_url = "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18"

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

print("Evaluating best sensor for each test...")
selected_sensors = {}

for fp, tname, desc in candidate_tests:
    pulses_url = f"{base_url}/{fp}/{tname}/{tname}.allpulses.json"
    req = urllib.request.Request(pulses_url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            pulses = json.loads(resp.read().decode())
        
        sensors = {}
        for p in pulses:
            sn = p["serial_number"]
            if sn not in sensors:
                sensors[sn] = []
            sensors[sn].append(p)
            
        # Select sensor with highest max SNR
        best_sn = None
        best_snr = -999.0
        for sn, plist in sensors.items():
            avg_snr = sum(p["signal_to_noise_dB"] for p in plist) / len(plist)
            if avg_snr > best_snr:
                best_snr = avg_snr
                best_sn = sn
                
        selected_sensors[(fp, tname)] = (best_sn, best_snr, len(sensors[best_sn]))
        print(f"[{fp}] {tname} ({desc}): Best Sensor {best_sn} (avg SNR: {best_snr:.1f} dB, {len(sensors[best_sn])} pulses)")
    except Exception as e:
        print(f"Error {fp} {tname}: {e}")

