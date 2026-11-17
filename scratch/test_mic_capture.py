import sys
import time
import numpy as np
import sounddevice as sd

print("Testing physical microphone capture via sounddevice...")
default_device = sd.default.device[0]
print(f"Default input device: {default_device}")

try:
    sr = 16000
    duration_sec = 2.0
    print(f"Recording {duration_sec}s from device {default_device} at {sr}Hz...")
    t0 = time.time()
    recording = sd.rec(int(duration_sec * sr), samplerate=sr, channels=1, dtype='float32', device=default_device)
    sd.wait()
    rec_time = time.time() - t0
    recording = recording.flatten()
    rms = float(np.sqrt(np.mean(recording ** 2)))
    peak = float(np.max(np.abs(recording)))
    print(f"Capture successful in {rec_time:.2f}s!")
    print(f"Samples captured: {len(recording)}, RMS: {rms:.6f}, Peak: {peak:.6f}")
    if rms < 1e-6 and peak < 1e-6:
        print("Note: Microphone captured digital silence (could be muted or privacy gated).")
    else:
        print("Live physical acoustic energy detected from microphone hardware!")
except Exception as e:
    print(f"Microphone capture error: {e}")

