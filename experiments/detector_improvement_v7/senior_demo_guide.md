# Senior Demonstration & Operator Guide: Detector Improvement V7

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!WARNING]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code developed strictly for acoustic signal processing and forensic audio research. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Demonstration Objective

This guide provides a structured walkthrough for senior engineers, researchers, and stakeholders to evaluate the **Detector Improvement V7** prototype.

The demonstration covers:
1. Web Dashboard interface navigation and model version selection.
2. Clean open-air gunshot detection with millisecond-scale latency.
3. Degraded pocket-occluded gunshot detection via dynamic channel estimation.
4. Robust rejection of challenging non-gunshot transients (aerial fireworks, firecrackers, heavy door slams).
5. Real-world urban field gunfire detection on independent ShotSpotter field recordings.
6. Continuous stream evaluation and real-time microphone testing.

---

## 2. Environment Setup & Launch Instructions

### 2.1 Starting the Demonstration Server
1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd E:\gunshot\gunshot
   python app.py
   ```
2. Open a modern web browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```
3. Verify that the mandatory safety banner is clearly visible across the header:
   ```
   RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
   ```

### 2.2 Selecting the Detector Model
- Locate the **Model Architecture** dropdown on the dashboard control panel.
- The default detector remains `Phase 14 (Frozen Baseline)`.
- Select `Detector Improvement V7 (Recovered & Discriminated)` to engage the V7 pipeline.
- Notice that all historical models (`Phase 14`, `V2`, `V3`, `V4`, `V5`, `V6`) remain fully accessible for side-by-side comparative verification.

---

## 3. Curated Demonstration Tracks

The following 6 demonstration tracks represent key acoustic operational regimes. All files are pre-loaded in the repository.

### Track 1: Genuine Open-Air Gunshot (Clean Acoustic Impulse)
- **File:** `data/phase12_independent_test/gunshot_clean/phase12_gunshot_clean_ar15_single_01.wav`
- **Acoustic Characteristics:** Sharp rise-time ($<2\text{ ms}$), high crest factor ($>16\text{ dB}$), balanced spectral rolloff.
- **Walkthrough Steps:**
  1. Click **Choose File** in the web dashboard and upload the file.
  2. Click **Analyze Recording**.
- **Expected Results:**
  - **Detector Decision:** `GUNSHOT DETECTED` (Green Alert Badge).
  - **Confidence Score:** $>0.95$.
  - **Channel Mode:** `CLEAR_NORMAL`.
  - **Trigger Mechanism:** `single_impulse_exception`.
  - **Inference Latency:** $<25\text{ ms}$.

---

### Track 2: Degraded / Pocket-Occluded Gunshot (Acoustic Absorption)
- **File:** `data/phase12_independent_test/gunshot_pocket/phase12_gunshot_pocket_glock9mm_single_02.wav`
- **Acoustic Characteristics:** Heavy high-frequency attenuation ($f > 2.5\text{ kHz}$ attenuated by textile fabric), reduced crest factor ($11.5 - 13.0\text{ dB}$).
- **Walkthrough Steps:**
  1. Upload the file and run analysis.
- **Expected Results:**
  - **Detector Decision:** `GUNSHOT DETECTED`.
  - **Online Condition Estimator:** Successfully transitions from `UNKNOWN` to `DEGRADED_OCCLUDED`.
  - **Confirmation Barrier:** Dynamically lowers threshold to $0.62$ and single-impulse crest factor to $10.5\text{ dB}$.
  - **Outcome:** Genuine event confirmed despite physical textile blockage.

---

### Track 3: Pyrotechnic Challenge (Aerial Fireworks Shell Burst)
- **File:** `data/phase12_independent_test/fireworks/phase12_fireworks_aerial_shell_burst_01.wav`
- **Acoustic Characteristics:** Loud explosive burst with prolonged chemical crackle and absence of ballistic supersonic crack.
- **Walkthrough Steps:**
  1. Upload the file and run analysis.
- **Expected Results:**
  - **Detector Decision:** `NO GUNSHOT DETECTED` (Clean Rejection).
  - **Raw Score:** High raw classifier confidence ($>0.85$).
  - **Suppression Category:** `fireworks_dominant` ($fw\_s \ge 0.45, fw\_s / pure\_gun \ge 1.8$).
  - **Calibrated Adjusted Score:** Attenuated to $<0.20$ (below threshold $0.70$).
  - **Outcome:** False alarm completely averted.

---

### Track 4: Heavy Mechanical Environmental Impact (Door Slam)
- **File:** `data/phase12_independent_test/environmental_urban/phase12_env_door_heavy_slam_01.wav`
- **Acoustic Characteristics:** High low-frequency mechanical thud, rapid high-frequency decay.
- **Walkthrough Steps:**
  1. Upload the file and run analysis.
- **Expected Results:**
  - **Detector Decision:** `NO GUNSHOT DETECTED`.
  - **Suppression Category:** `sub_bass_thud` or `mechanical_impact`.
  - **Outcome:** Zero false alerts emitted.

---

### Track 5: Real-World Urban Field Gunfire (ShotSpotter Field Audio)
- **File:** `data/phase19_independent_positive/normalized_16k/P19-CAT-A-FP1-test_004.wav`
- **Acoustic Characteristics:** Multi-path urban canyon reverberation with simultaneous explosive shockwave and pyrotechnic class activation.
- **Walkthrough Steps:**
  1. Upload the file and run analysis under **V6**: Observe missed detection (score attenuated to $0.2365$).
  2. Switch dropdown to **V7**: Observe instant detection (score recovered to $0.7212$, confirmed event).
- **Expected Results:**
  - **Ballistic Shockwave Override:** $bal\_s \ge 0.40 \land bal\_s \ge 0.85 \times fw\_s$ successfully protects genuine field gunfire from false fireworks suppression.

---

### Track 6: Continuous Audio Stream Evaluation
- **File:** `data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav`
- **Demonstration:**
  1. Use the **Stream Prerecorded Audio** tab.
  2. Select 30-second blocks across the 2-hour recording.
  3. Verify that urban background ambient noise and distant traffic do not trigger spurious alarms.

---

## 4. Live Microphone Testing & Verification

1. In the dashboard, switch to the **Live Microphone** tab.
2. Grant browser microphone permissions.
3. Observe real-time audio visualization:
   - Energy floor meter tracks ambient room noise.
   - Channel mode indicator displays `CLEAR_NORMAL` or `UNKNOWN`.
4. Produce non-hazardous acoustic sounds (hand claps, finger snaps, key jingles):
   - Hand clap: Observe peak crest factor and instantaneous rejection by ballistic coherence.
   - Key jingle: High frequencies ($>3\text{ kHz}$) correctly classified as non-target.
5. Verify average processing latency per hop remains $<25\text{ ms}$.

---

## 5. Technical Reviewer Checklist

| Evaluation Criterion | Expected Behavior | V7 Status |
| :--- | :--- | :---: |
| Mandatory Safety Banner | Displayed on all views | Pass |
| Clean Gunshot Detection | Rapid single-round detection ($score > 0.90$) | Pass |
| Pocket-Occluded Gunshot | Recall $\ge 55\%$ under heavy fabric occlusion | Pass |
| Fireworks Discrimination | Zero false alarms on Phase 15 holdout | Pass |
| Glass Shatter Discrimination | Zero false alarms on Phase 12 holdout | Pass |
| Field Gunfire Recovery | Phase 19 recall recovered to $\ge 90\%$ | Pass |
| Continuous Stability | 6.08 hours industrial exposure at $0.00\text{ alerts/hr}$ | Pass |
| Inference Latency | $<25\text{ ms}$ CPU processing budget | Pass |

