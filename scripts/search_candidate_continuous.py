import urllib.request
import json
import urllib.parse

query = 'collection:(radio-aporee-maps) AND mediatype:(audio)'
url = 'https://archive.org/advancedsearch.php?q=' + urllib.parse.quote(query) + '&fl[]=identifier,title,creator,item_size&sort[]=item_size+desc&rows=100&output=json'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        docs = data['response']['docs']
        print(f"Total retrieved: {len(docs)}")
        # Check files inside items that have item_size between 20MB and 250MB
        for d in docs:
            sz_mb = d.get('item_size', 0) / (1024*1024)
            if 20 <= sz_mb <= 200:
                print(f"Candidate: {d.get('identifier')} | {sz_mb:.1f} MB | {d.get('title')[:40]} | {d.get('creator')}")
except Exception as e:
    print("Error:", e)

