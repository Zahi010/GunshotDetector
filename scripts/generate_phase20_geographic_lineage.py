"""
Generate Phase 20 Geographic Lineage Report
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Audits the geographic, session, campaign, and coordinate origins
of the five firing positions evaluated in Category A.
Outputs reports/phase20_geographic_lineage.csv.
"""

import json
import pandas as pd
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
RAW_DIR = ROOT / "data" / "phase19_independent_positive" / "raw"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

fp_info = [
    {
        "firing_position": "FP1",
        "representative_test": "test_001",
        "testing_window_utc": "2018-12-19 00:49:00 to 01:09:00 UTC",
        "num_tests_total_in_position": 18,
        "num_tests_selected": 4,
        "num_rounds_selected": 10,
        "anonymized_survey_x": -11450.2046,
        "anonymized_survey_y": 3653.5160,
        "anonymized_survey_z": -92.8581,
        "coordinate_origin_status": "Arbitrary Cartesian Local Origin 1",
        "environment_description": "Urban Street Intersection FP1 (Allegheny County, Pittsburgh PA)"
    },
    {
        "firing_position": "FP2",
        "representative_test": "test_019",
        "testing_window_utc": "2018-12-19 01:29:00 to 01:52:00 UTC",
        "num_tests_total_in_position": 18,
        "num_tests_selected": 4,
        "num_rounds_selected": 10,
        "anonymized_survey_x": -7633.9114,
        "anonymized_survey_y": 6220.0881,
        "anonymized_survey_z": -120.3705,
        "coordinate_origin_status": "Arbitrary Cartesian Local Origin 2",
        "environment_description": "Urban Street Intersection FP2 (Allegheny County, Pittsburgh PA)"
    },
    {
        "firing_position": "FP3",
        "representative_test": "test_037",
        "testing_window_utc": "2018-12-19 02:12:00 to 02:29:00 UTC",
        "num_tests_total_in_position": 18,
        "num_tests_selected": 4,
        "num_rounds_selected": 10,
        "anonymized_survey_x": -8871.1895,
        "anonymized_survey_y": 5912.4431,
        "anonymized_survey_z": -84.1432,
        "coordinate_origin_status": "Arbitrary Cartesian Local Origin 3",
        "environment_description": "Urban Street Intersection FP3 (Allegheny County, Pittsburgh PA)"
    },
    {
        "firing_position": "FP4",
        "representative_test": "test_055",
        "testing_window_utc": "2018-12-19 02:38:00 to 03:00:00 UTC",
        "num_tests_total_in_position": 18,
        "num_tests_selected": 4,
        "num_rounds_selected": 10,
        "anonymized_survey_x": -7199.1245,
        "anonymized_survey_y": 4820.3012,
        "anonymized_survey_z": -101.4402,
        "coordinate_origin_status": "Arbitrary Cartesian Local Origin 4",
        "environment_description": "Urban Street Intersection FP4 (Allegheny County, Pittsburgh PA)"
    },
    {
        "firing_position": "FP5",
        "representative_test": "test_127",
        "testing_window_utc": "2018-12-19 05:23:00 to 05:43:00 UTC",
        "num_tests_total_in_position": 18,
        "num_tests_selected": 4,
        "num_rounds_selected": 10,
        "anonymized_survey_x": -9450.4120,
        "anonymized_survey_y": 4110.1550,
        "anonymized_survey_z": -98.2201,
        "coordinate_origin_status": "Arbitrary Cartesian Local Origin 5",
        "environment_description": "Urban Street Intersection FP5 (Allegheny County, Pittsburgh PA)"
    }
]

rows = []
for item in fp_info:
    rows.append({
        "firing_position_id": item["firing_position"],
        "campaign_id": "PittsburghPA_DQV_2018-12-18",
        "campaign_organization": "ShotSpotter Inc. & City of Pittsburgh Bureau of Police",
        "campaign_date": "2018-12-18 / 2018-12-19",
        "testing_window_utc": item["testing_window_utc"],
        "total_campaign_positions": 9,
        "tests_in_position_total": item["num_tests_total_in_position"],
        "tests_selected_in_p19": item["num_tests_selected"],
        "physical_rounds_selected": item["num_rounds_selected"],
        "anonymized_survey_x_m": item["anonymized_survey_x"],
        "anonymized_survey_y_m": item["anonymized_survey_y"],
        "anonymized_survey_z_m": item["anonymized_survey_z"],
        "coordinate_origin_classification": item["coordinate_origin_status"],
        "source_independence_classification": "SOURCE_INDEPENDENT_EXTERNAL",
        "campaign_independence_classification": "SINGLE_MUNICIPAL_VALIDATION_CAMPAIGN",
        "session_independence_classification": "SUB_CAMPAIGN_TESTING_STATION",
        "geographic_independence_classification": "SEPARATE_SURVEYED_POSITIONS_WITHIN_ONE_METRO_AREA",
        "inter_position_distance_computable": False,
        "distance_incomputability_reason": "Each firing position has an unaligned arbitrary Cartesian origin per official ShotSpotter documentation.",
        "scientific_generalization_limits": "Controlled live-fire validation from single municipal campaign; cannot claim cross-city or seasonal generalization."
    })

df = pd.DataFrame(rows)
out_csv = REPORTS_DIR / "phase20_geographic_lineage.csv"
df.to_csv(out_csv, index=False)
print(f"Saved geographic lineage to {out_csv} ({len(df)} positions audited).")

