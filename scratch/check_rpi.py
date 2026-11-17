import urllib.request
import json

url = 'https://zenodo.org/api/records/7493820'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    print(f"Total files in 7493820: {len(data.get('files', []))}")
    total_sz = 0
    for f in data.get('files', []):
        sz_mb = f.get('size', 0) / (1024*1024)
        total_sz += sz_mb
        print(f"  {f.get('key')}: {sz_mb:.1f} MB")
    print(f"Total size: {total_sz:.1f} MB")
except Exception as e:
    print('Failed:', e)
