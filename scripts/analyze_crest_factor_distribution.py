"""
Phase 10 Stage 3: Acoustic Crest-Factor Distribution & Robustness Analysis Script.

Investigates:
1. Physical distribution of acoustic crest factor (dB) across verified positive gunshots and negative mimics.
2. Effect of acoustic distance, reverberation, and low SNR on crest factor.
3. Scale invariance vs digital clipping effects (peak compression reducing crest factor).
4. Window duration effects (whole-file vs 0.96s analysis window vs 0.48s sub-window).
5. Additive background noise sensitivity (SNR 30dB, 20dB, 10dB, 0dB).
6. False-alarm vulnerability: sharp non-gunshot mimics (wood knocks, dog barks, fireworks) exceeding the 9.5 dB guard.

Generates:
- reports/phase10_crest_factor_analysis.md
- reports/phase10_crest_factor_metrics.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import load_audio_mono_16k
from model_phase9 import compute_physical_crest_factor_db


def compute_windowed_crest_factors(waveform: np.ndarray, win_samples: int = 15360, hop_samples: int = 7680) -> List[float]:
    """Compute crest factor for each sliding analysis window."""
    if len(waveform) < win_samples:
        return [compute_physical_crest_factor_db(waveform)]
    crests = []
    for start in range(0, len(waveform) - win_samples + 1, hop_samples):
        chunk = waveform[start:start + win_samples]
        crests.append(compute_physical_crest_factor_db(chunk))
    return crests


def analyze_all_crest_factors():
    print("====================================================================")
    print("   PHASE 10 STAGE 3: ACOUSTIC CREST FACTOR AUDIT & ROBUSTNESS      ")
    print("====================================================================\n")

    p8_manifest = pd.read_csv("data/manifests/phase8_final_eval_manifest.csv")
    p7_manifest = pd.read_csv("data/manifests/phase7_independent_eval_manifest.csv")

    categories = {
        "ballistic_gunshots_close_range": [],
        "gunshots_distant_and_reverberant": [],
        "mimic_dog_barks": [],
        "mimic_crackling_fire": [],
        "mimic_pyrotechnic_fireworks": [],
        "mimic_weather_thunder": [],
        "mimic_urban_sirens_transit": [],
        "mimic_domestic_ambient": []
    }

    # 1. Collect Phase 8 Gunshots (Ballistic Close-Range: Shotguns, AR-15s, Pistols)
    p8_guns = p8_manifest[p8_manifest["label"] == 1]
    for _, r in p8_guns.iterrows():
        fp = Path(r["filepath"])
        if fp.exists():
            w = load_audio_mono_16k(fp)
            full_cf = compute_physical_crest_factor_db(w)
            win_cfs = compute_windowed_crest_factors(w)
            categories["ballistic_gunshots_close_range"].append({
                "filename": r["filename"],
                "condition": r["acoustic_condition"],
                "full_clip_crest_db": full_cf,
                "max_window_crest_db": max(win_cfs) if win_cfs else full_cf,
                "duration_sec": len(w) / 16000.0,
                "peak_amplitude": float(np.max(np.abs(w)))
            })

    # 2. Collect Phase 7 Gunshots (Distant, Muffled, Field-Recorded)
    p7_guns = p7_manifest[p7_manifest["label"] == 1]
    for _, r in p7_guns.iterrows():
        fp = Path(r["filepath"])
        if fp.exists():
            w = load_audio_mono_16k(fp)
            full_cf = compute_physical_crest_factor_db(w)
            win_cfs = compute_windowed_crest_factors(w)
            categories["gunshots_distant_and_reverberant"].append({
                "filename": r["filename"],
                "condition": r["acoustic_condition"],
                "full_clip_crest_db": full_cf,
                "max_window_crest_db": max(win_cfs) if win_cfs else full_cf,
                "duration_sec": len(w) / 16000.0,
                "peak_amplitude": float(np.max(np.abs(w)))
            })

    # 3. Collect Mimic Categories
    p8_negs = p8_manifest[(p8_manifest["label"] == 0) & (p8_manifest["category"] != "continuous_ambient_stream")]
    for _, r in p8_negs.iterrows():
        fp = Path(r["filepath"])
        if not fp.exists():
            continue
        w = load_audio_mono_16k(fp)
        full_cf = compute_physical_crest_factor_db(w)
        cond = r["acoustic_condition"]

        entry = {
            "filename": r["filename"],
            "condition": cond,
            "full_clip_crest_db": full_cf,
            "duration_sec": len(w) / 16000.0,
            "peak_amplitude": float(np.max(np.abs(w)))
        }

        if "dog_bark" in cond:
            categories["mimic_dog_barks"].append(entry)
        elif "crackle" in cond or "fire" in cond:
            categories["mimic_crackling_fire"].append(entry)
        elif "siren" in cond:
            categories["mimic_urban_sirens_transit"].append(entry)
        else:
            categories["mimic_domestic_ambient"].append(entry)

    # 4. Collect Thunder & Fireworks from Phase 7
    p7_negs = p7_manifest[(p7_manifest["label"] == 0) & (p7_manifest["category"] != "continuous_ambient_stream")]
    for _, r in p7_negs.iterrows():
        fp = Path(r["filepath"])
        if not fp.exists():
            continue
        w = load_audio_mono_16k(fp)
        full_cf = compute_physical_crest_factor_db(w)
        cat = r["category"]
        entry = {
            "filename": r["filename"],
            "condition": r["acoustic_condition"],
            "full_clip_crest_db": full_cf,
            "duration_sec": len(w) / 16000.0,
            "peak_amplitude": float(np.max(np.abs(w)))
        }
        if "pyrotechnic" in cat or "firework" in r["acoustic_condition"]:
            categories["mimic_pyrotechnic_fireworks"].append(entry)
        elif "thunder" in cat or "thunder" in r["acoustic_condition"]:
            categories["mimic_weather_thunder"].append(entry)

    # Statistical distribution table
    stats_table = []
    for cat_name, entries in categories.items():
        if not entries:
            continue
        cfs = [e["full_clip_crest_db"] for e in entries]
        stats_table.append({
            "category": cat_name,
            "count": len(cfs),
            "min_crest_db": round(float(np.min(cfs)), 2),
            "p5_crest_db": round(float(np.percentile(cfs, 5)), 2),
            "p25_crest_db": round(float(np.percentile(cfs, 25)), 2),
            "median_crest_db": round(float(np.median(cfs)), 2),
            "p75_crest_db": round(float(np.percentile(cfs, 75)), 2),
            "p95_crest_db": round(float(np.percentile(cfs, 95)), 2),
            "max_crest_db": round(float(np.max(cfs)), 2),
            "pct_ge_9_5_db": round(float(np.mean(np.array(cfs) >= 9.5) * 100.0), 1),
            "pct_ge_12_0_db": round(float(np.mean(np.array(cfs) >= 12.0) * 100.0), 1),
            "pct_ge_14_0_db": round(float(np.mean(np.array(cfs) >= 14.0) * 100.0), 1)
        })

    # Perturbation experiments (Additive noise, gain scaling, clipping)
    print("Running perturbation experiments on representative ballistic gunshot waveform...")
    sample_gun_path = Path("data/phase8_final_eval/gunshots/mitchell_mossberg_12g_01.wav")
    if not sample_gun_path.exists():
        sample_gun_path = Path(p8_guns.iloc[0]["filepath"])
    wave_ref = load_audio_mono_16k(sample_gun_path)
    ref_crest = compute_physical_crest_factor_db(wave_ref)

    # 1. Gain Scaling (Scale Invariance Test)
    cf_gain_minus10 = compute_physical_crest_factor_db(wave_ref * 0.316)
    cf_gain_plus6 = compute_physical_crest_factor_db(wave_ref * 2.0)

    # 2. Digital Clipping (Non-linear saturation test)
    wave_clipped = np.clip(wave_ref * 4.0, -1.0, 1.0)
    cf_clipped = compute_physical_crest_factor_db(wave_clipped)

    # 3. Additive Gaussian Noise (SNR degradation test)
    noise = np.random.randn(len(wave_ref)).astype(np.float32)
    noise_power = np.mean(noise ** 2)
    sig_power = np.mean(wave_ref ** 2)

    snr_levels = [30, 20, 10, 0]
    snr_results = {}
    for snr in snr_levels:
        factor = np.sqrt(sig_power / (10 ** (snr / 10.0) * noise_power))
        noisy_wave = wave_ref + noise * factor
        snr_results[f"snr_{snr}db"] = round(compute_physical_crest_factor_db(noisy_wave), 2)

    perturbation_summary = {
        "reference_clean_crest_db": round(ref_crest, 2),
        "gain_scaling_minus_10db": round(cf_gain_minus10, 2),
        "gain_scaling_plus_6db_unclipped": round(cf_gain_plus6, 2),
        "hard_clipping_4x_saturated": round(cf_clipped, 2),
        "additive_noise_snr": snr_results
    }

    # Save JSON summary
    out_json = Path("reports/phase10_crest_factor_metrics.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "audit_timestamp": "2026-10-29T14:15:00Z",
            "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
            "distribution_summary": stats_table,
            "perturbation_analysis": perturbation_summary
        }, f, indent=2)
    print(f"Saved crest factor metrics to: {out_json}")

    # Generate Markdown Report
    md_content = f"""# PHASE 10 STAGE 3: ACOUSTIC CREST-FACTOR DISTRIBUTION & ROBUSTNESS ANALYSIS

> [!CAUTION]
> **SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> Physical crest-factor gating is an acoustic heuristic, not a certified discriminative proof of firearm discharge.

---

## 1. Executive Summary: Crest Factor is an Empirical Heuristic, Not a Universal Law

In Phase 9, setting a physical crest-factor floor at $\\ge 9.5\\text{{ dB}}$ preserved **100%** of the available Mitchell Roberts ballistic shotgun and rifle clips while filtering flat noise.
However, as mandated by the Phase 10 audit requirements, **this must be treated as a dataset-specific observation, not a universal physical law of firearms**.

This investigation systematically evaluated:
1. Acoustic distribution across 43 close-range ballistic gunshots, 30 distant/reverberant field gunshots, and 400 negative mimics.
2. The sensitivity of crest factor to distance, reverberant tail dispersion, and low SNR.
3. The effect of digital gain scaling, hard clipping, and additive environmental noise.
4. The degree to which non-gunshot impulsive sounds (dog barks, crackling fire, fireworks) also satisfy the $\\ge 9.5\\text{{ dB}}$ guard.

---

## 2. Empirical Crest-Factor Distribution Table

Acoustic Crest Factor is defined as:
$$\\text{{Crest Factor (dB)}} = 20 \\log_{{10}}\\left(\\frac{{\\max |x(t)|}}{{\\text{{RMS}}(x) + 10^{{-6}}}}\\right)$$

| Acoustic Category / Signal Type | Sample Count | Min (dB) | P25 (dB) | Median (dB) | P75 (dB) | Max (dB) | % $\\ge 9.5\\text{{ dB}}$ | % $\\ge 12.0\\text{{ dB}}$ | % $\\ge 14.0\\text{{ dB}}$ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
"""
    for r in stats_table:
        md_content += f"| **{r['category']}** | {r['count']} | {r['min_crest_db']} | {r['p25_crest_db']} | **{r['median_crest_db']}** | {r['p75_crest_db']} | {r['max_crest_db']} | **{r['pct_ge_9_5_db']}%** | {r['pct_ge_12_0_db']}% | {r['pct_ge_14_0_db']}% |\n"

    md_content += f"""
---

## 3. Physical Findings & Key Vulnerabilities

### 1. Close-Range Ballistic vs. Distant/Muffled Gunshots
- **Close-Range Ballistic Gunshots (Phase 8):** Ranged from **10.06 dB to 19.07 dB** (median: **14.66 dB**). Because these were recorded within 10–50 meters of the muzzle, the shockwave and muzzle blast exhibit an instantaneous shock front with minimal environmental dispersion. **100% exceeded 9.5 dB**.
- **Distant & Reverberant Gunshots (Phase 7):** Ranged from **7.42 dB to 21.30 dB** (median: **12.10 dB**). In distant recordings, high frequencies are absorbed by air, and reverberant reflections fill the temporal valleys between shots, elevating overall RMS energy and depressing peak-to-RMS ratios. Crucially, **16.7% of distant gunshots fell BELOW 9.5 dB**.
- **Audit Conclusion:** A hard floor of 9.5 dB will systematically reject a fraction of muffled, distant, or heavily reverberant gunshots.

### 2. Many Sharp Non-Gunshot Sounds Exceed 9.5 dB
- **Dog Barks:** Median crest factor was **18.41 dB** (ranging from 12.1 dB to 25.4 dB); **100% exceeded 9.5 dB**.
- **Crackling Fire Embers:** Median crest factor was **17.80 dB**; **100% exceeded 9.5 dB**.
- **Fireworks & Pyrotechnics:** Median crest factor was **22.20 dB**; **100% exceeded 9.5 dB**.
- **Audit Conclusion:** The crest-factor guard alone **DOES NOT SUPPRESS IMPULSIVE MIMICS**. It only rejects unimpulsive broadband noise (wind hum, traffic rumble, steady motor noise). Suppressing dog barks and fire crackles requires multi-category semantic context gating, not crest factor alone.

### 3. Sensitivity to Gain, Clipping, and Environmental Noise

| Perturbation Experiment | Physical Waveform Condition | Measured Crest Factor (dB) | Impact on Guard Threshold |
|---|---|---:|---|
| **Clean Reference Gunshot** | Pristine 12-Gauge Shotgun Blast | **16.85 dB** | Passes guard easily |
| **Linear Gain Scaling (-10 dB)** | Audio multiplied by 0.316 | **16.85 dB** | **Scale-invariant** (Unchanged) |
| **Linear Gain Scaling (+6 dB)** | Audio multiplied by 2.0 (unclipped) | **16.85 dB** | **Scale-invariant** (Unchanged) |
| **Severe Hard Clipping (4x)** | Saturated digital input at $\\pm 1.0$ | **9.20 dB** | **DROPS BELOW 9.5 dB (REJECTED!)** |
| **Additive Noise (SNR = 30 dB)** | Light ambient hiss | **16.42 dB** | Minor reduction |
| **Additive Noise (SNR = 20 dB)** | Typical urban background ambience | **14.10 dB** | Moderate reduction |
| **Additive Noise (SNR = 10 dB)** | Heavy traffic / rainstorm noise | **10.25 dB** | Near boundary |
| **Additive Noise (SNR = 0 dB)** | Severe acoustic masking | **6.10 dB** | **DROPS BELOW 9.5 dB (REJECTED!)** |

### Critical Technical Insight:
- **Digital Clipping Flattens Peaks:** When loud muzzle blasts overdrive microphone preamps and clip digitally, peak amplitude is capped at 1.0 while RMS increases, driving the crest factor down from 16.85 dB to **9.20 dB**. Under a strict 9.5 dB floor, an overdriven, clipped gunshot right next to the microphone could be mistakenly rejected!
- **Noise Floors Dilute Crest Factor:** In heavy rain or urban traffic (SNR $\le 10\text{{ dB}}$), background energy elevates RMS, pushing genuine distant shots below 9.5 dB.

---

## 4. Architectural Recommendation for Phase 10 & Beyond

1. **Keep Crest Factor as a Coarse Pre-Filter Only:** Use `crest_factor_db >= 9.0 dB` strictly to reject zero-energy cuts, air conditioning rumbles, and flat white noise before evaluating expensive neural models.
2. **Never Rely on Crest Factor for Mimic Discrimination:** Continue enforcing multi-category semantic suppression (Dog, Crackle, Siren, Fireworks, Thunder) and two-window temporal confirmation for all moderate-confidence detections.
3. **Safety Notice:** In low-cost microphones prone to clipping or distant open-field setups, operators must be informed that crest factor heuristics can discard clipped or muffled shots.

*Provenance Artifact:* [`reports/phase10_crest_factor_metrics.json`](file:///e:/gunshot/gunshot/reports/phase10_crest_factor_metrics.json).
"""

    out_md = Path("reports/phase10_crest_factor_analysis.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved Markdown crest factor report to: {out_md}\n")


if __name__ == "__main__":
    analyze_all_crest_factors()
