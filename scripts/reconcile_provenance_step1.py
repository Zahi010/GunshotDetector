import hashlib
import pathlib
import json
import re
import csv

repo = pathlib.Path('e:/gunshot/gunshot')
root = pathlib.Path('e:/gunshot')

targets = {
    'model_phase14.py': repo / 'model_phase14.py',
    'model_phase17.py': repo / 'model_phase17.py',
    'model_phase17_state_reset_candidate.py': repo / 'experiments/phase31/model_phase17_state_reset_candidate.py',
    'feature_extractor.py': repo / 'feature_extractor.py',
    'config.py': repo / 'config.py',
    'model_phase36.py': repo / 'experiments/phase36/model_phase36.py',
    'event_state_machine.py': repo / 'experiments/phase36/event_state_machine.py',
    'acoustic_features.py': repo / 'experiments/phase36/acoustic_features.py',
    'config_phase36.json': repo / 'experiments/phase36/config_phase36.json',
    'gunshot_detection_phase34.zip': root / 'gunshot_detection_phase34.zip',
    'gunshot_detection_phase35.zip': root / 'gunshot_detection_phase35.zip',
    'gunshot_detection_phase36.zip': root / 'gunshot_detection_phase36.zip',
    'gunshot_detection_phase37_audit.zip': root / 'gunshot_detection_phase37_audit.zip'
}

physical = {}
for name, p in targets.items():
    if p.exists():
        data = p.read_bytes()
        h = hashlib.sha256(data).hexdigest()
        size = len(data)
        physical[name] = {'exists': True, 'path': str(p).replace('\\', '/'), 'size': size, 'sha256': h}
    else:
        physical[name] = {'exists': False, 'path': str(p).replace('\\', '/'), 'size': 0, 'sha256': 'FILE_NOT_FOUND'}

# Search all reports and manifests for previously reported hashes
manifests_and_reports = list(repo.rglob('*manifest*.json')) + list(repo.rglob('*manifest*.csv')) + list(repo.rglob('*.md'))

historical_references = {}
for name in targets:
    historical_references[name] = []

hash_regex = re.compile(r'[a-f0-9]{64}', re.IGNORECASE)

for doc in manifests_and_reports:
    try:
        txt = doc.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
    rel = str(doc.relative_to(repo)).replace('\\', '/')
    for name in targets:
        if name in txt:
            # find lines mentioning name
            lines = [line for line in txt.splitlines() if name in line]
            for l in lines:
                hashes = hash_regex.findall(l)
                for h in hashes:
                    historical_references[name].append({
                        'source': rel,
                        'hash': h.lower(),
                        'line': l.strip()
                    })

print('=== Physical files and their historical mentions ===')
for name, pinfo in physical.items():
    print(f"\nArtifact: {name}")
    print(f"  Path: {pinfo['path']}")
    print(f"  Physical Size: {pinfo['size']} bytes")
    print(f"  Physical SHA-256: {pinfo['sha256']}")
    refs = historical_references[name]
    unique_hashes = set(r['hash'] for r in refs)
    print(f"  Found in {len(refs)} references across {len(set(r['source'] for r in refs))} documents")
    print(f"  Unique historical hashes cited: {len(unique_hashes)}")
    for uh in unique_hashes:
        sources = [r['source'] for r in refs if r['hash'] == uh]
        match_phys = (uh == pinfo['sha256'])
        print(f"    - Hash: {uh} | Matches Physical: {match_phys} | Count: {len(sources)} | Sample source: {sources[0]}")

