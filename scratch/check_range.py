import urllib.request

u = "https://zenodo.org/records/13893977/files/clipsforzenodo.zip?download=1"
req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0", "Range": "bytes=0-1024"})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print("Range request status:", resp.status)
        print("Content-Range:", resp.headers.get("Content-Range"))
        print("Bytes received:", len(resp.read()))
except Exception as e:
    print("Range error:", e)

