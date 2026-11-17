"""
Regression Test: Verify zero leakage across Train, Validation, and Test splits.
"""
import sys
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from dataset import GunshotDataset, compute_file_hash
from inventory import get_base_stem


class TestSplitIntegrity(unittest.TestCase):
    def setUp(self):
        self.dataset = GunshotDataset(data_dir=config.DATA_DIR)
        self.dataset.index_files()

    def test_disjoint_groups(self):
        """Verify train, val, and test group sets are completely mutually exclusive."""
        train_groups = set(self.dataset.splits["train"])
        val_groups = set(self.dataset.splits["val"])
        test_groups = set(self.dataset.splits["test"])

        self.assertEqual(len(train_groups.intersection(val_groups)), 0, "Leakage detected between Train and Val!")
        self.assertEqual(len(train_groups.intersection(test_groups)), 0, "Leakage detected between Train and Test!")
        self.assertEqual(len(val_groups.intersection(test_groups)), 0, "Leakage detected between Val and Test!")

    def test_disjoint_hashes(self):
        """Verify identical file hashes never appear across multiple splits."""
        split_hashes = {"train": set(), "val": set(), "test": set()}

        for sp in ["train", "val", "test"]:
            for g_key in self.dataset.splits[sp]:
                g_info = self.dataset.groups[g_key]
                for fpath in g_info["files"]:
                    if fpath.exists():
                        h = compute_file_hash(fpath)
                        split_hashes[sp].add(h)

        self.assertEqual(len(split_hashes["train"].intersection(split_hashes["val"])), 0, "MD5 hash collision between Train and Val!")
        self.assertEqual(len(split_hashes["train"].intersection(split_hashes["test"])), 0, "MD5 hash collision between Train and Test!")
        self.assertEqual(len(split_hashes["val"].intersection(split_hashes["test"])), 0, "MD5 hash collision between Val and Test!")


if __name__ == "__main__":
    unittest.main()
