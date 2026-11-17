import urllib.request
import re
import json

url = "https://github.com/9lash/spotting_gunshots/tree/master/inference_samples/gunshot_samples"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode()

m = re.findall(r'"name":\s*"([^"]+\.wav)"', html)
print("Found wav files in 9lash gunshot_samples:", set(m))

