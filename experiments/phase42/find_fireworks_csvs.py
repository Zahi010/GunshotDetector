import pandas as pd
import pathlib

REPO = pathlib.Path(".")
for p in REPO.rglob("*firework*.csv"):
    print(p)

for p in REPO.rglob("*distractor*.csv"):
    print(p)

