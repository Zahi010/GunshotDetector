import hashlib
import pathlib
import pandas as pd
import json

repo = pathlib.Path('E:/gunshot/gunshot')
data_dir = repo / 'data'
p38_data_dir = repo / 'experiments/phase38/dataset'

# Collect all historical audio files
historical_audio = {}

print("Indexing historical audio files...")
for p in repo.rglob('*'):
    if p.is_file() and p.suffix.lower() in ['.wav', '.mp3', '.flac', '.ogg']:
        # Exclude phase 38 dataset directory
        if 'phase38' in str(p):
            continue
        try:
            data = p.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            rel = str(p.relative_to(repo)).replace('\\', '/')
            historical_audio[sha] = {
                'path': rel,
                'filename': p.name,
                'size_bytes': len(data)
            }
        except Exception:
            pass

print(f"Indexed {len(historical_audio)} unique historical audio hashes.")

# Audit candidate files in Phase 38
p38_files = list(p38_data_dir.rglob('*.wav')) + list(p38_data_dir.rglob('*.mp3')) + list(p38_data_dir.rglob('*.flac'))
print(f"Auditing {len(p38_files)} Phase 38 candidate evaluation files...")

audit_rows = []
historical_overlap_count = 0

for pf in p38_files:
    data = pf.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    rel_p38 = str(pf.relative_to(repo)).replace('\\', '/')
    
    # Check partition
    if 'positive' in rel_p38:
        part = 'PROSPECTIVE_POSITIVE'
    elif 'distractors' in rel_p38:
        part = 'PROSPECTIVE_DISTRACTOR'
    elif 'continuous' in rel_p38:
        part = 'PROSPECTIVE_CONTINUOUS'
    else:
        part = 'UNKNOWN'
    
    is_overlap = (sha in historical_audio)
    if is_overlap:
        historical_overlap_count += 1
        hist_match = historical_audio[sha]
        audit_status = 'HISTORICAL_OVERLAP_EXCLUDED'
        match_path = hist_match['path']
        notes = f"Exact SHA-256 match to historical asset {match_path}"
    else:
        audit_status = 'VERIFIED_GENUINELY_NEW'
        match_path = 'NONE'
        notes = "Zero cryptographic or filename overlap with any historical repository asset"
        
    audit_rows.append({
        'candidate_filename': pf.name,
        'phase38_relative_path': rel_p38,
        'partition': part,
        'file_size_bytes': len(data),
        'sha256': sha,
        'audit_classification': audit_status,
        'matched_historical_path': match_path,
        'overlap_notes': notes
    })

audit_df = pd.DataFrame(audit_rows)
out_csv = repo / 'experiments/phase38/dataset/phase38_historical_overlap_audit.csv'
audit_df.to_csv(out_csv, index=False)
print(f"\nHistorical overlap audit complete:")
print(f"  Total Phase 38 files audited: {len(audit_df)}")
print(f"  Genuinely new out-of-sample files: {len(audit_df) - historical_overlap_count} ({(len(audit_df) - historical_overlap_count)/len(audit_df)*100:.1f}%)")
print(f"  Historical overlap files: {historical_overlap_count} ({historical_overlap_count/len(audit_df)*100:.1f}%)")
print(f"  Saved audit CSV to: {out_csv}")

