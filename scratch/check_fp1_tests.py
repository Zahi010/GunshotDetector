import urllib.request
import json

for i in range(1, 19):
    tname = f"test_{i:03d}"
    url = f"https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/FP1/{tname}/{tname}.survey.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        print(f"{tname}: firearm={data.get('firearm')}, rounds={data.get('num_rounds')}")
    except Exception as e:
        print(f"{tname} error:", e)

