import urllib.request
import json

base_url = "https://api.github.com/repos/ShotSpotter/research.accuracy-of-gunshot-location/contents/data/PittsburghPA_DQV_2018-12-18"
req = urllib.request.Request(base_url, headers={"User-Agent": "Mozilla/5.0"})

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        fps = json.loads(resp.read().decode("utf-8"))
    
    for fp in fps:
        fp_name = fp["name"]
        # check test 1 in each fp
        fp_req = urllib.request.Request(fp["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(fp_req, timeout=10) as fp_resp:
            tests = json.loads(fp_resp.read().decode("utf-8"))
        
        # sample first test in this FP
        first_test = tests[0]["name"]
        survey_url = f"https://raw.githubusercontent.com/ShotSpotter/research.accuracy-of-gunshot-location/master/data/PittsburghPA_DQV_2018-12-18/{fp_name}/{first_test}/{first_test}.survey.json"
        try:
            s_req = urllib.request.Request(survey_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(s_req, timeout=10) as s_resp:
                s_data = json.loads(s_resp.read().decode("utf-8"))
            print(f"{fp_name} ({first_test}): firearm={s_data.get('firearm')}, rounds={s_data.get('num_rounds')}, total_tests_in_fp={len(tests)}")
        except Exception as e:
            print(f"{fp_name} error:", e)
except Exception as e:
    print("Error:", e)

