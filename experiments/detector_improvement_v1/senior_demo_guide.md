# Senior Demonstration & Walkthrough Guide: Detector Improvement V1

> [!WARNING]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> This software is an uncertified acoustic research prototype. Never deploy it for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Demonstration Briefing

This walkthrough provides a clear, repeatable, and interactive demonstration protocol for senior leadership, research engineers, and evaluators to assess **Detector Improvement V1**.

### Core Problem Solved in this Sprint
Prior historical implementations exhibited two major shortcomings:
1. **Pyrotechnic False Alarms**: Phase 36 stripped semantic suppression, resulting in **57 / 100 fireworks false alarms** (+21.3% error surge).
2. **Duplicate Alert Fragmentation**: Phase 14 lacked a deterministic refractory state machine, resulting in **28 duplicate alerts** across 74 detected gunshots (27.45% duplicate rate).

### The Solution: Detector Improvement V1
Detector Improvement V1 combines **Calibrated Multi-Category Semantic Suppression V1** with a **Deterministic 4-State Refractory State Machine**:
- **Fireworks False Alarms**: Reduced from 57 down to **45** (**21.05% relative reduction** vs Phase 36).
- **Total Distractor False Alarms**: Reduced from 66 down to **52** (**21.21% relative reduction** vs Phase 36; drops to **37** under High Precision).
- **Duplicate Alerts**: Reduced from 28 down to **12** (**57.14% relative reduction** vs Phase 14).
- **Continuous Background False Alarm Rate**: Cut from 7.35 down to **6.16 alerts/hour** (**16.19% relative reduction** vs Phase 14; drops to **3.56 alerts/hour** under High Precision).
- **Computational Efficiency**: Total pipeline inference is **198.8 ms** per 960 ms audio window on standard CPU (Real-Time Factor $\text{RTF} = 0.207$, sustaining a **2.41x real-time margin**).

---

## 2. Environment Verification & Startup

### Step 1: Verify Directory and Environment
Ensure you are in the project workspace root:
```powershell
cd E:\gunshot\gunshot
```

### Step 2: Run the Automated Validation Suite
Execute the regression test suite to verify end-to-end functionality and model freeze hashes:
```powershell
pytest tests\test_detector_improvement_v1.py -v
```
*Expected Outcome: All 14 tests pass cleanly in under 45 seconds.*

### Step 3: Launch the Web Application
Start the Flask web server:
```powershell
python app.py
```
*The server will initialize the YAMNet feature extractor, load the frozen ensemble bundle, and bind to `http://127.0.0.1:5000`.*

### Step 4: Open the Dashboard
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 3. Interactive Walkthrough Protocol

The application dashboard features two primary operational modes:
1. **Continuous Live Streaming Mode** (with Pre-Recorded WAV Replay)
2. **Audio File Upload & Forensic Analysis Mode**

---

### Demonstration Track A: Pre-Recorded Benchmark WAV Replay (Zero Mic Required)

This mode allows you to demonstrate real-time streaming audio inference, state-machine transitions, and semantic suppression without requiring a physical microphone or ambient room noise.

#### Scenario 1: Authentic Gunshot Impulse (Ballistic Detection)
1. In the **Senior Walkthrough: Benchmark Audio Replay** box on the left card, click:
   $$\text{\textbf{[🔫 Gunshot Audio]}}$$
2. **Observe the Live UI Behaviors**:
   - The status bar indicates `REPLAYING: Gunshot Demo`.
   - The **RMS Audio Meter** jumps to high volume ($-12\text{ dB}$ to $-6\text{ dB}$).
   - The **Neural Gunshot Score Bar** surges past the threshold marker to $\ge 0.88$.
   - The **Live State Display** flips from `State: IDLE` $\to$ `State: CONFIRMED` (highlighted in red).
   - The **Crest Factor Display** shows sharp impulsivity ($\ge 14.0\text{ dB}$).
   - The **Red Emergency Alert Banner** appears: `ALERT: Gunshot-like Acoustic Event`.
   - The **Live Alert History Table** logs a new confirmed event record with exact timestamp, peak confidence score, duration, and status.
   - Once the audio impulse passes, the detector transitions into `State: COOLDOWN` for 2.0 seconds, preventing duplicate echo re-triggers.

#### Scenario 2: Fireworks / Pyrotechnic Challenge (False Alarm Suppression)
1. Click:
   $$\text{\textbf{[🧨 Fireworks Audio]}}$$
2. **Key Architectural Narrative for Reviewers**:
   - Explain to the audience that in Phase 36, this exact recording triggered a false alert because pyrotechnic suppression was absent.
3. **Observe the Live UI Behaviors in Detector Improvement V1**:
   - The audio contains loud, explosive cracking sounds (RMS reaches $-10\text{ dB}$).
   - The **Calibrated Semantic Suppression Engine** identifies high pyrotechnic energy ($p_{\text{fw}} > 0.30$) with low ballistic gunshot energy ($p_{\text{gun}} < 0.10$).
   - The suppression engine applies a $0.35\times$ attenuation factor.
   - The **Neural Score Bar** stays subdued in the $0.25 - 0.45$ range (well below the $0.75$ trigger threshold).
   - The **Live State Display** remains in `State: IDLE`.
   - **Zero false gunshot alerts are triggered**, demonstrating active pyrotechnic rejection!

#### Scenario 3: Urban Ambient Background (Continuous Environmental Baseline)
1. Click:
   $$\text{\textbf{[🏙️ Ambient Audio]}}$$
2. **Observe the Live UI Behaviors**:
   - Ambient urban background streams sequentially into the ring buffer.
   - Scores remain safely near $0.02 - 0.15$.
   - Audio meter registers low background flutter.
   - The detector maintains continuous clean operation.

#### Scenario 4: Replaying Any Custom Benchmark Audio
- Evaluators can click `[📁 Replay Custom WAV]`, select any local `.wav` file, and stream it sequentially through the live inference ring-buffer at native real-time speed.
- Click `[⏹ Stop Replay]` at any time to halt streaming.

---

### Demonstration Track B: Side-by-Side Architectural Toggle

Demonstrate the ability to switch between detector engines in real time:
1. Locate the **Detection Engine Architecture** dropdown:
   - Select `Detector Improvement V1` (Default).
   - Select `Phase 14 Balanced Baseline` (Historical baseline).
2. Switch to `High Precision Profile`:
   - Notice the threshold marker adjusts to $0.80$ and minimum crest factor to $9.5\text{ dB}$.
   - In noisy environments, this profile eliminates more than half of all ambient transient triggers (reducing continuous alerts to **3.56 alerts/hour**).
3. Switch to `High Sensitivity Profile`:
   - Notice the threshold marker adjusts to $0.70$.
   - This profile expands gunshot recall to **69.17% (+9 detected gunshots)** for remote perimeter monitoring.

---

### Demonstration Track C: Continuous Live Microphone Detection

Demonstrate live physical microphone capture with privacy safeguards:
1. **Privacy Safeguard Verification**:
   - Note that upon page load, the microphone is in **Standby**; the browser does not request or access audio hardware until the user explicitly clicks the start button.
2. **Raw Audio Mode DSP Bypass**:
   - Point out the `Raw Audio Mode: Bypass Browser Speech DSP` checkbox.
   - Explain that modern browsers apply Acoustic Echo Cancellation (AEC) and Noise Suppression by default, which can clamp or distort the rapid rise time ($<5\text{ ms}$) of ballistic impulses. Checking this box bypasses browser speech DSP for uncorrupted physical audio evaluation.
3. Click:
   $$\text{\textbf{[► Start Continuous Listening]}}$$
4. Grant microphone access when prompted by the browser.
5. **Acoustic Discrimination Test**:
   - Normal speech or ambient room noise produces scores near $0.01 - 0.08$.
   - Sharp non-ballistic transients (e.g. snapping fingers or tapping a table) may show high crest factor but lack neural gunshot embeddings, keeping scores safely below $0.40$.
6. Click `[⏸ Stop Listening]` to release microphone access.

---

### Demonstration Track D: Forensic Audio File Upload & Waveform Analysis

Demonstrate file-based forensic analysis:
1. Click the **Audio File Upload & Forensic Analysis** navigation tab at the top.
2. Drag and drop any audio recording (e.g. from `static/demo_samples/gunshot_positive_demo.wav`) onto the dropzone.
3. Select the engine (`Detector Improvement V1`) and click:
   $$\text{\textbf{[Analyze Audio File]}}$$
4. **Observe the Detailed Results View**:
   - **Verdict Banner**: Clear detection status with overall peak score, duration, and physical crest factor.
   - **Interactive Canvas Waveform**: The complete audio waveform is plotted in cyan with detected gunshot event regions highlighted in red bounding boxes.
   - **Audio Playback Sync**: Click the `[►]` play button to listen to the audio while a white playhead tracks across the waveform in real time.
   - **Detailed Event Table**: Lists each detected burst's start time, end time, duration, peak confidence score, and dispatch path (`multi_window_confirmation` or `single_window_high_confidence`).

---

## 4. Benchmark Reference Scorecard

Keep this summary scorecard available during senior presentations:

```
========================================================================================
METRIC / CAPABILITY               PHASE 14 BASELINE    PHASE 36 BRANCH    DETECTOR IMPROVEMENT V1
========================================================================================
Architecture                      Legacy Gating        4-State FSM        4-State FSM + Calibrated Gating
State Machine                     Soft Cooldown        Deterministic FSM  Deterministic 4-State Refractory FSM
Semantic Suppression              Calibrated Multi     Animal Only        Calibrated Multi-Category V1
----------------------------------------------------------------------------------------
Positive Gunshot Recall (N=120)   61.67% (74/120)      64.17% (77/120)    61.67% (74/120) [High Sens: 69.17%]
Duplicate Alerts on Positives     28 duplicates        13 duplicates      12 duplicates (-57.1% vs P14)
TP Duplicate Alert Rate           27.45%               14.44%             13.95% (Lowest duplicate rate)
----------------------------------------------------------------------------------------
Fireworks False Alarms (N=100)    47 / 100             57 / 100           45 / 100 (-21.1% vs Phase 36)
Other Distractors (N=120)         7 / 120              9 / 120            7 / 120 [High Prec: 3 / 120]
Total Challenge Distractors       54 / 220 (24.55%)    66 / 220 (30.0%)   52 / 220 (-21.2% vs Phase 36)
----------------------------------------------------------------------------------------
Continuous Audio FAR (4.22 hr)    7.35 alerts / hr     6.16 alerts / hr   6.16 alerts / hr (-16.2% vs P14)
Continuous Audio FAR (High Prec)  N/A                  N/A                3.56 alerts / hr (-51.6% vs P14)
----------------------------------------------------------------------------------------
Mean Window Latency (CPU)         199.2 ms             204.5 ms           198.8 ms (RTF = 0.207)
========================================================================================
```

---

## 5. Frequently Asked Questions for Evaluators

**Q1: Why did Phase 36 have higher fireworks false alarms than Phase 14?**  
*A: Phase 36 focused on event state-machine determinism and intentionally reduced semantic suppression to animal vocalizations only. This demonstrated that without pyrotechnic semantic suppression, neural embeddings from aerial fireworks and firecrackers trigger gunshot classifiers. Detector Improvement V1 restores and calibrates multi-category suppression.*

**Q2: Does semantic suppression accidentally mute real gunshots?**  
*A: No. Calibrated Semantic Suppression V1 incorporates a strict ballistic safeguard: suppression is only applied when the gunshot class probability is below 0.10. If an acoustic impulse contains genuine gunshot acoustic energy, suppression is disabled.*

**Q3: How does the detector achieve sub-200ms latency on CPU without GPU acceleration?**  
*A: YAMNet is based on MobileNet architecture, which uses depthwise separable convolutions optimized for low-power edge execution. Combined with fast vector operations in NumPy and scikit-learn/joblib, the entire 4-model ensemble and feature pipeline completes in under 200 ms.*

**Q4: Can this software be connected to emergency 911 dispatch?**  
*A: Absolutely not. This software is an uncertified research prototype. As prominently designated throughout the application, it must never be used for life-critical physical security, autonomous emergency response, or tactical dispatch.*

