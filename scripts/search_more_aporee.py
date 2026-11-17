import urllib.request
import json
import urllib.parse

query = 'collection:(radio-aporee-maps) AND mediatype:(audio) AND item_size:[20000000 TO 150000000]'
url = 'https://archive.org/advancedsearch.php?q=' + urllib.parse.quote(query) + '&fl[]=identifier,title,creator,item_size,description&sort[]=item_size+desc&rows=60&output=json'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        docs = json.loads(resp.read())['response']['docs']
        print(f"Retrieved {len(docs)} items:")
        candidates = []
        for d in docs:
            ident = d.get('identifier')
            title = d.get('title', 'Unknown')
            creator = d.get('creator', 'Unknown')
            sz_mb = d.get('item_size', 0) / (1024*1024)
            candidates.append({
                'identifier': ident,
                'title': title,
                'creator': creator,
                'size_mb': sz_mb
            })
            print(f"{ident} | {sz_mb:.1f} MB | {title[:40]} | {creator}")
except Exception as e:
    print("Error:", e)

