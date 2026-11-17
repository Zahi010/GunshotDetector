import urllib.request
import pathlib
import time
import hashlib
import soundfile as sf

dest_dir = pathlib.Path("E:/gunshot/gunshot/experiments/phase39/dataset/continuous")
dest_dir.mkdir(parents=True, exist_ok=True)

streams_to_acquire = [
    {
        "id": "p39_cont_01_crete_cave",
        "url": "https://archive.org/download/aporee_44627_50724/1677cave.mp3",
        "filename": "crete_cave_continuous.mp3",
        "campaign": "Greece_Crete_Cave_2019",
        "location": "Cave Agia Sofia, Crete, Greece",
        "creator": "alas23/sala",
        "license": "CC BY-NC-SA 3.0"
    },
    {
        "id": "p39_cont_02_bad_berka",
        "url": "https://archive.org/download/aporee_50678_61304/RainintheNeighborhoodBinaural0606211004AM.mp3",
        "filename": "bad_berka_rain_continuous.mp3",
        "campaign": "Germany_Thuringia_Suburban_2021",
        "location": "Bad Berka, Thuringia, Germany",
        "creator": "Samuel Kudjodzi",
        "license": "CC BY-NC 3.0"
    },
    {
        "id": "p39_cont_03_abergavenny",
        "url": "https://archive.org/download/aporee_53176_60763/Day3Garden.mp3",
        "filename": "abergavenny_garden_continuous.mp3",
        "campaign": "UK_Wales_Garden_2021",
        "location": "Abergavenny, Monmouthshire, Wales, UK",
        "creator": "Curtis James",
        "license": "CC BY 3.0"
    },
    {
        "id": "p39_cont_04_chevilly",
        "url": "https://archive.org/download/aporee_40216_45929/chevilly260517h30.mp3",
        "filename": "chevilly_irrigation_continuous.mp3",
        "campaign": "France_Loiret_Irrigation_2018",
        "location": "Chevilly, Loiret, France",
        "creator": "Vincent Duseigne",
        "license": "CC BY 3.0"
    },
    {
        "id": "p39_cont_05_montataire",
        "url": "https://archive.org/download/aporee_40840_46617/montatairegoss200711h30.mp3",
        "filename": "montataire_industrial_continuous.mp3",
        "campaign": "France_Oise_Industrial_2018",
        "location": "Montataire, Oise, France",
        "creator": "Vincent Duseigne",
        "license": "CC BY 3.0"
    },
    {
        "id": "p39_cont_06_aincourt",
        "url": "https://archive.org/download/aporee_40214_45926/aincourt270512h00.mp3",
        "filename": "aincourt_sanatorium_continuous.mp3",
        "campaign": "France_ValdOise_Sanatorium_2018",
        "location": "Aincourt, Val-d'Oise, France",
        "creator": "Vincent Duseigne",
        "license": "CC BY 3.0"
    },
    {
        "id": "p39_cont_07_camping",
        "url": "https://archive.org/download/aporee_40276_45994/camping200518h00.mp3",
        "filename": "couarde_camping_continuous.mp3",
        "campaign": "France_CharenteMaritime_Coastal_2018",
        "location": "La Couarde-sur-Mer, Charente-Maritime, France",
        "creator": "Vincent Duseigne",
        "license": "CC BY 3.0"
    },
    {
        "id": "p39_cont_08_aubignan",
        "url": "https://archive.org/download/aporee_11681_13735/AubignanGewitter01.mp3",
        "filename": "aubignan_storm_continuous.mp3",
        "campaign": "France_Vaucluse_Storm_2012",
        "location": "Aubignan, Vaucluse, France",
        "creator": "Frank Schulte",
        "license": "CC BY-NC 3.0"
    },
    {
        "id": "p39_cont_09_poznan",
        "url": "https://archive.org/download/aporee_10272_31781/containerplasti.mp3",
        "filename": "poznan_balcony_continuous.mp3",
        "campaign": "Poland_GreaterPoland_Urban_2012",
        "location": "Poznan, Greater Poland, Poland",
        "creator": "Maciej Janasik",
        "license": "CC BY 3.0"
    }
]

print(f"Starting acquisition of {len(streams_to_acquire)} new prospective continuous streams...")

downloaded_catalog = []
for s in streams_to_acquire:
    dest_path = dest_dir / s["filename"]
    if dest_path.exists() and dest_path.stat().st_size > 10000:
        print(f"[ALREADY EXISTS] {s['filename']} ({dest_path.stat().st_size} bytes)")
    else:
        print(f"[DOWNLOADING] {s['filename']} from {s['url']}...")
        t0 = time.time()
        try:
            req = urllib.request.Request(s["url"], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            dest_path.write_bytes(data)
            elapsed = time.time() - t0
            print(f"  -> SUCCESS: {len(data)} bytes in {elapsed:.1f}s")
        except Exception as e:
            print(f"  -> ERROR downloading {s['filename']}: {e}")
            continue

    # Inspect downloaded file
    info = sf.info(str(dest_path))
    raw_bytes = dest_path.read_bytes()
    sha = hashlib.sha256(raw_bytes).hexdigest()
    
    downloaded_catalog.append({
        "recording_id": s["id"],
        "filename": s["filename"],
        "relative_path": str(dest_path.relative_to(pathlib.Path("E:/gunshot/gunshot"))).replace("\\", "/"),
        "campaign_or_session": s["campaign"],
        "uploader_or_creator": s["creator"],
        "location_metadata": s["location"],
        "license": s["license"],
        "duration_seconds": round(info.duration, 4),
        "sample_rate_hz": info.samplerate,
        "channels": info.channels,
        "sha256": sha
    })
    print(f"  Verified: {info.duration:.1f}s ({info.duration/60:.1f}m) | {info.samplerate}Hz | {info.channels}ch | SHA-256: {sha[:16]}...")

total_new_dur = sum(c["duration_seconds"] for c in downloaded_catalog)
print(f"\nSuccessfully acquired {len(downloaded_catalog)} new continuous streams!")
print(f"Total new continuous duration: {total_new_dur:.2f} seconds ({total_new_dur/3600:.4f} hours)")

