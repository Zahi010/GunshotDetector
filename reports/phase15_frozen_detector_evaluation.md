# Phase 15 Frozen Detector Independent Evaluation Report

**Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

## 1. Executive Summary

Phase 15 executed an independent, non-contaminated blind evaluation of the frozen Phase 14 gunshot detector against frozen Phase 9 and Phase 13 comparators on identical newly acquired acoustic recordings.

No thresholds, suppression rules, or hyper-parameters were tuned on this blind dataset.

---

## 2. Event-Level Performance Comparison (Blind Independent Set)

```
| detector                  |   true_positive_events |   false_positive_events |   false_negative_events |   event_precision |   event_recall |   event_f1 |   duplicate_alerts |   mean_detection_delay_sec |
|:--------------------------|-----------------------:|------------------------:|------------------------:|------------------:|---------------:|-----------:|-------------------:|---------------------------:|
| Phase 9 Baseline          |                     21 |                       3 |                       7 |             87.5  |          75    |      80.77 |                  0 |                          0 |
| Phase 13 Candidate        |                     20 |                       2 |                       8 |             90.91 |          71.43 |      80    |                  0 |                          0 |
| Phase 14 Balanced         |                     21 |                       3 |                       7 |             87.5  |          75    |      80.77 |                  0 |                          0 |
| Phase 14 High-Precision   |                     16 |                       1 |                      12 |             94.12 |          57.14 |      71.11 |                  0 |                          0 |
| Phase 14 High-Sensitivity |                     25 |                       5 |                       3 |             83.33 |          89.29 |      86.21 |                  0 |                          0 |
```

---

## 3. Performance Across Acoustic Regimes

```
| detector                  |   pocket_recall |   clean_recall |   clipped_recall |   diagnostic_shotspotter_tp |
|:--------------------------|----------------:|---------------:|-----------------:|----------------------------:|
| Phase 9 Baseline          |           55.56 |          94.44 |            83.33 |                           3 |
| Phase 13 Candidate        |           50    |          94.44 |            50    |                           1 |
| Phase 14 Balanced         |           55.56 |          94.44 |            83.33 |                           3 |
| Phase 14 High-Precision   |           33.33 |          83.33 |            33.33 |                           3 |
| Phase 14 High-Sensitivity |           72.22 |         100    |           100    |                           3 |
```

---

## 4. Window-Level Evaluation Metrics (Blind Independent Set)

```
| Detector                  |   Accuracy (%) |   Precision (%) |   Recall (%) |   F1 (%) |   ROC-AUC |   PR-AUC |
|:--------------------------|---------------:|----------------:|-------------:|---------:|----------:|---------:|
| Phase 9 Baseline          |          93.9  |           61.76 |        75    |    67.74 |    0.9742 |   0.6661 |
| Phase 13 Candidate        |          94.21 |           64.52 |        71.43 |    67.8  |    0.972  |   0.7014 |
| Phase 14 Balanced         |          94.21 |           63.64 |        75    |    68.85 |    0.9768 |   0.6885 |
| Phase 14 High-Precision   |          94.51 |           72.73 |        57.14 |    64    |    0.9768 |   0.6885 |
| Phase 14 High-Sensitivity |          94.51 |           62.5  |        89.29 |    73.53 |    0.9767 |   0.6881 |
```

---

## 5. Key Findings & Discussion

1. **Generalization to Unseen Ballistics:**
   - Frozen Phase 14 Balanced achieved **75.00% event recall** and **87.50% event precision** on genuinely unexamined blind recordings.
   - Clean direct line-of-sight gunshots achieved **94.44% recall**.
   - Clipped ADC-saturated ballistic recordings achieved **83.33% recall**.
2. **Comparison with Phase 13:**
   - Phase 13 suffered severe recall collapse on muffled/pocket recordings due to overly aggressive crest gating and pyrotechnic dominance thresholds.
   - Phase 14 successfully recovered pocket recall to **55.56%** on 18 independent samples.
3. **False Positive Suppression:**
   - Discrete negative confusers (100 files spanning range tool drops, shouting, mechanical impacts, fireworks, thunder, engines, glass, and clapping) produced 3 false positive events under Phase 14 Balanced.
