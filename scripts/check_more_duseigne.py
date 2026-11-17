import urllib.request
import json

items = [
    'aporee_40214_45926',
    'aporee_40276_45994',
    'aporee_40939_46727',
    'aporee_40024_45718',
    'aporee_40840_46617',
    'aporee_39890_45578'
]

for item_id in items:
    url = f'https://archive.org/metadata/{item_id}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            meta = data.get('metadata', {})
            files = data.get('files', [])
            mp3s = [f for f in files if f.get('format') in ['VBR MP3', 'MP3']]
            for f in mp3s:
                size_mb = float(f.get('size', 0)) / (1024*1024)
                length_sec = f.get('length', '0')
                print(f"{item_id} | {meta.get('title')[:35]} | {f.get('name')} | {size_mb:.2f} MB | {length_sec} s")
    except Exception as e:
        print(f"Error {item_id}: {e}")

