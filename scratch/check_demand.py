import urllib.request
import json

url = 'https://zenodo.org/api/records/1227121'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    print(f"Total files in DEMAND (1227121): {len(data.get('files', []))}")
    for f in data.get('files', []):
        key = f.get('key', '')
        if '_16k.zip' in key:
            sz_mb = f.get('size', 0) / (1024*1024)
            print(f"  {key}: {sz_mb:.1f} MB")
except Exception as e:
    print('Failed:', e)

