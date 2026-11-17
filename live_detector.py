"""
Standalone Real-Time Gunshot Sound Detector.

Continuously captures live audio from a local microphone, processes it in
overlapping 0.96s windows (0.48s hop) at 16 kHz mono, and classifies it using
the trained YAMNet gunshot detection model.

Key Features:
- Class-Based Alerting: Alerts trigger ONLY when the gunshot neural network score
  exceeds the threshold—NEVER from general loud noises or volume level alone.
- Window Confirmation & Cooldown: Configurable consecutive positive windows (to
  prevent transient false alarms) and cooldown period (to prevent repetitive alerts).
- Visual & Sound Alerts: Terminal alert with timestamp and optional audible beep.
- Privacy-First: Audio is NOT saved by default. Opt-in saving via `--save-clips`
  stores 2-second alert clips in the `saved_alerts/` directory.
- Clear Diagnostics: Lists input devices, verifies model integrity, and handles errors.

Usage:
------
python live_detector.py --list-devices
python live_detector.py --device 1 --threshold 0.47 --cooldown 2.0 --sound-alert
"""
import os
import sys
import time
import queue
import argparse
import datetime
import threading
import numpy as np
import sounddevice as sd
import soundfile as sf
from pathlib import Path

# Optional Windows beep support
try:
    import winsound
except ImportError:
    winsound = None

import config
from model import load_model_bundle, GunshotDetector
from feature_extractor import YAMNetFeatureExtractor


def list_audio_devices():
    """Print available microphone and input devices."""
    print("\n=======================================================")
    print("      AVAILABLE MICROPHONE / AUDIO INPUT DEVICES")
    print("=======================================================")
    devices = sd.query_devices()
    default_in = sd.default.device[0]
    in_count = 0

    for idx, d in enumerate(devices):
        if d["max_input_channels"] > 0:
            is_def = " (DEFAULT)" if idx == default_in else ""
            print(f"  [{idx:2d}] {d['name']}{is_def}")
            print(f"       Channels: {d['max_input_channels']} | Default SR: {int(d['default_samplerate'])} Hz")
            in_count += 1

    if in_count == 0:
        print("  [ERROR] No microphone or audio input devices detected!")
    print("=======================================================\n")


class LiveGunshotListener:
    """
    Continuous real-time gunshot detector.
    """
    def __init__(
        self,
        bundle_dir: Path = config.MODELS_DIR / "gunshot_yamnet_bundle",
        device: int = None,
        threshold: float = config.DEFAULT_THRESHOLD,
        hop_secs: float = config.LIVE_STREAM_HOP_SECS,
        window_secs: float = config.LIVE_STREAM_WINDOW_SECS,
        confirm_windows: int = config.DEFAULT_CONFIRM_WINDOWS,
        cooldown_secs: float = config.DEFAULT_COOLDOWN_SECS,
        enable_sound_alert: bool = True,
        save_clips: bool = False,
        saved_alerts_dir: Path = config.SAVED_ALERTS_DIR
    ):
        self.device = device
        self.threshold = threshold
        self.hop_secs = hop_secs
        self.window_secs = window_secs
        self.window_samples = int(config.SAMPLE_RATE * window_secs)
        self.hop_samples = int(config.SAMPLE_RATE * hop_secs)
        self.confirm_windows = max(1, confirm_windows)
        self.cooldown_secs = cooldown_secs
        self.enable_sound_alert = enable_sound_alert
        self.save_clips = save_clips
        self.saved_alerts_dir = Path(saved_alerts_dir)
        if self.save_clips:
            self.saved_alerts_dir.mkdir(parents=True, exist_ok=True)

        self.audio_queue = queue.Queue()
        self.is_running = False
        self.consecutive_positives = 0
        self.last_alert_time = 0.0

        # Load Detector
        print(f"Loading YAMNet model bundle from: {bundle_dir}")
        self.detector = GunshotDetector(bundle_dir=bundle_dir, threshold=self.threshold)
        print(f"Detector ready. Selected Threshold: {self.detector.threshold:.3f}")

    def audio_callback(self, indata, frames, time_info, status):
        """Audio streaming callback from sounddevice."""
        if status:
            print(f"\n[Audio Warning] {status}", file=sys.stderr)
        # indata is (frames, channels). We take channel 0 for mono.
        mono_chunk = indata[:, 0].copy()
        self.audio_queue.put(mono_chunk)

    def trigger_alert(self, score: float, window_waveform: np.ndarray):
        """Handle confirmed gunshot alert."""
        now = time.time()
        now_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print("\n" + "=" * 65)
        print(f"  >>> [!] GUNSHOT DETECTED AT {now_dt} [!]")
        print(f"      Detection Score: {score:.4f} (Threshold: {self.threshold:.2f})")
        print(f"      Neural network identified firearm acoustic signature.")
        print("=" * 65)

        # Optional Sound Alert
        if self.enable_sound_alert:
            if winsound:
                try:
                    winsound.Beep(1200, 300)
                    winsound.Beep(1600, 400)
                except Exception:
                    print("\a", end="", flush=True)
            else:
                print("\a", end="", flush=True)

        # Optional Clip Saving (Opt-in)
        if self.save_clips:
            clip_name = f"gunshot_alert_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            clip_path = self.saved_alerts_dir / clip_name
            try:
                sf.write(str(clip_path), window_waveform, config.SAMPLE_RATE)
                print(f"      [Opt-in Saved] Alert clip recorded to: {clip_path}")
            except Exception as e:
                print(f"      [Warning] Failed to save clip: {e}")

        self.last_alert_time = now

    def start_listening(self):
        """Start continuous live audio detection loop."""
        self.is_running = True
        print("\n=======================================================")
        print("      LIVE GUNSHOT SOUND DETECTION ACTIVE")
        print("=======================================================")
        print(f"  Sample Rate:        {config.SAMPLE_RATE} Hz (Mono)")
        print(f"  Window Length:      {self.window_secs}s ({self.window_samples} samples)")
        print(f"  Hop Step:           {self.hop_secs}s ({self.hop_samples} samples)")
        print(f"  Detection Threshold:{self.threshold:.2f}")
        print(f"  Confirm Windows:    {self.confirm_windows}")
        print(f"  Alert Cooldown:     {self.cooldown_secs}s")
        print(f"  Audio Alert:        {'Enabled' if self.enable_sound_alert else 'Disabled'}")
        print(f"  Save Clips:         {'Enabled -> ' + str(self.saved_alerts_dir) if self.save_clips else 'Disabled (Privacy Mode)'}")
        print("  Press Ctrl+C to stop listening.")
        print("-------------------------------------------------------")

        # Circular buffer to hold 1 full window of audio
        ring_buffer = np.zeros(self.window_samples, dtype=np.float32)
        samples_since_last_eval = 0

        try:
            with sd.InputStream(
                samplerate=config.SAMPLE_RATE,
                channels=1,
                dtype="float32",
                device=self.device,
                callback=self.audio_callback,
                blocksize=int(config.SAMPLE_RATE * 0.05)  # 50ms chunks
            ):
                print("Listening through microphone... [OK]\n")
                while self.is_running:
                    try:
                        chunk = self.audio_queue.get(timeout=0.2)
                    except queue.Empty:
                        continue

                    chunk_len = len(chunk)
                    # Shift ring buffer left and append new chunk
                    ring_buffer = np.roll(ring_buffer, -chunk_len)
                    ring_buffer[-chunk_len:] = chunk
                    samples_since_last_eval += chunk_len

                    # When accumulated samples reach hop size, evaluate
                    if samples_since_last_eval >= self.hop_samples:
                        samples_since_last_eval = 0
                        current_window = ring_buffer.copy()

                        # Audio RMS energy
                        rms = float(np.sqrt(np.mean(current_window ** 2) + 1e-12))
                        # Energy squelch gate: true silence is ignored
                        if rms < 1e-4:
                            score = 0.0
                        else:
                            # Evaluate with YAMNet + Classifier Head
                            res = self.detector.detect_waveform(current_window, threshold=self.threshold)
                            score = res["overall_score"]

                        now = time.time()
                        in_cooldown = (now - self.last_alert_time) < self.cooldown_secs

                        # Status display in terminal
                        status_tag = "[ALERT COOLDOWN]" if in_cooldown else ("[TRIGGERED]" if score >= self.threshold else "[CLEAN]")
                        rms_db = 20 * np.log10(max(rms, 1e-6))
                        print(
                            f"\rScore: {score:5.3f} | Thresh: {self.threshold:.2f} | "
                            f"RMS: {rms_db:5.1f} dB | Status: {status_tag:<18}",
                            end="",
                            flush=True
                        )

                        # Decision logic
                        if score >= self.threshold and not in_cooldown:
                            self.consecutive_positives += 1
                            if self.consecutive_positives >= self.confirm_windows:
                                self.trigger_alert(score, current_window)
                                self.consecutive_positives = 0
                        else:
                            if not in_cooldown:
                                self.consecutive_positives = 0

        except KeyboardInterrupt:
            print("\n\nStopping live detector...")
        except Exception as e:
            print(f"\n[FATAL ERROR] Microphone stream failed: {e}")
        finally:
            self.is_running = False
            print("Microphone listening stopped safely.")


def main():
    parser = argparse.ArgumentParser(description="Live continuous gunshot detector using microphone.")
    parser.add_argument("--list-devices", action="store_true", help="List audio input devices and exit")
    parser.add_argument("--device", type=int, default=None, help="Input device ID (default: system default mic)")
    parser.add_argument("--threshold", type=float, default=config.DEFAULT_THRESHOLD, help="Detection score threshold")
    parser.add_argument("--cooldown", type=float, default=config.DEFAULT_COOLDOWN_SECS, help="Alert cooldown in seconds")
    parser.add_argument("--confirm-windows", type=int, default=config.DEFAULT_CONFIRM_WINDOWS, help="Consecutive positive windows to alert")
    parser.add_argument("--sound-alert", action="store_true", default=True, help="Enable audible alert beep on detection")
    parser.add_argument("--no-sound", dest="sound_alert", action="store_false", help="Disable audible alert beep")
    parser.add_argument("--save-clips", action="store_true", default=False, help="Opt-in: Save 2s audio clip on detection")
    parser.add_argument("--bundle", type=str, default=str(config.MODELS_DIR / "gunshot_yamnet_bundle"), help="Model bundle path")
    args = parser.parse_args()

    if args.list_devices:
        list_audio_devices()
        return

    listener = LiveGunshotListener(
        bundle_dir=Path(args.bundle),
        device=args.device,
        threshold=args.threshold,
        confirm_windows=args.confirm_windows,
        cooldown_secs=args.cooldown,
        enable_sound_alert=args.sound_alert,
        save_clips=args.save_clips
    )
    listener.start_listening()


if __name__ == "__main__":
    main()
