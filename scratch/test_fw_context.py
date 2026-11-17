import sys
sys.path.insert(0, '.')
from scratch.test_coherence import dev_data, NON_TARGET_CLASSES, BALLISTIC_EXP_CLASSES, GUN_CLASSES, FW_CLASSES, THUN_CLASSES, DOG_CLASSES, CRACKLE_CLASSES, SIREN_CLASSES, WIND_CLASSES, IMPACT_CLASSES
import numpy as np

def run_context_test(fw_memory_sec=3.0, memory_attenuation=0.30):
    pos_det = 0
    pos_total = 0
    fw_fps = 0
    fw_total = 0
    env_fps = 0
    env_total = 0
    cont_events = 0

    for d in dev_data:
        raw_s = d['raw_scores']
        ys = d['yamnet_scores']
        crest = d['crest_factor_db']
        dur = d['duration_sec']
        n_win = len(raw_s)
        sc = d['sub_category']
        gt = d['ground_truth']

        if gt == 1: pos_total += 1
        elif sc == 'DISTRACTOR_FIREWORKS': fw_total += 1
        elif sc.startswith('DISTRACTOR_'): env_total += 1

        adj_scores = []
        last_fw_time = -999.0

        for i in range(n_win):
            t = i * 0.48
            raw = float(raw_s[i])
            y = ys[i]
            gun_s = max(y[c] for c in GUN_CLASSES)
            fw_s = max(y[c] for c in FW_CLASSES)
            thun_s = max(y[c] for c in THUN_CLASSES)
            dog_s = max(y[c] for c in DOG_CLASSES)
            crackle_s = max(y[c] for c in CRACKLE_CLASSES)
            siren_s = max(y[c] for c in SIREN_CLASSES)
            wind_s = max(y[c] for c in WIND_CLASSES)
            impact_s = max(y[c] for c in IMPACT_CLASSES)
            ballistic_s = max(y[c] for c in BALLISTIC_EXP_CLASSES)
            non_target_s = max(y[c] for c in NON_TARGET_CLASSES)

            if fw_s >= 0.40:
                last_fw_time = t

            in_fw_context = (t - last_fw_time) <= fw_memory_sec

            adj = raw
            if ballistic_s < 0.015 and non_target_s >= 0.12:
                adj *= 0.20
            elif thun_s > 0.25 and thun_s >= gun_s * 1.5:
                adj *= 0.30
            # Instantaneous fireworks
            elif (fw_s >= 0.45 and fw_s >= gun_s * 1.8 and gun_s < 0.25):
                adj *= 0.30
            elif (fw_s >= 0.30 and fw_s >= gun_s * 1.5 and gun_s < 0.12):
                adj *= 0.35
            # Contextual fireworks
            elif in_fw_context and (fw_s >= 0.10 or gun_s < 0.75):
                adj *= memory_attenuation
            # Other categories
            elif wind_s >= 0.25 and wind_s >= gun_s * 1.5:
                adj *= 0.25
            elif impact_s >= 0.30 and impact_s >= gun_s * 1.5 and gun_s < 0.20:
                adj *= 0.35
            elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
                adj *= 0.35
            elif crackle_s > 0.25 and crackle_s >= gun_s * 1.5:
                adj *= 0.35
            elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
                adj *= 0.30

            adj_scores.append(adj)

        # FSM run
        events = []
        in_cand = False
        cand_win = None
        cooldown_until = -1.0
        has_sharp = (crest >= 12.0)
        is_short = (dur <= 1.05 and n_win == 1 and crest >= 8.8)

        for i, s in enumerate(adj_scores):
            t = i * 0.48
            if t < cooldown_until: continue
            qual_imm = (s >= 0.88 and has_sharp) or (is_short and s >= 0.75)
            if not in_cand:
                if qual_imm:
                    events.append(i); cooldown_until = t + 2.0
                elif s >= 0.75:
                    in_cand = True; cand_win = (i, t, s)
            else:
                if qual_imm:
                    events.append(i); in_cand = False; cooldown_until = t + 2.0
                elif s >= 0.75:
                    events.append(cand_win[0]); in_cand = False; cooldown_until = t + 2.0
                else:
                    if cand_win[2] >= 0.82 and crest >= 15.0 and dur <= 5.0 and not in_fw_context:
                        events.append(cand_win[0])
                        cooldown_until = cand_win[1] + 2.0
                    in_cand = False

        if gt == 1 and len(events) > 0: pos_det += 1
        elif sc == 'DISTRACTOR_FIREWORKS' and len(events) > 0: fw_fps += 1
        elif sc.startswith('DISTRACTOR_') and len(events) > 0: env_fps += 1
        elif sc == 'LONG_AMBIENT_STREAM': cont_events += len(events)

    print(f"Memory={fw_memory_sec:.1f}s | Atten={memory_attenuation:.2f} -> Pos: {pos_det}/{pos_total} ({pos_det/pos_total*100:.1f}%), FW_FP: {fw_fps}/{fw_total}, Env_FP: {env_fps}/{env_total}, Cont_Evs: {cont_events}")

print("Testing Pyrotechnic Context Memory on DEV set...")
for msec in [1.5, 2.5, 3.5]:
    for att in [0.25, 0.30, 0.35]:
        run_context_test(fw_memory_sec=msec, memory_attenuation=att)

