import json

with open('e:/FSD50K.dev_audio/FSD50K.metadata/eval_clips_info_FSD50K.json') as f:
    info = json.load(f)

for target in ['balloon', 'door slam', 'backfire', 'firework', 'glass', 'hammer', 'thunder']:
    matches = []
    for k, v in info.items():
        text = f"{v.get('title','')} {v.get('description','')} {' '.join(v.get('tags',[]))}".lower()
        if target in text:
            matches.append((k, v.get('title')))
    print(f"Target '{target}': {len(matches)} matches in eval clips info")
    for m in matches[:5]:
        print(f"   {m[0]}: {m[1]}")

