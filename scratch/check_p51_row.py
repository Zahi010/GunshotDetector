import pandas as pd

df = pd.read_csv("e:/gunshot/gunshot/experiments/phase52_validation/v8_v9_discrete_eval.csv")
row = df[df["filename"] == "mitchell_mossberg_12g_04.wav"]
print(row.to_string())

