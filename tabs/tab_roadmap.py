"""
Staged implementation roadmap (Section K).

Generic staged plan with no fabricated durations, performance targets, or
success probabilities. Timelines and targets are left for the user to fill
in for their own project.
"""
import streamlit as st

STAGES = [
    {
        "name": "1. Feedstock characterisation",
        "objective": "Establish composition, variability and safety baseline of your actual bran lots.",
        "activities": [
            "Sample multiple lots across mills/varieties/storage conditions",
            "Measure protein, moisture, FFA, peroxide value, oil, fibre",
            "Record traceability (mill, variety, date, storage history)",
        ],
        "data_needed": ["Lab access for proximate analysis", "Representative lot samples"],
        "deliverables": ["Composition dataset across lots", "Variability range for key parameters"],
        "decision_gate": "Composition and FFA/stability data are documented for at least a few representative lots.",
        "dependencies_risks": ["Lot-to-lot variability may be larger than literature ranges (PF02/PF26, PF01/PF29)."],
    },
    {
        "name": "2. Literature review & lab planning",
        "objective": "Select a specific extraction/stabilization method backed by a named study, matched to your feedstock.",
        "activities": [
            "Review candidate methods against your Step 1 composition data",
            "Draft a lab trial protocol with defined parameters (not assumed)",
        ],
        "data_needed": ["Access to source papers", "Step 1 composition data"],
        "deliverables": ["Chosen method(s) with cited source", "Written trial protocol"],
        "decision_gate": "A specific method and parameter set is selected with a traceable citation.",
        "dependencies_risks": ["Evidence files here (RB/PF series) do not yet cover extraction yield/purity data — may need further literature search."],
    },
    {
        "name": "3. Laboratory extraction trials",
        "objective": "Run the selected process at lab scale and record actual protein recovery, purity and yield.",
        "activities": [
            "Execute trial runs per protocol", "Record mass balance for each run",
            "Vary key parameters if resources allow",
        ],
        "data_needed": ["Lab equipment per Equipment planner tab", "Characterised feedstock from Step 1"],
        "deliverables": ["Measured protein recovery %, purity %, yield % (not assumed)"],
        "decision_gate": "At least one trial produces a measured, reproducible recovery/purity result.",
        "dependencies_risks": ["Without this stage, Cost tab figures remain 'assumed' placeholders, not real economics."],
    },
    {
        "name": "4. Analytical, sensory & safety testing",
        "objective": "Confirm the trial product is safe, and diagnose/resolve any sensory defects.",
        "activities": [
            "Run QC checklist items (microbiology, contaminants, FFA, oxidation)",
            "Sensory panel against defects identified in Diagnosis tab",
        ],
        "data_needed": ["QC checklist tab results", "Diagnosis tab candidate-cause findings"],
        "deliverables": ["Completed QC checklist with verified/failed statuses", "Sensory panel results"],
        "decision_gate": "No failed safety checks remain open; sensory defects are diagnosed to a specific cause.",
        "dependencies_risks": ["A 'Verified' status here must come from actual test results, never assumed."],
    },
    {
        "name": "5. Route optimisation",
        "objective": "Improve recovery, purity, functionality or cost based on Stage 3/4 results.",
        "activities": ["Iterate process parameters", "Re-test functionality for target application (RB08)"],
        "data_needed": ["Stage 3 trial data", "Target application spec (e.g. beverage, bakery, meat analogue)"],
        "deliverables": ["Optimised parameter set with before/after comparison"],
        "decision_gate": "Measured improvement in a defined metric (recovery, purity, functionality, or cost).",
        "dependencies_risks": ["Optimisation targets must be user-defined — no generic target is assumed here."],
    },
    {
        "name": "6. Pilot-scale validation",
        "objective": "Confirm the process holds up outside the lab, at a representative batch size.",
        "activities": ["Scale up with pilot equipment (see Equipment planner)", "Repeat mass balance, QC and sensory testing at pilot scale"],
        "data_needed": ["Pilot equipment access", "Stage 3/4/5 protocols"],
        "deliverables": ["Pilot-scale mass balance, cost and QC results"],
        "decision_gate": "Pilot results are consistent enough with lab results to justify commercial planning.",
        "dependencies_risks": ["Yields often drop at scale-up; do not assume lab-scale numbers hold."],
    },
    {
        "name": "7. Equipment & facility planning",
        "objective": "Finalise the equipment register and facility layout for the intended production scale.",
        "activities": ["Confirm availability/purchase status for each item (Equipment planner tab)", "Obtain supplier quotations"],
        "data_needed": ["Pilot-scale results", "Supplier quotes"],
        "deliverables": ["Finalised equipment register with costs no longer marked 'Needs quotation'"],
        "decision_gate": "All required equipment has a confirmed source and quoted cost.",
        "dependencies_risks": ["Utility requirements (water, power) must be confirmed on-site, not assumed."],
    },
    {
        "name": "8. Regulatory review",
        "objective": "Confirm FSSAI approval pathway for the specific ingredient and intended use (RB13).",
        "activities": ["Determine if the ingredient/use is already standardised", "If not, prepare Non-Specified Food application materials"],
        "data_needed": ["Final product specification", "Stage 3/4 test data"],
        "deliverables": ["Documented regulatory status/approval pathway"],
        "decision_gate": "Regulatory pathway is confirmed in writing, not assumed from rice bran's general familiarity.",
        "dependencies_risks": ["Approval timelines are not estimated here — depend on regulator process."],
    },
    {
        "name": "9. Commercial-scale engineering & financial validation",
        "objective": "Build a bankable cost/ROI case from real pilot and quotation data.",
        "activities": ["Update Cost tab with pilot-scale, quoted figures", "Build financial model with real inputs"],
        "data_needed": ["Pilot-scale cost and yield data", "Confirmed equipment/utility costs", "Market price data for comparison"],
        "deliverables": ["Cost sheet with measured/quoted inputs replacing all 'assumed' placeholders"],
        "decision_gate": "Break-even and cost comparisons use measured/quoted data, not assumptions.",
        "dependencies_risks": ["No ROI, payback period or margin should be claimed before this stage is complete."],
    },
]


def render():
    st.subheader("🗺️ Staged implementation roadmap")
    st.caption(
        "Generic staged plan. No durations, performance targets or success probabilities are "
        "assumed — define your own timelines and targets per stage below."
    )

    for stage in STAGES:
        with st.container(border=True):
            st.markdown(f"### {stage['name']}")
            st.write(f"**Objective:** {stage['objective']}")
            st.markdown("**Required activities:**")
            for a in stage["activities"]:
                st.markdown(f"- {a}")
            st.markdown("**Data/resources needed:** " + "; ".join(stage["data_needed"]))
            st.markdown("**Deliverables:** " + "; ".join(stage["deliverables"]))
            st.success(f"**Decision gate:** {stage['decision_gate']}")
            for r in stage["dependencies_risks"]:
                st.warning(r)
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Your target date (optional)", key=f"roadmap_date_{stage['name']}")
            with c2:
                st.selectbox(
                    "Status", ["Not started", "In progress", "Blocked", "Complete"],
                    key=f"roadmap_status_{stage['name']}",
                )

    return {"stages": [s["name"] for s in STAGES]}
