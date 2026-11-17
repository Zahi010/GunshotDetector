import pandas as pd
import pathlib
import json
import hashlib
import soundfile as sf

repo = pathlib.Path('E:/gunshot/gunshot')
p38_data_dir = repo / 'experiments/phase38/dataset'

# Load positive and distractor catalogs
pos_df = pd.read_csv(p38_data_dir / 'phase38_positive_catalog.csv')
dist_df = pd.read_csv(p38_data_dir / 'phase38_distractor_catalog.csv')

# Continuous streams metadata
cont_streams = [
    {
        'recording_id': 'p38_cont_01_goussainville',
        'filename': 'goussainville_1hr_continuous.mp3',
        'partition': 'PARTITION_PROSPECTIVE_CONTINUOUS',
        'category': 'CONTINUOUS_AMBIENT',
        'source_dataset': 'Radio_Aporee_Maps_ArchiveOrg',
        'uploader_session': 'Vincent Duseigne',
        'campaign_id': 'France_Urban_ValDOise_2018',
        'location': 'Goussainville, Val-d\'Oise, France',
        'license': 'CC BY 3.0',
        'license_url': 'http://creativecommons.org/licenses/by/3.0/',
        'file_path': 'experiments/phase38/dataset/continuous/goussainville_1hr_continuous.mp3'
    },
    {
        'recording_id': 'p38_cont_02_binche',
        'filename': 'binche_34min_continuous.mp3',
        'partition': 'PARTITION_PROSPECTIVE_CONTINUOUS',
        'category': 'CONTINUOUS_AMBIENT',
        'source_dataset': 'Radio_Aporee_Maps_ArchiveOrg',
        'uploader_session': 'Vincent Duseigne',
        'campaign_id': 'Belgium_Industrial_Hainaut_2018',
        'location': 'Binche, Hainaut, Belgium',
        'license': 'CC BY 3.0',
        'license_url': 'http://creativecommons.org/licenses/by/3.0/',
        'file_path': 'experiments/phase38/dataset/continuous/binche_34min_continuous.mp3'
    },
    {
        'recording_id': 'p38_cont_03_hautmont',
        'filename': 'hautmont_10min_continuous.mp3',
        'partition': 'PARTITION_PROSPECTIVE_CONTINUOUS',
        'category': 'CONTINUOUS_AMBIENT',
        'source_dataset': 'Radio_Aporee_Maps_ArchiveOrg',
        'uploader_session': 'Vincent Duseigne',
        'campaign_id': 'France_Nord_Suburban_2018',
        'location': 'Hautmont, Nord, France',
        'license': 'CC BY 3.0',
        'license_url': 'http://creativecommons.org/licenses/by/3.0/',
        'file_path': 'experiments/phase38/dataset/continuous/hautmont_10min_continuous.mp3'
    },
    {
        'recording_id': 'p38_cont_04_courcelles',
        'filename': 'courcelles_6min_continuous.mp3',
        'partition': 'PARTITION_PROSPECTIVE_CONTINUOUS',
        'category': 'CONTINUOUS_AMBIENT',
        'source_dataset': 'Radio_Aporee_Maps_ArchiveOrg',
        'uploader_session': 'Vincent Duseigne',
        'campaign_id': 'Belgium_Industrial_Factory_2018',
        'location': 'Courcelles, Hainaut, Belgium',
        'license': 'CC BY 3.0',
        'license_url': 'http://creativecommons.org/licenses/by/3.0/',
        'file_path': 'experiments/phase38/dataset/continuous/courcelles_6min_continuous.mp3'
    },
    {
        'recording_id': 'p38_cont_05_hameln',
        'filename': 'hameln_train_continuous.mp3',
        'partition': 'PARTITION_PROSPECTIVE_CONTINUOUS',
        'category': 'CONTINUOUS_AMBIENT',
        'source_dataset': 'Radio_Aporee_Maps_ArchiveOrg',
        'uploader_session': 'sonoquilibrium',
        'campaign_id': 'Germany_Rail_Station_2021',
        'location': 'Hameln, Niedersachsen, Germany',
        'license': 'Public Domain Mark 1.0',
        'license_url': 'http://creativecommons.org/publicdomain/mark/1.0/',
        'file_path': 'experiments/phase38/dataset/continuous/hameln_train_continuous.mp3'
    },
    {
        'recording_id': 'p38_cont_06_neringos',
        'filename': 'neringos_forest_continuous.mp3',
        'partition': 'PARTITION_PROSPECTIVE_CONTINUOUS',
        'category': 'CONTINUOUS_AMBIENT',
        'source_dataset': 'Radio_Aporee_Maps_ArchiveOrg',
        'uploader_session': 'john grzinich',
        'campaign_id': 'Lithuania_Curonian_Spit_2015',
        'location': 'Neringos sav., Lithuania',
        'license': 'CC BY-NC-ND 3.0',
        'license_url': 'http://creativecommons.org/licenses/by-nc-nd/3.0/',
        'file_path': 'experiments/phase38/dataset/continuous/neringos_forest_continuous.mp3'
    },
    {
        'recording_id': 'p38_cont_07_devon',
        'filename': 'devon_wind_continuous.mp3',
        'partition': 'PARTITION_PROSPECTIVE_CONTINUOUS',
        'category': 'CONTINUOUS_AMBIENT',
        'source_dataset': 'Radio_Aporee_Maps_ArchiveOrg',
        'uploader_session': 'Andy Dickinson',
        'campaign_id': 'UK_Rural_Devon_2014',
        'location': 'Dartington, Devon, UK',
        'license': 'CC BY 3.0',
        'license_url': 'http://creativecommons.org/licenses/by/3.0/',
        'file_path': 'experiments/phase38/dataset/continuous/devon_wind_continuous.mp3'
    }
]

cont_rows = []
for cs in cont_streams:
    full_p = repo / cs['file_path']
    data = full_p.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    info = sf.info(str(full_p))
    cs['sha256'] = sha
    cs['size_bytes'] = len(data)
    cs['duration_seconds'] = round(info.duration, 4)
    cs['sample_rate_hz'] = info.samplerate
    cs['channels'] = info.channels
    cont_rows.append(cs)

cont_df = pd.DataFrame(cont_rows)

# Assemble Master Dataset Registry
registry_records = []

# 1. Continuous streams
for idx, row in cont_df.iterrows():
    registry_records.append({
        'recording_id': row['recording_id'],
        'filename': row['filename'],
        'relative_path': row['file_path'],
        'partition': row['partition'],
        'category': row['category'],
        'source_dataset': row['source_dataset'],
        'campaign_or_session': row['campaign_id'],
        'uploader_or_creator': row['uploader_session'],
        'location_metadata': row['location'],
        'license': row['license'],
        'duration_seconds': row['duration_seconds'],
        'sample_rate_hz': row['sample_rate_hz'],
        'channels': row['channels'],
        'sha256': row['sha256'],
        'annotated_events_count': 0,
        'provenance_status': 'NEWLY_SOURCED_VERIFIED'
    })

# 2. Positive clips
for idx, row in pos_df.iterrows():
    registry_records.append({
        'recording_id': row['recording_id'],
        'filename': row['filename'],
        'relative_path': f"experiments/phase38/dataset/positive/{row['filename']}",
        'partition': row['partition'],
        'category': 'GUNSHOT_POSITIVE',
        'source_dataset': row['source_dataset'],
        'campaign_or_session': f"fsd50k_session_{row['uploader_session']}",
        'uploader_or_creator': row['uploader_session'],
        'location_metadata': row['title'],
        'license': row['license'],
        'duration_seconds': row['duration_seconds'],
        'sample_rate_hz': row['sample_rate_hz'],
        'channels': row['channels'],
        'sha256': row['sha256'],
        'annotated_events_count': int(row['annotated_rounds_count']),
        'provenance_status': 'NEWLY_SOURCED_VERIFIED'
    })

# 3. Distractor clips
for idx, row in dist_df.iterrows():
    registry_records.append({
        'recording_id': row['recording_id'],
        'filename': row['filename'],
        'relative_path': f"experiments/phase38/dataset/distractors/{row['filename']}",
        'partition': row['partition'],
        'category': row['distractor_category'],
        'source_dataset': row['source_dataset'],
        'campaign_or_session': f"fsd50k_session_{row['uploader_session']}",
        'uploader_or_creator': row['uploader_session'],
        'location_metadata': row['title'],
        'license': row['license'],
        'duration_seconds': row['duration_seconds'],
        'sample_rate_hz': row['sample_rate_hz'],
        'channels': row['channels'],
        'sha256': row['sha256'],
        'annotated_events_count': 0,
        'provenance_status': 'NEWLY_SOURCED_VERIFIED'
    })

master_registry_df = pd.DataFrame(registry_records)
out_registry_csv = repo / 'experiments/phase38/dataset/phase38_dataset_registry.csv'
master_registry_df.to_csv(out_registry_csv, index=False)
print(f"Saved master dataset registry to {out_registry_csv} ({len(master_registry_df)} total recordings)")

# Build License Register
license_records = []
for lic, group in master_registry_df.groupby('license'):
    license_records.append({
        'license_type': lic,
        'recordings_count': len(group),
        'partitions_represented': "; ".join(sorted(group['partition'].unique())),
        'sources_represented': "; ".join(sorted(group['source_dataset'].unique())),
        'commercial_use_permitted': 'Yes' if 'nc' not in lic.lower() else 'No (Non-Commercial Research Only)',
        'redistribution_permitted': 'Yes' if 'nd' not in lic.lower() else 'Yes (Unmodified with Attribution)',
        'attribution_required': 'Yes' if 'zero' not in lic.lower() and 'public' not in lic.lower() else 'No (Public Domain / CC0)'
    })

lic_df = pd.DataFrame(license_records)
out_lic_csv = repo / 'experiments/phase38/dataset/phase38_dataset_license_register.csv'
lic_df.to_csv(out_lic_csv, index=False)
print(f"Saved license register to {out_lic_csv} ({len(lic_df)} unique license regimes)")

