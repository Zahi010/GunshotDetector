import urllib.request
import json
import urllib.parse

query = 'collection:(radio-aporee-maps) AND mediatype:(audio) AND ("1 hour" OR "1hr" OR "30 min" OR "30min" OR "soundscape" OR "binaural" OR "continuous")'
url = 'https://archive.org/advancedsearch.php?q=' + urllib.parse.quote(query) + '&fl[]=identifier,title,creator,item_size,downloads&sort[]=downloads+desc&rows=50&output=json'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        docs = data['response']['docs']
        print(f"Retrieved {len(docs)} items:")
        for d in docs[:25]:
            sz_mb = d.get('item_size', 0) / (1024*1024)
            print(f"{d.get('identifier')} | {sz_mb:.1f} MB | {d.get('title')[:45]} | {d.get('creator')}")
except Exception as e:
    print("Error:", e)

