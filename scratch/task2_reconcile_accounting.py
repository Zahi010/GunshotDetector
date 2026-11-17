import pandas as pd
from pathlib import Path

pred_csv = "e:/gunshot/gunshot/experiments/phase54_final_validation/recording_level_predictions.csv"
df = pd.read_csv(pred_csv)

print(f"Total rows in predictions: {len(df)}")
pos_df = df[df["ground_truth_label"] == 1]
neg_df = df[df["ground_truth_label"] == 0]

print(f"Positives: {len(pos_df)} (Detected: {pos_df['prediction'].sum()}, Missed: {len(pos_df) - pos_df['prediction'].sum()})")
print(f"Negatives: {len(neg_df)} (False Positives: {neg_df['prediction'].sum()}, True Negatives: {len(neg_df) - neg_df['prediction'].sum()})")

rows = []
for (cat, subcat, gt), g in df.groupby(["category", "sub_category", "ground_truth_label"]):
    total = len(g)
    pred_pos = g["prediction"].sum()
    pred_neg = total - pred_pos
    if gt == 1:
        tp = pred_pos
        fn = pred_neg
        fp = 0
        tn = 0
        rec = tp / total if total > 0 else 0.0
        fpr = 0.0
    else:
        tp = 0
        fn = 0
        fp = pred_pos
        tn = pred_neg
        rec = 0.0
        fpr = fp / total if total > 0 else 0.0
        
    rows.append({
        "category": cat,
        "sub_category": subcat,
        "ground_truth_label": gt,
        "total_recordings": total,
        "detected_as_gunshot": pred_pos,
        "rejected_as_non_gunshot": pred_neg,
        "true_positives": tp,
        "false_negatives": fn,
        "false_positives": fp,
        "true_negatives": tn,
        "metric_rate_pct": round((rec if gt == 1 else fpr) * 100.0, 2),
        "displayed_in_phase54_decision_table": "YES" if subcat != "bioacoustic_human_vocalizations" else "OMITTED_IN_SUMMARY_TABLE"
    })

audit_df = pd.DataFrame(rows)
out_csv = Path("e:/gunshot/gunshot/experiments/phase55_failure_analysis/corpus_accounting_audit.csv")
audit_df.to_csv(out_csv, index=False)
print(f"Corpus accounting audit written to {out_csv}")
print(audit_df.to_string())

