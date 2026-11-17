import urllib.request
import json
import pathlib
import time
import soundfile as sf
import hashlib

dest_dir = pathlib.Path("E:/gunshot/gunshot/experiments/phase39/dataset/continuous")
dest_dir.mkdir(parents=True, exist_ok=True)

test_items = [
    {
        "id": "p39_cont_01_crete_cave",
        "ident": "aporee_44627_50724",
        "campaign": "Greece_Crete_Cave_2019",
        "location": "Cave Agia Sofia, Crete, Greece",
        "creator": "alas23/sala",
        "license": "CC BY-NC-SA 3.0"
    },
    {
        "id": "p39_cont_02_bad_berka",
        "ident": "aporee_50678_61304",
        "campaign": "Germany_Thuringia_Suburban_2021",
        "location": "Bad Berka, Thuringia, Germany",
        "creator": "Samuel Kudjodzi",
        "license": "CC BY-NC 3.0"
    },
    {
        "id": "p39_cont_03_abergavenny",
        "ident": "aporee_53176_60763",
        "campaign": "UK_Wales_Garden_2021",
        "location": "Abergavenny, Monmouthshire, Wales, UK",
        "creator": "Curtis James",
        "license": "CC BY 3.0"
    },
    {
        "id": "p39_cont_04_chevilly",
        "ident": "aporee_40216_45929",
        "campaign": "France_Loiret_Irrigation_2018",
        "location": "Chevilly, Loiret, France",
        "creator": "Vincent Duseigne",
        "license": "CC BY 3.0"
    },
    {
        "id": "p39_cont_05_montataire",
        "ident": "aporee_40840_46617",
        "campaign": "France_Oise_Industrial_2018",
        "location": "Montataire, Oise, France",
        "creator": "Vincent Duseigne",
        "license": "CC BY 3.0"
    }
]

print("Fetching file details from Archive.org...")
download_queue = []
for item in test_items:
    url = f"https://archive.org/metadata/{item['ident']}/files"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            files = data.get('result', [])
            mp3s = [f for f in files if f.get('name', '').endswith('.mp3')]
            if mp3s:
                # pick largest mp3
                best = sorted(mp3s, key=lambda x: int(x.get('size', 0)), reverse=True)[0]
                download_queue.append({
                    "meta": item,
                    "filename": best['name'],
                    "url": f"https://archive.org/download/{item['ident']}/{best['name']}",
                    "size_mb": int(best.get('size', 0)) / (1024*1024)
                })
    except Exception as e:
        print(f"Error {item['ident']}: {e}")

print(f"Queue has {len(download_queue)} files:")
for q in download_queue:
    print(f"  {q['meta']['id']} | {q['size_mb']:.1f} MB | {q['url']}")

