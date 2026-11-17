import urllib.request
import json

candidate_ids = [
    ("p40_cont_01_tartu", "aporee_27491_31684", "Estonia_Tartu_Courtyard_2015", "Patrick McGinley", "CC BY-NC-SA 3.0"),
    ("p40_cont_02_tromsdalen", "aporee_64126_73974", "Norway_Tromsdalen_Forest_2023", "Angus Carlyle", "CC BY 3.0"),
    ("p40_cont_03_bruxelles", "aporee_48288_54924", "Belgium_Bruxelles_Park_2020", "Flavien Gillié", "CC BY 3.0"),
    ("p40_cont_04_sivry", "aporee_26063_30146", "Belgium_SivryRance_Woods_2015", "Simon Lebel", "CC BY 3.0"),
    ("p40_cont_05_hamburg", "aporee_32438_37296", "Germany_Hamburg_Port_2016", "Patrick McGinley", "CC BY-NC-SA 3.0"),
    ("p40_cont_06_abcoude", "aporee_41314_47135", "Netherlands_Abcoude_Rural_2018", "Jillis Molenaar", "CC BY 3.0"),
    ("p40_cont_07_chindrieux", "aporee_60009_68925", "France_Savoie_Lake_2022", "Georges Castagne", "CC BY 3.0"),
    ("p40_cont_08_yeruham", "aporee_66803_77279", "Israel_Negev_Desert_2023", "Eyal Nach", "CC BY 3.0")
]

print("Inspecting candidate item files on Archive.org...")
valid_downloads = []

for cid, ident, camp, creator, lic in candidate_ids:
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
                    valid_downloads.append({
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
    json.dump(valid_downloads, out_f, indent=2)
print(f"Found {len(valid_downloads)} valid stream downloads. Saved candidate_streams_to_acquire.json.")

