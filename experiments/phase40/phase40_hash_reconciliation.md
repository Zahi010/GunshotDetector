# PHASE 40 HISTORICAL HASH RECONCILIATION REPORT
## Independent Cryptographic Audit of Detector Model Files & Release Archives

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This audit conducted an independent, physical-byte verification of all six detector implementation files and six historical release archives across Phases 34–39.

### Key Forensic Findings:
1. **Physical Files Are Cryptographically Frozen (`VERIFIED_FROM_PHYSICAL_FILE`):**
   Every physical model file on disk matches its authentic historical manifest hash exactly:
   - `model_phase14.py`: `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` (23,340 bytes)
   - `model_phase17.py`: `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` (29,067 bytes)
   - `model_phase17_state_reset_candidate.py`: `c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5` (29,718 bytes)
   - `model_phase36.py`: `2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a` (13,891 bytes)
   - `event_state_machine.py`: `a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31` (24,905 bytes)
   - `acoustic_features.py`: `5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51` (9,812 bytes)

2. **Divergent Hashes in Prior Reports are Transcription Errors (`REPORT_TRANSCRIPTION_ERROR`):**
   - **Phase 37 Report Markdown:** All four model hashes printed in the Phase 37 text report share the exact 16-character hexadecimal prefix with the true physical file, but diverge completely for characters 17–64. This occurred when truncated console logs (e.g. 16-character display width) were expanded by language model completion rather than copied from raw JSON manifests.
   - **Phase 38 Chat Response Tables:** The tabular responses in Phase 38 chat emitted unverified hashes for models (e.g. `103f6f9fc53fa675...` for Phase 14) that never existed on disk, while the machine-generated JSON freeze manifest [phase38_detector_freeze_manifest.json](file:///E:/gunshot/gunshot/experiments/phase38/phase38_detector_freeze_manifest.json) recorded the correct physical hash.
   - **Phase 38 Phase 34 Archive Hash:** The Phase 38 report printed `1c9618931102be8d...` for `gunshot_detection_phase34.zip`, whereas the actual physical archive is `1c961893c89285a48c5bf2a61a09b3dd71860febc12ac2fb56f0e43fd2a41208` (matching the first 8 characters `1c961893`).

---

## 2. Core Model Hash Lineage Table

| Model File | Physical Size (B) | Authoritative Physical SHA-256 | Phase 37 Manifest | Phase 37 Printed Report | Phase 38 Manifest | Phase 38 Chat Table | Evidence Label |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| `model_phase14.py` | 23,340 | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | `a2685516...c065` (Match) | `a2685516...be39` (Prefix 16 Match) | `a2685516...c065` (Match) | `103f6f9f...6d80` (Erroneous) | `VERIFIED_FROM_PHYSICAL_FILE` |
| `model_phase17.py` | 29,067 | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | `e2b262b8...b819` (Match) | `e2b262b8...0353` (Prefix 16 Match) | `e2b262b8...b819` (Match) | `e2b262b8...115b` (Prefix 8 Match) | `VERIFIED_FROM_PHYSICAL_FILE` |
| `model_phase17_state_reset_candidate.py` | 29,718 | `c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5` | `c144b917...9ea5` (Match) | `c144b917...0a1d` (Prefix 16 Match) | `c144b917...9ea5` (Match) | `29fd13b9...1a75` (Erroneous) | `VERIFIED_FROM_PHYSICAL_FILE` |
| `model_phase36.py` | 13,891 | `2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a` | `2774ab4c...563a` (Match) | `2774ab4c...2241` (Prefix 16 Match) | `2774ab4c...563a` (Match) | `4172f3e8...9f8a` (Erroneous) | `VERIFIED_FROM_PHYSICAL_FILE` |
| `event_state_machine.py` | 24,905 | `a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31` | `a91e9bc6...3c31` (Match) | `a91e9bc6...3c31` (Match) | `a91e9bc6...3c31` (Match) | `a91e9bc6...3c31` (Match) | `VERIFIED_FROM_PHYSICAL_FILE` |
| `acoustic_features.py` | 9,812 | `5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51` | `5cc775f9...0a51` (Match) | `5cc775f9...0a51` (Match) | `5cc775f9...0a51` (Match) | `5cc775f9...0a51` (Match) | `VERIFIED_FROM_PHYSICAL_FILE` |

---

## 3. Historical Release Archive Reconciliation Table

| Archive Filename | Physical Size (Bytes) | Authoritative Physical SHA-256 | Internal File Count | ZIP CRC Integrity | Audit Status |
|---|:---:|:---:|:---:|:---:|:---|
| `gunshot_detection_phase34.zip` | 4,552,249 | `1c961893c89285a48c5bf2a61a09b3dd71860febc12ac2fb56f0e43fd2a41208` | 43 | PASS | `AUTHENTIC_FROZEN_RECORD` |
| `gunshot_detection_phase35.zip` | 4,561,967 | `142402f6d48c8167124807d0a5389ed322dd9e57e676f3dd5c3971ab8635f707` | 41 | PASS | `AUTHENTIC_FROZEN_RECORD` |
| `gunshot_detection_phase36.zip` | 137,665 | `44240bd32145fe0972cee5e7b088fe9524b2504b0b3d30a602703ba837174385` | 24 | PASS | `AUTHENTIC_FROZEN_RECORD` |
| `gunshot_detection_phase37_audit.zip` | 28,814 | `4d107c2c92de8d3580474cfb1a0f56566322f2525c5f7f04c472fa8398da7eb9` | 14 | PASS | `AUTHENTIC_FROZEN_RECORD` |
| `gunshot_detection_phase38_prospective_evaluation.zip` | 100,636 | `e75834294ddb1bfea4b321f179b984de06daf3e40df24e73e08f68bda2829765` | 22 | PASS | `AUTHENTIC_FROZEN_RECORD` |
| `gunshot_detection_phase39_evaluation.zip` | 122,871 | `42436b45c2daf86f1df8eac09bb7754d2c228de3d414be954858fb92e6653515` | 30 | PASS | `AUTHENTIC_FROZEN_RECORD` |

Full CSV lineage: [phase40_hash_history.csv](file:///E:/gunshot/gunshot/experiments/phase40/phase40_hash_history.csv).

