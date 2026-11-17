import urllib.request
import json
from datetime import datetime

base_url = "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18"

# Available wavs mapping from task-7166
available_wavs = {
    ("FP1", "test_001"): ['SCP-00-BNG-5567', 'SCP-00-BNG-5594', 'SCP-00-BNQ-0979', 'SCP-00-BNQ-1120', 'SCP-00-BNQ-1409', 'SCP-00-BNQ-1582'],
    ("FP1", "test_004"): ['SCP-00-BNG-5567', 'SCP-00-BNG-5594', 'SCP-00-BNQ-0979', 'SCP-00-BNQ-1120', 'SCP-00-BNQ-1409', 'SCP-00-BNQ-1582'],
    ("FP1", "test_007"): ['SCP-00-BNG-5567', 'SCP-00-BNG-5594', 'SCP-00-BNQ-0979', 'SCP-00-BNQ-1120', 'SCP-00-BNQ-1409', 'SCP-00-BNQ-1635'],
    ("FP1", "test_013"): ['SCP-00-BNG-5567', 'SCP-00-BNG-5594', 'SCP-00-BNQ-0979', 'SCP-00-BNQ-1409'],
    ("FP2", "test_019"): ['SCP-00-BNG-5137', 'SCP-00-BNQ-0559', 'SCP-00-BNQ-0681', 'SCP-00-BNQ-0696', 'SCP-00-BNQ-1159', 'SCP-00-BNQ-2069'],
    ("FP2", "test_022"): ['SCP-00-BNG-5137', 'SCP-00-BNQ-0559', 'SCP-00-BNQ-0681', 'SCP-00-BNQ-0696', 'SCP-00-BNQ-1159', 'SCP-00-BNQ-2069'],
    ("FP2", "test_025"): ['SCP-00-BNG-5137', 'SCP-00-BNQ-0559', 'SCP-00-BNQ-0681', 'SCP-00-BNQ-0696', 'SCP-00-BNQ-1159', 'SCP-00-BNQ-2069'],
    ("FP2", "test_031"): ['SCP-00-BNQ-0559', 'SCP-00-BNQ-0681', 'SCP-00-BNQ-1159', 'SCP-00-BNQ-2069'],
    ("FP3", "test_037"): ['SCP-00-BNG-5515', 'SCP-00-BNG-5545', 'SCP-00-BNG-5565', 'SCP-00-BNQ-1592', 'SCP-00-BNQ-1705', 'SCP-00-BNQ-2143'],
    ("FP3", "test_040"): ['SCP-00-BNG-5515', 'SCP-00-BNG-5545', 'SCP-00-BNG-5565', 'SCP-00-BNQ-1592', 'SCP-00-BNQ-1705', 'SCP-00-BNQ-2143'],
    ("FP3", "test_043"): ['SCP-00-BNG-5515', 'SCP-00-BNG-5545', 'SCP-00-BNQ-1705', 'SCP-00-BNQ-2143'],
    ("FP3", "test_049"): ['SCP-00-BNG-5515', 'SCP-00-BNG-5545', 'SCP-00-BNG-5565', 'SCP-00-BNQ-2143'],
    ("FP4", "test_055"): ['SCP-00-BNG-5573', 'SCP-00-BNG-5606', 'SCP-00-BNQ-1651', 'SCP-00-BNQ-1720', 'SCP-00-BNQ-1748', 'SCP-00-BNQ-2143'],
    ("FP4", "test_058"): ['SCP-00-BNG-5573', 'SCP-00-BNG-5606', 'SCP-00-BNQ-1651', 'SCP-00-BNQ-2143'],
    ("FP4", "test_061"): ['SCP-00-BNG-5125', 'SCP-00-BNG-5573', 'SCP-00-BNQ-1787', 'SCP-00-BNQ-2143'],
    ("FP4", "test_067"): ['SCP-00-BNG-5573', 'SCP-00-BNG-5606', 'SCP-00-BNQ-1651', 'SCP-00-BNQ-1705'],
    ("FP5", "test_127"): ['SCP-00-BNQ-1392', 'SCP-00-BNQ-1493', 'SCP-00-BNQ-1662', 'SCP-00-BNQ-2167'],
    ("FP5", "test_130"): ['SCP-00-BNQ-1392', 'SCP-00-BNQ-1493', 'SCP-00-BNQ-1662', 'SCP-00-BNQ-2167'],
    ("FP5", "test_133"): ['SCP-00-BNQ-0933', 'SCP-00-BNQ-1392', 'SCP-00-BNQ-1493', 'SCP-00-BNQ-1662'],
    ("FP5", "test_139"): ['SCP-00-BNQ-1392', 'SCP-00-BNQ-1493', 'SCP-00-BNQ-1662', 'SCP-00-BNQ-2167']
}

candidate_tests = [
    ("FP1", "test_001", ".45 ACP 3-round burst", 3),
    ("FP1", "test_004", ".45 ACP single shot", 1),
    ("FP1", "test_007", ".40 S&W 3-round burst", 3),
    ("FP1", "test_013", "9x19mm 3-round burst", 3),
    ("FP2", "test_019", ".45 ACP 3-round burst", 3),
    ("FP2", "test_022", ".45 ACP single shot", 1),
    ("FP2", "test_025", ".40 S&W 3-round burst", 3),
    ("FP2", "test_031", "9x19mm 3-round burst", 3),
    ("FP3", "test_037", ".45 ACP 3-round burst", 3),
    ("FP3", "test_040", ".45 ACP single shot", 1),
    ("FP3", "test_043", ".40 S&W 3-round burst", 3),
    ("FP3", "test_049", "9x19mm 3-round burst", 3),
    ("FP4", "test_055", ".45 ACP 3-round burst", 3),
    ("FP4", "test_058", ".45 ACP single shot", 1),
    ("FP4", "test_061", ".40 S&W 3-round burst", 3),
    ("FP4", "test_067", "9x19mm 3-round burst", 3),
    ("FP5", "test_127", ".45 ACP 3-round burst", 3),
    ("FP5", "test_130", ".45 ACP single shot", 1),
    ("FP5", "test_133", ".40 S&W 3-round burst", 3),
    ("FP5", "test_139", "9x19mm 3-round burst", 3),
]

selected_manifest = []

for fp, tname, desc, n_rounds in candidate_tests:
    pulses_url = f"{base_url}/{fp}/{tname}/{tname}.allpulses.json"
    req = urllib.request.Request(pulses_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        pulses = json.loads(resp.read().decode())
        
    avail = available_wavs[(fp, tname)]
    
    # Filter pulses to available sensors
    sensors = {}
    for p in pulses:
        sn = p["serial_number"]
        if sn in avail:
            if sn not in sensors:
                sensors[sn] = []
            sensors[sn].append(p)
            
    # Pick sensor with highest max SNR
    best_sn = None
    best_snr = -999.0
    for sn, plist in sensors.items():
        avg_snr = sum(p["signal_to_noise_dB"] for p in plist) / len(plist)
        if avg_snr > best_snr:
            best_snr = avg_snr
            best_sn = sn
            
    # Now get sensor json to calculate exact pulse relative arrival times
    sensor_url = f"{base_url}/{fp}/{tname}/{tname}.audio.{best_sn}.json"
    s_req = urllib.request.Request(sensor_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(s_req) as resp:
        s_meta = json.loads(resp.read().decode())
        
    t_start = datetime.fromisoformat(s_meta["timestamp"].replace("Z", "+00:00"))
    p_offsets = []
    for p in sensors[best_sn]:
        t_pulse = datetime.fromisoformat(p["arrival_time_utc"].replace("Z", "+00:00"))
        rel_s = (t_pulse - t_start).total_seconds()
        p_offsets.append((rel_s, p["signal_to_noise_dB"], p["power_dB_SPL"]))
        
    selected_manifest.append({
        "firing_point": fp,
        "test_name": tname,
        "description": desc,
        "rounds_ground_truth": n_rounds,
        "sensor_serial": best_sn,
        "wav_filename": f"{tname}.audio.{best_sn}.wav",
        "avg_snr_db": best_snr,
        "pulse_count_sensor": len(sensors[best_sn]),
        "pulse_offsets": p_offsets
    })
    print(f"[{fp}] {tname}: Best avail sensor {best_sn} (avg SNR: {best_snr:.1f} dB, pulses: {len(p_offsets)})")
    for po in p_offsets:
        print(f"    t = {po[0]:.3f}s (SNR {po[1]:.1f} dB, SPL {po[2]:.1f} dB)")

with open("gunshot/scratch/selected_pittsburgh_manifest.json", "w") as f:
    json.dump(selected_manifest, f, indent=2)
print("Saved gunshot/scratch/selected_pittsburgh_manifest.json")

