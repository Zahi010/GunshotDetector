import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

df = pd.read_csv('e:/gunshot/gunshot/scratch/missed_positives_detailed_forensics.csv')
print(f"Total rows: {len(df)}")
cols = [
    'filename', 'sub_category', 'condition', 'duration_sec', 'n_wins', 
    'max_raw_score', 'max_adj_score', 'crest_db', 'peak_amp', 'cent_hz', 
    'lo', 'mid', 'hi', 'm2l', 'pure_gun', 'explosion', 
    'p_mlp', 'p_cb', 'p_lgb', 'p_xgb', 'suppressed', 'supp_cat', 'mode', 'fsm_state', 'single_allowed'
]
print(df[cols].to_string())

