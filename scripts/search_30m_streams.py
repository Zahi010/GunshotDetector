import urllib.request
import json
import urllib.parse

# Search radio-aporee-maps with length:[1800 TO 7200]
query = 'collection:(radio-aporee-maps) AND mediatype:(audio) AND length:[1800 TO 7200]'
url = 'https://archive.org/advancedsearch.php?q=' + urllib.parse.quote(query) + '&fl[]=identifier,title,creator,length,item_size&rows=50&output=json'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
        docs = data['response']['docs']
        print(f"Retrieved {len(docs)} items with length 30m - 2h:")
        for d in docs[:20]:
            print(f"{d.get('identifier')} | len: {d.get('length')} s | {d.get('title')[:40]} | {d.get('creator')}")
except Exception as e:
    print("Error:", e)

