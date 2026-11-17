import urllib.request
import json

req = urllib.request.Request(
    'https://archive.org/advancedsearch.php?q=' + urllib.parse.quote('collection:(radio-aporee-maps) AND ("Vincent Duseigne" OR soundscape OR ambient OR continuous)') + '&fl[]=identifier,title,creator,description,downloads&sort[]=downloads+desc&rows=100&output=json',
    headers={'User-Agent': 'Mozilla/5.0'}
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        docs = data['response']['docs']
        print(f"Retrieved {len(docs)} documents")
        # Let's inspect items with 'Duseigne' or check metadata
        duseigne_items = [d for d in docs if 'Duseigne' in d.get('creator', '') or 'Vincent' in d.get('title', '')]
        print(f"Duseigne items: {len(duseigne_items)}")
        for d in duseigne_items[:10]:
            print(f"- {d.get('identifier')} | {d.get('title')}")
except Exception as e:
    print('Error:', e)

