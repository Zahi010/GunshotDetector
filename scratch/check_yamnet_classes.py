import csv
from pathlib import Path

csv_path = Path(r"C:\Users\zahia\.cache\kagglehub\models\google\yamnet\tensorFlow2\yamnet\1\assets\yamnet_class_map.csv")
with open(csv_path, "r", encoding="utf-8") as f:
    reader = list(csv.reader(f))

classes = {int(row[0]): (row[1], row[2]) for row in reader[1:]}

check_ids = [466, 477, 461, 56, 420, 421, 422, 424, 425, 428, 429, 430, 426, 427]
for cid in check_ids:
    mid, name = classes.get(cid, ("?", "Unknown"))
    print(f"Class {cid:3d}: {name} ({mid})")
