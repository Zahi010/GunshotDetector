import sys
import urllib.request
import json
import urllib.parse

sys.stdout.reconfigure(encoding='utf-8')

# Search for Zenodo records with large WAV files (>= 100MB)
queries = [
    '"soundscape" "wav" continuous',
    '"ambient" "wav" continuous',
    '"field recording" "wav" 30 minutes',
    '"acoustic monitoring" "wav" 1 hour'
]

for q in queries:
    url = "https://zenodo.org/api/records?q=" + urllib.parse.quote(q) + "&size=4"
    req = urllib.request.Request(url, headers={'User-Agent': 'GunshotResearchPhase16/1.0'})
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
                    if any(key.lower().endswith(ext) for ext in ['.wav', '.flac', '.mp3']) and sz_mb >= 50.0:
                        print(f"     Direct Audio: {key} ({sz_mb:.1f} MB) -> {f.get('links', {}).get('self')}")
    except Exception as e:
        print("Error:", e)
