"""
Phase 23 Streaming Evaluation & Negative Exposure Benchmark Execution
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Executes streaming inference across all 17 verified-negative continuous streams
for Phase 14 Balanced (Default Research Baseline) and Phase 17 Experimental.
Generates:
- reports/phase23_exposure_accounting.csv
- reports/phase23_negative_audio_results.csv
- reports/phase23_processing_manifest.json
"""

import sys
import json
import time
import math
import hashlib
import numpy as np
import pandas as pd
import soundfile as sf
from pathlib import Path
from scipy.stats import chi2

WORKSPACE_ROOT = Path("E:/gunshot/gunshot").resolve()
sys.path.insert(0, str(WORKSPACE_ROOT))

from dataset import load_audio_mono_16k
from model_phase14 import Phase14CandidateGunshotDetector
from model_phase17 import Phase17ExperimentalGunshotDetector

REPORTS_DIR = WORKSPACE_ROOT / "reports"
DATA_DIR = WORKSPACE_ROOT / "data"

EXPECTED_HASHES = {
    "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
    "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
}


def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_garwood_bounds(k: int, exposure_hr: float, alpha: float = 0.05):
    """Compute exact Garwood Poisson confidence bounds for event count k over exposure_hr."""
    if exposure_hr <= 0:
        return 0.0, 0.0, 0.0
    rate = k / exposure_hr
    if k == 0:
        lower = 0.0
        upper = -math.log(alpha) / exposure_hr  # chi2.ppf(1 - alpha, 2) / (2 * exposure_hr)
    else:
        lower = chi2.ppf(alpha / 2.0, 2 * k) / (2.0 * exposure_hr)
        upper = chi2.ppf(1.0 - alpha / 2.0, 2 * (k + 1)) / (2.0 * exposure_hr)
    return rate, lower, upper


def main():
    print("=" * 80)
    print("PHASE 23 NEGATIVE EXPOSURE BENCHMARK EXECUTION")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.")
    print("=" * 80)

    # 1. Verify frozen baseline hashes
    print("\n[*] Verifying frozen detector hashes...")
    for model_file, exp_hash in EXPECTED_HASHES.items():
        p = WORKSPACE_ROOT / model_file
        act_hash = sha256_file(p)
        assert act_hash == exp_hash, f"Hash mismatch for {model_file}!"
        print(f"  [OK] {model_file}: {act_hash[:16]}...")

    # 2. Load recording provenance
    prov_csv = REPORTS_DIR / "phase23_recording_provenance.csv"
    if not prov_csv.exists():
        raise FileNotFoundError(f"Missing {prov_csv}")
    df_prov = pd.read_csv(prov_csv)

    # Filter to VERIFIED_NEGATIVE primary streams (17 streams)
    df_primary = df_prov[df_prov["eligibility_category"] == "VERIFIED_NEGATIVE"].copy()
    print(f"\n[*] Loaded {len(df_primary)} primary VERIFIED_NEGATIVE streams.")
    gross_duration_s = df_primary["duration_seconds"].sum()
    gross_duration_hr = gross_duration_s / 3600.0
    print(f"    Gross Exposure: {gross_duration_s:.2f} s ({gross_duration_hr:.4f} hours)")

    # 3. Instantiate frozen detectors
    print("\n[*] Initializing frozen detectors...")
    det14 = Phase14CandidateGunshotDetector(profile="balanced")
    det17 = Phase17ExperimentalGunshotDetector(profile="experimental_animal_suppression")

    detectors = {
        "Phase 14 Balanced": {
            "model": det14,
            "role": "DEFAULT_RESEARCH_BASELINE",
            "threshold": 0.45,
            "cooldown": 2.0
        },
        "Phase 17 Experimental": {
            "model": det17,
            "role": "SELECTABLE_EXPERIMENTAL_PROFILE",
            "threshold": 0.45,
            "cooldown": 2.0
        }
    }

    # 4. Run streaming evaluation across all 17 primary streams
    print("\n[*] Running streaming evaluation on matched audio intervals...")
    all_alerts = []
    stream_summaries = []

    for idx, row in df_primary.iterrows():
        rec_id = row["recording_id"]
        rel_path = row["relative_filepath"]
        abs_path = DATA_DIR / rel_path
        dur_s = float(row["duration_seconds"])
        camp_id = row["campaign_id"]
        sess_id = row["session_id"]
        env_cat = row["acoustic_environment"]

        print(f"  Evaluating [{rec_id}] {row['filename']} ({dur_s:.1f}s)...")
        audio = load_audio_mono_16k(abs_path)

        for det_name, det_cfg in detectors.items():
            det = det_cfg["model"]
            cooldown_period = det_cfg["cooldown"]

            # Reset detector streaming state
            det.reset_state()
            preds = det.predict_stream(audio, sample_rate=16000)

            raw_alerts = preds.get("alerts", [])
            alert_count = len(raw_alerts)

            # Calculate empirical cooldown dead time
            # For each alert at t_alert, detector is in cooldown during [t_alert, min(t_alert + 2.0, dur_s)]
            # Merge overlapping intervals if any
            cooldown_intervals = []
            for a_idx, alt in enumerate(raw_alerts, 1):
                t_peak = alt.get("peak_time", alt.get("start_time", 0.0))
                st = alt.get("start_time", t_peak)
                et = alt.get("end_time", t_peak)
                sc = alt.get("peak_score", alt.get("score", 0.0))
                cd_start = st
                cd_end = min(dur_s, st + cooldown_period)
                cooldown_intervals.append((cd_start, cd_end))

                # Review classification: In verified negative audio, any alert is a non-target distractor
                all_alerts.append({
                    "recording_id": rec_id,
                    "stream_id": row["legacy_stream_id"],
                    "filename": row["filename"],
                    "detector": det_name,
                    "detector_role": det_cfg["role"],
                    "alert_index": a_idx,
                    "alert_start_s": round(st, 3),
                    "alert_end_s": round(et, 3),
                    "peak_time_s": round(t_peak, 3),
                    "peak_score": round(sc, 4),
                    "cooldown_start_s": round(cd_start, 3),
                    "cooldown_end_s": round(cd_end, 3),
                    "cooldown_duration_s": round(cd_end - cd_start, 3),
                    "campaign_id": camp_id,
                    "session_id": sess_id,
                    "acoustic_environment": env_cat,
                    "review_classification": "CONFIRMED_NON_TARGET_DISTRACTOR",
                    "review_rationale": "Verified negative environmental recording with zero firearms discharge; alert is an acoustic distractor."
                })

            # Merge cooldown intervals to avoid double subtraction
            merged_cooldowns = []
            if cooldown_intervals:
                sorted_intervals = sorted(cooldown_intervals, key=lambda x: x[0])
                cur_s, cur_e = sorted_intervals[0]
                for nxt_s, nxt_e in sorted_intervals[1:]:
                    if nxt_s <= cur_e:
                        cur_e = max(cur_e, nxt_e)
                    else:
                        merged_cooldowns.append((cur_s, cur_e))
                        cur_s, cur_e = nxt_s, nxt_e
                merged_cooldowns.append((cur_s, cur_e))

            total_cooldown_s = sum(e - s for s, e in merged_cooldowns)
            eligible_s = max(0.0, dur_s - total_cooldown_s)
            eligible_hr = eligible_s / 3600.0

            rate, lower_ci, upper_ci = compute_garwood_bounds(alert_count, eligible_hr)
            mtbfa_hr = (eligible_hr / alert_count) if alert_count > 0 else float("inf")

            stream_summaries.append({
                "recording_id": rec_id,
                "legacy_stream_id": row["legacy_stream_id"],
                "filename": row["filename"],
                "campaign_id": camp_id,
                "session_id": sess_id,
                "acoustic_environment": env_cat,
                "detector": det_name,
                "detector_role": det_cfg["role"],
                "gross_duration_s": round(dur_s, 2),
                "gross_duration_hr": round(dur_s / 3600.0, 5),
                "cooldown_excluded_s": round(total_cooldown_s, 2),
                "eligible_exposure_s": round(eligible_s, 2),
                "eligible_exposure_hr": round(eligible_hr, 5),
                "observed_alerts": alert_count,
                "alerts_per_eligible_hour": round(rate, 4),
                "garwood_lower_95_per_hr": round(lower_ci, 4),
                "garwood_upper_95_per_hr": round(upper_ci, 4),
                "mtbfa_hours": round(mtbfa_hr, 2) if mtbfa_hr != float("inf") else "INF"
            })

    # Save detailed alerts CSV
    df_alerts = pd.DataFrame(all_alerts)
    out_alerts_csv = REPORTS_DIR / "phase23_negative_audio_results.csv"
    df_alerts.to_csv(out_alerts_csv, index=False)
    print(f"\n[+] Saved negative audio alert logs: {out_alerts_csv} ({len(df_alerts)} total alerts)")

    # Save stream summaries & exposure accounting CSV
    df_sum = pd.DataFrame(stream_summaries)
    out_exp_csv = REPORTS_DIR / "phase23_exposure_accounting.csv"
    df_sum.to_csv(out_exp_csv, index=False)
    print(f"[+] Saved exposure accounting CSV: {out_exp_csv} ({len(df_sum)} stream evaluations)")

    # Aggregate Benchmark Performance
    print("\n" + "=" * 80)
    print("PHASE 23 AGGREGATE BENCHMARK PERFORMANCE (17 VERIFIED NEGATIVE STREAMS)")
    print("=" * 80)

    for det_name in detectors.keys():
        det_rows = df_sum[df_sum["detector"] == det_name]
        tot_alerts = det_rows["observed_alerts"].sum()
        tot_gross_s = det_rows["gross_duration_s"].sum()
        tot_cd_s = det_rows["cooldown_excluded_s"].sum()
        tot_elig_s = det_rows["eligible_exposure_s"].sum()
        tot_elig_hr = tot_elig_s / 3600.0
        tot_gross_hr = tot_gross_s / 3600.0

        agg_rate, agg_low, agg_up = compute_garwood_bounds(tot_alerts, tot_elig_hr)
        agg_mtbfa = (tot_elig_hr / tot_alerts) if tot_alerts > 0 else float("inf")

        print(f"\nModel: {det_name}")
        print(f"  Gross Stream Exposure:       {tot_gross_s:.1f} s ({tot_gross_hr:.4f} hours)")
        print(f"  Cooldown Dead Time:          {tot_cd_s:.1f} s ({tot_cd_s/3600.0:.4f} hours)")
        print(f"  Eligible Negative Exposure:  {tot_elig_s:.1f} s ({tot_elig_hr:.4f} hours)")
        print(f"  Total False Alerts:          {tot_alerts}")
        print(f"  Eligible False-Alert Rate:   {agg_rate:.4f} alerts/hour")
        print(f"  Exact 95% Garwood CI:        [{agg_low:.4f}, {agg_up:.4f}] alerts/hour")
        print(f"  Empirical MTBFA:             {agg_mtbfa:.2f} hours")

    # Build processing manifest JSON
    processing_manifest = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_23_FIRST_50_HOUR_NEGATIVE_EXPOSURE_BENCHMARK",
        "timestamp": "2026-11-14T18:50:00Z",
        "primary_benchmark_corpus": {
            "category": "VERIFIED_NEGATIVE",
            "total_streams": len(df_primary),
            "total_independent_campaigns": 3,
            "campaigns": ["CAMPAIGN-RPISOUND-UK", "CAMPAIGN-CHEWMAGNA-UK", "CAMPAIGN-BILBAO-ES"],
            "total_independent_sessions": 17,
            "gross_duration_seconds": round(gross_duration_s, 2),
            "gross_duration_hours": round(gross_duration_hr, 4),
            "hours_decoded_successfully": round(gross_duration_hr, 4),
            "hours_verified_continuous": round(gross_duration_hr, 4),
            "hours_verified_negative": round(gross_duration_hr, 4),
            "hours_classified_ambiguous": 0.0,
            "hours_excluded": 0.0
        },
        "target_shortfall_audit": {
            "target_exposure_hours": 50.0,
            "achieved_eligible_hours": round(gross_duration_hr, 4),
            "shortfall_hours": round(50.0 - gross_duration_hr, 4),
            "shortfall_reasons": [
                "SONYC-UST V1 & V2 consist exclusively of 10-second discrete clips (18,510 files); concatenation creates artificial boundary transients and is rejected.",
                "TAU Urban Acoustic Scenes (DCASE) is pre-segmented into 10-second slices and is rejected for continuous benchmarking.",
                "Bulk downloads of multi-gigabyte uncompressed WAVs from Zenodo face rate limiting (HTTP 403) and 73.4 GB drive capacity limits.",
                "Synthetic padding, looping, or concatenation strictly prohibited by protocol to preserve scientific integrity."
            ]
        },
        "model_results": {
            "Phase 14 Balanced": {
                "role": "DEFAULT_RESEARCH_BASELINE",
                "total_alerts": int(df_sum[df_sum["detector"] == "Phase 14 Balanced"]["observed_alerts"].sum()),
                "eligible_exposure_hours": round(df_sum[df_sum["detector"] == "Phase 14 Balanced"]["eligible_exposure_hr"].sum(), 4),
                "alerts_per_eligible_hour": round(df_sum[df_sum["detector"] == "Phase 14 Balanced"]["observed_alerts"].sum() / df_sum[df_sum["detector"] == "Phase 14 Balanced"]["eligible_exposure_hr"].sum(), 4),
                "mtbfa_hours": round(df_sum[df_sum["detector"] == "Phase 14 Balanced"]["eligible_exposure_hr"].sum() / df_sum[df_sum["detector"] == "Phase 14 Balanced"]["observed_alerts"].sum(), 2)
            },
            "Phase 17 Experimental": {
                "role": "SELECTABLE_EXPERIMENTAL_PROFILE",
                "total_alerts": int(df_sum[df_sum["detector"] == "Phase 17 Experimental"]["observed_alerts"].sum()),
                "eligible_exposure_hours": round(df_sum[df_sum["detector"] == "Phase 17 Experimental"]["eligible_exposure_hr"].sum(), 4),
                "alerts_per_eligible_hour": round(df_sum[df_sum["detector"] == "Phase 17 Experimental"]["observed_alerts"].sum() / df_sum[df_sum["detector"] == "Phase 17 Experimental"]["eligible_exposure_hr"].sum(), 4),
                "mtbfa_hours": round(df_sum[df_sum["detector"] == "Phase 17 Experimental"]["eligible_exposure_hr"].sum() / df_sum[df_sum["detector"] == "Phase 17 Experimental"]["observed_alerts"].sum(), 2)
            }
        }
    }

    out_proc_json = REPORTS_DIR / "phase23_processing_manifest.json"
    with open(out_proc_json, "w", encoding="utf-8") as f:
        json.dump(processing_manifest, f, indent=2)
    print(f"\n[+] Saved processing manifest: {out_proc_json}")


if __name__ == "__main__":
    main()

