import urllib.request
import json

base_url = "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18"

# Check test_001, test_004, test_019, test_037
for fp, tname in [("FP1", "test_001"), ("FP1", "test_004"), ("FP2", "test_019"), ("FP3", "test_037")]:
    url = f"{base_url}/{fp}/{tname}/{tname}.allpulses.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        pulses = json.loads(resp.read().decode())
    
    # group by sensor serial number
    sensors = {}
    for p in pulses:
        sn = p["serial_number"]
        if sn not in sensors:
            sensors[sn] = []
        sensors[sn].append(p)
    
    print(f"\n[{fp}] {tname} total pulses: {len(pulses)}, unique sensors: {len(sensors)}")
    for sn, p_list in sensors.items():
        max_snr = max(p["signal_to_noise_dB"] for p in p_list)
        max_spl = max(p["power_dB_SPL"] for p in p_list)
        print(f"  Sensor {sn}: {len(p_list)} pulses, max SNR={max_snr:.1f} dB, max SPL={max_spl:.1f} dB")

