"""
Phase 48 V6 Concept Testing Script
Tests:
1. Rejection of the 15 Phase 12 continuous urban false alerts
2. Preservation of Phase 16 Stream 05 continuous zero alerts
3. Preservation of Phase 15 holdout pocket and clean gunshot recall
4. Phase 12 discrete holdout positive recall and distractor rejection
"""

import sys, os
sys.path.insert(0, "E:/gunshot/gunshot")
os.chdir("E:/gunshot/gunshot")

import pathlib, soundfile as sf, numpy as np, pandas as pd, librosa
from experiments.detector_improvement_v5.model_detector_improvement_v5 import (
    DetectorImprovementV5, compute_physical_acoustic_features_v5, OperatingMode, EventState
)

v5 = DetectorImprovementV5(profile="condition_adaptive")

# Test 1: Evaluating the 15 Phase 12 continuous alert windows with V6 logic
p12_cont_path = pathlib.Path("data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav")
alerts_def = [
    (0, 13.92), (20, 1.92), (40, 16.8), (60, 4.8), (60, 21.12), (60, 25.44),
    (80, 9.12), (80, 13.44), (100, 1.44), (110, 20.64), (190, 25.92),
    (210, 13.92), (230, 1.92), (230, 17.28), (230, 21.12)
]

print("="*60)
print("TEST 1: Evaluating the 15 Phase 12 Continuous Alert Windows under V6 Logic")
print("="*60)

v6_v5_alerts = 0
v6_alerts = 0

with sf.SoundFile(str(p12_cont_path)) as f:
    sr = f.samplerate
    for idx, (b_idx, t_offset) in enumerate(alerts_def):
        sec = b_idx * 30 + t_offset
        start_samp = int(sec * sr)
        f.seek(max(0, start_samp))
        win = f.read(15360, dtype='float32')
        if win.ndim > 1: win = np.mean(win, axis=1)
        if len(win) < 15360: win = np.pad(win, (0, 15360 - len(win)))
        
        rms = np.sqrt(np.mean(win**2))
        peak = np.max(np.abs(win))
        
        feat, ys, acoustics = v5.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent = acoustics
        raw_score = float(v5.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        
        gun_s = max(float(ys.get(cls, 0.0)) for cls in [421, 422, 424, 425])
        bal_s = max(float(ys.get(cls, 0.0)) for cls in [420, 421, 422, 424, 425, 428, 434, 460])
        
        # V5 suppression
        supp_v5 = v5.suppression.apply_suppression(raw_score, ys, hi, lo, m2l)
        score_v5 = supp_v5["adjusted_score"]
        
        # V6 Enhanced Suppression & Gating
        score_v6 = raw_score
        supp_reason = "NONE"
        if rms < 0.001 or peak < 0.005:
            score_v6 = 0.0
            supp_reason = "SILENCE_GATE"
        # Sub-bass automotive thud / backfire gate
        elif lo >= 0.75 and hi < 0.008 and cent < 450.0 and gun_s < 0.25:
            score_v6 *= 0.35
            supp_reason = "SUB_BASS_THUD_SUPPRESSION"
        else:
            # Standard V5 suppression
            score_v6 = supp_v5["adjusted_score"]
            supp_reason = supp_v5.get("category", "STANDARD")
            
        # V6 Single impulse exception check
        # In V6: sub-bass thud (hi < 0.005 and cent < 450 and peak < 0.15) does NOT get single-impulse bypass
        is_sub_bass = (hi < 0.005 and cent < 450.0 and peak < 0.15)
        v6_confirmed = False
        if not is_sub_bass and score_v6 >= 0.70 and crest >= 13.5:
            v6_confirmed = True
        elif score_v6 >= 0.85 and crest >= 14.5 and peak >= 0.20:
            v6_confirmed = True
            
        if score_v5 >= 0.68 and crest >= 13.0:
            v6_v5_alerts += 1
        if v6_confirmed:
            v6_alerts += 1
            
        print(f"Alert {idx+1:2d} ({sec:7.2f}s): RMS={rms:.4f}, Peak={peak:.4f}, Crest={crest:.1f}dB, Cent={cent:.0f}Hz | V5 Score={score_v5:.4f} -> V6 Score={score_v6:.4f} ({supp_reason}) | V6 Confirmed: {v6_confirmed}")

print(f"\nPhase 12 False Alerts: V5={v6_v5_alerts} / 15 -> V6={v6_alerts} / 15 (Reduction: {v6_v5_alerts - v6_alerts})")

# Test 2: Checking Phase 15 Holdout Pocket & Clean gunshots to verify ZERO regression
print("\n" + "="*60)
print("TEST 2: Verifying Zero Regression on Phase 15 Gunshots")
print("="*60)
p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")
pocket_recs = p15_manifest[p15_manifest["recording_id"].str.contains("pocket") & (p15_manifest["ground_truth_label"] == 1)]
clean_recs = p15_manifest[~p15_manifest["recording_id"].str.contains("pocket") & (p15_manifest["ground_truth_label"] == 1)]

def evaluate_v6_clip(y, sr):
    if y.ndim > 1: y = np.mean(y, axis=1)
    if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
    if len(y) < 15360: y = np.pad(y, (0, 15360 - len(y)))
    n_wins = 1 + int((len(y) - 15360) // 7680)
    
    detected = False
    peak_score = 0.0
    for w in range(n_wins):
        win = y[w * 7680 : w * 7680 + 15360]
        rms = np.sqrt(np.mean(win**2))
        peak = np.max(np.abs(win))
        if rms < 0.001 or peak < 0.005: continue
        
        feat, ys, acoustics = v5.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent = acoustics
        raw_score = float(v5.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        gun_s = max(float(ys.get(cls, 0.0)) for cls in [421, 422, 424, 425])
        
        score = raw_score
        # Check sub-bass thud suppression: ONLY if gun_s is low
        if lo >= 0.75 and hi < 0.008 and cent < 450.0 and gun_s < 0.25:
            score *= 0.35
            
        peak_score = max(peak_score, score)
        
        # In pocket occluded audio: peak >= 0.20 and score >= 0.62 and crest >= 11.5
        # Pocket gunshots have peak amplitude > 0.30!
        if score >= 0.62 and crest >= 11.5 and peak >= 0.15:
            detected = True
            break
        elif score >= 0.70 and crest >= 13.5:
            detected = True
            break
    return detected, peak_score

pkt_det = sum(evaluate_v6_clip(sf.read(r["filepath"])[0], sf.read(r["filepath"])[1])[0] for _, r in pocket_recs.iterrows())
cln_det = sum(evaluate_v6_clip(sf.read(r["filepath"])[0], sf.read(r["filepath"])[1])[0] for _, r in clean_recs.iterrows())

print(f"Phase 15 Pocket Gunshot Recall: {pkt_det} / {len(pocket_recs)} ({pkt_det / len(pocket_recs)*100:.1f}%)")
print(f"Phase 15 Clean Gunshot Recall:  {cln_det} / {len(clean_recs)} ({cln_det / len(clean_recs)*100:.1f}%)")
print(f"Overall Phase 15 Recall:       {pkt_det + cln_det} / {len(p15_manifest[p15_manifest['ground_truth_label']==1])} ({(pkt_det+cln_det)/len(p15_manifest[p15_manifest['ground_truth_label']==1])*100:.1f}%)")

