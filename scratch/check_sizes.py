import urllib.request

urls = [
    ("C3GD.zip", "https://zenodo.org/records/22286299/files/C3GD.zip?download=1"),
    ("clipsforzenodo.zip", "https://zenodo.org/records/13893977/files/clipsforzenodo.zip?download=1"),
    ("CADAS", "https://zenodo.org/records/7004819/files/edge-collected-gunshot-audio.zip?download=1")
]

for name, u in urls:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        req.get_method = lambda: "HEAD"
        with urllib.request.urlopen(req, timeout=10) as resp:
            cl = resp.headers.get("Content-Length")
            sz_mb = int(cl) / (1024*1024) if cl else -1
            print(f"{name}: {sz_mb:.2f} MB ({cl} bytes), status: {resp.status}")
    except Exception as e:
        print(f"{name} Error:", e)

