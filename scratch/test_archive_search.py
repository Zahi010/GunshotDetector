import urllib.request
import json
import urllib.parse

# Search for actual environmental field recordings
queries = [
    'title:("traffic") AND mediatype:audio AND format:(VBR MP3)',
    'title:("rain" OR "thunderstorm") AND mediatype:audio AND format:(VBR MP3)',
    'title:("forest" OR "birds" OR "birdsong") AND mediatype:audio AND format:(VBR MP3)',
    'title:("urban" OR "street" OR "city") AND mediatype:audio AND format:(VBR MP3)',
    'title:("subway" OR "train" OR "industrial" OR "factory") AND mediatype:audio AND format:(VBR MP3)',
    'title:("indoor" OR "room" OR "office" OR "crowd") AND mediatype:audio AND format:(VBR MP3)'
]

for q in queries:
    url = 'https://archive.org/advancedsearch.php?q=' + urllib.parse.quote(q) + '&fl[]=identifier,title,downloads,format&sort[]=downloads+desc&rows=5&page=1&output=json'
    req = urllib.request.Request(url, headers={'User-Agent': 'GunshotResearchPhase16/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            docs = data.get('response', {}).get('docs', [])
            print(f"\n--- Query: {q[:30]}... ({len(docs)} found) ---")
            for d in docs:
                print(f"  {d.get('identifier')} | {d.get('title')}")
    except Exception as e:
        print('Search error:', e)
