import pathlib
import soundfile as sf
import pandas as pd
import hashlib

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# Check phase19
p19_dir = pathlib.Path("e:/gunshot/gunshot/data/phase19_independent_positive/normalized_16k")
p19_files = list(p19_dir.glob("*.wav"))
print(f"Phase 19 positive files: {len(p19_files)}")

# Check phase12 gunshots
p12_dir = pathlib.Path("e:/gunshot/gunshot/data/phase12_independent_test/gunshots")
p12_files = list(p12_dir.glob("*.wav")) if p12_dir.exists() else []
print(f"Phase 12 gunshot files: {len(p12_files)}")

# Check phase15 gunshots
p15_dir = pathlib.Path("e:/gunshot/gunshot/data/phase15_independent_eval/gunshots")
p15_files = list(p15_dir.glob("*.wav")) if p15_dir.exists() else []
print(f"Phase 15 gunshot files: {len(p15_files)}")

# Check phase12 negatives
p12_neg = pathlib.Path("e:/gunshot/gunshot/data/phase12_independent_test/negatives")
p12_neg_files = list(p12_neg.glob("*.wav")) if p12_neg.exists() else []
print(f"Phase 12 negative files: {len(p12_neg_files)}")

# Check phase15 negatives
p15_neg = pathlib.Path("e:/gunshot/gunshot/data/phase15_independent_eval/negatives")
p15_neg_files = list(p15_neg.glob("*.wav")) if p15_neg.exists() else []
print(f"Phase 15 negative files: {len(p15_neg_files)}")

# Check SHA256 overlap with Phase 51 manifest
p51_manifest = pd.read_csv("e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv")
p51_hashes = set(p51_manifest["sha256"])

overlap_p19 = 0
for f in p19_files:
    if sha256_file(f) in p51_hashes:
        overlap_p19 += 1
print(f"Phase 19 overlap with Phase 51: {overlap_p19} / {len(p19_files)}")

overlap_p15 = 0
for f in p15_files:
    if sha256_file(f) in p51_hashes:
        overlap_p15 += 1
print(f"Phase 15 overlap with Phase 51: {overlap_p15} / {len(p15_files)}")

