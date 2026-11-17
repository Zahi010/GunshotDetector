import urllib.request
import json

urls = [
    ("survey", "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/FP1/test_001/test_001.survey.json"),
    ("pulses", "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/FP1/test_001/test_001.allpulses.json"),
    ("sensor_json", "https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/FP1/test_001/test_001.audio.SCP-00-BNG-5567.json")
]

for name, u in urls:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"=== {name} ===")
            print(json.dumps(data, indent=2)[:800])
    except Exception as e:
        print(f"Error {name}:", e)

