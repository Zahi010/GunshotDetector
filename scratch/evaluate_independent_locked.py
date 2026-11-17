import sys
import pathlib
import pandas as pd
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from scratch.run_full_v9_evaluation import DetectorImprovementV9
from scratch.test_v10_from_v8 import DetectorImprovementV10

def evaluate_locked_corpus():
    # 1. Phase 19 independent positive corpus (N=23, 0 overlap with Phase 51)
    p19_dir = pathlib.Path("e:/gunshot/gunshot/data/phase19_independent_positive/normalized_16k")
    p19_files = sorted(list(p19_dir.glob("*.wav")))
    
    # 2. Phase 15 independent evaluation corpus (gunshots + negatives)
    p15_gun_dir = pathlib.Path("e:/gunshot/gunshot/data/phase15_independent_eval/gunshots")
    p15_gun_files = sorted(list(p15_gun_dir.glob("*.wav"))) if p15_gun_dir.exists() else []
    p15_neg_dir = pathlib.Path("e:/gunshot/gunshot/data/phase15_independent_eval/negatives")
    p15_neg_files = sorted(list(p15_neg_dir.glob("*.wav"))) if p15_neg_dir.exists() else []
    
    det9 = DetectorImprovementV9()
    det10 = DetectorImprovementV10()
    
    # Evaluate Phase 19
    det9_p19 = 0
    det10_p19 = 0
    for f in p19_files:
        audio, sr = sf.read(str(f), dtype="float32")
        r9 = det9.evaluate_waveform(audio, sr)
        r10 = det10.evaluate_waveform(audio, sr)
        if r9["detected"]: det9_p19 += 1
        if r10["detected"]: det10_p19 += 1
        
    print("=" * 65)
    print(f"INDEPENDENT LOCKED CORPUS: Phase 19 Positives (N={len(p19_files)}):")
    print(f"  V9 Recall:  {det9_p19} / {len(p19_files)} ({det9_p19/len(p19_files)*100:.2f}%)")
    print(f"  V10 Recall: {det10_p19} / {len(p19_files)} ({det10_p19/len(p19_files)*100:.2f}%)")
    print("=" * 65)
    
    # Evaluate Phase 15 gunshots if present
    if p15_gun_files:
        det9_p15 = 0
        det10_p15 = 0
        for f in p15_gun_files:
            audio, sr = sf.read(str(f), dtype="float32")
            r9 = det9.evaluate_waveform(audio, sr)
            r10 = det10.evaluate_waveform(audio, sr)
            if r9["detected"]: det9_p15 += 1
            if r10["detected"]: det10_p15 += 1
            
        print(f"INDEPENDENT LOCKED CORPUS: Phase 15 Positives (N={len(p15_gun_files)}):")
        print(f"  V9 Recall:  {det9_p15} / {len(p15_gun_files)} ({det9_p15/len(p15_gun_files)*100:.2f}%)")
        print(f"  V10 Recall: {det10_p15} / {len(p15_gun_files)} ({det10_p15/len(p15_gun_files)*100:.2f}%)")
        print("=" * 65)
        
    if p15_neg_files:
        fa9_p15 = 0
        fa10_p15 = 0
        for f in p15_neg_files:
            audio, sr = sf.read(str(f), dtype="float32")
            r9 = det9.evaluate_waveform(audio, sr)
            r10 = det10.evaluate_waveform(audio, sr)
            if r9["detected"]: fa9_p15 += 1
            if r10["detected"]: fa10_p15 += 1
            
        print(f"INDEPENDENT LOCKED CORPUS: Phase 15 Negatives (N={len(p15_neg_files)}):")
        print(f"  V9 FPR:  {fa9_p15} / {len(p15_neg_files)} ({fa9_p15/len(p15_neg_files)*100:.2f}%)")
        print(f"  V10 FPR: {fa10_p15} / {len(p15_neg_files)} ({fa10_p15/len(p15_neg_files)*100:.2f}%)")
        print("=" * 65)

if __name__ == "__main__":
    evaluate_locked_corpus()
