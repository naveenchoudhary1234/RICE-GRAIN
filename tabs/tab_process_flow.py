"""
Process flow diagram (Section E).

Built only from the Route A / Route B step sequences already documented in
RB10 / RB11 (data/rice_bran_evidence.json via diagnosis.ROUTES). This is a
candidate process structure, not a validated/optimized flowsheet.
"""
import plotly.graph_objects as go
import streamlit as st

from diagnosis import ROUTES
from evidence_utils import badge, get_evidence_by_id, source_expander

# step -> (purpose, inputs, outputs, equipment_hint, quality_risk)
STEP_DETAILS = {
    "Prompt collection": (
        "Move bran out of the mill quickly before lipase/lipoxygenase activity progresses.",
        "Fresh bran from mill", "Bran lot ready for stabilization",
        "Collection bins, conveyors", "Delay here raises FFA before processing even starts.",
    ),
    "Validated stabilization": (
        "Deactivate lipase/lipoxygenase enzymes to halt rancidity.",
        "Fresh bran", "Stabilized bran",
        "Extrusion, dry/steam heat, or infrared stabilizer (method must be validated, not assumed)",
        "Under-stabilization leaves residual enzyme activity; over-heating can denature protein functionality.",
    ),
    "Cooling": (
        "Bring stabilized bran to safe storage/handling temperature.",
        "Hot stabilized bran", "Cooled bran",
        "Cooling conveyor/bin", "Needs data — cooling rate/target not specified in evidence.",
    ),
    "Milling/sieving": (
        "Achieve target particle size and remove hull fragments.",
        "Cooled bran", "Sized bran fraction",
        "Mill, sieve/sifter", "Hull fragments raise ash (PF27) — sieving cut-point affects composition.",
    ),
    "Barrier packaging": (
        "Protect from moisture/oxygen pickup during storage and transport.",
        "Sized bran", "Packaged stabilized-bran ingredient",
        "Barrier-film packaging line", "Needs data — packaging spec not in evidence.",
    ),
    "Shelf-life study": (
        "Confirm the stabilized product remains stable over its intended shelf life.",
        "Packaged product + time", "Shelf-life data",
        "Storage chamber, periodic FFA/peroxide/sensory testing", "No shelf-life value can be assumed without this study.",
    ),
    "Characterize": (
        "Establish composition of the specific lot before choosing extraction parameters.",
        "Raw/stabilized bran", "Lot composition data",
        "Lab: protein, oil, fibre, moisture assays", "Extraction parameters must come from a specific study matched to this composition.",
    ),
    "Optional defatting": (
        "Remove oil if it interferes with extraction or target product is a defatted fraction.",
        "Characterized bran", "Defatted bran + oil fraction",
        "Mechanical press or solvent/CO2 extraction", "Needs data — method and yield not specified in evidence.",
    ),
    "Extraction/fractionation": (
        "Solubilize/separate protein from the bran matrix.",
        "Defatted or whole bran", "Protein-containing liquid + residual solids",
        "Mixing tank, pH control (alkaline/enzyme/other per chosen study)", "Method choice affects protein recovery, purity and functionality — set from a specific study, not assumed.",
    ),
    "Solid-liquid separation": (
        "Separate liquid extract from insoluble solids.",
        "Extraction slurry", "Protein-rich liquid + solid residue",
        "Centrifuge or filter press", "Needs data — separation efficiency not specified in evidence.",
    ),
    "Recovery": (
        "Precipitate/concentrate protein from the liquid fraction.",
        "Protein-rich liquid", "Wet protein concentrate/isolate",
        "Isoelectric precipitation tank or membrane system", "Yield and purity must come from a pilot trial, not assumed (RB11).",
    ),
    "Drying": (
        "Reduce moisture of the recovered fraction for storage and handling.",
        "Wet protein concentrate", "Dried protein ingredient",
        "Spray dryer or tray dryer", "Drying conditions can affect solubility/functionality (RB08) — needs validation for target use.",
    ),
}


def _step_list(description: str):
    return [s.strip() for s in description.split(">")]


def render(rb_evidence):
    st.subheader("🔀 Process flow diagram")
    st.caption(
        "Candidate process structure built only from the Route A / Route B step sequences in "
        "RB10 / RB11. Not a claim that every step is necessary or that the sequence is validated — "
        "see Known Gaps."
    )

    route_name = st.radio("Select route to view", list(ROUTES.keys()), key="flow_route")
    route = ROUTES[route_name]
    st.markdown(f"**Evidence:** {route['evidence_id']}")
    source_expander(get_evidence_by_id(rb_evidence, route["evidence_id"]))

    steps = _step_list(route["description"])

    fig = go.Figure()
    x_positions = list(range(len(steps)))
    fig.add_trace(go.Scatter(
        x=x_positions, y=[0] * len(steps), mode="markers+lines+text",
        marker=dict(size=28, color="#1b5e20"),
        line=dict(color="#1b5e20", width=2),
        text=steps, textposition="top center",
    ))
    fig.update_layout(
        height=220, showlegend=False,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, width="stretch")

    st.markdown("#### Step details")
    for step in steps:
        detail = STEP_DETAILS.get(step)
        with st.container(border=True):
            st.markdown(f"**{step}**")
            if detail:
                purpose, inputs, outputs, equip, risk = detail
                st.write(f"**Purpose:** {purpose}")
                c1, c2 = st.columns(2)
                with c1:
                    st.caption(f"Input: {inputs}")
                with c2:
                    st.caption(f"Output: {outputs}")
                st.markdown(f"**Possible equipment:** {equip}")
                st.warning(f"**Quality risk / missing parameter:** {risk}")
            else:
                st.info("Needs data — step not yet detailed in evidence files.")
            st.caption(f"Supporting evidence: {route['evidence_id']} " + badge("given"), unsafe_allow_html=True)

    return {"route": route_name, "steps": steps}
