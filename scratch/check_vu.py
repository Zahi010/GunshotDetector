import urllib.request
import re

url = "https://zenodo.org/records/13893977"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
    matches = re.findall(r"/records/13893977/files/([^\"'?]+)", html)
    print("Found files in HTML 13893977:", len(matches))
    for m in set(matches):
        print(" -", m)
except Exception as e:
    print("Error:", e)

