import urllib.request
import json

candidate_ids_2 = [
    ("p40_cont_09_bad_berka_suburban", "aporee_57990_66455", "Germany_Thuringia_Suburban_2022", "Samuel Kudjodzi", "CC BY-NC 3.0"),
    ("p40_cont_10_portland_first", "aporee_71321_85712", "USA_Oregon_Portland_2023", "jmfosterpdx", "CC BY 3.0"),
    ("p40_cont_11_fukutsu_japan", "aporee_71475_83387", "Japan_Fukuoka_Fukutsu_2023", "Thomas Martin Nutt", "CC BY 3.0"),
    ("p40_cont_12_blanca_spain", "aporee_66404_76773", "Spain_Murcia_Blanca_2023", "The LFTT Library", "CC BY 3.0")
]

with open("candidate_streams_to_acquire.json") as f:
    existing = json.load(f)

for cid, ident, camp, creator, lic in candidate_ids_2:
    url = f"https://archive.org/metadata/{ident}/files"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            files = json.loads(resp.read()).get('result', [])
            for f in files:
                name = f.get('name', '')
                if name.endswith('.mp3'):
                    sz_mb = int(f.get('size', 0)) / (1024*1024)
                    length = f.get('length')
                    dl_url = f"https://archive.org/download/{ident}/{name}"
                    print(f"[{cid}] {ident} -> {name} | {sz_mb:.1f} MB | {length} s | {dl_url}")
                    existing.append({
                        "id": cid,
                        "identifier": ident,
                        "filename": f"{cid}.mp3",
                        "archive_filename": name,
                        "url": dl_url,
                        "campaign": camp,
                        "creator": creator,
                        "license": lic,
                        "size_mb": sz_mb,
                        "length": length
                    })
                    break
    except Exception as e:
        print(f"Error checking {ident}: {e}")

with open("candidate_streams_to_acquire.json", "w") as out_f:
    json.dump(existing, out_f, indent=2)
print(f"Total candidate streams: {len(existing)}. Saved candidate_streams_to_acquire.json.")

