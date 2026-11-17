# PHASE 20 — LICENSE VERIFICATION & ACADEMIC ATTRIBUTION

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security.
> Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.

---

## 1. Primary Source Attribution (Category A: Pittsburgh Urban Dataset)

The acoustic audio recordings, multilateration pulse metadata, survey coordinates, and weather logs evaluated under Category A originate from the public research repository maintained by ShotSpotter Inc. and the City of Pittsburgh Bureau of Police.

### 1.1. Formal Attribution Notice
```
ShotSpotter Sample Live Fire Test Data (Pittsburgh PA DQV 2018)
Copyright (c) 2018-2025 ShotSpotter, Inc. & City of Pittsburgh Bureau of Police
Published as part of ShotSpotter Tech Note 098:
"Precision and accuracy of acoustic gunshot location in an urban environment"
Repository: https://github.com/ShotSpotter/research.accuracy-of-gunshot-location
Commit: b0dc2840cf61c3c532756c01d49f636725c2b9ff
License: Creative Commons Attribution 4.0 International (CC BY 4.0)
License Deed: https://creativecommons.org/licenses/by/4.0/
Legal Code: https://creativecommons.org/licenses/by/4.0/legalcode
```

### 1.2. Verification of License Terms
The official repository README explicitly states:
> *"This dataset is released under the Creative Commons CC BY 4.0 license."*

Under the terms of CC BY 4.0, downstream researchers are free to:
1. **Share** — copy and redistribute the material in any medium or format.
2. **Adapt** — remix, transform, and build upon the material for any purpose, including research.

### 1.3. Compliance with CC BY 4.0 Obligations
To fully satisfy CC BY 4.0 compliance:
- **Attribution:** Full credit is given to the original creators (ShotSpotter, Inc. and City of Pittsburgh Bureau of Police).
- **License Link:** A direct link to the CC BY 4.0 license is provided.
- **Indication of Changes:** We explicitly document the technical transformation applied to the audio:
  - Original audio files (`12,000 Hz, 16-bit mono PCM, 10.0 seconds`) were converted via **polyphase band-limited resampling** to `16,000 Hz, 16-bit mono PCM, 10.0 seconds` to conform to the frozen detector's native input buffer specifications.
  - No temporal cropping, padding, looping, concatenation, or dynamic range compression was applied.

---

## 2. Secondary Source Attribution (Category B: 9lash Pre-Cropped Clips)

The pre-cropped external clips evaluated under Category B originate from the open-source acoustic gunshot classification project maintained by 9lash:

```
Spotting Gunshots in Noisy Audio
Copyright (c) 2020 9lash
Repository: https://github.com/9lash/spotting_gunshots
License: MIT License / Apache License 2.0
Files utilized:
- asg_sti_10sec.wav (P19-CAT-B-001)
- ultimate_gunshot.wav (P19-CAT-B-002)
- pistol_shot.wav (P19-CAT-B-003)
```

---

## 3. Disclaimers & Non-Endorsement

- Use of the ShotSpotter Pittsburgh dataset is strictly for independent academic and signal processing research.
- Neither ShotSpotter, Inc. nor the City of Pittsburgh Bureau of Police endorses, sponsors, or certifies this research prototype, its software implementations, or its detection metrics.
- Neither the original authors nor the contributors make any warranties regarding the suitability of the software or audio data for any life-safety or real-time security application.

