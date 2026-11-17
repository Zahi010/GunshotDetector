import urllib.request
import soundfile as sf
import os

url = "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/FP1/test_001/test_001.audio.SCP-00-BNG-5567.wav"
out_path = "gunshot/scratch/sample_pittsburgh.wav"

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=15) as resp:
    data = resp.read()

with open(out_path, "wb") as f:
    f.write(data)

info = sf.info(out_path)
print("File:", out_path)
print("Samplerate:", info.samplerate)
print("Channels:", info.channels)
print("Duration:", info.duration, "seconds")
print("Frames:", info.frames)
print("Format:", info.format, info.subtype)

