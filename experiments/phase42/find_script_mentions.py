import pathlib

REPO = pathlib.Path(".")
for py in REPO.glob("scripts/*.py"):
    text = py.read_text(encoding="utf-8", errors="ignore")
    if "62" in text and "firework" in text.lower():
        print(f"Found '62' & firework in {py.name}")
    if "58" in text and "firework" in text.lower():
        print(f"Found '58' & firework in {py.name}")

