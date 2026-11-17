import urllib.request
import json

req = urllib.request.Request(
    'https://archive.org/advancedsearch.php?q=' + urllib.parse.quote('creator:"Vincent Duseigne"') + '&fl[]=identifier,title,date,description&rows=50&output=json',
    headers={'User-Agent': 'Mozilla/5.0'}
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        docs = data['response']['docs']
        print(f"Total Vincent Duseigne items: {len(docs)}")
        for d in docs[:15]:
            print(f"- {d.get('identifier')} | {d.get('title')}")
except Exception as e:
    print('Error:', e)

