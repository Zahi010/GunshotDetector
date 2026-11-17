import urllib.request
import struct

url = 'https://zenodo.org/api/records/1227121/files/NPARK_16k.zip/content'
req = urllib.request.Request(url, headers={'User-Agent': 'GunshotResearchPhase16/1.0', 'Range': 'bytes=0-100'})
with urllib.request.urlopen(req, timeout=10) as resp:
    cr = resp.headers.get('content-range', '')
    total_size = int(cr.split('/')[-1])

tail_req = urllib.request.Request(url, headers={'User-Agent': 'GunshotResearchPhase16/1.0', 'Range': f'bytes={total_size - 16384}-{total_size - 1}'})
with urllib.request.urlopen(tail_req, timeout=10) as resp:
    tail_data = resp.read()

eocd_pos = tail_data.rfind(b'\x50\x4b\x05\x06')
disk_num, cd_disk, disk_entries, cd_entries, cd_size, cd_offset, comment_len = struct.unpack('<HHHHIIH', tail_data[eocd_pos+4:eocd_pos+22])
cd_req = urllib.request.Request(url, headers={'User-Agent': 'GunshotResearchPhase16/1.0', 'Range': f'bytes={cd_offset}-{cd_offset + cd_size - 1}'})
with urllib.request.urlopen(cd_req, timeout=10) as resp:
    cd_data = resp.read()

pos = 0
while pos < len(cd_data):
    if cd_data[pos:pos+4] != b'\x50\x4b\x01\x02':
        break
    comp_method, mod_time, mod_date, crc, comp_size, uncomp_size, fn_len, extra_len, comment_len = struct.unpack('<HHHHIIHHH', cd_data[pos+10:pos+32])
    local_hdr_offset = struct.unpack('<I', cd_data[pos+42:pos+46])[0]
    fn_bytes = cd_data[pos+46:pos+46+fn_len]
    fn = fn_bytes.decode('ascii', errors='replace')
    print(f"Entry: {fn} -> offset={local_hdr_offset}, comp={comp_size/(1024*1024):.2f}MB, uncomp={uncomp_size/(1024*1024):.2f}MB, method={comp_method}")
    pos += 46 + fn_len + extra_len + comment_len
