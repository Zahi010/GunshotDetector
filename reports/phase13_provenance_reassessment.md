# Phase 13 Provenance Reassessment & Source-Independence Audit

> **SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

---

## 1. Executive Reassessment and Incident Reconciliation

In Phase 12, an audit confirmed that zero cryptographic file hashes overlapped between the new benchmark and prior development partitions. However, Phase 12 disclosed in Section 4 that three ShotSpotter urban acoustic sensor files originated from the same Chicago incident request (`ChicagoILDistrict7_312 Request 4072698`) as the Phase 7 diagnostic set.

### Reconciliation of Source Independence
- **The Core Problem:** A differing cryptographic hash or a different microphone channel does **not** establish acoustic independence if the sensor is capturing the same physical gunfire incident.
- **Physical Shared Context:** In a multi-sensor urban array, all sensors record the exact same weapon discharges, muzzle blasts, supersonic shockwaves, local atmospheric conditions (temperature, humidity, wind), and urban street reflections.
- **Formal Finding:** Different sensor channels from a single physical incident are **correlated multi-channel observations**, not independent generalization tests.
- **Resolution:** In Phase 13, all multi-sensor recordings of previously examined incidents are formally classified as **Previously Examined Incident or Source**. They must not be claimed as zero-shot independent generalization benchmarks.

---

## 2. Definitive Provenance Classification Matrix

Every acoustic subset across the project's history is classified into one of five rigorous tiers:

| Acoustic Subset | File Count | Tier Classification | Justification & Prior Project Influence |
| :--- | :--- | :--- | :--- |
| **Phase 1–4 Training / Val Partitions** | 210 | **Previously examined development data** | Checkpoints for MLP, CatBoost, LightGBM, and XGBoost were directly trained on these files. |
| **Phase 5–6 Historical Test Partitions** | 47 | **Previously examined development data** | Used to tune operational decision thresholds (0.690 to 0.750). |
| **Phase 7 Diagnostic Set (Mitchell & ShotSpotter D5/D7)**| 239 | **Previously examined development data** | Examined to diagnose short-event detection failures and multi-window confirmation requirements. |
| **Phase 8–9 Diagnostic Set (Mitchell Ballistic & ESC-50)**| 246 | **Previously examined development data** | Examined to design semantic suppression rules for thunder, fire, and dogs. |
| **Phase 12 ShotSpotter D7 Sensors (`c7ba`, `da57`, `e058`)** | 3 | **Previously examined incident or source** | Distinct sensor channels and hashes, but record the identical physical gunfire incident as Phase 7. |
| **Phase 12 Mitchell Ballistic Gunshots (`testing/`)** | 45 | **New recording from previously represented source** | Acquired from the untouched `testing/` directory of the Mitchell Roberts repository. |
| **Phase 12 ESC-50 Negative Clips (Untouched Folds)** | 80 | **New recording from previously represented source** | Acquired from untouched categories and folds of the ESC-50 repository. |
| **Phase 12 Impulsive Range Mimics (`loud noises 1-10..29`)** | 20 | **New recording from previously represented source** | Untouched non-gunshot testing partition of the Mitchell Roberts repository. |
| **Phase 12 Controlled Edge Cases (`label = -1`)** | 5 | **Genuinely unexamined source** | Project-native controlled acoustic edge-case synthesis lab. |
| **Phase 12 Continuous Negative Stream (2.0 hrs)** | 1 | **New recording from previously represented source** | Assembled by crossfading unexamined ESC-50 negative clips. |

---

## 3. Strict Development vs Evaluation Boundaries for Phase 13

1. **Phase 12 Benchmark Status:** The entire Phase 12 dataset (`data/manifests/phase12_independent_eval_manifest.csv`) has been examined. Per Non-Negotiable Rule 3, **it is now classified as DIAGNOSTIC ONLY.**
2. **No Reverse Contamination:** No Phase 12 test recordings may be transferred into training or validation sets.
3. **Controlled Development Pool:** Phase 13 experiments must be conducted exclusively on verified development data, with final continuous validation evaluated on a newly assembled, source-tracked continuous benchmark.
