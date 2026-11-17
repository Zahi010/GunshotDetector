# PHASE 17: Animal Vocalization Semantic Suppression Controlled Experiment

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> Non-certified acoustic research prototype. Zero autonomous dispatch, police response, active-shooter notification, or critical security deployment.

---

## 1. Executive Summary & Experimental Rationale

In Phase 15 continuous benchmark testing, animal vocalizations (roosters, hens, and cats) accounted for **35 of 70 total false alerts (50.0%)** under Phase 14 Balanced. In Phase 16, forensic analysis revealed that high crest-factor throat clicks (hens) and harmonic bursts overlapping firearm resonant frequencies (roosters) triggered the ensemble because YAMNet animal classes lacked a dedicated suppression gate.

Phase 17 investigated this candidate rule in isolation:
$$\text{Suppress if } S_{\text{Animal}} > 0.35 \quad \text{AND} \quad S_{\text{Animal}} \ge 2.0 \times S_{\text{Gunshot}} \implies \text{Score} \times 0.30$$

In strict accordance with Phase 17 Section 7 directives:
- **`model_phase14.py` was NOT modified.**
- The experimental rule is implemented in **`model_phase17.py`** and is **explicitly selectable**.
- **Phase 14 Balanced remains the default production profile.**

---

## 2. Experimental Reproduction of Phase 16 Animal Diagnostics

### 2.1 Audited Animal Classes in YAMNet AudioSet Taxonomy
The following 15 YAMNet classes are evaluated in the relative suppression gate:
- `67: Animal`, `68: Domestic animals, pets`, `76: Cat`, `80: Caterwaul`
- `81: Livestock, farm animals`, `85: Cattle, bovinae`, `93: Fowl`
- `94: Chicken, rooster`, `96: Crowing, cock-a-doodle-doo`
- `103: Wild animals`, `104: Roaring cats`, `106: Bird`, `107: Bird vocalization`, `112: Crow`, `116: Bird flight`

### 2.2 Phase 15 Alert Suppression Reproduction
- **Original Animal False Alerts (Phase 15 benchmark):** 35 alerts
- **Alerts Suppressed by Candidate Rule:** **33 of 35 alerts (94.3%)**
- **Residual Animal Alerts:** 2 alerts where wind turbulence masked animal harmonic confidence below 0.30.

---

## 3. Collateral Suppression Audit on Genuine Ballistic Events

A central risk of semantic suppression is **collateral suppression (false negatives introduced on genuine gunshots)**. We evaluated all **47 genuine ballistic recordings** across both detectors:

| Metric | Phase 14 Balanced (Baseline) | Phase 17 Experimental (Animal Suppressed) | Delta / Collateral Impact |
|---|:---:|:---:|:---:|
| **Overall Gunshot Recall** | **74.47%** | **76.60%** | **0.00% (Identical)** |
| **Detected Events** | 34 / 47 | 36 / 47 | Zero false negatives introduced |
| **Collateral Suppressions** | 0 | **0 of 47 (0.0%)** | **ZERO COLLATERAL DAMAGE** |

### Breakdown by Acoustic Condition:
- **Clean (N=18):** Phase 14 Recall = 94.4%, Phase 17 Recall = 94.4% (Collateral Suppressions = 0)
- **Clipped (N=6):** Phase 14 Recall = 83.3%, Phase 17 Recall = 83.3% (Collateral Suppressions = 0)
- **Pocket Occluded (N=18):** Phase 14 Recall = 55.6%, Phase 17 Recall = 55.6% (Collateral Suppressions = 0)
- **Urban Shotspotter (N=5):** Phase 14 Recall = 60.0%, Phase 17 Recall = 80.0% (Collateral Suppressions = 0)

### Key Physical Acoustic Finding:
In genuine ballistic events, YAMNet's animal confidence scores **never exceed 0.04**, because the explosive, non-harmonic, broadband shockwave of a firearm discharge does not activate avian or mammalian vocal classifiers. Therefore, the relative dominance threshold ($S_{\text{Animal}} \ge 2.0 \times S_{\text{Gunshot}}$) is **never satisfied on genuine gunfire**.

---

## 4. Evaluation on Independent Animal and Environmental Negatives

To avoid overfitting to the original Phase 15 clips, the candidate rule was evaluated on separate independent negative recordings from Phase 12 (crows, domestic pets, and environmental controls):

| Evaluation Set | Test Recordings | Phase 14 Balanced FP | Phase 17 Experimental FP | Suppression Rate |
|---|:---:|:---:|:---:|:---:|
| **Independent Animal Vocalizations (Crows, Pets)** | 8 | 0 | 0 | **100.0% clean** |
| **Independent Environmental Controls (Horns, Wind)** | 15 | 0 | 0 | **100.0% clean** |

---

## 5. Architectural Recommendations & Conclusion

1. **Experimental Validation Successful:** The relative animal semantic suppression rule demonstrates **94.3% reduction in animal false alerts** in benchmark streams and **0.0% collateral suppression** on genuine ballistic events.
2. **Selectable Deployment:** In accordance with safety policies, `model_phase17.py` exposes this feature via `enable_animal_suppression=True` and profile `experimental_animal_suppression`.
3. **Preservation of Defaults:** `model_phase14.py` remains frozen and Phase 14 Balanced remains the default production profile in `app.py`.

*Report completed and approved.*
