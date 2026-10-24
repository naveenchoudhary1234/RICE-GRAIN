import io

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from evidence_utils import badge, metric_with_badge


def _cost_per_kg(raw_price, yield_pct, energy, labour, capex):
    return (raw_price + energy + labour + capex) / (yield_pct / 100.0)


def render(byproducts):
    st.markdown(f"**All inputs below are {badge('assumed')} placeholders — edit to match your own plant.**", unsafe_allow_html=True)
    bp_name = st.selectbox("By-product", [k for k in byproducts if not k.startswith("_")], key="cost_bp")
    bp_info = byproducts[bp_name]

    st.sidebar.header("Cost assumptions (assumed)")
    raw_price = st.sidebar.number_input("Raw material price (₹/kg)", value=float(bp_info["price_per_kg"]), step=0.5)
    yield_base = st.sidebar.slider("Base process yield (kg concentrate / 100kg raw)", 5.0, 60.0, 25.0, step=0.5)
    yield_spread = st.sidebar.slider("Yield uncertainty (± percentage points)", 0.0, 20.0, 8.0, step=1.0)
    energy_base = st.sidebar.number_input("Energy cost (₹/kg raw)", value=3.0, step=0.5)
    labour_base = st.sidebar.number_input("Labour cost (₹/kg raw)", value=2.5, step=0.5)
    capex_base = st.sidebar.number_input("Capex amortization (₹/kg raw)", value=1.5, step=0.5)
    cost_spread_pct = st.sidebar.slider("Energy/labour/capex uncertainty (±%)", 0.0, 50.0, 20.0, step=5.0)
    pea_price = st.sidebar.number_input("Imported pea isolate price (₹/kg, assumed)", value=320.0, step=5.0)

    scenarios = {
        "Low (best case)": _cost_per_kg(raw_price, yield_base + yield_spread, energy_base * (1 - cost_spread_pct / 100), labour_base * (1 - cost_spread_pct / 100), capex_base * (1 - cost_spread_pct / 100)),
        "Base": _cost_per_kg(raw_price, yield_base, energy_base, labour_base, capex_base),
        "High (worst case)": _cost_per_kg(raw_price, max(yield_base - yield_spread, 1.0), energy_base * (1 + cost_spread_pct / 100), labour_base * (1 + cost_spread_pct / 100), capex_base * (1 + cost_spread_pct / 100)),
    }

    st.subheader("Cost per kg of concentrate — low / base / high")
    c1, c2, c3 = st.columns(3)
    for col, (label, val) in zip((c1, c2, c3), scenarios.items()):
        with col:
            metric_with_badge(label, f"{val:.0f}", "assumed", suffix=" ₹/kg")

    st.subheader("Sensitivity: cost vs. yield")
    yields = list(range(max(int(yield_base - 20), 5), min(int(yield_base + 20), 60) + 1, 1))
    costs = [_cost_per_kg(raw_price, y, energy_base, labour_base, capex_base) for y in yields]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yields, y=costs, mode="lines", name="Cost per kg concentrate", line=dict(color="#1b5e20", width=3)))
    fig.add_hline(y=pea_price, line_dash="dash", line_color="#b71c1c", annotation_text="Pea isolate price (assumed)")
    fig.update_layout(xaxis_title="Process yield (kg concentrate / 100kg raw)", yaxis_title="₹ / kg concentrate", height=400)
    st.plotly_chart(fig, width="stretch")

    breakeven_yield = None
    for y in sorted(yields):
        c = _cost_per_kg(raw_price, y, energy_base, labour_base, capex_base)
        if c <= pea_price:
            breakeven_yield = y
            break
    if breakeven_yield:
        st.success(f"Break-even yield vs. pea isolate price: **{breakeven_yield}% ** (at current cost assumptions)")
    else:
        st.warning("No yield in the plotted range reaches the pea isolate break-even price at current cost assumptions.")

    st.subheader("Comparison vs. imported pea isolate")
    compare_df = pd.DataFrame({
        "Product": [f"{bp_name} concentrate (base)", "Imported pea isolate (assumed)"],
        "Price (₹/kg)": [scenarios["Base"], pea_price],
    })
    fig2 = go.Figure(go.Bar(x=compare_df["Product"], y=compare_df["Price (₹/kg)"], marker_color=["#1b5e20", "#b71c1c"]))
    fig2.update_layout(yaxis_title="₹ / kg", height=350)
    st.plotly_chart(fig2, width="stretch")

    cost_results = {
        "by_product": bp_name, "scenarios": {k: round(v, 1) for k, v in scenarios.items()},
        "pea_isolate_price_assumed": pea_price, "breakeven_yield_pct": breakeven_yield,
        "assumptions": {"raw_price": raw_price, "yield_base": yield_base, "energy_base": energy_base,
                        "labour_base": labour_base, "capex_base": capex_base},
    }
    st.session_state["cost_results"] = cost_results

    st.divider()
    _render_pdf_button(cost_results)
    return cost_results


def _render_pdf_button(cost_results):
    st.subheader("📄 Download plan as PDF")
    if st.button("Generate PDF"):
        try:
            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "ByProduct2Protein - Cost Summary", ln=True)
            pdf.set_font("Helvetica", size=11)
            pdf.ln(4)
            pdf.multi_cell(0, 7, f"By-product: {cost_results['by_product']}")
            for label, val in cost_results["scenarios"].items():
                pdf.multi_cell(0, 7, f"{label}: Rs {val}/kg (assumed)")
            pdf.multi_cell(0, 7, f"Imported pea isolate price (assumed): Rs {cost_results['pea_isolate_price_assumed']}/kg")
            be = cost_results["breakeven_yield_pct"]
            pdf.multi_cell(0, 7, f"Break-even yield: {be}%" if be else "Break-even yield: not reached in plotted range")
            pdf.ln(4)
            pdf.set_font("Helvetica", "I", 9)
            pdf.multi_cell(0, 6, "All cost figures are ASSUMED placeholders, not lab-validated. See Limitations.")
            pdf_bytes = bytes(pdf.output(dest="S"))
            st.download_button("Download PDF", data=pdf_bytes, file_name="byproduct2protein_plan.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"Could not generate PDF: {e}")
