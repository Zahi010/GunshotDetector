import json
from datetime import datetime

with open("gunshot/scratch/check_test_metadata.py") as f:
    pass

# Read sensor json timestamp
sensor_url = "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/FP1/test_001/test_001.audio.SCP-00-BNG-5567.json"
import urllib.request
req = urllib.request.Request(sensor_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    sensor_meta = json.loads(resp.read().decode())

pulses_url = "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/FP1/test_001/test_001.allpulses.json"
req = urllib.request.Request(pulses_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    pulses_meta = json.loads(resp.read().decode())

print("Sensor start timestamp UTC:", sensor_meta["timestamp"])
t_start = datetime.fromisoformat(sensor_meta["timestamp"].replace("Z", "+00:00"))

# Find pulses for this sensor serial number
sensor_sn = sensor_meta["serial_number"]
sensor_pulses = [p for p in pulses_meta if p["serial_number"] == sensor_sn]
print(f"Pulses detected by sensor {sensor_sn}: {len(sensor_pulses)}")
for p in sensor_pulses:
    t_pulse = datetime.fromisoformat(p["arrival_time_utc"].replace("Z", "+00:00"))
    rel_time = (t_pulse - t_start).total_seconds()
    print(f"  Pulse at {p['arrival_time_utc']} -> relative offset in WAV: {rel_time:.3f} s (SNR: {p['signal_to_noise_dB']:.1f} dB, Power: {p['power_dB_SPL']:.1f} dB SPL)")

