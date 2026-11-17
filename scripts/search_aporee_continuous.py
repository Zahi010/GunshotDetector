import urllib.request
import json

queries = [
    'collection:(radio-aporee-maps) AND (ambient OR soundscape OR street OR park OR forest OR river OR wind)',
    'mediatype:audio AND (subject:"field recording" OR subject:"soundscape") AND (licenseurl:*publicdomain* OR licenseurl:*creativecommons*)'
]

req = urllib.request.Request(
    'https://archive.org/advancedsearch.php?q=' + urllib.parse.quote('collection:(radio-aporee-maps) AND (soundscape OR ambient OR forest OR street)') + '&fl[]=identifier,title,description,downloads,licenseurl&sort[]=downloads+desc&rows=30&output=json',
    headers={'User-Agent': 'Mozilla/5.0'}
)

try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        docs = data['response']['docs']
        print(f"Found {len(docs)} documents in aporee")
        for d in docs[:15]:
            print(f"- {d.get('identifier')} | {d.get('title')[:40]} | {d.get('downloads')} dl")
except Exception as e:
    print('Error:', e)

