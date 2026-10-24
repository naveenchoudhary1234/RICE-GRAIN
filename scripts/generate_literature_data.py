"""
PLACEHOLDER DATA GENERATOR
---------------------------
Generates data/literature_data.csv with synthetic-but-plausible rows used
ONLY to let the Streamlit demo train a model out of the box.

Replace this generated file with real literature / experimental data before
drawing any conclusions. See README.md for the expected schema.
"""
import csv
import random

random.seed(42)

BY_PRODUCTS = {
    "Guar meal": 42.0,
    "Groundnut cake": 45.0,
    "Almond cake": 38.0,
    "Rice bran": 14.0,
    "Pulse residue": 24.0,
}

TREATMENTS = [
    "Enzymatic hydrolysis (mannanase)",
    "Hot water extraction",
    "Dry heat / roasting",
    "Autoclaving (steam, 121C)",
    "Fermentation (Bacillus subtilis)",
    "Ammoniation",
    "Adsorption (activated clay)",
    "Alkaline soaking (NaOH/NaHCO3)",
    "Fermentation",
    "Soaking + boiling",
    "Enzymatic treatment (beta-glucosidase)",
    "Phytase enzyme treatment",
    "Extrusion stabilization",
    "Microwave stabilization",
    "Water extraction / washing",
    "Enzymatic hydrolysis (alpha-galactosidase)",
]

rows = []
for bp, base_protein in BY_PRODUCTS.items():
    for treatment in TREATMENTS:
        for _ in range(3):  # a few replicates per combination with noise
            temp = round(random.uniform(25, 130), 1)
            time_min = round(random.uniform(10, 180), 1)
            enzyme_dose = round(random.uniform(0, 2.5), 2)  # % w/w, 0 for non-enzymatic
            protein_before = round(base_protein + random.uniform(-1.5, 1.5), 2)

            # Heuristic "literature-like" relationship for placeholder purposes
            thermal_effect = min(temp / 130, 1.0) * 3.0
            time_effect = min(time_min / 180, 1.0) * 2.0
            enzyme_effect = enzyme_dose * 4.0
            protein_gain = 0.4 * thermal_effect + 0.3 * time_effect + 0.5 * enzyme_effect
            protein_after = round(protein_before + protein_gain + random.uniform(-0.8, 0.8), 2)

            bitterness_before = round(random.uniform(5.0, 9.0), 2)  # arbitrary 0-10 sensory scale
            bitterness_reduction = 0.03 * thermal_effect * 10 + 0.04 * time_effect * 10 + 0.05 * enzyme_effect * 10
            bitterness_after = round(max(0.5, bitterness_before - bitterness_reduction / 10 - random.uniform(0, 1.0)), 2)

            rows.append([
                bp, treatment, temp, time_min, enzyme_dose,
                protein_before, protein_after, bitterness_before, bitterness_after
            ])

with open("data/literature_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "by_product", "treatment", "temp", "time", "enzyme_dose",
        "protein_before", "protein_after", "bitterness_before", "bitterness_after"
    ])
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to data/literature_data.csv")
