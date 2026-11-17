"""
Phase 4 Training Feature Extraction & Low-SNR Augmentation Pipeline.

Preserves validation and test splits 100% untouched.
Applies:
1. Low-SNR & distance augmentation to training gunshots:
   - Realistic SNR background mixing (0 dB to 15 dB)
   - Distance/atmospheric high-frequency roll-off filtering (lowpass 2.5 - 4.0 kHz)
   - Gain variation (-12 dB to +3 dB)
2. Ingests verified real-world metallic chimes/bells negatives into the training split.
3. Produces .cache_features/features_train_phase4.npz for Phase 4 ensemble training.
"""
import os
import sys
import time
import random
from pathlib import Path
import numpy as np
import scipy.signal
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import GunshotDataset, load_audio_mono_16k, get_base_stem
from feature_extractor import YAMNetFeatureExtractor


def apply_distance_filter(wave: np.ndarray, sr: int = 16000, cutoff_hz: float = 3000.0) -> np.ndarray:
    """Simulate atmospheric high-frequency absorption over distance."""
    nyquist = sr / 2.0
    norm_cutoff = min(0.95, max(0.05, cutoff_hz / nyquist))
    b, a = scipy.signal.butter(2, norm_cutoff, btype="low")
    return scipy.signal.lfilter(b, a, wave).astype(np.float32)


def main():
    print("\n=======================================================")
    print("   PHASE 4: TRAINING FEATURE & LOW-SNR AUGMENTATION    ")
    print("=======================================================")
    t0 = time.time()

    # 1. Load existing Phase 3 train cache
    train_cache = np.load(".cache_features/features_train.npz", allow_pickle=True)
    X_train_base = train_cache["X"]
    y_train_base = train_cache["y"]
    meta_train_base = list(train_cache["meta"]) if "meta" in train_cache else []

    print(f"Base training features: {X_train_base.shape}, Positives={sum(y_train_base==1)}, Negatives={sum(y_train_base==0)}")

    # Load approved hard negatives
    hn_cache = np.load(".cache_features/features_hard_negatives.npz", allow_pickle=True)
    X_hn = hn_cache["X"]
    y_hn = hn_cache["y"]
    print(f"Approved hard negatives: {X_hn.shape}")

    # 2. Extract features from new metallic church bells (strictly training negatives)
    extractor = YAMNetFeatureExtractor()
    bells_dir = Path("data/raw/background/metallic_chimes_and_bells")
    bell_files = list(bells_dir.glob("*.wav"))
    print(f"\nExtracting features from {len(bell_files)} metallic church bells / chimes...")

    X_bells = []
    y_bells = []
    meta_bells = []

    for fpath in bell_files:
        try:
            wave = load_audio_mono_16k(fpath)
            embs, ts = extractor.extract_continuous_recording(wave)
            for emb, (st, et) in zip(embs, ts):
                X_bells.append(emb)
                y_bells.append(0)
                meta_bells.append({
                    "recording_id": f"esc50_chime_{fpath.stem}",
                    "start_time": st,
                    "end_time": et,
                    "label": 0,
                    "category": "metallic_chimes_and_bells"
                })
        except Exception as e:
            print(f"  Error loading {fpath.name}: {e}")

    if X_bells:
        X_bells = np.array(X_bells, dtype=np.float32)
        y_bells = np.array(y_bells, dtype=np.int32)
        print(f"Extracted {len(y_bells)} metallic bell windows.")
    else:
        X_bells = np.empty((0, 1024), dtype=np.float32)
        y_bells = np.empty((0,), dtype=np.int32)

    # 3. Create low-SNR augmented training gunshots
    print("\nSynthesizing low-SNR and distant gunshot training representations...")
    ds = GunshotDataset()
    ds.index_files()

    train_pos_groups = [g for g in ds.splits["train"] if ds.groups[g]["label"] == 1]
    train_bg_files = []
    for g in ds.splits["train"]:
        if ds.groups[g]["label"] == 0:
            train_bg_files.extend(ds.groups[g]["files"])

    print(f"Train positive groups: {len(train_pos_groups)}, Train background source files: {len(train_bg_files)}")

    # Load a few background clips into RAM for mixing
    bg_pool = []
    for bg_f in train_bg_files[:30]:
        try:
            w = load_audio_mono_16k(bg_f)
            if len(w) > 16000:
                bg_pool.append(w)
        except Exception:
            pass

    random.seed(42)
    np.random.seed(42)

    X_low_snr = []
    y_low_snr = []
    meta_low_snr = []

    for gk in train_pos_groups:
        primary_file = ds.groups[gk]["files"][0]
        base_stem = ds.groups[gk]["base_stem"]
        try:
            wave = load_audio_mono_16k(primary_file)
            dur = len(wave) / 16000.0

            # Generate 2 low-SNR augmentations per training gunshot
            for aug_i in range(2):
                aug_wave = wave.copy()

                # A. Atmospheric distance low-pass filter
                cutoff = float(np.random.uniform(2200.0, 3800.0))
                aug_wave = apply_distance_filter(aug_wave, sr=16000, cutoff_hz=cutoff)

                # B. Gain attenuation (-12 dB to -3 dB)
                atten_db = float(np.random.uniform(-12.0, -3.0))
                gain = 10.0 ** (atten_db / 20.0)
                aug_wave = aug_wave * gain

                # C. Background noise mixing (0 dB to 15 dB SNR)
                if bg_pool:
                    bg_clip = random.choice(bg_pool)
                    if len(bg_clip) >= len(aug_wave):
                        idx = np.random.randint(0, len(bg_clip) - len(aug_wave) + 1)
                        bg_seg = bg_clip[idx:idx + len(aug_wave)]
                    else:
                        rep = int(np.ceil(len(aug_wave) / len(bg_clip)))
                        bg_seg = np.tile(bg_clip, rep)[:len(aug_wave)]

                    sig_rms = np.sqrt(np.mean(aug_wave ** 2) + 1e-9)
                    bg_rms = np.sqrt(np.mean(bg_seg ** 2) + 1e-9)
                    snr_target_db = float(np.random.uniform(2.0, 15.0))
                    target_bg_rms = sig_rms / (10.0 ** (snr_target_db / 20.0))
                    aug_wave = aug_wave + bg_seg * (target_bg_rms / bg_rms)

                # Extract YAMNet windows
                embs, ts = extractor.extract_continuous_recording(aug_wave)
                
                # Check events overlap to assign label
                events = ds.events_by_id.get(base_stem, [])
                for emb, (w_st, w_et) in zip(embs, ts):
                    overlap = 0.0
                    for ev in events:
                        e_st = ev["start_time_sec"]
                        e_et = ev["end_time_sec"]
                        ov = max(0.0, min(w_et, e_et) - max(w_st, e_st))
                        if ov > overlap:
                            overlap = ov

                    if overlap >= 0.15:
                        X_low_snr.append(emb)
                        y_low_snr.append(1)
                        meta_low_snr.append({
                            "recording_id": f"aug_low_snr_{base_stem}_{aug_i}",
                            "start_time": w_st,
                            "end_time": w_et,
                            "label": 1,
                            "snr_augmented": True
                        })
        except Exception as e:
            print(f"  Error augmenting {primary_file.name}: {e}")

    X_low_snr = np.array(X_low_snr, dtype=np.float32)
    y_low_snr = np.array(y_low_snr, dtype=np.int32)
    print(f"Generated {len(y_low_snr)} low-SNR gunshot windows for training.")

    # 4. Assemble final Phase 4 training feature set
    X_train_phase4 = np.vstack([X_train_base, X_hn, X_bells, X_low_snr])
    y_train_phase4 = np.concatenate([y_train_base, y_hn, y_bells, y_low_snr])

    out_path = Path(".cache_features/features_train_phase4.npz")
    np.savez_compressed(
        out_path,
        X=X_train_phase4,
        y=y_train_phase4,
        meta_base_count=len(y_train_base),
        meta_hn_count=len(y_hn),
        meta_bells_count=len(y_bells),
        meta_low_snr_count=len(y_low_snr)
    )

    print("\n=======================================================")
    print(f"Phase 4 training cache saved to: {out_path}")
    print(f"Total training windows: {len(y_train_phase4)}")
    print(f"  - Base training windows:        {len(y_train_base)} (Pos: {sum(y_train_base==1)}, Neg: {sum(y_train_base==0)})")
    print(f"  - Approved hard negatives:      {len(y_hn)} (Neg: {len(y_hn)})")
    print(f"  - Metallic chimes & bells:      {len(y_bells)} (Neg: {len(y_bells)})")
    print(f"  - Low-SNR augmented gunshots:   {len(y_low_snr)} (Pos: {len(y_low_snr)})")
    print(f"Final training class balance:     {sum(y_train_phase4==1)} Positives vs {sum(y_train_phase4==0)} Negatives")
    print(f"Elapsed time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
