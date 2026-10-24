"""
Equipment and infrastructure planner (Section G).

Equipment register derived from the same Route A/B steps as the process
flow diagram. Availability status is set by the user per item — the app
never claims a mill already owns a machine. Costs are "Needs quotation"
unless the user supplies one.
"""
import pandas as pd
import streamlit as st

from diagnosis import ROUTES
from tabs.tab_process_flow import STEP_DETAILS, _step_list

AVAILABILITY_OPTIONS = [
    "Unverified — ask mill/partner", "Existing at facility (confirmed)",
    "To be purchased", "Not needed for this route",
]
CATEGORY_OPTIONS = ["Process equipment", "Laboratory / QC equipment", "Pilot-scale", "Commercial-scale"]


def render():
    st.subheader("🏭 Equipment & infrastructure planner")
    st.caption(
        "Equipment list is derived from the process-flow steps for your selected route. "
        "Nothing here is assumed to already exist at a partner mill — confirm each item yourself."
    )

    route_name = st.radio("Route", list(ROUTES.keys()), key="equip_route")
    route = ROUTES[route_name]
    steps = _step_list(route["description"])

    rows = []
    for step in steps:
        detail = STEP_DETAILS.get(step)
        equip_text = detail[3] if detail else "Needs data"
        with st.container(border=True):
            st.markdown(f"**{step}**")
            st.caption(f"Candidate equipment: {equip_text}")
            c1, c2, c3 = st.columns(3)
            with c1:
                availability = st.selectbox(
                    "Availability", AVAILABILITY_OPTIONS, key=f"equip_avail_{route_name}_{step}",
                )
            with c2:
                category = st.selectbox(
                    "Category", CATEGORY_OPTIONS, key=f"equip_cat_{route_name}_{step}",
                )
            with c3:
                cost_input = st.text_input(
                    "Cost basis (₹, optional)", key=f"equip_cost_{route_name}_{step}",
                    placeholder="Needs quotation",
                )
            rows.append({
                "Process step": step,
                "Candidate equipment": equip_text,
                "Availability": availability,
                "Category": category,
                "Cost": cost_input or "Needs quotation",
            })

    st.divider()
    st.markdown("#### Register summary")
    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    to_purchase = sum(1 for r in rows if r["Availability"] == "To be purchased")
    unverified = sum(1 for r in rows if r["Availability"] == "Unverified — ask mill/partner")
    quoted = sum(1 for r in rows if r["Cost"] != "Needs quotation")
    c1, c2, c3 = st.columns(3)
    c1.metric("Items to purchase", to_purchase)
    c2.metric("Items needing availability confirmation", unverified)
    c3.metric("Items with a cost basis entered", f"{quoted}/{len(rows)}")

    if quoted < len(rows):
        st.info(
            f"{len(rows) - quoted} item(s) still show 'Needs quotation' — no price has been invented "
            "for these; get a supplier quote before using them in the cost sheet."
        )

    return {"route": route_name, "items": rows}
