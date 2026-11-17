import urllib.request
import json

sample_ids = [
    'aporee_30411_34998',
    'aporee_22715_26368',
    'aporee_19705_22887',
    'aporee_40066_45764',
    'aporee_53029_60598',
    'aporee_14369_16722',
    'aporee_40216_45929',
    'aporee_44627_50724'
]

for item_id in sample_ids:
    url = f'https://archive.org/metadata/{item_id}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            meta = data.get('metadata', {})
            files = data.get('files', [])
            audio_files = [f for f in files if f.get('format') in ['VBR MP3', 'MP3', 'WAVE', 'Flac']]
            print(f"=== {item_id} ===")
            print(f"  Title: {meta.get('title')}")
            print(f"  Creator: {meta.get('creator')} | License: {meta.get('licenseurl')}")
            print(f"  Coverage: {meta.get('coverage')}")
            for af in audio_files[:3]:
                print(f"    - {af.get('name')} | {float(af.get('size',0))/(1024*1024):.2f} MB | {af.get('length')} s ({float(af.get('length',0))/60:.1f} min)")
    except Exception as e:
        print(f"Error {item_id}: {e}")

