import csv
import hashlib
import pathlib

root = pathlib.Path('E:/gunshot')
repo = root / 'gunshot'

rows = [
    {
        'artifact_name': 'model_phase14.py',
        'file_path': 'gunshot/model_phase14.py',
        'physical_byte_size': 23340,
        'physical_sha256': 'a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065',
        'historical_reported_sha256': 'a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065',
        'phase37_text_reported_sha256': 'a268551604ae8b73f8b1c4e7cfce0dfca2996e382d628eb4bb8e6c7c00e1be39',
        'phase37_manifest_sha256': 'a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical file matches historical record across 21+ phase documents and phase37_input_hash_manifest.json. Discrepancy was a text transcription error in Phase 37 chat table.'
    },
    {
        'artifact_name': 'model_phase17.py',
        'file_path': 'gunshot/model_phase17.py',
        'physical_byte_size': 29067,
        'physical_sha256': 'e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819',
        'historical_reported_sha256': 'e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819',
        'phase37_text_reported_sha256': 'e2b262b866fdd5d7b579133bb7f54c1fc18ba7dc151837c768991b15488c0353',
        'phase37_manifest_sha256': 'e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical file matches historical record across 17+ phase documents and phase37_input_hash_manifest.json. Discrepancy was a text transcription error in Phase 37 chat table.'
    },
    {
        'artifact_name': 'model_phase17_state_reset_candidate.py',
        'file_path': 'gunshot/experiments/phase31/model_phase17_state_reset_candidate.py',
        'physical_byte_size': 29718,
        'physical_sha256': 'c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5',
        'historical_reported_sha256': 'c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5',
        'phase37_text_reported_sha256': 'c144b917b5653278df7961b6c0082987a0b3b44b6f722369680c10b42f1f0a1d',
        'phase37_manifest_sha256': 'c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical file matches Phase 31/32/36 test records and phase37_input_hash_manifest.json. Discrepancy was a text transcription error in Phase 37 chat table.'
    },
    {
        'artifact_name': 'feature_extractor.py',
        'file_path': 'gunshot/feature_extractor.py',
        'physical_byte_size': 6218,
        'physical_sha256': '1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f',
        'historical_reported_sha256': '1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f',
        'phase37_text_reported_sha256': '1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f',
        'phase37_manifest_sha256': '1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical file matches historical freeze records and all manifests.'
    },
    {
        'artifact_name': 'config.py',
        'file_path': 'gunshot/config.py',
        'physical_byte_size': 2619,
        'physical_sha256': '55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858',
        'historical_reported_sha256': '55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858',
        'phase37_text_reported_sha256': '55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858',
        'phase37_manifest_sha256': '55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical file matches historical freeze records and all manifests.'
    },
    {
        'artifact_name': 'model_phase36.py',
        'file_path': 'gunshot/experiments/phase36/model_phase36.py',
        'physical_byte_size': 13891,
        'physical_sha256': '2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a',
        'historical_reported_sha256': '2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a',
        'phase37_text_reported_sha256': '2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a',
        'phase37_manifest_sha256': '2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical file matches Phase 36/37 manifests and unit tests.'
    },
    {
        'artifact_name': 'event_state_machine.py',
        'file_path': 'gunshot/experiments/phase36/event_state_machine.py',
        'physical_byte_size': 24905,
        'physical_sha256': 'a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31',
        'historical_reported_sha256': 'a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31',
        'phase37_text_reported_sha256': 'a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31',
        'phase37_manifest_sha256': 'a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical file matches Phase 36/37 manifests and unit tests.'
    },
    {
        'artifact_name': 'acoustic_features.py',
        'file_path': 'gunshot/experiments/phase36/acoustic_features.py',
        'physical_byte_size': 9812,
        'physical_sha256': '5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51',
        'historical_reported_sha256': '5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51',
        'phase37_text_reported_sha256': '5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51',
        'phase37_manifest_sha256': '5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical file matches Phase 36/37 manifests and unit tests.'
    },
    {
        'artifact_name': 'config_phase36.json',
        'file_path': 'gunshot/experiments/phase36/config_phase36.json',
        'physical_byte_size': 1337,
        'physical_sha256': '1aaffd5423e116958807372855d989e294d3ff12b614052e10df78346d62e363',
        'historical_reported_sha256': '1aaffd5423e116958807372855d989e294d3ff12b614052e10df78346d62e363',
        'phase37_text_reported_sha256': '1aaffd5423e116958807372855d989e294d3ff12b614052e10df78346d62e363',
        'phase37_manifest_sha256': '1aaffd5423e116958807372855d989e294d3ff12b614052e10df78346d62e363',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical file matches Phase 36/37 manifests and configuration.'
    },
    {
        'artifact_name': 'gunshot_detection_phase34.zip',
        'file_path': 'gunshot_detection_phase34.zip',
        'physical_byte_size': 4552249,
        'physical_sha256': '1c961893c89285a48c5bf2a61a09b3dd71860febc12ac2fb56f0e43fd2a41208',
        'historical_reported_sha256': '1c961893c89285a48c5bf2a61a09b3dd71860febc12ac2fb56f0e43fd2a41208',
        'phase37_text_reported_sha256': '1c961893c89285a48c5bf2a61a09b3dd71860febc12ac2fb56f0e43fd2a41208',
        'phase37_manifest_sha256': '1c961893c89285a48c5bf2a61a09b3dd71860febc12ac2fb56f0e43fd2a41208',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical archive intact, CRC PASS. Discrepancy in historical prompt was documentation copy-paste transposition.'
    },
    {
        'artifact_name': 'gunshot_detection_phase35.zip',
        'file_path': 'gunshot_detection_phase35.zip',
        'physical_byte_size': 4561967,
        'physical_sha256': '142402f6d48c8167124807d0a5389ed322dd9e57e676f3dd5c3971ab8635f707',
        'historical_reported_sha256': '142402f6d48c8167124807d0a5389ed322dd9e57e676f3dd5c3971ab8635f707',
        'phase37_text_reported_sha256': '142402f6d48c8167124807d0a5389ed322dd9e57e676f3dd5c3971ab8635f707',
        'phase37_manifest_sha256': '142402f6d48c8167124807d0a5389ed322dd9e57e676f3dd5c3971ab8635f707',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical archive intact, CRC PASS.'
    },
    {
        'artifact_name': 'gunshot_detection_phase36.zip',
        'file_path': 'gunshot_detection_phase36.zip',
        'physical_byte_size': 137665,
        'physical_sha256': '44240bd32145fe0972cee5e7b088fe9524b2504b0b3d30a602703ba837174385',
        'historical_reported_sha256': '44240bd32145fe0972cee5e7b088fe9524b2504b0b3d30a602703ba837174385',
        'phase37_text_reported_sha256': '44240bd32145fe0972cee5e7b088fe9524b2504b0b3d30a602703ba837174385',
        'phase37_manifest_sha256': '44240bd32145fe0972cee5e7b088fe9524b2504b0b3d30a602703ba837174385',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical archive intact, CRC PASS.'
    },
    {
        'artifact_name': 'gunshot_detection_phase37_audit.zip',
        'file_path': 'gunshot_detection_phase37_audit.zip',
        'physical_byte_size': 28814,
        'physical_sha256': '4d107c2c92de8d3580474cfb1a0f56566322f2525c5f7f04c472fa8398da7eb9',
        'historical_reported_sha256': '4d107c2c92de8d3580474cfb1a0f56566322f2525c5f7f04c472fa8398da7eb9',
        'phase37_text_reported_sha256': '4d107c2c92de8d3580474cfb1a0f56566322f2525c5f7f04c472fa8398da7eb9',
        'phase37_manifest_sha256': '4d107c2c92de8d3580474cfb1a0f56566322f2525c5f7f04c472fa8398da7eb9',
        'classification': 'PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD',
        'reconciliation_notes': 'Physical audit archive intact, CRC PASS.'
    }
]

out_path = repo / 'experiments/phase38/provenance/phase38_frozen_asset_hash_reconciliation.csv'
out_path.parent.mkdir(parents=True, exist_ok=True)

with open(out_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(rows)} records to {out_path}")

