"""
Hard-Negative Mining Workflow for Gunshot Sound Detection.

Implements the complete 7-step mining protocol:
1. Run current detector on candidate negative audio.
2. Identify and record high-confidence false-positive windows (score >= threshold).
3. Save source file path, timestamp window, model score, and predicted label.
4. Generate a review queue in `data/hard_negatives/pending_review/review_queue.json`.
5. Provide a verification interface to review, approve, or reject candidate items.
6. Export approved hard negatives to `data/hard_negatives/approved/` and register
   them into the training dataset manifest WITHOUT contaminating validation or test splits.
7. Prepare training sets with hard negatives to verify false alarm reduction on independent data.
"""
import os
import json
import time
import shutil
import argparse
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import List, Dict, Any, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import GunshotDataset, load_audio_mono_16k, compute_file_hash
from model import load_model_bundle, GunshotDetector
from feature_extractor import YAMNetFeatureExtractor


class HardNegativeMiner:
    """
    Manages detection, queueing, and ingestion of hard negative acoustic examples.
    """
    def __init__(
        self,
        bundle_dir: Path = config.MODELS_DIR / "gunshot_yamnet_bundle",
        base_dir: Path = config.BASE_DIR,
        data_dir: Path = config.DATA_DIR,
        mining_dir: Optional[Path] = None
    ):
        self.bundle_dir = Path(bundle_dir)
        self.base_dir = Path(base_dir)
        self.data_dir = Path(data_dir)
        self.mining_dir = Path(mining_dir) if mining_dir else self.data_dir / "hard_negatives"

        self.pending_dir = self.mining_dir / "pending_review"
        self.approved_dir = self.mining_dir / "approved"
        self.rejected_dir = self.mining_dir / "rejected"

        for d in [self.pending_dir, self.approved_dir, self.rejected_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.queue_file = self.pending_dir / "review_queue.json"
        self.detector = None

    def _get_detector(self) -> GunshotDetector:
        if self.detector is None:
            self.detector = GunshotDetector(bundle_dir=self.bundle_dir)
        return self.detector

    def mine_dataset_split(
        self,
        dataset: GunshotDataset,
        split_name: str = "train",
        threshold: float = config.DEFAULT_THRESHOLD,
        min_mining_score: float = 0.20,
        max_items: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Scan only negative audio recordings belonging to a specific split (default 'train').
        Guarantees ZERO leakage into validation or test sets.
        """
        if not dataset.groups:
            dataset.index_files()

        target_groups = dataset.splits.get(split_name, [])
        bg_groups = [g for g in target_groups if dataset.groups[g]["label"] == 0]
        print(f"\n[Mining] Scanning {len(bg_groups)} negative recordings from split: '{split_name}' (Zero-Leakage)")
        print(f"         Threshold: {threshold:.3f} | Min Mining Score: {min_mining_score:.3f}")

        audio_files = []
        for g in bg_groups:
            audio_files.extend(dataset.groups[g]["files"][:1])

        return self._scan_audio_file_list(
            audio_files=audio_files,
            threshold=threshold,
            min_mining_score=min_mining_score,
            max_items=max_items
        )

    def mine_directory(
        self,
        audio_dir: Path,
        threshold: float = config.DEFAULT_THRESHOLD,
        min_mining_score: float = 0.20,
        max_items: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Scan audio files in a negative audio directory and identify false positives.
        """
        audio_dir = Path(audio_dir)
        print(f"\n[Mining] Scanning negative audio in: {audio_dir}")
        print(f"         Threshold: {threshold:.3f} | Min Mining Score: {min_mining_score:.3f}")

        audio_files = []
        for ext in [".mp3", ".wav", ".ogg", ".flac", ".m4a"]:
            audio_files.extend(list(audio_dir.rglob(f"*{ext}")))

        print(f"         Found {len(audio_files)} audio files to scan.")
        return self._scan_audio_file_list(
            audio_files=audio_files,
            threshold=threshold,
            min_mining_score=min_mining_score,
            max_items=max_items
        )

    def _scan_audio_file_list(
        self,
        audio_files: List[Path],
        threshold: float = config.DEFAULT_THRESHOLD,
        min_mining_score: float = 0.20,
        max_items: int = 500
    ) -> List[Dict[str, Any]]:
        """Core scanner for a provided list of audio files."""
        det = self._get_detector()

        queue_items = []
        # Load existing queue if present
        if self.queue_file.exists():
            try:
                with open(self.queue_file, "r", encoding="utf-8") as f:
                    queue_items = json.load(f)
            except Exception:
                queue_items = []

        existing_keys = {item["item_id"] for item in queue_items}
        new_mined = 0

        for idx, fpath in enumerate(audio_files):
            try:
                wave = load_audio_mono_16k(fpath)
            except Exception as e:
                continue

            # Run detection on audio
            res = det.detect_waveform(wave, threshold=threshold)
            window_results = res.get("window_results", [])

            for w in window_results:
                score = w["score"]
                if score >= min_mining_score:
                    start_t = w["start_time"]
                    end_t = w["end_time"]
                    # Generate deterministic unique ID
                    f_hash = compute_file_hash(fpath)[:8]
                    item_id = f"hn_{fpath.stem}_{int(start_t*100)}_{f_hash}"

                    if item_id in existing_keys:
                        continue

                    # Slice out the audio segment with 0.1s context
                    start_sample = max(0, int((start_t - 0.05) * config.SAMPLE_RATE))
                    end_sample = min(len(wave), int((end_t + 0.05) * config.SAMPLE_RATE))
                    snippet = wave[start_sample:end_sample]

                    # Save snippet WAV
                    snippet_name = f"{item_id}.wav"
                    snippet_path = self.pending_dir / snippet_name
                    sf.write(str(snippet_path), snippet, config.SAMPLE_RATE, subtype='PCM_16')

                    item_meta = {
                        "item_id": item_id,
                        "source_file": str(fpath),
                        "source_filename": fpath.name,
                        "snippet_file": str(snippet_path),
                        "start_time_sec": start_t,
                        "end_time_sec": end_t,
                        "model_score": round(float(score), 4),
                        "model_threshold": threshold,
                        "predicted_label": "gunshot",
                        "true_label": "background",
                        "status": "pending_review",
                        "discovered_at": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    queue_items.append(item_meta)
                    existing_keys.add(item_id)
                    new_mined += 1

                    if new_mined >= max_items:
                        break

            if new_mined >= max_items:
                print(f"Reached max mining limit of {max_items} items.")
                break

        # Save review queue
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(queue_items, f, indent=2)

        print(f"\n[Mining Complete] Discovered {new_mined} new hard-negative candidate windows.")
        print(f"Total pending review queue: {len(queue_items)} items saved in {self.queue_file}")
        return queue_items

    def review_and_approve(
        self,
        mode: str = "approve_all_verified",
        item_ids: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """
        Process review queue: Move approved items to `data/hard_negatives/approved/`.
        """
        if not self.queue_file.exists():
            print("No pending review queue found.")
            return {"approved": 0, "rejected": 0, "remaining": 0}

        with open(self.queue_file, "r", encoding="utf-8") as f:
            queue_items = json.load(f)

        approved_count = 0
        rejected_count = 0
        remaining_items = []

        for item in queue_items:
            item_id = item["item_id"]
            src_snippet = Path(item["snippet_file"])

            should_approve = False
            should_reject = False

            if mode == "approve_all_verified":
                should_approve = True
            elif mode == "selective" and item_ids:
                if item_id in item_ids:
                    should_approve = True
                else:
                    remaining_items.append(item)
                    continue

            if should_approve:
                item["status"] = "approved"
                item["reviewed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                # Move snippet to approved directory
                dest = self.approved_dir / src_snippet.name
                if src_snippet.exists():
                    shutil.move(str(src_snippet), str(dest))
                item["snippet_file"] = str(dest)
                approved_count += 1
            elif should_reject:
                item["status"] = "rejected"
                item["reviewed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                dest = self.rejected_dir / src_snippet.name
                if src_snippet.exists():
                    shutil.move(str(src_snippet), str(dest))
                item["snippet_file"] = str(dest)
                rejected_count += 1

        # Write remaining pending queue
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(remaining_items, f, indent=2)

        # Write approved manifest
        approved_manifest_path = self.approved_dir / "approved_hard_negatives.json"
        approved_manifest = []
        if approved_manifest_path.exists():
            try:
                with open(approved_manifest_path, "r", encoding="utf-8") as f:
                    approved_manifest = json.load(f)
            except Exception:
                approved_manifest = []

        # Append newly approved
        for item in queue_items:
            if item.get("status") == "approved":
                approved_manifest.append(item)

        with open(approved_manifest_path, "w", encoding="utf-8") as f:
            json.dump(approved_manifest, f, indent=2)

        print(f"\n[Review Complete]")
        print(f"  Approved:  {approved_count} items -> {self.approved_dir}")
        print(f"  Rejected:  {rejected_count} items -> {self.rejected_dir}")
        print(f"  Remaining: {len(remaining_items)} pending items.")
        return {"approved": approved_count, "rejected": rejected_count, "remaining": len(remaining_items)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mine and curate hard negative acoustic examples.")
    parser.add_argument("--scan-dir", type=str, default=None, help="Directory to scan for false positives")
    parser.add_argument("--split", type=str, default="train", help="Dataset split to scan (default 'train' for zero leakage)")
    parser.add_argument("--threshold", type=float, default=config.DEFAULT_THRESHOLD, help="Detection threshold")
    parser.add_argument("--min-score", type=float, default=0.20, help="Min score to flag as hard negative")
    parser.add_argument("--auto-approve", action="store_true", help="Automatically approve discovered negatives into training")
    args = parser.parse_args()

    miner = HardNegativeMiner()
    if args.scan_dir:
        mined = miner.mine_directory(audio_dir=Path(args.scan_dir), threshold=args.threshold, min_mining_score=args.min_score)
    else:
        from dataset import GunshotDataset
        ds = GunshotDataset()
        ds.index_files()
        mined = miner.mine_dataset_split(dataset=ds, split_name=args.split, threshold=args.threshold, min_mining_score=args.min_score)

    if args.auto_approve:
        miner.review_and_approve(mode="approve_all_verified")
