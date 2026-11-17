"""
Phase 10 Deployment Packaging and Integrity Verification Script.
Packages the verified Phase 10 workspace into gunshot_detection_phase10.zip,
verifies zip readability using testzip(), computes its SHA-256 checksum,
and updates reports/phase10_artifact_manifest.json on disk.
"""

import os
import zipfile
import hashlib
import json
from pathlib import Path


def main():
    root = Path("e:/gunshot/gunshot").resolve()
    zip_path = Path("e:/gunshot/gunshot_detection_phase10.zip").resolve()

    print(f"Packaging {root} into {zip_path}...")
    file_count = 0

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirnames, filenames in os.walk(root):
            # Exclude cache and git directories
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git", ".pytest_cache")]
            for f in filenames:
                if f.endswith(".pyc") or f.endswith(".tmp"):
                    continue
                full_p = Path(dirpath) / f
                rel_p = full_p.relative_to(root)
                z.write(full_p, rel_p)
                file_count += 1

    print(f"Successfully packaged {file_count} files into {zip_path}.")

    # Verify integrity
    print("Verifying archive integrity with testzip()...")
    with zipfile.ZipFile(zip_path, "r") as z:
        err = z.testzip()
        if err is not None:
            raise RuntimeError(f"Corrupted file found in archive: {err}")
        print("Archive testzip() verification: PASSED (None - zero corruption).")

    # Compute SHA-256
    print("Computing SHA-256 checksum...")
    hasher = hashlib.sha256()
    with open(zip_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    sha = hasher.hexdigest()
    size_bytes = zip_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    print("\n" + "=" * 60)
    print("PHASE 10 DEPLOYMENT ARCHIVE SUMMARY")
    print("=" * 60)
    print(f"Path:       {zip_path}")
    print(f"Size:       {size_mb:.2f} MB ({size_bytes} bytes)")
    print(f"Files:      {file_count}")
    print(f"SHA-256:    {sha}")
    print("Integrity:  VERIFIED (testzip passed)")
    print("=" * 60 + "\n")

    # Update reports/phase10_artifact_manifest.json on disk
    manifest_p = root / "reports" / "phase10_artifact_manifest.json"
    if manifest_p.exists():
        with open(manifest_p, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        manifest_data.setdefault("deployment_archives", {})["phase10_zip"] = {
            "path": str(zip_path),
            "size_bytes": size_bytes,
            "sha256": sha,
            "file_count": file_count,
            "integrity_testzip": "PASSED"
        }
        with open(manifest_p, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)
        print(f"Updated {manifest_p} with phase10_zip details.")


if __name__ == "__main__":
    main()
