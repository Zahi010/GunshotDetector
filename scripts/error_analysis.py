"""
Error analysis script for Gunshot Detection System.
Inspects individual window and recording level errors on the held-out test set.
Categorizes errors by source file, time offset, confidence score, and acoustic type.
"""
import json
import numpy as np
from pathlib import Path
from collections import defaultdict
import tensorflow as tf

import sys
import os
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from dataset import GunshotDataset
from model import load_model_bundle

def analyze_errors(bundle_dir="models/gunshot_yamnet_bundle", output_json="reports/error_analysis_report.json"):
    bundle_path = Path(bundle_dir)
    classifier_head, bundle_info = load_model_bundle(bundle_path)
    threshold = bundle_info.get("selected_threshold", 0.295)
    
    # Load cached features
    cache_file = Path(".cache_features/features_test.npz")
    data = np.load(cache_file, allow_pickle=True)
    X_test = data["X"]
    y_test = data["y"]
    meta_test = list(data["meta"])
    
    preds = classifier_head.predict(X_test, verbose=0).flatten()
    
    fps = []
    fns = []
    tps = []
    tns = []
    
    for i, (score, target, m) in enumerate(zip(preds, y_test, meta_test)):
        rec_id = m.get("recording_id") if isinstance(m, dict) else m["recording_id"]
        start_t = m.get("start_time") if isinstance(m, dict) else m["start_time"]
        end_t = m.get("end_time") if isinstance(m, dict) else m["end_time"]
        
        info = {
            "window_index": i,
            "recording_id": rec_id,
            "start_time": round(float(start_t), 3),
            "end_time": round(float(end_t), 3),
            "score": round(float(score), 4),
            "ground_truth": int(target)
        }
        
        if score >= threshold and target == 0:
            fps.append(info)
        elif score < threshold and target == 1:
            fns.append(info)
        elif score >= threshold and target == 1:
            tps.append(info)
        else:
            tns.append(info)
            
    # Group FPs and FNs by recording_id
    fp_by_rec = defaultdict(list)
    for fp in fps:
        fp_by_rec[fp["recording_id"]].append(fp)
        
    fn_by_rec = defaultdict(list)
    for fn in fns:
        fn_by_rec[fn["recording_id"]].append(fn)
        
    print(f"=== ERROR ANALYSIS AT THRESHOLD {threshold:.3f} ===")
    print(f"Total Test Windows: {len(y_test)}")
    print(f"True Positives:  {len(tps)}")
    print(f"True Negatives:  {len(tns)}")
    print(f"False Positives: {len(fps)}")
    print(f"False Negatives: {len(fns)}")
    print(f"\n--- Top False Positive Recordings ({len(fp_by_rec)} recordings affected) ---")
    
    fp_summary = []
    for rec_id, items in sorted(fp_by_rec.items(), key=lambda x: len(x[1]), reverse=True):
        scores = [x["score"] for x in items]
        print(f"  {rec_id}: {len(items)} FP windows (mean score: {np.mean(scores):.3f}, max: {np.max(scores):.3f})")
        fp_summary.append({
            "recording_id": rec_id,
            "count": len(items),
            "mean_score": round(float(np.mean(scores)), 4),
            "max_score": round(float(np.max(scores)), 4),
            "windows": items
        })
        
    print(f"\n--- False Negative Recordings ({len(fn_by_rec)} recordings affected) ---")
    fn_summary = []
    for rec_id, items in sorted(fn_by_rec.items(), key=lambda x: len(x[1]), reverse=True):
        scores = [x["score"] for x in items]
        print(f"  {rec_id}: {len(items)} FN windows (mean score: {np.mean(scores):.3f}, min: {np.min(scores):.3f})")
        fn_summary.append({
            "recording_id": rec_id,
            "count": len(items),
            "mean_score": round(float(np.mean(scores)), 4),
            "min_score": round(float(np.min(scores)), 4),
            "windows": items
        })
        
    report = {
        "threshold": threshold,
        "total_test_windows": len(y_test),
        "tp_count": len(tps),
        "tn_count": len(tns),
        "fp_count": len(fps),
        "fn_count": len(fns),
        "precision": round(len(tps) / (len(tps) + len(fps)), 4),
        "recall": round(len(tps) / (len(tps) + len(fns)), 4),
        "f1": round(2 * len(tps) / (2 * len(tps) + len(fps) + len(fns)), 4),
        "accuracy": round((len(tps) + len(tns)) / len(y_test), 4),
        "top_fp_recordings": fp_summary,
        "top_fn_recordings": fn_summary
    }
    
    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport written to {output_json}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run error analysis on test split.")
    parser.add_argument("--bundle", type=str, default="models/gunshot_yamnet_bundle")
    parser.add_argument("--output", type=str, default="reports/phase3_error_analysis.json")
    parser.add_argument("--threshold", type=float, default=None)
    args = parser.parse_args()

    analyze_errors(
        bundle_dir=args.bundle,
        output_json=args.output
    )
