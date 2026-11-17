import urllib.request
import time

url = 'https://zenodo.org/records/7004819/files/edge-collected-gunshot-audio.zip?download=1'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Range': 'bytes=0-5242880'})
t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    elapsed = time.time() - t0
    mb = len(data) / (1024*1024)
    speed = mb / elapsed
    print(f"Downloaded {mb:.2f} MB in {elapsed:.2f}s ({speed:.2f} MB/s)")
except Exception as e:
    print('Failed:', e)
