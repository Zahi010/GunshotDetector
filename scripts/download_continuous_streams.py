import urllib.request
import pathlib
import time
import hashlib

dest_dir = pathlib.Path('E:/gunshot/gunshot/experiments/phase38/dataset/continuous')
dest_dir.mkdir(parents=True, exist_ok=True)

streams_to_download = [
    {
        'id': 'p38_cont_01_goussainville',
        'url': 'https://archive.org/download/aporee_40024_45718/goussainville01058h28192.mp3',
        'filename': 'goussainville_1hr_continuous.mp3',
        'campaign': 'France_Urban_Abandonment_2018',
        'location': 'Goussainville, Val-d\'Oise, France',
        'creator': 'Vincent Duseigne',
        'license': 'CC BY 3.0',
        'expected_duration_s': 3600.04
    },
    {
        'id': 'p38_cont_02_binche',
        'url': 'https://archive.org/download/aporee_40066_45764/ressaix100511h45.mp3',
        'filename': 'binche_34min_continuous.mp3',
        'campaign': 'Belgium_Industrial_Spoil_2018',
        'location': 'Binche, Hainaut, Belgium',
        'creator': 'Vincent Duseigne',
        'license': 'CC BY 3.0',
        'expected_duration_s': 2040.06
    },
    {
        'id': 'p38_cont_03_hautmont',
        'url': 'https://archive.org/download/aporee_39890_45578/hautmont22047h37.mp3',
        'filename': 'hautmont_10min_continuous.mp3',
        'campaign': 'France_Nord_Suburban_2018',
        'location': 'Hautmont, Nord, France',
        'creator': 'Vincent Duseigne',
        'license': 'CC BY 3.0',
        'expected_duration_s': 600.06
    },
    {
        'id': 'p38_cont_04_courcelles',
        'url': 'https://archive.org/download/aporee_40939_46727/rouxagcpigeons05087h20.mp3',
        'filename': 'courcelles_6min_continuous.mp3',
        'campaign': 'Belgium_Industrial_Factory_2018',
        'location': 'Courcelles, Hainaut, Belgium',
        'creator': 'Vincent Duseigne',
        'license': 'CC BY 3.0',
        'expected_duration_s': 360.08
    },
    {
        'id': 'p38_cont_05_hameln',
        'url': 'https://archive.org/download/aporee_53029_60598/PotniskiVlak.mp3',
        'filename': 'hameln_train_continuous.mp3',
        'campaign': 'Germany_Rail_Station_2021',
        'location': 'Hameln, Niedersachsen, Germany',
        'creator': 'sonoquilibrium',
        'license': 'Public Domain Mark 1.0',
        'expected_duration_s': 141.45
    },
    {
        'id': 'p38_cont_06_neringos',
        'url': 'https://archive.org/download/aporee_30411_34998/NidaForestambiencesoft.mp3',
        'filename': 'neringos_forest_continuous.mp3',
        'campaign': 'Lithuania_Curonian_Spit_2015',
        'location': 'Neringos sav., Lithuania',
        'creator': 'john grzinich',
        'license': 'CC BY-NC-ND 3.0',
        'expected_duration_s': 180.24
    },
    {
        'id': 'p38_cont_07_devon',
        'url': 'https://archive.org/download/aporee_22715_26368/DartWind200414Fades.mp3',
        'filename': 'devon_wind_continuous.mp3',
        'campaign': 'UK_Rural_Devon_2014',
        'location': 'Dartington, Devon, UK',
        'creator': 'Andy Dickinson',
        'license': 'CC BY 3.0',
        'expected_duration_s': 110.42
    }
]

print(f"Starting acquisition of {len(streams_to_download)} prospective continuous streams...")
total_sec = sum(s['expected_duration_s'] for s in streams_to_download)
print(f"Total target continuous duration: {total_sec:.2f} s ({total_sec/3600:.2f} hours)")

for s in streams_to_download:
    dest_path = dest_dir / s['filename']
    if dest_path.exists() and dest_path.stat().st_size > 10000:
        print(f"[ALREADY EXISTS] {s['filename']} ({dest_path.stat().st_size} bytes)")
        continue
    print(f"[DOWNLOADING] {s['filename']} from {s['url']}...")
    t0 = time.time()
    try:
        req = urllib.request.Request(s['url'], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        dest_path.write_bytes(data)
        elapsed = time.time() - t0
        sha = hashlib.sha256(data).hexdigest()
        print(f"  -> SUCCESS: {len(data)} bytes in {elapsed:.1f}s | SHA-256: {sha[:16]}...")
    except Exception as e:
        print(f"  -> ERROR downloading {s['filename']}: {e}")

