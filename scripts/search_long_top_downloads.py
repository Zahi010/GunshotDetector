import urllib.request
import json
import urllib.parse

query = 'collection:(radio-aporee-maps) AND mediatype:(audio)'
url = 'https://archive.org/advancedsearch.php?q=' + urllib.parse.quote(query) + '&fl[]=identifier,title,creator,item_size&sort[]=downloads+desc&rows=100&output=json'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15) as resp:
    docs = json.loads(resp.read())['response']['docs']

print(f"Checking top downloaded items for long MP3s...")
found = []
for d in docs[:40]:
    ident = d['identifier']
    url2 = f"https://archive.org/metadata/{ident}/files"
    try:
        r2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(r2, timeout=4) as resp2:
            files = json.loads(resp2.read()).get('result', [])
            for f in files:
                if f.get('name', '').endswith('.mp3'):
                    sz_mb = int(f.get('size', 0)) / (1024*1024)
                    dur = f.get('length')
                    if sz_mb > 15.0:
                        found.append({
                            'ident': ident,
                            'title': d['title'],
                            'creator': d.get('creator', 'Unknown'),
                            'filename': f['name'],
                            'size_mb': sz_mb,
                            'length': dur
                        })
    except Exception as e:
        pass

print(f"Found {len(found)} long MP3 files (>15MB):")
for f in sorted(found, key=lambda x: x['size_mb'], reverse=True):
    print(f"{f['ident']} | {f['size_mb']:.1f} MB | {f['length']} | {f['title'][:40]} | {f['filename']}")

