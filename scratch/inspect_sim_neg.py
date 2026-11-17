import pandas as pd

neg = pd.read_csv("e:/gunshot/gunshot/scratch/sim_neg_results.csv")
print("Unique sub_categories in neg:")
print(neg["sub_category"].value_counts())
print("\nFalse positives in V9:")
print(neg[neg["v9_detected"]][["filename", "sub_category", "condition", "v9_peak", "v10_peak"]])
print("\nFalse positives in V10:")
print(neg[neg["v10_detected"]][["filename", "sub_category", "condition", "v9_peak", "v10_peak"]])

