import urllib.request
import time

u = "https://zenodo.org/records/13893977/files/clipsforzenodo.zip?download=1"
req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read(5 * 1024 * 1024) # 5 MB
    elapsed = time.time() - t0
    print(f"Downloaded {len(data)/(1024*1024):.2f} MB in {elapsed:.2f}s ({len(data)/(1024*1024)/elapsed:.2f} MB/s)")
except Exception as e:
    print("Download error:", e)

