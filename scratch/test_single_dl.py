import urllib.request
import json
import soundfile as sf
from pathlib import Path

out_dir = Path("gunshot/scratch/test_dl")
out_dir.mkdir(parents=True, exist_ok=True)

test_files = [
    ("test_001.survey.json", "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/FP1/test_001/test_001.survey.json"),
    ("test_001.allpulses.json", "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/FP1/test_001/test_001.allpulses.json"),
    ("test_001.audio.SCP-00-BNG-5567.json", "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/FP1/test_001/test_001.audio.SCP-00-BNG-5567.json"),
    ("test_001.audio.SCP-00-BNG-5567.wav", "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/FP1/test_001/test_001.audio.SCP-00-BNG-5567.wav")
]

for fname, url in test_files:
    p = out_dir / fname
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        p.write_bytes(resp.read())
    print(f"Downloaded {fname}: {p.stat().st_size} bytes")

info = sf.info(out_dir / "test_001.audio.SCP-00-BNG-5567.wav")
print(f"WAV Info: {info.samplerate} Hz, {info.channels} ch, {info.duration}s")

