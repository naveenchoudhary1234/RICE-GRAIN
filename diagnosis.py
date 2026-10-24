"""
Diagnosis-first logic for rice bran defects.

Maps an observed sensory defect to candidate causes, each referencing an
RB-series evidence ID and naming the one test that confirms it. This is a
simple rule table grounded directly in data/rice_bran_evidence.json — it
does not invent new causal claims.
"""

# defect -> list of (evidence_id, plausibility note, confirming test)
DEFECT_CAUSES = {
    "Rancid or soapy": [
        ("RB03", "Endogenous lipase hydrolyses oil into free fatty acids + glycerol, "
                  "a known driver of rancid/soapy notes.", "Free fatty acids (FFA) / acid value test"),
        ("RB04", "Lipoxygenase-driven oxidation, combined with moisture and storage, "
                  "can also produce off-flavours.", "Peroxide value + sensory odour assessment"),
        ("RB09", "Poor moisture/water-activity control accelerates both lipase activity "
                  "and oxidation during storage.", "Moisture (%) and water activity (aw) measurement"),
    ],
    "Bitter": [
        ("RB05", "Phytate is discussed in rice-bran literature as a possible contributor, "
                  "but must not be assumed without testing.", "Phytate assay (compare treated vs untreated)"),
        ("RB06", "Phenolic compounds (e.g. ferulic acid) can affect taste/colour, "
                  "but not all phenolics are undesirable.", "Sensory panel + phenolic assay if justified"),
        ("RB03", "Free fatty acids from lipolysis can also read as bitter/off notes "
                  "on a sensory panel.", "FFA / acid value test"),
    ],
    "Astringent": [
        ("RB06", "Phenolic compounds can interact with proteins and contribute to "
                  "astringency.", "Sensory panel + phenolic assay if justified"),
        ("RB05", "Phytate-mineral interactions are discussed alongside other antinutrient "
                  "factors in rice bran.", "Phytate assay (compare treated vs untreated)"),
    ],
    "Beany": [
        ("RB07", "Beany notes are a known but non-specific taste defect category; cause "
                  "must be diagnosed, not assumed.", "Sensory panel combined with FFA, oxidation and phytate/phenolic tests"),
        ("RB04", "Lipid oxidation products can produce beany/green off-notes.", "Peroxide value + sensory odour assessment"),
    ],
    "None / no defect": [],
}

ROUTES = {
    "Route A: Stabilised bran ingredient": {
        "evidence_id": "RB10",
        "description": "Prompt collection > validated stabilization > cooling > milling/sieving > "
                        "barrier packaging > shelf-life study.",
        "pros": ["Lower process complexity than protein extraction", "Retains more of the original nutrients"],
        "cons": ["Retains flavour, fibre and fat constraints", "Protein is not concentrated"],
    },
    "Route B: Protein-rich fraction": {
        "evidence_id": "RB11",
        "description": "Characterize > stabilize if needed > optional defatting > extraction/fractionation "
                        "> solid-liquid separation > recovery > drying.",
        "pros": ["Raises protein concentration for food/ingredient use"],
        "cons": ["Adds processing cost, water use, protein losses and effluent", "Yield must come from a pilot, not assumed"],
    },
}

FFA_THRESHOLDS = {
    "unfit_above": 10.0,   # PF10: >10% FFA unfit for human consumption
    "desirable_below": 5.0,  # PF10: <5% FFA desirable
}


def rank_causes(defect: str):
    """Return the ranked candidate-cause list for a given defect label."""
    return DEFECT_CAUSES.get(defect, [])


def ffa_flag(ffa_pct: float):
    """Classify a measured FFA% against published thresholds (PF10)."""
    if ffa_pct is None:
        return None
    if ffa_pct > FFA_THRESHOLDS["unfit_above"]:
        return "unfit", f"FFA {ffa_pct:.1f}% is above the 10% threshold flagged as unfit for food use (PF10)."
    if ffa_pct < FFA_THRESHOLDS["desirable_below"]:
        return "desirable", f"FFA {ffa_pct:.1f}% is below the 5% threshold described as desirable (PF10)."
    return "borderline", f"FFA {ffa_pct:.1f}% is between the desirable (<5%) and unfit (>10%) thresholds (PF10)."


def recommend_route(defect: str, ffa_pct: float = None):
    """Very simple, evidence-anchored route suggestion with trade-offs shown to the user.

    This is a heuristic nudge, not a definitive answer — the app must always
    show both routes and their trade-offs (per spec) rather than picking one
    silently.
    """
    notes = []
    if defect == "Rancid or soapy" or (ffa_pct is not None and ffa_pct > FFA_THRESHOLDS["desirable_below"]):
        notes.append("Elevated rancidity/FFA signals favour prioritising stabilization (Route A evidence: RB10, RB03) "
                      "before considering protein extraction.")
    if defect in ("Bitter", "Astringent", "Beany"):
        notes.append("Taste defects other than rancidity should be diagnosed with a sensory panel before choosing "
                      "a route (RB07) — do not assume Route B will fix flavour.")
    return notes
