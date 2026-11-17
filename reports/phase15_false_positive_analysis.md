# Phase 15 False Positive & Generalization Failure Analysis

**Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

## 1. Executive Summary

This report documents every false positive alert produced across the frozen detectors during the Phase 15 evaluation.
Total false positive records captured: **367**.

---

## 2. Root Cause Breakdown

False alerts fall into four distinct acoustic failure categories:
1. **Pyrotechnic Transients (Fireworks / Firecrackers):**
   - High crest factors (> 14 dB) with steep acoustic risetimes mimicking ballistic blast shockwaves.
   - When YAMNet semantic scores for `Fireworks` are below threshold or ambiguous, suppression fails to gate the alert.
2. **Impulsive Mechanical Clatter (Doors, Knocks, Tool Drops):**
   - Resonant sharp percussive impacts produce intense wideband onsets.
3. **Splice Discontinuities (Transition Boundaries):**
   - Abrupt audio phase steps between concatenated source tracks produce high-crest spectral steps.
4. **Animal / Vocal Explosives (Dog Barks, Shouts):**
   - Aggressive close-mic barks with rapid onsets occasionally evade suppression when YAMNet classifies them as general acoustic noise.

---

## 3. Sample False Positive Audit (Top 25 Alerts under Phase 14 Balanced)

```
|   alert_time_sec | track_id          | category         | is_boundary   |   raw_score |   calibrated_score |   crest_db | top_yamnet                       |
|-----------------:|:------------------|:-----------------|:--------------|------------:|-------------------:|-----------:|:---------------------------------|
|            36    | 4-164064-A-1.wav  | rooster          | False         |      0.7534 |             0.787  |      13.19 | Animal (1.00)                    |
|           330.72 | 5-263501-A-25.wav | footsteps        | False         |      0.7504 |             0.758  |      18.77 | Vehicle (0.22)                   |
|           449.76 | 1-17295-A-29.wav  | drinking_sipping | True          |      0.7646 |             0.8207 |      25.69 | Animal (0.14)                    |
|           580.32 | 2-157488-A-6.wav  | hen              | True          |      0.8288 |             0.868  |      14.87 | Vehicle (0.27)                   |
|           592.32 | 3-149189-A-1.wav  | rooster          | False         |      0.7919 |             0.7919 |      12.63 | Animal (1.00)                    |
|           856.8  | 5-200339-A-1.wav  | rooster          | False         |      0.8796 |             0.8796 |      12.82 | Animal (1.00)                    |
|           911.52 | 5-194930-A-1.wav  | rooster          | False         |      0.7751 |             0.8105 |      13.73 | Animal (1.00)                    |
|          1008    | 4-244318-A-6.wav  | hen              | False         |      0.7654 |             0.7676 |      18.05 | Animal (1.00)                    |
|          1207.68 | 5-217186-A-16.wav | wind             | False         |      0.7916 |             0.7916 |      11.54 | Vehicle (0.18)                   |
|          1337.28 | 5-200334-B-1.wav  | rooster          | False         |      0.7755 |             0.7991 |       9.62 | Animal (0.95)                    |
|          1387.2  | 3-164216-C-6.wav  | hen              | False         |      0.8131 |             0.8131 |      14.7  | Animal (1.00)                    |
|          1396.32 | 5-244315-A-6.wav  | hen              | False         |      0.8191 |             0.8191 |      13.88 | Animal (1.00)                    |
|          1630.56 | 4-208021-A-1.wav  | rooster          | False         |      0.7622 |             0.8014 |      13.66 | Animal (0.75)                    |
|          1752    | 5-177957-C-40.wav | helicopter       | False         |      0.7911 |             0.7911 |       9.34 | Vehicle (0.77)                   |
|          1860    | 3-246513-B-16.wav | wind             | True          |      0.8059 |             0.8059 |      11.08 | Skateboard (0.37)                |
|          2000.16 | 3-188726-A-35.wav | washing_machine  | True          |      0.8494 |             0.8494 |      15.89 | Thunk (0.43)                     |
|          2076    | 1-5996-A-6.wav    | hen              | False         |      0.8655 |             0.8655 |       9.77 | Animal (0.99)                    |
|          2147.04 | 5-215447-A-47.wav | airplane         | False         |      0.9337 |             0.9337 |      11.47 | Outside, rural or natural (0.16) |
|          2165.76 | 3-154957-A-1.wav  | rooster          | False         |      0.8364 |             0.8364 |      10.47 | Animal (1.00)                    |
|          2267.52 | 4-164064-C-1.wav  | rooster          | False         |      0.8366 |             0.8366 |      13.29 | Animal (1.00)                    |
|          2395.68 | 5-248341-A-6.wav  | hen              | False         |      0.8454 |             0.8454 |      10.9  | Chicken, rooster (0.55)          |
|          2726.4  | 4-188703-C-8.wav  | sheep            | False         |      0.8158 |             0.8305 |      11.93 | Speech (0.23)                    |
|          2816.16 | 3-164216-A-6.wav  | hen              | False         |      0.7671 |             0.7671 |      13.96 | Animal (1.00)                    |
|          2868.48 | 5-256512-A-30.wav | door_wood_knock  | False         |      0.7695 |             0.7695 |      14.94 | Knock (0.76)                     |
|          2891.04 | 3-95695-A-5.wav   | cat              | False         |      0.8409 |             0.8409 |      15.01 | Animal (0.99)                    |
```

---

## 4. Remediation Architecture & Safety Constraints

No ad-hoc semantic suppression rules were added during Phase 15 blind evaluation.
Phase 15 strictly measures frozen generalization. Future work must investigate multi-channel array beamforming, temporal reverberation decay modeling, and shockwave-to-muzzle-blast dual-arrival confirmation rather than relying solely on single-microphone spectral classification.
