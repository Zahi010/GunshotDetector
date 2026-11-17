"""
Phase 9 Deployment Packaging and Integrity Verification Script.
"""

import os
import zipfile
import hashlib
from pathlib import Path


def main():
    root = Path("e:/gunshot/gunshot").resolve()
    zip_path = Path("e:/gunshot/gunshot_detection_phase9.zip").resolve()

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
    size_mb = zip_path.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 60)
    print("PHASE 9 DEPLOYMENT ARCHIVE SUMMARY")
    print("=" * 60)
    print(f"Path:       {zip_path}")
    print(f"Size:       {size_mb:.2f} MB")
    print(f"Files:      {file_count}")
    print(f"SHA-256:    {sha}")
    print("Integrity:  VERIFIED (testzip passed)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
