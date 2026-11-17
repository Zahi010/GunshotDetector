import urllib.request
import json
import urllib.parse

req = urllib.request.Request(
    'https://archive.org/advancedsearch.php?q=' + urllib.parse.quote('creator:"Vincent Duseigne"') + '&fl[]=identifier,title,date&rows=50&output=json',
    headers={'User-Agent': 'Mozilla/5.0'}
)

with urllib.request.urlopen(req, timeout=10) as resp:
    docs = json.loads(resp.read())['response']['docs']

print(f"Checking files for {len(docs)} items...")
candidates = []
for d in docs[:25]:
    ident = d['identifier']
    url = f"https://archive.org/metadata/{ident}/files"
    try:
        r2 = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(r2, timeout=5) as resp2:
            files = json.loads(resp2.read()).get('result', [])
            for f in files:
                if f.get('name', '').endswith('.mp3'):
                    sz_mb = int(f.get('size', 0)) / (1024*1024)
                    length_s = f.get('length', '0')
                    candidates.append({
                        'identifier': ident,
                        'title': d['title'],
                        'filename': f['name'],
                        'size_mb': sz_mb,
                        'length': length_s
                    })
    except Exception as e:
        pass

for c in sorted(candidates, key=lambda x: float(x['size_mb']), reverse=True)[:15]:
    print(f"{c['identifier']} | {c['size_mb']:.1f} MB | {c['length']} s | {c['title'][:40]} | {c['filename']}")

