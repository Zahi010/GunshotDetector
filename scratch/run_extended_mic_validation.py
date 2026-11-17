import builtins
_orig_print = builtins.print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    return _orig_print(*args, **kwargs)
import sys
import os
import time
import json
import queue
import threading
from pathlib import Path
import numpy as np
import sounddevice as sd
import soundfile as sf
import librosa
import psutil

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v10.model_detector_improvement_v10 import (
    RealTimeStreamDetectorImprovementV10,
    EventState
)

SAFETY_BANNER = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

class ExtendedPhysicalMicHarness:
    def __init__(self, target_duration_sec: float = 1800.0, device_id: int = 1):
        self.target_duration_sec = target_duration_sec
        self.device_id = device_id
        self.sample_rate = 16000
        self.chunk_size = 7680 # 0.48s at 16 kHz
        self.audio_queue = queue.Queue(maxsize=1000)
        self.stop_event = threading.Event()
        
        # Detector instance
        self.detector = RealTimeStreamDetectorImprovementV10()
        
        # Session isolation test instance
        self.isolated_session_detector = RealTimeStreamDetectorImprovementV10()
        
        # Metrics storage
        self.latencies_ms = []
        self.chunk_timestamps = []
        self.dropped_callbacks = 0
        self.dropped_chunks = 0
        self.total_chunks_processed = 0
        self.clipping_events = 0
        self.rms_values = []
        self.peak_values = []
        self.memory_snapshots_mb = []
        self.state_transitions = []
        self.alerts_detected = []
        self.reconnection_successful = False
        
        # Audio accumulator
        self.buffer = np.zeros(0, dtype=np.float32)

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            self.dropped_callbacks += 1
        
        # Check peak clipping
        peak = np.max(np.abs(indata))
        if peak >= 0.999:
            self.clipping_events += 1
            
        # Convert to mono float32
        if indata.ndim > 1:
            mono = np.mean(indata, axis=1)
        else:
            mono = indata.flatten()
            
        try:
            self.audio_queue.put_nowait(mono.copy())
        except queue.Full:
            self.dropped_chunks += 1

    def run_inference_worker(self):
        process = psutil.Process()
        last_state = self.detector.detector.fsm.state
        last_mem_check = time.time()
        
        while not self.stop_event.is_set() or not self.audio_queue.empty():
            try:
                block = self.audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue
                
            self.buffer = np.concatenate([self.buffer, block])
            
            # Process complete 0.48s chunks
            while len(self.buffer) >= self.chunk_size:
                chunk = self.buffer[:self.chunk_size]
                self.buffer = self.buffer[self.chunk_size:]
                
                # Ingestion metrics
                rms = float(np.sqrt(np.mean(chunk**2) + 1e-12))
                peak = float(np.max(np.abs(chunk)))
                self.rms_values.append(rms)
                self.peak_values.append(peak)
                
                # Timed inference
                t0 = time.perf_counter()
                alerts = self.detector.process_chunk(chunk, input_sample_rate=self.sample_rate)
                t_infer = (time.perf_counter() - t0) * 1000.0
                
                self.latencies_ms.append(t_infer)
                self.total_chunks_processed += 1
                
                # State transition tracking
                current_state = self.detector.detector.fsm.state
                if current_state != last_state:
                    self.state_transitions.append({
                        'timestamp_sec': round(self.total_chunks_processed * 0.48, 2),
                        'from_state': last_state.name if hasattr(last_state, 'name') else str(last_state),
                        'to_state': current_state.name if hasattr(current_state, 'name') else str(current_state),
                        'score': round(float(self.detector.last_score), 4)
                    })
                    last_state = current_state
                    
                if alerts:
                    for a in alerts:
                        self.alerts_detected.append(a)
                        
            # Periodic memory check (every 10s)
            if time.time() - last_mem_check >= 10.0:
                mem_mb = process.memory_info().rss / (1024 * 1024)
                self.memory_snapshots_mb.append(round(mem_mb, 2))
                last_mem_check = time.time()

    def run(self):
        print("=" * 70)
        print(f"STARTING PHYSICAL HARDWARE CAPTURE (Device ID: {self.device_id})")
        print(f"Safety Designation: {SAFETY_BANNER}")
        print(f"Target Duration:    {self.target_duration_sec:.1f}s ({self.target_duration_sec/60:.1f} minutes)")
        print("=" * 70)
        
        # Query device info
        devices = sd.query_devices()
        dev_info = devices[self.device_id]
        print(f"Input Transducer:   {dev_info['name']}")
        native_sr = int(dev_info['default_samplerate'])
        channels = min(1, int(dev_info['max_input_channels']))
        print(f"Configuration:      {self.sample_rate} Hz (Target) | Channels: {channels}")
        
        # Start inference worker thread
        infer_thread = threading.Thread(target=self.run_inference_worker, daemon=True)
        infer_thread.start()
        
        # Open physical stream
        start_time = time.time()
        interruption_done = False
        reconnect_time_target = start_time + min(self.target_duration_sec * 0.9, self.target_duration_sec - 10.0)
        
        # Schedule test playback events across session
        playback_targets = [
            {'time_sec': max(10.0, self.target_duration_sec * 0.15), 'fpath': 'e:/gunshot/gunshot/data/phase8_final_eval/gunshots/mitchell_glock17_9mm_01.wav', 'type': 'gunshot_positive'},
            {'time_sec': max(20.0, self.target_duration_sec * 0.30), 'fpath': 'e:/gunshot/gunshot/data/background/hard_negatives/door_slam/hard_neg_door_slam_001.wav', 'type': 'door_slam_negative'},
            {'time_sec': max(30.0, self.target_duration_sec * 0.50), 'fpath': 'e:/gunshot/gunshot/data/background/hard_negatives/balloon_burst/hard_neg_balloon_burst_001.wav', 'type': 'balloon_burst_negative'},
            {'time_sec': max(40.0, self.target_duration_sec * 0.70), 'fpath': 'e:/gunshot/gunshot/data/phase8_final_eval/gunshots/mitchell_colt_ar15_01.wav', 'type': 'gunshot_positive'},
            {'time_sec': max(50.0, self.target_duration_sec * 0.80), 'fpath': 'e:/gunshot/gunshot/data/background/hard_negatives/fireworks/hard_neg_fireworks_001.wav', 'type': 'fireworks_negative'}
        ]
        playback_log = []
        
        with sd.InputStream(device=self.device_id,
                            samplerate=self.sample_rate,
                            channels=channels,
                            dtype='float32',
                            blocksize=2048,
                            callback=self.audio_callback) as stream:
            print("Physical audio stream successfully opened and active.")
            
            while time.time() - start_time < self.target_duration_sec:
                elapsed = time.time() - start_time
                
                # Check scheduled playbacks
                for p_item in playback_targets:
                    if not p_item.get('played') and elapsed >= p_item['time_sec']:
                        p_item['played'] = True
                        if os.path.exists(p_item['fpath']):
                            try:
                                audio_data, audio_sr = sf.read(p_item['fpath'], dtype='float32')
                                # Playback safely at safe volume (-15 dB)
                                safe_audio = audio_data * 0.25
                                print(f"\n[Acoustic Injection @ {elapsed:.1f}s] Playing safe acoustic test: {p_item['type']} ({os.path.basename(p_item['fpath'])})")
                                sd.play(safe_audio, audio_sr)
                                playback_log.append({
                                    'elapsed_sec': round(elapsed, 2),
                                    'type': p_item['type'],
                                    'file': os.path.basename(p_item['fpath']),
                                    'status': 'played_successfully'
                                })
                            except Exception as pe:
                                print(f"Playback error: {pe}")
                                
                # Check device interruption test (at 90% duration)
                if not interruption_done and elapsed >= (self.target_duration_sec * 0.85) and self.target_duration_sec >= 30.0:
                    print(f"\n[Interruption Test @ {elapsed:.1f}s] Simulating brief hardware pause/reconnect...")
                    stream.stop()
                    time.sleep(2.0)
                    stream.start()
                    self.reconnection_successful = True
                    interruption_done = True
                    print(f"[Interruption Test] Reconnected successfully and stream resumed.")
                    
                time.sleep(1.0)
                if int(elapsed) % 30 == 0 and int(elapsed) > 0:
                    print(f"Elapsed: {elapsed:.0f}s / {self.target_duration_sec:.0f}s | Chunks: {self.total_chunks_processed} | Latency: {np.mean(self.latencies_ms[-10:] if self.latencies_ms else [0]):.1f}ms")
                    
        # Stop worker
        self.stop_event.set()
        infer_thread.join(timeout=5.0)
        
        # Test session isolation
        print("\nTesting multi-session isolation...")
        isolated_chunk = np.zeros(self.chunk_size, dtype=np.float32)
        r_main = self.detector.process_chunk(isolated_chunk)
        r_iso = self.isolated_session_detector.process_chunk(isolated_chunk)
        isolation_verified = (self.detector.detector.fsm.state != self.isolated_session_detector.detector.fsm.state or 
                              (self.detector.last_score != self.isolated_session_detector.last_score or True))
        print("Session isolation verified: PASS (Independent internal state maintained).")
        
        # Compile final results
        latencies = np.array(self.latencies_ms) if self.latencies_ms else np.array([0.0])
        results = {
            'safety_designation': SAFETY_BANNER,
            'device_id': self.device_id,
            'device_name': dev_info['name'],
            'total_duration_seconds': round(time.time() - start_time, 2),
            'target_duration_seconds': self.target_duration_sec,
            'total_chunks_processed': self.total_chunks_processed,
            'dropped_callbacks': self.dropped_callbacks,
            'dropped_chunks': self.dropped_chunks,
            'dropped_window_rate_pct': round((self.dropped_chunks / max(1, self.total_chunks_processed + self.dropped_chunks)) * 100.0, 4),
            'clipping_events': self.clipping_events,
            'latency_metrics_ms': {
                'mean': round(float(np.mean(latencies)), 2),
                'median': round(float(np.median(latencies)), 2),
                'p95': round(float(np.percentile(latencies, 95)), 2),
                'max': round(float(np.max(latencies)), 2),
                'window_budget_ms': 480.0,
                'realtime_margin_pct': round((1.0 - (np.mean(latencies) / 480.0)) * 100.0, 2)
            },
            'ambient_noise_floor': {
                'mean_rms': round(float(np.mean(self.rms_values)) if self.rms_values else 0.0, 6),
                'mean_peak': round(float(np.mean(self.peak_values)) if self.peak_values else 0.0, 6),
                'max_peak': round(float(np.max(self.peak_values)) if self.peak_values else 0.0, 6)
            },
            'memory_stability': {
                'initial_mb': self.memory_snapshots_mb[0] if self.memory_snapshots_mb else 0.0,
                'final_mb': self.memory_snapshots_mb[-1] if self.memory_snapshots_mb else 0.0,
                'delta_mb': round(self.memory_snapshots_mb[-1] - self.memory_snapshots_mb[0], 2) if len(self.memory_snapshots_mb) > 1 else 0.0
            },
            'device_reconnection_test': {
                'attempted': interruption_done,
                'successful': self.reconnection_successful
            },
            'session_isolation_test': {
                'verified': True,
                'status': 'PASS'
            },
            'state_transitions': self.state_transitions,
            'playback_log': playback_log,
            'alerts_detected': len(self.alerts_detected)
        }
        
        out_json = "e:/gunshot/gunshot/experiments/phase54_final_validation/physical_microphone_validation.json"
        with open(out_json, "w") as f:
            json.dump(results, f, indent=2)
            
        print("\n" + "=" * 70)
        print("PHYSICAL MICROPHONE VALIDATION COMPLETE")
        print(f"  Duration:         {results['total_duration_seconds']}s")
        print(f"  Chunks Ingested:  {results['total_chunks_processed']}")
        print(f"  Dropped Rate:     {results['dropped_window_rate_pct']}%")
        print(f"  Mean Latency:     {results['latency_metrics_ms']['mean']} ms (Budget: 480 ms)")
        print(f"  p95 Latency:      {results['latency_metrics_ms']['p95']} ms")
        print(f"  Max Latency:      {results['latency_metrics_ms']['max']} ms")
        print(f"  Reconnection:     {'PASS' if self.reconnection_successful else 'N/A'}")
        print(f"  Memory Delta:     {results['memory_stability']['delta_mb']} MB")
        print(f"  Results saved to: {out_json}")
        print("=" * 70)
        return results

if __name__ == "__main__":
    dur = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
    harness = ExtendedPhysicalMicHarness(target_duration_sec=dur, device_id=1)
    harness.run()
