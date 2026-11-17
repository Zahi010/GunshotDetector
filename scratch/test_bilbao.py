import urllib.request
import json

url = "https://zenodo.org/api/records/18561165"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())

files = data.get('files', [])
print(f"Total files in Zenodo 18561165: {len(files)}")
total_bytes = sum(f.get('size', 0) for f in files)
print(f"Total size: {total_bytes / (1024*1024):.1f} MB")
for f in files[:10]:
    sz_mb = f.get('size', 0) / (1024*1024)
    print(f"  {f.get('key')}: {sz_mb:.1f} MB")
