import urllib.request
import json
import urllib.parse

queries = [
    'soundscape 1 hour wav',
    'urban ambience 60 minutes wav',
    'environmental continuous audio wav',
    'soundscape 30 minutes wav'
]

for q in queries:
    url = "https://zenodo.org/api/records?q=" + urllib.parse.quote(q) + "&size=5"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            hits = data.get('hits', {}).get('hits', [])
            print(f"\n=== Query: {q} ({len(hits)} hits) ===")
            for h in hits:
                meta = h.get('metadata', {})
                print(f"  ID: {h.get('id')} | Title: {meta.get('title')}")
                for f in h.get('files', []):
                    sz_mb = f.get('size', 0) / (1024*1024)
                    key = f.get('key', '')
                    if any(key.lower().endswith(ext) for ext in ['.wav', '.flac']) and sz_mb >= 50.0:
                        print(f"     Direct Audio: {key} ({sz_mb:.1f} MB) -> {f.get('links', {}).get('self')}")
    except Exception as e:
        print(f"Query {q} failed:", e)
