import pandas as pd
import pathlib

REPO = pathlib.Path(".")
ids = ["51749", "115295"]

print("Searching for 51749 and 115295 across all CSV/JSON dataset manifests in the repo...")
found_records = []
for p in REPO.rglob("*.csv"):
    if "phase41" in str(p) or "phase42" in str(p):
        continue
    try:
        df = pd.read_csv(p)
        for col in df.columns:
            matches = df[df[col].astype(str).str.contains("51749|115295", regex=True, na=False)]
            if len(matches) > 0:
                print(f"Found match in {p.name} (col: {col}): {len(matches)} rows")
                found_records.append((str(p), col, len(matches)))
                break
    except Exception:
        pass

for p in REPO.rglob("*.json"):
    if "phase41" in str(p) or "phase42" in str(p):
        continue
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
        if "51749" in text or "115295" in text:
            print(f"Found match in JSON: {p.name}")
    except Exception:
        pass

