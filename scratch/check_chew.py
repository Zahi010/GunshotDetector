import urllib.request
import re

url = "https://zenodo.org/records/3938837"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
matches = re.findall(r'Chew%20Magna[^<]*', html)
print('matches in 3938837:', matches[:5])
size_m = re.findall(r'([0-9\.]+\s*(?:MB|GB|KB))', html)
print('Sizes in 3938837:', size_m[:10])

