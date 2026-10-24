"""
ByProduct2Protein - Streamlit app (Hack the Fork 2026)
Diagnosis-first upcycling tool for India's agri by-products, starting with
rice bran.

Data honesty rule: every number shown anywhere in this app carries a badge
(published / measured / assumed / synthetic / needs_lab_test). Values with
no source show "Needs pilot data" instead of a number. See README.md.
"""
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from evidence_utils import badge_legend, load_json
from tabs import (
    tab_diagnosis, tab_cost, tab_evidence, tab_demo_model, tab_mass_balance,
    tab_qc, tab_process_flow, tab_equipment, tab_roadmap,
)

st.set_page_config(page_title="ByProduct2Protein", layout="wide", page_icon="🌾")

st.title("🌾 ByProduct2Protein — Rice Bran Deep Dive")
st.caption(
    "Hack the Fork 2026 · Upcycling India's agri by-products for alternative proteins. "
    "Every number below is badged by data status — see legend."
)
badge_legend()
st.divider()

byproducts = load_json("byproducts.json")
treatments_db = load_json("treatments.json")
rb_evidence = load_json("rice_bran_evidence.json")
paper_facts = load_json("paper_facts.json")
known_gaps = load_json("known_gaps.json")

tab_names = [
    "🩺 Diagnosis", "🔀 Process flow", "🏭 Equipment", "💰 Cost",
    "⚖️ Mass balance", "✅ QC checklist", "🗺 Roadmap", "📚 Evidence",
    "🧪 Demo model (synthetic data)",
]
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(tab_names)

with tab1:
    diag_results = tab_diagnosis.render(rb_evidence, byproducts)

with tab2:
    flow_results = tab_process_flow.render(rb_evidence)

with tab3:
    equipment_results = tab_equipment.render()

with tab4:
    cost_results = tab_cost.render(byproducts)

with tab5:
    mass_balance_results = tab_mass_balance.render()

with tab6:
    qc_results = tab_qc.render(rb_evidence)

with tab7:
    roadmap_results = tab_roadmap.render()

with tab8:
    tab_evidence.render(rb_evidence, paper_facts)

with tab9:
    tab_demo_model.render(byproducts, treatments_db)



