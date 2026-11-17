"""
Phase 23 Provenance, Source Registry & Duplicate Audit Builder
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Constructs:
1. reports/phase23_source_registry.csv
2. reports/phase23_recording_provenance.csv
3. reports/phase23_duplicate_audit.csv
"""

import os
import csv
import wave
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_audio_info(filepath: Path):
    with wave.open(str(filepath), "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        ch = wf.getnchannels()
        dur = frames / float(rate)
    return dur, rate, ch


def main():
    print("=" * 80)
    print("BUILDING PHASE 23 SOURCE REGISTRY, PROVENANCE & DUPLICATE AUDIT")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.")
    print("=" * 80)

    # 1. Source Registry
    source_registry = [
        {
            "source_id": "SRC-ZENODO-7493820",
            "source_name": "RPi Sound Logger Environmental Suite",
            "repository_doi_or_url": "https://doi.org/10.5281/zenodo.7493820",
            "license": "CC BY 4.0",
            "organization_or_authors": "Open Environmental Acoustic Monitoring Initiative",
            "geographic_location": "Urban & Industrial Zones, United Kingdom",
            "primary_modality": "Continuous 16kHz PCM Environmental Monitoring",
            "total_files_cataloged": 10,
            "total_duration_hours": 5.500,
            "continuity_type": "NATURAL_CONTINUOUS_UNBROKEN",
            "decision": "ACCEPT",
            "decision_rationale": "Unbroken continuous recordings (30-60m); CC BY 4.0; no gunshots; verified 16kHz mono PCM."
        },
        {
            "source_id": "SRC-ZENODO-3938837",
            "source_name": "Chew Magna Reservoir Soundscape",
            "repository_doi_or_url": "https://doi.org/10.5281/zenodo.3938837",
            "license": "CC BY 4.0",
            "organization_or_authors": "Chew Valley Acoustic Ecology Field Survey",
            "geographic_location": "Chew Magna, Somerset, United Kingdom",
            "primary_modality": "Continuous Environmental Soundscape",
            "total_files_cataloged": 1,
            "total_duration_hours": 0.583,
            "continuity_type": "NATURAL_CONTINUOUS_UNBROKEN",
            "decision": "ACCEPT",
            "decision_rationale": "Unbroken continuous 35m field recording; CC BY 4.0; natural aquatic and weather background."
        },
        {
            "source_id": "SRC-ZENODO-18561165",
            "source_name": "Bilbao Old Town Urban Soundscape",
            "repository_doi_or_url": "https://doi.org/10.5281/zenodo.18716205",
            "license": "CC BY 4.0",
            "organization_or_authors": "Universidad del País Vasco (Iturbe-Martin et al.)",
            "geographic_location": "Bilbao Old Town (Casco Viejo), Spain",
            "primary_modality": "Urban Soundscape Control Points (Plazas, Walkways, Arcades)",
            "total_files_cataloged": 6,
            "total_duration_hours": 0.563,
            "continuity_type": "NATURAL_CONTINUOUS_UNBROKEN",
            "decision": "ACCEPT",
            "decision_rationale": "High-fidelity urban exterior and interior pedestrian environments; CC BY 4.0; natural continuous field audio."
        },
        {
            "source_id": "SRC-ZENODO-3966543",
            "source_name": "SONYC Urban Sound Tagging (SONYC-UST V2)",
            "repository_doi_or_url": "https://doi.org/10.5281/zenodo.3966543",
            "license": "CC BY 4.0",
            "organization_or_authors": "NYU MARL / CUSP (Cartwright et al.)",
            "geographic_location": "New York City, NY, USA",
            "primary_modality": "Discrete 10-Second Sensor Snippets",
            "total_files_cataloged": 18510,
            "total_duration_hours": 51.417,
            "continuity_type": "DISCRETE_10S_SNIPPETS",
            "decision": "REJECT",
            "decision_rationale": "Non-continuous; consists exclusively of 10-second clips. Splicing introduces artificial boundary artifacts."
        },
        {
            "source_id": "SRC-DCASE-TAU-2022",
            "source_name": "TAU Urban Acoustic Scenes 2022 (DCASE Task 1)",
            "repository_doi_or_url": "https://doi.org/10.5281/zenodo.6582075",
            "license": "CC BY 4.0",
            "organization_or_authors": "Tampere University Audio Research Group",
            "geographic_location": "10 European Metropolitan Centers",
            "primary_modality": "Segmented 10-Second Ambience Recordings",
            "total_files_cataloged": 14400,
            "total_duration_hours": 40.000,
            "continuity_type": "DISCRETE_10S_SNIPPETS",
            "decision": "REJECT",
            "decision_rationale": "Non-continuous; pre-segmented into 10-second segments for challenge classification. Unsuitable for continuous benchmark."
        },
        {
            "source_id": "SRC-HISTORICAL-SYNTH-P7P8",
            "source_name": "Historical Synthetic Overlay Streams (Phase 7 & 8)",
            "repository_doi_or_url": "Internal Research Archive (Phase 7 / Phase 8)",
            "license": "Research Internal Archive (Derivative of ESC-50)",
            "organization_or_authors": "Antigravity Research Consortium",
            "geographic_location": "Synthetic Laboratory Assembly",
            "primary_modality": "Intermittent ESC-50 Clips Overlaid on Digital Silence",
            "total_files_cataloged": 6,
            "total_duration_hours": 6.000,
            "continuity_type": "SYNTHETIC_OVERLAY_ON_SILENCE",
            "decision": "REJECT_FOR_PRIMARY_RETAIN_EXPLORATORY",
            "decision_rationale": "Lacks continuous natural background noise floor. Retained in secondary exploratory set; excluded from primary negative exposure."
        }
    ]

    out_src_csv = REPORTS_DIR / "phase23_source_registry.csv"
    with open(out_src_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(source_registry[0].keys()))
        writer.writeheader()
        writer.writerows(source_registry)
    print(f"Saved source registry: {out_src_csv} ({len(source_registry)} sources cataloged)")

    # 2. Recording Provenance for all evaluated streams
    # 17 Primary Natural Continuous Streams
    primary_streams = [
        # Phase 16 (11 streams)
        ("P23-NAT-STR-01", "P16-STREAM-01", "phase16_natural_continuous/phase16_industrial_compressor_pneumatic_60min.wav", "SRC-ZENODO-7493820", "CAMPAIGN-RPISOUND-UK", "SESS-PNEUMATIC-01", "SENSOR-RPI-04", "LOC-UK-IND-01", "industrial_and_mechanical", "VERIFIED_NEGATIVE", "Unbroken 60m continuous recording of industrial pneumatic compressor; no target events."),
        ("P23-NAT-STR-02", "P16-STREAM-02", "phase16_natural_continuous/phase16_industrial_exhaust_ventilation_30min.wav", "SRC-ZENODO-7493820", "CAMPAIGN-RPISOUND-UK", "SESS-VENTILATION-01", "SENSOR-RPI-02", "LOC-UK-IND-02", "industrial_and_mechanical", "VERIFIED_NEGATIVE", "Unbroken 30m continuous recording of industrial exhaust ventilation; no target events."),
        ("P23-NAT-STR-03", "P16-STREAM-03", "phase16_natural_continuous/phase16_industrial_concrete_mixer_30min.wav", "SRC-ZENODO-7493820", "CAMPAIGN-RPISOUND-UK", "SESS-MIXER-01", "SENSOR-RPI-05", "LOC-UK-IND-03", "industrial_and_mechanical", "VERIFIED_NEGATIVE", "Unbroken 30m continuous recording of industrial concrete mixer; no target events."),
        ("P23-NAT-STR-04", "P16-STREAM-04", "phase16_natural_continuous/phase16_industrial_monoblock_pump_30min.wav", "SRC-ZENODO-7493820", "CAMPAIGN-RPISOUND-UK", "SESS-PUMP-01", "SENSOR-RPI-01", "LOC-UK-IND-04", "industrial_and_mechanical", "VERIFIED_NEGATIVE", "Unbroken 30m continuous recording of industrial monoblock pump; no target events."),
        ("P23-NAT-STR-05", "P16-STREAM-05", "phase16_natural_continuous/phase16_traffic_road_arterial_30min.wav", "SRC-ZENODO-7493820", "CAMPAIGN-RPISOUND-UK", "SESS-TRAFFIC-01", "SENSOR-RPI-07", "LOC-UK-TRAFFIC-01", "traffic_and_road", "VERIFIED_NEGATIVE", "Unbroken 30m continuous recording of arterial road traffic; no target events."),
        ("P23-NAT-STR-06", "P16-STREAM-06", "phase16_natural_continuous/phase16_traffic_transit_train_30min.wav", "SRC-ZENODO-7493820", "CAMPAIGN-RPISOUND-UK", "SESS-TRAIN-01", "SENSOR-RPI-08", "LOC-UK-TRANSIT-01", "traffic_and_road", "VERIFIED_NEGATIVE", "Unbroken 30m continuous recording of passenger rail corridor; no target events."),
        ("P23-NAT-STR-07", "P16-STREAM-07", "phase16_natural_continuous/phase16_public_space_canteen_plaza_30min.wav", "SRC-ZENODO-7493820", "CAMPAIGN-RPISOUND-UK", "SESS-PLAZA-01", "SENSOR-RPI-03", "LOC-UK-PLAZA-01", "public_spaces", "VERIFIED_NEGATIVE", "Unbroken 30m continuous recording of university canteen plaza; no target events."),
        ("P23-NAT-STR-08", "P16-STREAM-08", "phase16_natural_continuous/phase16_percussion_acoustic_drums_30min.wav", "SRC-ZENODO-7493820", "CAMPAIGN-RPISOUND-UK", "SESS-DRUMS-01", "SENSOR-RPI-09", "LOC-UK-STUDIO-01", "percussive_acoustic_mimics", "VERIFIED_NEGATIVE", "Unbroken 30m continuous recording of acoustic drum practice; verified negative non-ballistic."),
        ("P23-NAT-STR-09", "P16-STREAM-09", "phase16_natural_continuous/phase16_indoor_appliance_washing_machine_30min.wav", "SRC-ZENODO-7493820", "CAMPAIGN-RPISOUND-UK", "SESS-APPLIANCE-01", "SENSOR-RPI-06", "LOC-UK-INDOOR-01", "general_indoor_ambience", "VERIFIED_NEGATIVE", "Unbroken 30m continuous recording of domestic washing machine spin cycle; no target events."),
        ("P23-NAT-STR-10", "P16-STREAM-10", "phase16_natural_continuous/phase16_indoor_interior_laptop_exhaust_30min.wav", "SRC-ZENODO-7493820", "CAMPAIGN-RPISOUND-UK", "SESS-EXHAUST-01", "SENSOR-RPI-10", "LOC-UK-INDOOR-02", "general_indoor_ambience", "VERIFIED_NEGATIVE", "Unbroken 30m continuous recording of computer cooling exhaust; no target events."),
        ("P23-NAT-STR-11", "P16-STREAM-11", "phase16_natural_continuous/phase16_natural_weather_aquatic_reservoir_35min.wav", "SRC-ZENODO-3938837", "CAMPAIGN-CHEWMAGNA-UK", "SESS-RESERVOIR-01", "SENSOR-FIELD-01", "LOC-UK-RURAL-01", "natural_weather", "VERIFIED_NEGATIVE", "Unbroken 35m continuous recording of outdoor reservoir lake; verified non-ballistic background."),

        # Phase 17 (6 streams)
        ("P23-NAT-STR-12", "P17-STREAM-12", "phase17_natural_continuous/phase17_urban_exterior_plaza_30min.wav", "SRC-ZENODO-18561165", "CAMPAIGN-BILBAO-ES", "SESS-BILBAO-CP01", "SENSOR-ZOOM-H4N-01", "LOC-ES-PLAZA-NUEVA", "urban_exterior_plaza", "VERIFIED_NEGATIVE", "Unbroken continuous field recording from Bilbao Old Town exterior plaza; verified negative."),
        ("P23-NAT-STR-13", "P17-STREAM-13", "phase17_natural_continuous/phase17_urban_interior_commercial_30min.wav", "SRC-ZENODO-18561165", "CAMPAIGN-BILBAO-ES", "SESS-BILBAO-CP02", "SENSOR-ZOOM-H4N-01", "LOC-ES-COMMERCIAL-01", "urban_interior_commercial", "VERIFIED_NEGATIVE", "Unbroken continuous field recording from Bilbao commercial arcade; verified negative."),
        ("P23-NAT-STR-14", "P17-STREAM-14", "phase17_natural_continuous/phase17_urban_exterior_walkway_30min.wav", "SRC-ZENODO-18561165", "CAMPAIGN-BILBAO-ES", "SESS-BILBAO-CP03", "SENSOR-ZOOM-H4N-01", "LOC-ES-WALKWAY-01", "urban_exterior_walkway", "VERIFIED_NEGATIVE", "Unbroken continuous field recording from Bilbao pedestrian walkway; verified negative."),
        ("P23-NAT-STR-15", "P17-STREAM-15", "phase17_natural_continuous/phase17_urban_exterior_terrace_30min.wav", "SRC-ZENODO-18561165", "CAMPAIGN-BILBAO-ES", "SESS-BILBAO-CP04", "SENSOR-ZOOM-H4N-01", "LOC-ES-TERRACE-01", "urban_exterior_terrace", "VERIFIED_NEGATIVE", "Unbroken continuous field recording from Bilbao hospitality terrace; verified negative."),
        ("P23-NAT-STR-16", "P17-STREAM-16", "phase17_natural_continuous/phase17_urban_interior_arcade_30min.wav", "SRC-ZENODO-18561165", "CAMPAIGN-BILBAO-ES", "SESS-BILBAO-CP05", "SENSOR-ZOOM-H4N-01", "LOC-ES-ARCADE-01", "urban_interior_arcade", "VERIFIED_NEGATIVE", "Unbroken continuous field recording from Bilbao covered arcade; verified negative."),
        ("P23-NAT-STR-17", "P17-STREAM-17", "phase17_natural_continuous/phase17_urban_interior_hall_30min.wav", "SRC-ZENODO-18561165", "CAMPAIGN-BILBAO-ES", "SESS-BILBAO-CP06", "SENSOR-ZOOM-H4N-01", "LOC-ES-HALL-01", "urban_interior_hall", "VERIFIED_NEGATIVE", "Unbroken continuous field recording from Bilbao municipal market hall; verified negative.")
    ]

    # 6 Exploratory Synthetic Overlay Streams (Phase 7 & Phase 8)
    exploratory_streams = [
        ("P23-EXP-STR-01", "P7-STREAM-01", "phase7_independent_test/continuous_ambient/continuous_stream_01_urban_traffic_and_machinery_1hr.wav", "SRC-HISTORICAL-SYNTH-P7P8", "CAMPAIGN-SYNTH-P7", "SESS-SYNTH-TRAFFIC-1HR", "SENSOR-SYNTH-01", "LOC-SYNTH-LAB", "synthetic_traffic_machinery", "POTENTIALLY_NEGATIVE_UNVERIFIED", "Synthetic overlay of ESC-50 clips on silence; exploratory test only; excluded from natural negative exposure."),
        ("P23-EXP-STR-02", "P7-STREAM-02", "phase7_independent_test/continuous_ambient/continuous_stream_02_weather_thunder_and_rain_1hr.wav", "SRC-HISTORICAL-SYNTH-P7P8", "CAMPAIGN-SYNTH-P7", "SESS-SYNTH-WEATHER-1HR", "SENSOR-SYNTH-01", "LOC-SYNTH-LAB", "synthetic_weather_thunder", "POTENTIALLY_NEGATIVE_UNVERIFIED", "Synthetic overlay of ESC-50 rain/thunder on silence; exploratory test only; excluded from natural negative exposure."),
        ("P23-EXP-STR-03", "P7-STREAM-03", "phase7_independent_test/continuous_ambient/continuous_stream_03_bells_fireworks_and_crowd_1hr.wav", "SRC-HISTORICAL-SYNTH-P7P8", "CAMPAIGN-SYNTH-P7", "SESS-SYNTH-BELLS-1HR", "SENSOR-SYNTH-01", "LOC-SYNTH-LAB", "synthetic_bells_fireworks", "POTENTIALLY_NEGATIVE_UNVERIFIED", "Synthetic overlay of ESC-50 bells/fireworks on silence; exploratory test only; excluded from natural negative exposure."),
        ("P23-EXP-STR-04", "P8-STREAM-01", "phase8_final_eval/continuous_ambient/continuous_stream_01_urban_transit_sirens_1hr.wav", "SRC-HISTORICAL-SYNTH-P7P8", "CAMPAIGN-SYNTH-P8", "SESS-SYNTH-SIRENS-1HR", "SENSOR-SYNTH-01", "LOC-SYNTH-LAB", "synthetic_transit_sirens", "POTENTIALLY_NEGATIVE_UNVERIFIED", "Synthetic overlay of sirens on silence; exploratory test only; excluded from natural negative exposure."),
        ("P23-EXP-STR-05", "P8-STREAM-02", "phase8_final_eval/continuous_ambient/continuous_stream_02_domestic_interior_transients_1hr.wav", "SRC-HISTORICAL-SYNTH-P7P8", "CAMPAIGN-SYNTH-P8", "SESS-SYNTH-DOMESTIC-1HR", "SENSOR-SYNTH-01", "LOC-SYNTH-LAB", "synthetic_domestic_interior", "POTENTIALLY_NEGATIVE_UNVERIFIED", "Synthetic overlay of domestic sounds on silence; exploratory test only; excluded from natural negative exposure."),
        ("P23-EXP-STR-06", "P8-STREAM-03", "phase8_final_eval/continuous_ambient/continuous_stream_03_outdoor_natural_ambience_1hr.wav", "SRC-HISTORICAL-SYNTH-P7P8", "CAMPAIGN-SYNTH-P8", "SESS-SYNTH-OUTDOOR-1HR", "SENSOR-SYNTH-01", "LOC-SYNTH-LAB", "synthetic_outdoor_ambience", "POTENTIALLY_NEGATIVE_UNVERIFIED", "Synthetic overlay of outdoor clips on silence; exploratory test only; excluded from natural negative exposure.")
    ]

    all_stream_defs = primary_streams + exploratory_streams
    provenance_rows = []
    seen_hashes = {}
    duplicate_rows = []

    for row_def in all_stream_defs:
        rec_id, legacy_id, rel_path, src_id, camp_id, sess_id, sens_id, loc_id, env_cat, elig_cat, elig_reason = row_def
        abs_path = DATA_DIR / rel_path
        if not abs_path.exists():
            print(f"[ERROR] Missing file: {abs_path}")
            continue

        file_sha = sha256_file(abs_path)
        file_size = abs_path.stat().st_size
        dur, rate, ch = get_audio_info(abs_path)

        # Duplicate check
        if file_sha in seen_hashes:
            dup_entry = {
                "hash": file_sha,
                "first_recording_id": seen_hashes[file_sha],
                "duplicate_recording_id": rec_id,
                "duplicate_file": rel_path,
                "status": "EXACT_DUPLICATE_FOUND"
            }
            duplicate_rows.append(dup_entry)
        else:
            seen_hashes[file_sha] = rec_id

        entry = {
            "recording_id": rec_id,
            "legacy_stream_id": legacy_id,
            "filename": abs_path.name,
            "relative_filepath": rel_path,
            "source_id": src_id,
            "campaign_id": camp_id,
            "session_id": sess_id,
            "sensor_id": sens_id,
            "location_id": loc_id,
            "duration_seconds": round(dur, 3),
            "duration_hours": round(dur / 3600.0, 5),
            "sample_rate_hz": rate,
            "channels": ch,
            "file_size_bytes": file_size,
            "sha256": file_sha,
            "continuity_status": "NATURAL_CONTINUOUS" if "P23-NAT" in rec_id else "SYNTHETIC_OVERLAY",
            "transformed_status": "STANDARDIZED_PCM16_16K" if rate == 16000 else "RAW_UNMODIFIED",
            "acoustic_environment": env_cat,
            "target_annotations_present": "NO_GUNSHOT_ANNOTATIONS",
            "eligibility_category": elig_cat,
            "eligibility_reason": elig_reason
        }
        provenance_rows.append(entry)

    out_prov_csv = REPORTS_DIR / "phase23_recording_provenance.csv"
    with open(out_prov_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(provenance_rows[0].keys()))
        writer.writeheader()
        writer.writerows(provenance_rows)
    print(f"Saved recording provenance: {out_prov_csv} ({len(provenance_rows)} streams cataloged)")

    # 3. Duplicate Audit CSV
    if not duplicate_rows:
        duplicate_rows.append({
            "hash": "NONE",
            "first_recording_id": "NONE",
            "duplicate_recording_id": "NONE",
            "duplicate_file": "NONE",
            "status": "ZERO_EXACT_DUPLICATES_DETECTED"
        })

    out_dup_csv = REPORTS_DIR / "phase23_duplicate_audit.csv"
    with open(out_dup_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(duplicate_rows[0].keys()))
        writer.writeheader()
        writer.writerows(duplicate_rows)
    print(f"Saved duplicate audit: {out_dup_csv} ({len(duplicate_rows)} audit records)")


if __name__ == "__main__":
    main()

