#!/usr/bin/env python3
"""
tests/test_phase41_audit.py

Phase 41 Independent Evidence Reconciliation and Statistical Robustness Audit
Automated Forensic Regression & Verification Suite
"""

import hashlib
import json
import pathlib
import zipfile
import pytest
import numpy as np
import pandas as pd
from scipy import stats

REPO_ROOT = pathlib.Path("E:/gunshot/gunshot")
PROJECT_ROOT = pathlib.Path("E:/gunshot")
P41_DIR = REPO_ROOT / "experiments" / "phase41"


class TestPhase41SafetyAndProtocol:
    """Verifies mandatory safety designations and protocol integrity."""

    def test_mandatory_safety_designation_in_reports(self):
        reports = [
            P41_DIR / "phase41_inventory_reconciliation.md",
            P41_DIR / "phase41_hash_provenance_report.md",
            P41_DIR / "phase41_similarity_methodology.md",
            P41_DIR / "phase41_fireworks_cluster_analysis.md",
            P41_DIR / "phase41_cluster_robust_analysis.md",
            P41_DIR / "phase41_audit_scope_reconciliation.md"
        ]
        mandatory_phrase = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY."
        for r_path in reports:
            assert r_path.exists(), f"Missing report: {r_path.name}"
            content = r_path.read_text(encoding="utf-8")
            assert mandatory_phrase in content, f"Safety notice missing in {r_path.name}"


class TestDetectorModelFreezeHashes:
    """Verifies exact physical hashes and byte sizes of all frozen detector files."""

    FROZEN_HASHES = {
        "model_phase14.py": ("a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065", 23340),
        "model_phase17.py": ("e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819", 29067),
        "experiments/phase31/model_phase17_state_reset_candidate.py": ("c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5", 29718),
        "experiments/phase36/model_phase36.py": ("2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a", 13891),
        "experiments/phase36/event_state_machine.py": ("a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31", 24905),
        "experiments/phase36/acoustic_features.py": ("5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51", 9812),
        "feature_extractor.py": ("1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f", 6218),
        "config.py": ("55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858", 2619),
        "experiments/phase40/phase40_evaluation_protocol.md": ("05aa77bd3fb30f7c472fa1b2db2862283bf1bf5fd25111142ae95993245b1fc7", 5575)
    }

    @pytest.mark.parametrize("rel_path,expected", FROZEN_HASHES.items())
    def test_model_hash_and_size(self, rel_path, expected):
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Missing file: {rel_path}"
        data = full_path.read_bytes()
        actual_sha = hashlib.sha256(data).hexdigest()
        actual_size = len(data)
        assert actual_sha == expected[0], f"Hash mismatch for {rel_path}: {actual_sha} vs {expected[0]}"
        assert actual_size == expected[1], f"Size mismatch for {rel_path}: {actual_size} vs {expected[1]}"


class TestWorkstreamAInventoryReconciliation:
    """Verifies canonical 368-entry inventory and duplicate waveform reconciliation."""

    def test_inventory_record_count_and_partitions(self):
        inv_path = P41_DIR / "phase41_recording_inventory.csv"
        assert inv_path.exists()
        df = pd.read_csv(inv_path)
        assert len(df) == 368, f"Expected 368 entries, got {len(df)}"

        pos_count = len(df[df["evaluation_partition"] == "POSITIVE_GUNSHOT"])
        dist_count = len(df[df["evaluation_partition"] == "DISTRACTOR_NOISE"])
        cont_count = len(df[df["evaluation_partition"] == "CONTINUOUS_AMBIENT"])
        fw_count = len(df[df["is_fireworks_eval"] == True])
        other_dist_count = len(df[(df["evaluation_partition"] == "DISTRACTOR_NOISE") & (~df["is_fireworks_eval"])])

        assert pos_count == 120
        assert dist_count == 220
        assert fw_count == 100
        assert other_dist_count == 120
        assert cont_count == 28

    def test_exact_duplicate_waveform_pair(self):
        inv_path = P41_DIR / "phase41_recording_inventory.csv"
        df = pd.read_csv(inv_path)
        
        # Exactly 367 unique physical waveforms
        assert df["sha256"].nunique() == 367
        
        # Exactly 1 pair of duplicated SHA-256
        dup_rows = df[df.duplicated(subset=["sha256"], keep=False)]
        assert len(dup_rows) == 2
        
        filenames = dup_rows["filename"].tolist()
        assert any("51749" in fn for fn in filenames)
        assert any("115295" in fn for fn in filenames)
        assert dup_rows["sha256"].iloc[0] == "6b272b5b52c6766f76c4ee879f1dabc191f3ca698b00de3cc5279033c9051d5f"


class TestWorkstreamBHashReconciliation:
    """Verifies cryptographic hash reconstruction across historical phases."""

    def test_hash_reconciliation_csv_contents(self):
        csv_path = P41_DIR / "phase41_hash_reconciliation.csv"
        assert csv_path.exists()
        df = pd.read_csv(csv_path)
        assert len(df) == 17
        assert (df["manifest_match"] == True).all()

        p36_row = df[df["item_name"] == "model_phase36.py"].iloc[0]
        assert p36_row["physical_sha256"] == "2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a"
        assert p36_row["phase37_report_printed_sha256"].startswith("2774ab4cae0fca6d")
        assert p36_row["phase37_report_printed_sha256"].endswith("2241")

    def test_historical_release_archives_crc(self):
        archives = [
            ("gunshot_detection_phase34.zip", 4552249, "1c961893c89285a48c5bf2a61a09b3dd71860febc12ac2fb56f0e43fd2a41208", 43),
            ("gunshot_detection_phase35.zip", 4561967, "142402f6d48c8167124807d0a5389ed322dd9e57e676f3dd5c3971ab8635f707", 41),
            ("gunshot_detection_phase36.zip", 137665, "44240bd32145fe0972cee5e7b088fe9524b2504b0b3d30a602703ba837174385", 24),
            ("gunshot_detection_phase37_audit.zip", 28814, "4d107c2c92de8d3580474cfb1a0f56566322f2525c5f7f04c472fa8398da7eb9", 14),
            ("gunshot_detection_phase38_prospective_evaluation.zip", 100636, "e75834294ddb1bfea4b321f179b984de06daf3e40df24e73e08f68bda2829765", 22),
            ("gunshot_detection_phase39_evaluation.zip", 122871, "42436b45c2daf86f1df8eac09bb7754d2c228de3d414be954858fb92e6653515", 30),
            ("gunshot_detection_phase40_audit.zip", 90838, "c853ad85946e4ef7940402dc9363e540a7fe5ca33a90116d518a5a79638e491a", 31),
        ]
        for arc_name, exp_size, exp_sha, exp_files in archives:
            arc_path = PROJECT_ROOT / arc_name
            assert arc_path.exists(), f"Missing archive {arc_name}"
            data = arc_path.read_bytes()
            assert len(data) == exp_size, f"Size mismatch for {arc_name}"
            assert hashlib.sha256(data).hexdigest() == exp_sha, f"SHA mismatch for {arc_name}"
            zf = zipfile.ZipFile(arc_path)
            assert len(zf.namelist()) == exp_files, f"Internal file count mismatch for {arc_name}"
            assert zf.testzip() is None, f"CRC failure in {arc_name}"


class TestWorkstreamCSourceAndSimilarity:
    """Verifies source lineage and pairwise similarity matrix."""

    def test_source_lineage_metrics(self):
        lineage_path = P41_DIR / "phase41_source_lineage.csv"
        assert lineage_path.exists()
        df = pd.read_csv(lineage_path)
        assert len(df) == 6

        # Check Total row
        tot = df[df["partition_name"] == "TOTAL_EVALUATION_CORPUS"].iloc[0]
        assert tot["total_recordings"] == 368
        assert tot["unique_waveforms"] == 367
        assert tot["unique_uploaders_or_recordists"] == 310
        assert tot["total_duration_hours"] == 4.9406

        # Check continuous ambient
        cont = df[df["partition_name"] == "PARTITION_CONTINUOUS_AMBIENT"].iloc[0]
        assert cont["total_recordings"] == 28
        assert cont["unique_uploaders_or_recordists"] == 19
        assert "duseigne" in cont["top_uploader_identity"].lower()
        assert cont["top_uploader_clip_count"] == 8

    def test_similarity_results(self):
        sim_path = P41_DIR / "phase41_similarity_results.csv"
        assert sim_path.exists()
        df = pd.read_csv(sim_path)
        assert len(df) == 1234

        # Verify duplicate pair has sim 1.000000
        dups = df[df["similarity_classification"] == "EXACT_DUPLICATE"]
        assert len(dups) == 1
        d_row = dups.iloc[0]
        assert d_row["embedding_cosine_similarity"] == 1.000000
        assert d_row["exact_waveform_sha_collision"] == True


class TestWorkstreamDFireworksMechanismAudit:
    """Verifies fireworks paired evaluation, McNemar significance, and crest gate forensics."""

    def test_fireworks_contingency_table(self):
        recon_path = P41_DIR / "phase41_fireworks_reconstruction.csv"
        assert recon_path.exists()
        df = pd.read_csv(recon_path)
        assert len(df) == 100

        counts = df["pair_status"].value_counts().to_dict()
        assert counts.get("BOTH_TRIGGERED", 0) == 47
        assert counts.get("PHASE36_ONLY", 0) == 10
        assert counts.get("PHASE14_ONLY", 0) == 0
        assert counts.get("NEITHER_TRIGGERED", 0) == 43

    def test_mcnemar_and_binomial_significance(self):
        # McNemar continuity corrected: ((|10 - 0| - 1)^2) / 10 = 81 / 10 = 8.1000
        chi2_corr = 8.1000
        p_corr = float(stats.chi2.sf(chi2_corr, df=1))
        assert abs(p_corr - 0.004427) < 1e-5

        # Exact paired binomial test: 2 * (0.5)^10 = 2 / 1024 = 0.001953
        exact_res = stats.binomtest(10, n=10, p=0.5, alternative="two-sided")
        assert abs(exact_res.pvalue - 0.001953) < 1e-5

    def test_discordant_crest_factor_mechanism(self):
        mech_path = P41_DIR / "phase41_crest_factor_mechanism_audit.csv"
        assert mech_path.exists()
        df = pd.read_csv(mech_path)
        assert len(df) == 100

        # Filter to discordant clips (Phase 36 decision True, Phase 14 False)
        disc = df[(df["p36_decision"] == True) & (df["p14_decision"] == False)]
        assert len(disc) == 10

        # All 10 discordant clips have crest factor >= 12.0 dB
        assert (disc["crest_factor_db"] >= 12.0).all()
        assert (disc["crest_factor_ge_12db"] == True).all()

        # All 10 discordant clips come from 10 distinct uploaders
        assert disc["uploader_or_creator"].nunique() == 10


class TestWorkstreamEContinuousRobustness:
    """Verifies continuous background benchmark, Wilcoxon tests, and cluster-robust variance."""

    def test_continuous_six_condition_metrics(self):
        recon_path = P41_DIR / "phase41_continuous_reconstruction.csv"
        assert recon_path.exists()
        df = pd.read_csv(recon_path)
        assert len(df) == 168

        # Verify alert counts per condition
        cond_alerts = df.groupby("condition_id")["false_alerts_count"].sum().to_dict()
        assert cond_alerts["COND1"] == 31
        assert cond_alerts["COND2"] == 104
        assert cond_alerts["COND3"] == 31
        assert cond_alerts["COND4"] == 26
        assert cond_alerts["COND5"] == 26
        assert cond_alerts["COND6"] == 26

    def test_continuous_far_statistical_non_significance(self):
        json_path = P41_DIR / "phase41_statistical_reproduction.json"
        assert json_path.exists()
        with open(json_path, "r", encoding="utf-8") as f:
            stats_data = json.load(f)

        tests = stats_data["continuous_statistical_tests"]
        stream_test = tests["cond1_vs_cond6_stream_level_wilcoxon"]
        rec_test = tests["cond1_vs_cond6_recordist_level_wilcoxon"]
        clustered_test = tests["cond1_vs_cond6_cluster_robust_rate_difference"]

        # Assert p-values > 0.05
        assert stream_test["p_value"] == pytest.approx(0.10247, abs=1e-4)
        assert stream_test["is_statistically_significant_alpha_0_05"] == False

        assert rec_test["p_value"] == pytest.approx(0.10247, abs=1e-4)
        assert rec_test["is_statistically_significant_alpha_0_05"] == False

        assert clustered_test["p_value"] == pytest.approx(0.1799, abs=1e-3)
        assert clustered_test["is_statistically_significant_alpha_0_05"] == False

        # Phase 17 defect is significant
        p17_test = tests["cond2_vs_cond1_phase17_defect_wilcoxon"]
        assert p17_test["is_statistically_significant_alpha_0_05"] == True
        assert p17_test["phase17_excess_alerts"] == 73


class TestWorkstreamFClaimEvidenceMatrix:
    """Verifies claim-to-evidence matrix and audit scope reconciliation."""

    def test_claim_matrix_completeness(self):
        mat_path = P41_DIR / "phase41_claim_evidence_matrix.csv"
        assert mat_path.exists()
        df = pd.read_csv(mat_path)
        assert len(df) == 11
        assert set(df["claim_id"]) == {f"CLM-{i:02d}" for i in range(1, 12)}

        # Verify CLM-10 (statistical significance claim refuted)
        clm10 = df[df["claim_id"] == "CLM-10"].iloc[0]
        assert clm10["evidence_label"] == "NOT_ESTABLISHED"
        assert "CLAIM_NOT_SUPPORTED_BY_EVIDENCE" in clm10["audit_classification"]


class TestWorkstreamHPackagingAndManifest:
    """Verifies Phase 41 output release archive and machine manifest."""

    def test_output_manifest_and_archive(self):
        manifest_path = P41_DIR / "phase41_output_hash_manifest.json"
        assert manifest_path.exists()
        with open(manifest_path, "r", encoding="utf-8") as f:
            m = json.load(f)

        arc_info = m["release_archive"]
        assert arc_info["filename"] == "gunshot_detection_phase41_audit.zip"
        assert arc_info["crc_status"] == "PASS"
        assert arc_info["internal_file_count"] == 29

        zip_p = PROJECT_ROOT / "gunshot_detection_phase41_audit.zip"
        assert zip_p.exists()
        assert len(zip_p.read_bytes()) == arc_info["byte_size"]
        assert hashlib.sha256(zip_p.read_bytes()).hexdigest() == arc_info["sha256"]

        zf = zipfile.ZipFile(zip_p)
        assert zf.testzip() is None
        assert len(zf.namelist()) == 29

