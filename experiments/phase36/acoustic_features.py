"""
Phase 36 Acoustic Feature & Suppression Gating Engine
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
This experimental acoustic machine-learning software is uncertified and must never
be deployed for autonomous emergency dispatch, tactical police response,
active-shooter alerting, automated evacuation, building lockdown, or life-critical
physical security. Safe recorded audio playback only; no live-fire testing.
"""

from enum import Enum
from typing import Dict, Any, Optional, Tuple, List
import numpy as np


class SuppressionMode(str, Enum):
    NONE = "NONE"
    LEGACY_ANIMAL = "LEGACY_ANIMAL"
    CONSERVATIVE = "CONSERVATIVE"


# YAMNet semantic class indices
YAMNET_ANIMAL_CLASSES = [
    67,   # Animal
    68,   # Domestic animals, pets
    69,   # Dog
    70,   # Bark
    71,   # Yip
    72,   # Howl
    73,   # Bow-wow
    74,   # Growling
    75,   # Whimper (dog)
    76,   # Cat
    77,   # Purr
    78,   # Meow
    79,   # Hiss
    80,   # Caterwaul
    81,   # Livestock, farm animals, working animals
    82,   # Horse
    83,   # Clip-clop
    84,   # Neigh, whinny
    85,   # Cattle, bovinae
    86,   # Moo
    87,   # Cowbell
    88,   # Pig
    89,   # Oink
    90,   # Goat
    91,   # Bleat
    92,   # Sheep
    93,   # Fowl
    94,   # Chicken, rooster
    95,   # Cluck
    96,   # Crowing, cock-a-doodle-doo
    97,   # Turkey
    98,   # Gobble
    99,   # Duck
    100,  # Quack
    101,  # Goose
    102,  # Honk
    103,  # Wild animals
    104,  # Roaring cats (lions, tigers)
    105,  # Roar
    106,  # Bird
    107,  # Bird vocalization, bird call, bird song
    108,  # Chirp, tweet
    109,  # Squawk
    110,  # Pigeon, dove
    111,  # Coo
    112,  # Crow
    113,  # Caw
    114,  # Owl
    115,  # Hoot
    116,  # Bird flight, flapping wings
    117   # Canidae, dogs, wolves
]

# Aviation and vehicular broad-spectrum classes
YAMNET_AVIATION_VEHICLE_CLASSES = [
    334,  # Aircraft
    335,  # Aircraft engine
    336,  # Jet engine
    337,  # Propeller, airscrew
    338,  # Helicopter
    339,  # Fixed-wing aircraft, airplane
    314,  # Motor vehicle (road)
    315,  # Car
    316,  # Vehicle horn
    324,  # Truck
    328   # Emergency vehicle / siren
]


def compute_physical_crest_factor_db(waveform_chunk: np.ndarray, eps: float = 1e-9) -> float:
    """
    Computes true physical crest factor in decibels:
    Crest (dB) = 20 * log10( max|x| / (RMS(x) + eps) )
    """
    if waveform_chunk is None or len(waveform_chunk) == 0:
        return 0.0

    peak = float(np.max(np.abs(waveform_chunk)))
    rms = float(np.sqrt(np.mean(waveform_chunk.astype(np.float64) ** 2)))

    if rms < eps or peak < eps:
        return 0.0

    return float(20.0 * np.log10(peak / (rms + eps)))


class AcousticSuppressionEngine:
    """
    Experimental Acoustic Suppression Isolation Module:
    Maintains clean separation between raw acoustic classifier predictions
    and post-hoc semantic suppression gates. Never modifies raw score history.
    """

    def __init__(
        self,
        mode: SuppressionMode = SuppressionMode.CONSERVATIVE,
        legacy_animal_thresh: float = 0.35,
        legacy_animal_ratio: float = 2.0,
        legacy_attenuation: float = 0.30,
        conservative_animal_thresh: float = 0.50,
        conservative_animal_ratio: float = 2.5,
        conservative_attenuation: float = 0.50,
        conservative_min_crest_db: float = 12.0
    ):
        self.mode = mode
        self.legacy_animal_thresh = legacy_animal_thresh
        self.legacy_animal_ratio = legacy_animal_ratio
        self.legacy_attenuation = legacy_attenuation
        self.conservative_animal_thresh = conservative_animal_thresh
        self.conservative_animal_ratio = conservative_animal_ratio
        self.conservative_attenuation = conservative_attenuation
        self.conservative_min_crest_db = conservative_min_crest_db

    def apply_suppression(
        self,
        raw_score: float,
        yamnet_scores: Optional[np.ndarray] = None,
        crest_factor_db: Optional[float] = None,
        is_in_confirmed_event: bool = False,
        threshold_off: float = 0.48
    ) -> Dict[str, Any]:
        """
        Evaluates acoustic suppression on a single window.
        Returns a dict containing:
        - raw_score
        - adjusted_score
        - suppression_active: bool
        - suppression_category: Optional[str]
        - suppression_strength: float (attenuation multiplier applied, 1.0 = none)
        """
        raw_score = float(raw_score)

        if self.mode == SuppressionMode.NONE or yamnet_scores is None:
            return {
                "raw_score": raw_score,
                "adjusted_score": raw_score,
                "suppression_active": False,
                "suppression_category": None,
                "suppression_strength": 1.0,
                "suppression_reason": None
            }

        # ---------------------------------------------------------------------
        # Condition 1: Legacy Phase 17 Animal Suppression
        # ---------------------------------------------------------------------
        if self.mode == SuppressionMode.LEGACY_ANIMAL:
            animal_score = float(max(yamnet_scores[cls_idx] for cls_idx in YAMNET_ANIMAL_CLASSES if cls_idx < len(yamnet_scores)))
            if animal_score > self.legacy_animal_thresh and animal_score >= raw_score * self.legacy_animal_ratio:
                adj = raw_score * self.legacy_attenuation
                return {
                    "raw_score": raw_score,
                    "adjusted_score": round(adj, 4),
                    "suppression_active": True,
                    "suppression_category": "animal_vocalization_legacy",
                    "suppression_strength": self.legacy_attenuation,
                    "suppression_reason": f"animal_score={animal_score:.3f} >= {raw_score:.3f} * {self.legacy_animal_ratio}"
                }
            return {
                "raw_score": raw_score,
                "adjusted_score": raw_score,
                "suppression_active": False,
                "suppression_category": None,
                "suppression_strength": 1.0,
                "suppression_reason": None
            }

        # ---------------------------------------------------------------------
        # Condition 2: Phase 36 Conservative Context-Aware Suppression
        # ---------------------------------------------------------------------
        if self.mode == SuppressionMode.CONSERVATIVE:
            animal_score = float(max(yamnet_scores[cls_idx] for cls_idx in YAMNET_ANIMAL_CLASSES if cls_idx < len(yamnet_scores)))
            aviation_score = float(max(yamnet_scores[cls_idx] for cls_idx in YAMNET_AVIATION_VEHICLE_CLASSES if cls_idx < len(yamnet_scores)))

            # If aviation or wideband engine roar is elevated, do not apply animal dips
            if aviation_score > 0.25 and aviation_score > animal_score * 0.5:
                return {
                    "raw_score": raw_score,
                    "adjusted_score": raw_score,
                    "suppression_active": False,
                    "suppression_category": "aviation_masked_override",
                    "suppression_strength": 1.0,
                    "suppression_reason": f"aviation_score={aviation_score:.3f} protected from animal fragmentation"
                }

            # Check conservative qualification: higher threshold (0.50) + higher ratio (2.5x)
            qualifies_animal = (
                animal_score >= self.conservative_animal_thresh
                and animal_score >= raw_score * self.conservative_animal_ratio
            )

            # Check impulsive crest factor: animals (roosters/hens) have sharp clicks (> 12 dB)
            has_impulsive_crest = (crest_factor_db is None or crest_factor_db >= self.conservative_min_crest_db)

            if qualifies_animal and has_impulsive_crest:
                # If currently in a CONFIRMED event, protect against fragmentation
                if is_in_confirmed_event:
                    # Do not force score below threshold_off unless animal score is overwhelmingly high (> 0.80)
                    if animal_score > 0.80:
                        adj = raw_score * self.conservative_attenuation
                        cat = "animal_confirmed_overwhelming"
                    else:
                        # Soft floor above threshold_off to prevent state-machine thrashing
                        adj = max(threshold_off + 0.02, raw_score * 0.80)
                        cat = "animal_confirmed_sustained_soft"
                else:
                    adj = raw_score * self.conservative_attenuation
                    cat = "animal_vocalization_conservative"

                return {
                    "raw_score": raw_score,
                    "adjusted_score": round(adj, 4),
                    "suppression_active": True,
                    "suppression_category": cat,
                    "suppression_strength": round(adj / raw_score, 3) if raw_score > 0 else 1.0,
                    "suppression_reason": f"animal_score={animal_score:.3f} (crest={crest_factor_db}dB)"
                }

            return {
                "raw_score": raw_score,
                "adjusted_score": raw_score,
                "suppression_active": False,
                "suppression_category": None,
                "suppression_strength": 1.0,
                "suppression_reason": None
            }

        return {
            "raw_score": raw_score,
            "adjusted_score": raw_score,
            "suppression_active": False,
            "suppression_category": None,
            "suppression_strength": 1.0,
            "suppression_reason": None
        }

