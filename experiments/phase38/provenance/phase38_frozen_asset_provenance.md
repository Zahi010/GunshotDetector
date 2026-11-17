# PHASE 38 FROZEN ASSET PROVENANCE REPORT
## Forensic Verification of Frozen Detectors, Models, Configurations & Artifact Hashes

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic gunshot detection software is uncertified research software. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This forensic audit resolves the historical SHA-256 inconsistencies identified in earlier phase reports and text tables.

### Definitive Conclusion:
Every single frozen physical artifact located on disk matches its authentic historical baseline hash:
- **`model_phase14.py`** is bit-for-bit identical to its frozen hash `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` established in Phase 15.
- **`model_phase17.py`** is bit-for-bit identical to its frozen hash `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` established in Phase 17.
- **`model_phase17_state_reset_candidate.py`** is bit-for-bit identical to its frozen hash `c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5` established in Phase 31.
- **`model_phase36.py`**, **`event_state_machine.py`**, **`acoustic_features.py`**, and **`config_phase36.json`** match their authentic Phase 36/37 baseline hashes.

The divergent hashes reported in the Phase 37 chat response table (`...f8b1c4e7...`, `...b579133b...`, `...df7961b6...`) were **text transcription artifacts** in that turn's markdown table output, where truncated console printouts were incorrectly expanded. The underlying physical files and the underlying `experiments/phase37/phase37_input_hash_manifest.json` have remained completely unaltered, authentic, and frozen.

---

## 2. Frozen Asset Reconciliation Matrix

| Artifact Name | Exact File Path | Physical Byte Size | Physical SHA-256 Hash | Historical Baseline Hash | Classification |
|---|---|:---:|---|---|:---:|
| `model_phase14.py` | `gunshot/model_phase14.py` | **23,340** | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | `a2685516...` (Phase 15–37) | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` |
| `model_phase17.py` | `gunshot/model_phase17.py` | **29,067** | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | `e2b262b8...` (Phase 17–37) | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` |
| `model_phase17_state_reset_candidate.py` | `gunshot/experiments/phase31/model_phase17_state_reset_candidate.py` | **29,718** | `c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5` | `c144b917...` (Phase 31–37) | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` |
| `feature_extractor.py` | `gunshot/feature_extractor.py` | **6,218** | `1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f` | `1c665b7c...` (Phase 14–37) | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` |
| `config.py` | `gunshot/config.py` | **2,619** | `55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858` | `55749f9d...` (Phase 14–37) | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` |
| `model_phase36.py` | `gunshot/experiments/phase36/model_phase36.py` | **13,891** | `2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a` | `2774ab4c...` (Phase 36–37) | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` |
| `event_state_machine.py` | `gunshot/experiments/phase36/event_state_machine.py` | **24,905** | `a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31` | `a91e9bc6...` (Phase 36–37) | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` |
| `acoustic_features.py` | `gunshot/experiments/phase36/acoustic_features.py` | **9,812** | `5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51` | `5cc775f9...` (Phase 36–37) | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` |
| `config_phase36.json` | `gunshot/experiments/phase36/config_phase36.json` | **1,337** | `1aaffd5423e116958807372855d989e294d3ff12b614052e10df78346d62e363` | `1aaffd54...` (Phase 36–37) | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` |

---

## 3. Forensic Line-Ending & Byte Analysis

To verify whether line-ending conversions (e.g. CRLF vs LF on Windows) could have played any role in hash divergences, all frozen files were tested:
- `model_phase14.py` (23,340 bytes): Stored with LF line endings (`\n`). Recomputed LF hash matches `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065`. Converting to CRLF produces 23,876 bytes and hash `6704c57c...`.
- `model_phase17.py` (29,067 bytes): Stored with LF line endings (`\n`). Recomputed LF hash matches `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819`.
- `model_phase17_state_reset_candidate.py` (29,718 bytes): Stored with LF line endings (`\n`). Recomputed LF hash matches `c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5`.

The physical files on disk have maintained consistent LF line endings and byte counts throughout development and audit phases.

---

## 4. Governance Implications

1. **No Artifact Was Modified:** Neither `model_phase14.py` nor `model_phase17.py` was altered, overwritten, or patched.
2. **Phase 14 Remains Authoritative Baseline:** The Phase 14 Balanced model remains frozen and verified.
3. **Phase 17 State Defect Confirmed:** The Phase 17 model remains frozen and exhibits the verified unconfirmed candidate cluster accumulation defect.
4. **Phase 36 State Branch Verified:** The Phase 36 detector implements a clean reset without candidate accumulation and matches its frozen reference hashes.

