import urllib.request
import time
from pathlib import Path

url = "https://zenodo.org/api/records/18561165/files/CP_18_Exterior_30-06-16_18%2C30h.wav/content"
out_p = Path("E:/gunshot/gunshot/scratch/CP_18_Exterior.wav")

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
t0 = time.time()
print("Starting download...")
try:
    with urllib.request.urlopen(req, timeout=60) as resp, open(out_p, "wb") as f:
        while chunk := resp.read(1024*1024):
            f.write(chunk)
    elapsed = time.time() - t0
    sz_mb = out_p.stat().st_size / (1024*1024)
    print(f"Downloaded {sz_mb:.2f} MB in {elapsed:.2f}s ({sz_mb/elapsed:.2f} MB/s)")
except Exception as e:
    print("Download failed:", e)

