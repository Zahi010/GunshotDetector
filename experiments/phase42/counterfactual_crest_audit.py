import pandas as pd
import numpy as np
import pathlib
import sys

REPO = pathlib.Path(".")
if str(REPO.resolve()) not in sys.path:
    sys.path.insert(0, str(REPO.resolve()))

inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
fw_recon = pd.read_csv("experiments/phase41/phase41_fireworks_reconstruction.csv")
cache_dir = REPO / "experiments" / "phase39" / "feature_cache"

from experiments.phase36.model_phase36 import EventStateMachine, AcousticSuppressionEngine, SuppressionMode

discordant = fw_recon[fw_recon["pair_status"] == "PHASE36_ONLY"].copy()
print(f"Auditing {len(discordant)} discordant clips...")

counterfactual_results = []

for _, row in discordant.iterrows():
    rid = row["recording_id"]
    npz = np.load(cache_dir / f"{rid}.npz")
    raw_scores = npz["raw_scores"]
    yamnet_scores = npz["yamnet_scores"]
    dur_sec = float(npz["duration_seconds"])
    actual_crest = float(npz["crest_factor_db"])
    
    # 1. Animal scores in these clips
    animal_indices = [74, 75, 76, 77, 78, 79, 80]
    max_animal = float(np.max([yamnet_scores[:, c] for c in animal_indices if c < yamnet_scores.shape[1]]))
    
    # 2. Fireworks scores in these clips
    fw_indices = [434, 435]
    max_fw = float(np.max([yamnet_scores[:, c] for c in fw_indices if c < yamnet_scores.shape[1]]))
    
    # 3. Number of windows >= threshold_base (0.75) and >= threshold_high (0.88)
    n_win_base = int(np.sum(raw_scores >= 0.75))
    n_win_high = int(np.sum(raw_scores >= 0.88))
    
    # Run Baseline Phase 36 (Actual)
    fsm_act = EventStateMachine(
        threshold_base=0.75, threshold_high=0.88, threshold_off=0.48,
        confirm_windows=2, cooldown_secs=2.0, min_crest_factor_db=8.8, single_win_min_crest_db=12.0
    )
    supp_act = AcousticSuppressionEngine(mode=SuppressionMode.CONSERVATIVE, conservative_min_crest_db=12.0)
    
    act_alerts = 0
    for i in range(len(raw_scores)):
        sc_res = supp_act.apply_suppression(raw_scores[i], yamnet_scores[i], crest_factor_db=actual_crest)
        win_rec = {"window_index": i, "start_time": round(i*0.48, 3), "end_time": round(i*0.48+0.96, 3), "score": sc_res["adjusted_score"], "raw_ensemble_score": float(raw_scores[i])}
        ev = fsm_act.process_window(win_rec, crest_factor_db=actual_crest)
        if ev: act_alerts += 1
    ev_final = fsm_act.flush()
    if ev_final: act_alerts += 1
    
    # Run Counterfactual 1: Crest gate disabled (crest_factor_db set to 0.0 dB, so crest < 12.0 dB)
    fsm_cf1 = EventStateMachine(
        threshold_base=0.75, threshold_high=0.88, threshold_off=0.48,
        confirm_windows=2, cooldown_secs=2.0, min_crest_factor_db=8.8, single_win_min_crest_db=12.0
    )
    supp_cf1 = AcousticSuppressionEngine(mode=SuppressionMode.CONSERVATIVE, conservative_min_crest_db=12.0)
    
    cf1_alerts = 0
    for i in range(len(raw_scores)):
        sc_res = supp_cf1.apply_suppression(raw_scores[i], yamnet_scores[i], crest_factor_db=0.0)
        win_rec = {"window_index": i, "start_time": round(i*0.48, 3), "end_time": round(i*0.48+0.96, 3), "score": sc_res["adjusted_score"], "raw_ensemble_score": float(raw_scores[i])}
        ev = fsm_cf1.process_window(win_rec, crest_factor_db=0.0)
        if ev: cf1_alerts += 1
    ev_final = fsm_cf1.flush()
    if ev_final: cf1_alerts += 1

    # Run Counterfactual 2: Phase 14 semantic suppression applied to Phase 36 raw scores
    # Phase 14 rule: if fw_s > 0.35, cal_s *= 0.35
    fsm_cf2 = EventStateMachine(
        threshold_base=0.75, threshold_high=0.88, threshold_off=0.48,
        confirm_windows=2, cooldown_secs=2.0, min_crest_factor_db=8.8, single_win_min_crest_db=12.0
    )
    cf2_alerts = 0
    for i in range(len(raw_scores)):
        cal_s = float(raw_scores[i])
        fw_s = float(np.max(yamnet_scores[i, [434, 435]]))
        gun_s = float(np.max(yamnet_scores[i, [426, 427, 428, 429]]))
        if fw_s > 0.35 and fw_s >= gun_s * 2.0 and gun_s < 0.05:
            cal_s *= 0.35
        win_rec = {"window_index": i, "start_time": round(i*0.48, 3), "end_time": round(i*0.48+0.96, 3), "score": cal_s, "raw_ensemble_score": float(raw_scores[i])}
        ev = fsm_cf2.process_window(win_rec, crest_factor_db=actual_crest)
        if ev: cf2_alerts += 1
    ev_final = fsm_cf2.flush()
    if ev_final: cf2_alerts += 1
    
    counterfactual_results.append({
        "recording_id": rid,
        "crest_factor_db": actual_crest,
        "max_raw_score": float(np.max(raw_scores)),
        "max_animal_score": max_animal,
        "max_fireworks_score": max_fw,
        "n_windows_ge_075": n_win_base,
        "n_windows_ge_088": n_win_high,
        "actual_phase36_alerts": act_alerts,
        "cf1_zero_crest_alerts": cf1_alerts,
        "cf2_p14_suppression_alerts": cf2_alerts
    })

cf_df = pd.DataFrame(counterfactual_results)
print(cf_df.to_string())
