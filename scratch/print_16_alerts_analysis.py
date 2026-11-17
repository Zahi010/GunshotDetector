import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import pandas as pd
import json

df = pd.read_csv("scratch/v7_continuous_alerts_audit.csv")
print("=== 16 CONTINUOUS ALERTS IN V7 ===")
for idx, r in df.iterrows():
    print(f"Alert {r['alert_idx']:2d}: t={r['file_time_s']:7.2f}s | raw={r['raw_score']:.4f} | v6_adj={r['v6_adj_score']:.4f} | v7_adj={r['v7_adj_score']:.4f} | v6_cat={r['v6_supp_cat']} | v7_cat={r['v7_supp_cat']} | crest={r['crest_db']:.2f}dB | lo={r['low_ratio']:.2f} | cent={r['centroid_hz']:.1f}Hz | pure_gun={r['pure_gun']:.3f} | bal_s={r['bal_s']:.3f} | top={r['top_yamnet']}")

