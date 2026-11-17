import urllib.request
import json

base_url = "https://api.github.com/repos/ShotSpotter/research.accuracy-of-gunshot-location/contents/data/PittsburghPA_DQV_2018-12-18"
req = urllib.request.Request(base_url, headers={"User-Agent": "Mozilla/5.0"})

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        fps = json.loads(resp.read().decode("utf-8"))
    print(f"Total Firing Points: {len(fps)}")
    for fp in fps:
        fp_name = fp["name"]
        # get contents of fp
        fp_req = urllib.request.Request(fp["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(fp_req, timeout=10) as fp_resp:
            tests = json.loads(fp_resp.read().decode("utf-8"))
        print(f"  {fp_name}: {len(tests)} tests (sample: {[t['name'] for t in tests[:3]]})")
except Exception as e:
    print("Error:", e)

