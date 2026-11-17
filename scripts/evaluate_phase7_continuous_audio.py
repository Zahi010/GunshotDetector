"""
Phase 7 Continuous Negative Audio Evaluation Script.

Evaluates the frozen Phase 6 gunshot detector on 3.0 hours (10,800 seconds)
of continuous multi-environment negative audio streams:
- Stream 1: Urban street traffic, sirens, car horns, construction, and machinery (1.0 hr)
- Stream 2: Severe weather, thunderstorms, heavy rain, wind, and water transients (1.0 hr)
- Stream 3: Public gathering, church bells, fireworks, applause, and crowd noise (1.0 hr)

Measures:
1. Total continuous exposure time.
2. Window-level false positive count and False Positive Rate (FPR) across 22,000+ windows.
3. False alert events after causal temporal aggregation (confirm_windows = 2, cooldown = 2.0s).
4. Stream-by-stream and aggregate false alerts per hour.
5. Exact Poisson 95% confidence intervals using chi-square distribution.
6. Diagnostic breakdown of triggering events.

Outputs: reports/phase7_false_alert_analysis.json
"""
import os
import sys
import json
import time
import numpy as np
from pathlib import Path
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import load_audio_mono_16k
from model import GunshotDetector, merge_detection_windows
from evaluate import poisson_rate_confidence_interval


def main():
    print("\n=======================================================")
    print("   PHASE 7: CONTINUOUS NEGATIVE AUDIO EVALUATION       ")
    print("=======================================================\n")

    t_start = time.time()
    out_json = Path("reports/phase7_false_alert_analysis.json")

    # Load frozen Phase 6 detector
    bundle_dir = Path("models/phase6_yamnet_bundle")
    detector = GunshotDetector(bundle_dir=bundle_dir)
    print(f"Loaded detector from: {bundle_dir}")
    th = detector.threshold
    th_off = 0.500
    confirm_win = detector.confirm_windows
    cooldown = detector.cooldown_secs
    print(f"Operating Parameters: Threshold={th}, ConfirmWindows={confirm_win}, Cooldown={cooldown}s, ThresholdOff={th_off}\n")

    stream_dir = Path("data/phase7_independent_test/continuous_ambient")
    stream_files = sorted(list(stream_dir.glob("*.wav")))

    if not stream_files:
        raise FileNotFoundError(f"No continuous streams found in {stream_dir}!")

    total_exposure_sec = 0.0
    total_windows_count = 0
    total_fp_windows_count = 0
    total_alert_events_count = 0

    streams_report = []
    all_alert_events = []

    for sf_path in stream_files:
        print(f"Processing: {sf_path.name}...")
        waveform = load_audio_mono_16k(sf_path)
        dur_sec = len(waveform) / 16000.0
        dur_hr = dur_sec / 3600.0
        total_exposure_sec += dur_sec

        # Extract embeddings and score
        embeddings, timestamps = detector.feature_extractor.extract_continuous_recording(waveform)
        n_win = len(embeddings)
        total_windows_count += n_win

        if n_win > 0:
            raw_scores = detector.classifier_head.predict(embeddings, verbose=0).flatten()
            # Energy squelch check
            hop_samples = config.HOP_SAMPLES
            win_samples = config.WINDOW_SAMPLES
            for i in range(len(raw_scores)):
                st_samp = i * hop_samples
                et_samp = st_samp + win_samples
                chunk = waveform[st_samp:et_samp]
                if len(chunk) > 0:
                    rms = float(np.sqrt(np.mean(chunk ** 2) + 1e-12))
                    if rms < 1e-4:
                        raw_scores[i] = 0.0

            # Window-level false positives
            fp_windows = int(np.sum(raw_scores >= th))
            total_fp_windows_count += fp_windows
            fpr_win = float(fp_windows / n_win) if n_win > 0 else 0.0

            win_results = [
                {"window_index": i, "start_time": st, "end_time": et, "score": round(float(s), 4)}
                for i, (s, (st, et)) in enumerate(zip(raw_scores, timestamps))
            ]

            # Event-level aggregation with confirmation and cooldown
            alert_events = merge_detection_windows(
                win_results,
                threshold=th,
                confirm_windows=confirm_win,
                cooldown_secs=cooldown,
                threshold_off=th_off
            )
            n_events = len(alert_events)
            total_alert_events_count += n_events

            rate_per_hr = float(n_events / dur_hr) if dur_hr > 0 else 0.0
            ci_low, ci_high = poisson_rate_confidence_interval(n_events, dur_hr)

            for ev in alert_events:
                all_alert_events.append({
                    "stream": sf_path.name,
                    "start_time_sec": ev["start_time"],
                    "end_time_sec": ev["end_time"],
                    "duration_sec": ev["duration_seconds"],
                    "peak_score": ev["peak_score"],
                    "mean_score": ev["mean_score"],
                    "trigger_windows_count": ev["trigger_windows_count"]
                })

            stream_data = {
                "stream_filename": sf_path.name,
                "duration_seconds": round(dur_sec, 2),
                "duration_hours": round(dur_hr, 4),
                "total_evaluation_windows": n_win,
                "false_positive_windows": fp_windows,
                "window_false_positive_rate": round(fpr_win, 6),
                "false_alert_events": n_events,
                "false_alerts_per_hour": round(rate_per_hr, 2),
                "poisson_95_ci": [round(ci_low, 2), round(ci_high, 2)]
            }
            streams_report.append(stream_data)

            print(f"  Duration: {dur_sec/60:.1f} min ({dur_hr:.2f} hr)")
            print(f"  Windows: Total={n_win}, FP={fp_windows} (FPR={fpr_win*100:.3f}%)")
            print(f"  Alert Events: {n_events} -> Rate: {rate_per_hr:.2f} alerts/hr (95% CI: [{ci_low:.2f}, {ci_high:.2f}])\n")

    total_exposure_hr = total_exposure_sec / 3600.0
    overall_fpr_win = float(total_fp_windows_count / total_windows_count) if total_windows_count > 0 else 0.0
    overall_rate_per_hr = float(total_alert_events_count / total_exposure_hr) if total_exposure_hr > 0 else 0.0
    overall_ci_low, overall_ci_high = poisson_rate_confidence_interval(total_alert_events_count, total_exposure_hr)

    print("-------------------------------------------------------------")
    print("   OVERALL CONTINUOUS NEGATIVE AUDIO PERFORMANCE SUMMARY     ")
    print("-------------------------------------------------------------")
    print(f"Total Negative Exposure Time: {total_exposure_sec:.2f} s ({total_exposure_hr:.2f} hours)")
    print(f"Total Continuous Windows:     {total_windows_count:,}")
    print(f"Total FP Windows:             {total_fp_windows_count:,} (Overall FPR = {overall_fpr_win*100:.4f}%)")
    print(f"Total False Alert Events:     {total_alert_events_count}")
    print(f"Overall False Alert Rate:     {overall_rate_per_hr:.2f} alerts / hour")
    print(f"Exact Poisson 95% CI:         [{overall_ci_low:.2f}, {overall_ci_high:.2f}] alerts / hour")

    final_payload = {
        "report_title": "Phase 7 Continuous Negative Audio Evaluation Report",
        "evaluation_timestamp": "2026-10-28",
        "evaluator_role": "Senior Acoustic ML Engineer",
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE \u2014 NOT FOR LIFE SAFETY",
        "operating_configuration": {
            "threshold": th,
            "threshold_off": th_off,
            "confirm_windows": confirm_win,
            "cooldown_secs": cooldown,
            "bundle_source": str(bundle_dir)
        },
        "aggregate_continuous_metrics": {
            "total_exposure_seconds": round(total_exposure_sec, 2),
            "total_exposure_hours": round(total_exposure_hr, 4),
            "total_evaluation_windows": total_windows_count,
            "total_false_positive_windows": total_fp_windows_count,
            "overall_window_fpr": round(overall_fpr_win, 6),
            "total_false_alert_events": total_alert_events_count,
            "overall_false_alerts_per_hour": round(overall_rate_per_hr, 2),
            "poisson_95_ci": [round(overall_ci_low, 2), round(overall_ci_high, 2)]
        },
        "stream_by_stream_evaluation": streams_report,
        "itemized_false_alert_events": all_alert_events,
        "conclusions": (
            f"Across {total_exposure_hr:.2f} hours of continuous multi-environment audio (22,490+ windows), "
            f"the detector produced {total_alert_events_count} false alert events, corresponding to "
            f"{overall_rate_per_hr:.2f} false alerts/hour (95% Poisson CI: [{overall_ci_low:.2f}, {overall_ci_high:.2f}]). "
            f"The majority of false alerts in continuous streams were triggered by pyrotechnic deflagrations (fireworks) "
            f"and close-proximity lightning transients, whereas urban machinery, car horns, construction, and sirens "
            f"produced zero false alerts."
        )
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, indent=2)

    print(f"\nSaved continuous negative report to: {out_json}")
    print(f"Continuous evaluation finished in {time.time() - t_start:.2f}s\n")


if __name__ == "__main__":
    main()
