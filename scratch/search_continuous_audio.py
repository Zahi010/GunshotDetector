import urllib.request
import json
import urllib.parse
from pathlib import Path

queries = [
    'soundscape filetype:audio',
    'field recording filetype:audio',
    'traffic ambience filetype:audio',
    'birds singing filetype:audio',
    'rain storm filetype:audio',
    'street market filetype:audio',
    'subway train filetype:audio',
    'factory industrial filetype:audio',
    'indoor ambience filetype:audio',
    'weather wind filetype:audio',
    'city soundscape filetype:audio',
    'nature soundscape filetype:audio'
]

discovered = {}

for q in queries:
    url = 'https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=' + urllib.parse.quote(q) + '&srnamespace=6&format=json&srlimit=40'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'GunshotResearchPhase16/1.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            for item in data.get('query', {}).get('search', []):
                title = item.get('title')
                if title and title not in discovered:
                    discovered[title] = q
    except Exception as e:
        print('Error searching ' + q + ':', e)

print(f'Discovered {len(discovered)} unique titles. Querying metadata...')

titles_list = list(discovered.keys())
long_recordings = []

for i in range(0, len(titles_list), 25):
    batch = titles_list[i:i+25]
    t_str = '|'.join(batch)
    url = 'https://commons.wikimedia.org/w/api.php?action=query&titles=' + urllib.parse.quote(t_str) + '&prop=imageinfo&iiprop=url|size|duration|mime&format=json'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'GunshotResearchPhase16/1.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            pages = data.get('query', {}).get('pages', {})
            for pid, pinfo in pages.items():
                title = pinfo.get('title')
                ii_list = pinfo.get('imageinfo', [])
                if ii_list:
                    ii = ii_list[0]
                    dur = ii.get('duration', 0)
                    sz = ii.get('size', 0)
                    u = ii.get('url', '')
                    mime = ii.get('mime', '')
                    if dur and dur >= 180.0:  # >= 3 minutes
                        long_recordings.append({
                            'title': title,
                            'duration': float(dur),
                            'size': int(sz),
                            'url': u,
                            'mime': mime,
                            'query': discovered.get(title, '')
                        })
    except Exception as e:
        print('Batch error:', e)

print(f'Total qualified long recordings (>= 180s): {len(long_recordings)}')
total_sec = sum(r['duration'] for r in long_recordings)
print(f'Total exposure time: {total_sec:.1f}s ({total_sec/3600:.2f} hours)')

with open('scratch/discovered_long_recordings.json', 'w') as f:
    json.dump(long_recordings, f, indent=2)

for r in sorted(long_recordings, key=lambda x: -x['duration'])[:35]:
    dur_m = r['duration'] / 60.0
    sz_mb = r['size'] / (1024 * 1024.0)
    print(f"  {r['duration']:6.1f}s ({dur_m:4.1f}m, {sz_mb:5.1f}MB) | {r['title']} | {r['query']}")
