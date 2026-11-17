from scratch.test_coherence import dev_data, NON_TARGET_CLASSES, BALLISTIC_EXP_CLASSES, GUN_CLASSES, FW_CLASSES, THUN_CLASSES, DOG_CLASSES, CRACKLE_CLASSES, SIREN_CLASSES, WIND_CLASSES, IMPACT_CLASSES
import numpy as np

for d in dev_data:
    if d['sub_category'] != 'LONG_AMBIENT_STREAM':
        continue
    raw_s = d['raw_scores']
    ys = d['yamnet_scores']
    dur = d['duration_sec']
    crest = d['crest_factor_db']
    n_win = len(raw_s)

    adj_scores = []
    for i in range(n_win):
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

        adj = raw
        if ballistic_s < 0.015 and non_target_s >= 0.12:
            adj *= 0.20
        elif thun_s > 0.25 and thun_s >= gun_s * 1.5:
            adj *= 0.30
        elif fw_s >= 0.45 and fw_s >= gun_s * 1.8 and gun_s < 0.25:
            adj *= 0.30
        elif fw_s >= 0.30 and fw_s >= gun_s * 1.5 and gun_s < 0.12:
            adj *= 0.35
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

    # Simple 2-window check
    events = []
    in_cand = False
    cooldown = -1.0
    for i, s in enumerate(adj_scores):
        t = i * 0.48
        if t < cooldown: continue
        if (s >= 0.88 and crest >= 12.0):
            events.append(i); cooldown = t + 2.0; in_cand = False
        elif not in_cand and s >= 0.75:
            in_cand = True
        elif in_cand:
            if s >= 0.75:
                events.append(i-1); cooldown = t + 2.0
            in_cand = False
    if len(events) > 0:
        print(f"{d['recording_id']}: {len(events)} events at windows {events}")

