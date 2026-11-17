import urllib.request
import json
import urllib.parse

records_to_search = [
    'DEMAND Diverse Environments Multichannel Acoustic Noise Database',
    'A Collection of Fully-Annotated Soundscape Recordings from the Southwestern Amazon Basin',
    'Dataset of Environmental Audio Recordings Containing Chainsaw Events',
    'Multi-Environment Audio Dataset using RPi-based Sound Logger'
]

for rec in records_to_search:
    url = 'https://zenodo.org/api/records?q=' + urllib.parse.quote(rec) + '&size=3'
    req = urllib.request.Request(url, headers={'User-Agent': 'GunshotResearchPhase16/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            hits = data.get('hits', {}).get('hits', [])
            print(f"\n=== Search: {rec[:40]}... ({len(hits)} hits) ===")
            for h in hits:
                meta = h.get('metadata', {})
                print(f"  ID: {h.get('id')} | Title: {meta.get('title')}")
                for f in h.get('files', [])[:5]:
                    sz_mb = f.get('size', 0) / (1024*1024)
                    print(f"     {f.get('key')} ({sz_mb:.1f} MB) -> {f.get('links', {}).get('self')}")
    except Exception as e:
        print("Error:", e)
