"""
Acoustically Modeled Hard-Negative Audio Generator.

Synthesizes realistic, physically modeled impulsive negative sounds that typically
trigger false positives in gunshot detection systems:
1. Fireworks and firecrackers (rapid crackles, propellant blast, reverberation)
2. Vehicle backfires and engine exhaust pops (metallic pipe resonance, low thud)
3. Balloon bursts (sharp pressure release pop, fast acoustic dissipation)
4. Construction hammering and metal impacts (sharp hammer strike + metallic modal decay)
5. Heavy door and car door slams (deep frame thud + mechanical latch click)
6. Thunder and distant explosive rumbles (rolling low-frequency thunderclaps)
7. Drum kit and acoustic percussion (sharp snare rimshots, kick transients)

All audio is generated at 16 kHz mono float32 (standard YAMNet format) with
reproducible random seeds and strict provenance logging.
"""
import os
import argparse
import numpy as np
import soundfile as sf
from pathlib import Path
from scipy import signal
from typing import List, Dict, Any, Tuple

import config


def apply_envelope(signal_data: np.ndarray, attack_sec: float, decay_sec: float, sr: int = 16000) -> np.ndarray:
    """Apply an exponential AD (Attack-Decay) envelope."""
    n_samples = len(signal_data)
    t = np.arange(n_samples) / sr
    attack_samples = max(1, int(attack_sec * sr))
    
    env = np.zeros(n_samples, dtype=np.float32)
    # Attack: linear or fast rise
    env[:attack_samples] = np.linspace(0.0, 1.0, attack_samples) ** 1.5
    # Decay: exponential
    decay_samples = n_samples - attack_samples
    if decay_samples > 0:
        decay_curve = np.exp(-t[:decay_samples] / max(0.001, decay_sec))
        env[attack_samples:] = decay_curve
    return (signal_data * env).astype(np.float32)


def apply_reverb(audio: np.ndarray, decay: float = 0.35, delays_ms: List[float] = [23, 37, 51, 73], sr: int = 16000) -> np.ndarray:
    """Add multi-tap comb filter acoustic reverberation."""
    out = audio.copy()
    for d_ms in delays_ms:
        delay_samples = int(d_ms * sr / 1000.0)
        if delay_samples < len(audio):
            delayed = np.zeros_like(audio)
            delayed[delay_samples:] = audio[:-delay_samples] * decay
            out += delayed
            decay *= 0.75
    # Normalize peak
    peak = np.max(np.abs(out)) + 1e-8
    return out / peak * 0.95


def synth_fireworks(duration_sec: float = 2.0, num_pops: int = 4, sr: int = 16000) -> np.ndarray:
    """Synthesize firecracker / firework sequence (multi-burst crackle + low blast)."""
    n_samples = int(duration_sec * sr)
    out = np.zeros(n_samples, dtype=np.float32)

    # Base low-frequency air concussion blast
    t = np.arange(n_samples) / sr
    low_blast = np.sin(2 * np.pi * 55 * t) * np.exp(-t / 0.4)
    out += low_blast * 0.4

    # Multiple crackle pops
    pop_times = np.random.uniform(0.05, duration_sec - 0.4, size=num_pops)
    for p_time in pop_times:
        p_idx = int(p_time * sr)
        pop_len = int(0.25 * sr)
        if p_idx + pop_len > n_samples:
            pop_len = n_samples - p_idx
        if pop_len <= 0:
            continue
        # Noise burst with sharp high-pass
        noise = np.random.randn(pop_len).astype(np.float32)
        # BPF around 1.5kHz - 6kHz
        sos = signal.butter(4, [1200, 6500], btype='bandpass', fs=sr, output='sos')
        filtered_pop = signal.sosfilt(sos, noise)
        env_pop = apply_envelope(filtered_pop, attack_sec=0.001, decay_sec=0.035, sr=sr)
        out[p_idx:p_idx + pop_len] += env_pop * np.random.uniform(0.5, 0.9)

    out = apply_reverb(out, decay=0.3, delays_ms=[19, 41, 67], sr=sr)
    return out


def synth_vehicle_backfire(duration_sec: float = 1.8, sr: int = 16000) -> np.ndarray:
    """Synthesize vehicle engine backfire / exhaust pop."""
    n_samples = int(duration_sec * sr)
    t = np.arange(n_samples) / sr
    out = np.zeros(n_samples, dtype=np.float32)

    # Initial sharp detonation transient
    detonation = np.random.randn(n_samples).astype(np.float32)
    sos_det = signal.butter(2, [180, 2200], btype='bandpass', fs=sr, output='sos')
    detonation = signal.sosfilt(sos_det, detonation)
    detonation = apply_envelope(detonation, attack_sec=0.0005, decay_sec=0.02, sr=sr)

    # Exhaust pipe acoustic cavity resonance (120 Hz fundamental + 360 Hz harmonic)
    pipe_res = (
        np.sin(2 * np.pi * 135 * t + 0.2) * np.exp(-t / 0.18) * 0.6 +
        np.sin(2 * np.pi * 380 * t) * np.exp(-t / 0.12) * 0.35 +
        np.sin(2 * np.pi * 850 * t) * np.exp(-t / 0.08) * 0.2
    )

    out = detonation * 0.7 + pipe_res * 0.5
    # Add trailing tail
    out = apply_reverb(out, decay=0.25, delays_ms=[15, 31, 55], sr=sr)
    return out


def synth_balloon_burst(duration_sec: float = 1.2, sr: int = 16000) -> np.ndarray:
    """Synthesize balloon burst (sharp non-reverberant high-frequency impulse pop)."""
    n_samples = int(duration_sec * sr)
    t = np.arange(n_samples) / sr
    # Very sharp impulse (< 1 ms attack)
    pop = np.random.randn(n_samples).astype(np.float32)
    sos = signal.butter(3, [800, 7000], btype='bandpass', fs=sr, output='sos')
    pop = signal.sosfilt(sos, pop)
    # Fast exponential decay, very little low frequency
    pop = apply_envelope(pop, attack_sec=0.0003, decay_sec=0.012, sr=sr)
    # Gentle air rush tail
    air_tail = np.random.randn(n_samples).astype(np.float32) * 0.1
    sos_air = signal.butter(2, [2000, 5000], btype='bandpass', fs=sr, output='sos')
    air_tail = signal.sosfilt(sos_air, air_tail)
    air_tail = apply_envelope(air_tail, attack_sec=0.01, decay_sec=0.15, sr=sr)

    out = pop * 0.85 + air_tail * 0.15
    return (out / (np.max(np.abs(out)) + 1e-8) * 0.90).astype(np.float32)


def synth_metal_hammer_impact(duration_sec: float = 1.5, sr: int = 16000) -> np.ndarray:
    """Synthesize metal-on-metal hammer strike with high-Q modal resonances."""
    n_samples = int(duration_sec * sr)
    t = np.arange(n_samples) / sr
    out = np.zeros(n_samples, dtype=np.float32)

    # Initial impact transient
    impact = np.random.randn(n_samples).astype(np.float32)
    impact = apply_envelope(impact, attack_sec=0.0002, decay_sec=0.008, sr=sr)

    # Sharp modal resonant frequencies of steel / anvil
    modes = [950, 1850, 2920, 4400, 6100]
    modal_sound = np.zeros(n_samples, dtype=np.float32)
    for freq in modes:
        decay_time = np.random.uniform(0.15, 0.45)
        phase = np.random.uniform(0, 2 * np.pi)
        modal_sound += np.sin(2 * np.pi * freq * t + phase) * np.exp(-t / decay_time)

    out = impact * 0.4 + modal_sound * 0.6
    out = apply_reverb(out, decay=0.2, delays_ms=[12, 28, 48], sr=sr)
    return out


def synth_door_slam(duration_sec: float = 1.6, sr: int = 16000) -> np.ndarray:
    """Synthesize heavy door or car door slam (low frame thud + latch click)."""
    n_samples = int(duration_sec * sr)
    t = np.arange(n_samples) / sr

    # Mechanical latch click (sharp high transient at t=0.02s)
    click = np.random.randn(n_samples).astype(np.float32)
    sos_click = signal.butter(4, [2500, 7000], btype='bandpass', fs=sr, output='sos')
    click = signal.sosfilt(sos_click, click)
    click = apply_envelope(click, attack_sec=0.0005, decay_sec=0.015, sr=sr)

    # Heavy cabinet / car body low-frequency thump (80-160 Hz)
    thud_noise = np.random.randn(n_samples).astype(np.float32)
    sos_thud = signal.butter(3, [50, 220], btype='bandpass', fs=sr, output='sos')
    thud = signal.sosfilt(sos_thud, thud_noise)
    thud = apply_envelope(thud, attack_sec=0.005, decay_sec=0.22, sr=sr)
    # Add resonant low tone
    low_res = np.sin(2 * np.pi * 95 * t) * np.exp(-t / 0.18) * 0.5

    out = click * 0.4 + thud * 0.5 + low_res * 0.3
    out = apply_reverb(out, decay=0.3, delays_ms=[25, 45, 80], sr=sr)
    return out


def synth_thunder_rumble(duration_sec: float = 3.0, sr: int = 16000) -> np.ndarray:
    """Synthesize rolling thunder clap and low-frequency rumble."""
    n_samples = int(duration_sec * sr)
    t = np.arange(n_samples) / sr
    # Low frequency noise filtered between 30 and 250 Hz
    noise = np.random.randn(n_samples).astype(np.float32)
    sos = signal.butter(3, [35, 280], btype='bandpass', fs=sr, output='sos')
    rumble = signal.sosfilt(sos, noise)
    
    # Complex multi-crest envelope (rolling sound)
    env = (
        0.3 * np.exp(-((t - 0.2) ** 2) / 0.05) +
        0.7 * np.exp(-((t - 0.5) ** 2) / 0.12) +
        0.5 * np.exp(-((t - 1.1) ** 2) / 0.25) +
        0.2 * np.exp(-((t - 1.8) ** 2) / 0.4)
    )
    out = rumble * env
    return (out / (np.max(np.abs(out)) + 1e-8) * 0.85).astype(np.float32)


def synth_percussion_transient(duration_sec: float = 1.2, sr: int = 16000) -> np.ndarray:
    """Synthesize drum snare rimshot / acoustic percussion strike."""
    n_samples = int(duration_sec * sr)
    t = np.arange(n_samples) / sr

    # Snare wire high-frequency noise
    noise = np.random.randn(n_samples).astype(np.float32)
    sos_snare = signal.butter(3, [1500, 6500], btype='bandpass', fs=sr, output='sos')
    snare = signal.sosfilt(sos_snare, noise)
    snare = apply_envelope(snare, attack_sec=0.0005, decay_sec=0.06, sr=sr)

    # Drum head fundamental tone (~180 Hz)
    head_tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.08)

    out = snare * 0.7 + head_tone * 0.4
    out = apply_reverb(out, decay=0.25, delays_ms=[15, 35, 60], sr=sr)
    return out


GENERATORS = {
    "fireworks": synth_fireworks,
    "vehicle_backfire": synth_vehicle_backfire,
    "balloon_burst": synth_balloon_burst,
    "metal_hammer_impact": synth_metal_hammer_impact,
    "door_slam": synth_door_slam,
    "thunder_rumble": synth_thunder_rumble,
    "percussion_transient": synth_percussion_transient,
}


def generate_hard_negative_dataset(
    output_dir: Path,
    num_per_category: int = 10,
    seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Generate balanced set of difficult acoustic negatives.
    """
    np.random.seed(seed)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    print(f"\nGenerating {num_per_category} hard-negative examples per category into: {output_dir}")

    for cat_name, gen_func in GENERATORS.items():
        cat_dir = output_dir / cat_name
        cat_dir.mkdir(parents=True, exist_ok=True)

        for i in range(1, num_per_category + 1):
            dur = np.random.uniform(1.2, 3.2)
            audio = gen_func(duration_sec=dur, sr=config.SAMPLE_RATE)
            fname = f"hard_neg_{cat_name}_{i:03d}.wav"
            fpath = cat_dir / fname

            sf.write(str(fpath), audio, config.SAMPLE_RATE, subtype='PCM_16')
            records.append({
                "filename": fname,
                "relative_path": str(fpath.relative_to(output_dir.parent.parent)),
                "category": cat_name,
                "duration_sec": round(float(dur), 3),
                "sample_rate": config.SAMPLE_RATE,
                "class": "background"
            })

        print(f"  [OK] Generated {num_per_category} files for '{cat_name}'")

    print(f"\nTotal Hard-Negative Audio Records Generated: {len(records)}")
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate hard acoustic negative examples.")
    parser.add_argument("--output-dir", type=str, default="data/background/hard_negatives", help="Output directory")
    parser.add_argument("--count", type=int, default=10, help="Count per category")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    out_p = Path(args.output_dir)
    generate_hard_negative_dataset(output_dir=out_p, num_per_category=args.count, seed=args.seed)
