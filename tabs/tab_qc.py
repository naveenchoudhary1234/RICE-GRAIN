"""
Quality-control / food-safety checklist (Section J).

Route-specific checklist with explicit statuses. No item is ever marked
"Verified" unless the user says so — the app never claims compliance.
"""
import streamlit as st

from evidence_utils import badge, get_evidence_by_id, source_expander

STATUSES = ["Not assessed", "Testing required", "In progress", "Verified", "Failed"]

CHECKLIST_ITEMS = [
    ("Feedstock identity & traceability", "RB01", "Confirm mill, variety, lot ID, storage history."),
    ("Moisture & storage stability", "RB09", "Measure moisture and water activity; confirm stabilization status."),
    ("Rancidity / FFA", "RB03", "Free fatty acid / acid value test."),
    ("Oxidative stability", "RB04", "Peroxide value + sensory odour assessment, especially for oil-rich fractions."),
    ("Anti-nutritional factors (phytate/phenolics)", "RB05", "Phytate assay and/or phenolic assay if sensory issues are present."),
    ("Protein composition & purity", "RB02", "Measure protein content and, if extracted, isolate purity."),
    ("Protein/ingredient functionality", "RB08", "Solubility, water/oil binding, emulsification or gelation for intended use."),
    ("Microbiological hazards", "RB12", "Risk-based microbiology testing per supplier traceability and condition."),
    ("Chemical contaminants (mycotoxins, pesticides, heavy metals)", "RB12", "Risk-based contaminant testing."),
    ("Sensory quality", "RB07", "Sensory panel for rancid/bitter/astringent/beany defects."),
    ("Process validation", None, "Confirm the chosen route's process parameters are set from a specific study/trial, not assumed."),
    ("Packaging & shelf-life", "RB10", "Barrier packaging and shelf-life study for the stabilized or finished ingredient."),
    ("Regulatory status (FSSAI)", "RB13", "Check approval status under Non-Specified Food and Food Ingredients Regulations, 2017."),
]


def render(rb_evidence):
    st.subheader("✅ Quality-control & food-safety checklist")
    st.caption(
        "Statuses are set by you. The app never marks an item Verified on its own, and never "
        "implies the ingredient is safe or approved just because a process recommendation exists."
    )

    results = []
    verified_count = 0
    for label, evid_id, test in CHECKLIST_ITEMS:
        with st.container(border=True):
            cols = st.columns([3, 2])
            with cols[0]:
                st.markdown(f"**{label}**")
                st.caption(f"Confirming test / action: {test}")
                if evid_id:
                    ev = get_evidence_by_id(rb_evidence, evid_id)
                    if ev:
                        source_expander(ev)
            with cols[1]:
                status = st.selectbox(
                    "Status", STATUSES, key=f"qc_{label}",
                    label_visibility="collapsed",
                )
            if status == "Verified":
                verified_count += 1
            results.append({"item": label, "evidence_id": evid_id, "status": status})

    st.divider()
    total = len(CHECKLIST_ITEMS)
    if verified_count == total:
        st.success(f"All {total} checklist items marked Verified by you.")
    else:
        st.warning(
            f"{verified_count}/{total} items marked Verified. This checklist does not itself "
            "certify safety, compliance, or approval — it only reflects the statuses you set."
        )

    st.caption(f"Safety & regulatory sources: {badge('given')} RB12, RB13.", unsafe_allow_html=True)
    return {"items": results, "verified_count": verified_count, "total": total}
