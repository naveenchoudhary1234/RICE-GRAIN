"""
Mass balance calculator (Section H).

Pure arithmetic on user-entered quantities. No defaults are fabricated —
every stream starts empty/zero and must be entered by the user. Shows a
partial balance and lists missing streams when inputs are incomplete.
"""
import streamlit as st

from evidence_utils import badge


def render():
    st.subheader("⚖️ Mass balance calculator")
    st.caption(
        "All values below are "
        + badge("measured")
        + " — entered by you for your own lot. Nothing is pre-filled. "
        "Basis: per 100 kg of wet feedstock, unless you state otherwise.",
        unsafe_allow_html=True,
    )

    st.markdown("#### Inputs — feedstock")
    c1, c2, c3 = st.columns(3)
    with c1:
        wet_feed = st.number_input("Wet feed mass (kg)", min_value=0.0, value=0.0, step=1.0)
        moisture_pct = st.number_input("Feed moisture (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
    with c2:
        protein_pct = st.number_input("Protein content of feed (% dry basis)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
        oil_pct = st.number_input("Oil content of feed (% dry basis)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    with c3:
        fibre_pct = st.number_input("Fibre content of feed (% dry basis)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
        water_added = st.number_input("Process water added (kg)", min_value=0.0, value=0.0, step=1.0)

    st.markdown("#### Outputs — recovered streams")
    o1, o2, o3 = st.columns(3)
    with o1:
        protein_fraction_mass = st.number_input("Protein-rich fraction, recovered mass (kg)", min_value=0.0, value=0.0, step=0.1)
        protein_fraction_protein_pct = st.number_input("Protein content of that fraction (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
    with o2:
        oil_recovered = st.number_input("Oil recovered (kg)", min_value=0.0, value=0.0, step=0.1)
        other_coproducts = st.number_input("Other co-products, recovered mass (kg)", min_value=0.0, value=0.0, step=0.1)
    with o3:
        water_out = st.number_input("Water/effluent output (kg)", min_value=0.0, value=0.0, step=1.0)
        solid_waste = st.number_input("Solid waste / discard (kg)", min_value=0.0, value=0.0, step=0.1)

    missing = []
    if wet_feed <= 0:
        missing.append("Wet feed mass")
    if moisture_pct <= 0:
        missing.append("Feed moisture %")
    if protein_pct <= 0:
        missing.append("Feed protein %")

    dry_matter = wet_feed * (1 - moisture_pct / 100.0) if wet_feed and moisture_pct else None
    protein_in = dry_matter * (protein_pct / 100.0) if dry_matter is not None and protein_pct else None
    protein_recovered = protein_fraction_mass * (protein_fraction_protein_pct / 100.0) if protein_fraction_mass and protein_fraction_protein_pct else None

    st.divider()
    st.markdown("#### Calculated basis")
    b1, b2, b3 = st.columns(3)
    with b1:
        st.metric("Dry matter (kg)", f"{dry_matter:.1f}" if dry_matter is not None else "Needs data")
    with b2:
        st.metric("Protein entering process (kg)", f"{protein_in:.2f}" if protein_in is not None else "Needs data")
    with b3:
        st.metric("Protein recovered (kg)", f"{protein_recovered:.2f}" if protein_recovered is not None else "Needs data")

    if protein_in and protein_recovered is not None:
        recovery_pct = (protein_recovered / protein_in) * 100.0
        st.success(f"Protein recovery: **{recovery_pct:.1f}%** of protein entering the process (calculated from your inputs, not assumed).")
        protein_remaining = protein_in - protein_recovered
        st.caption(f"Protein remaining in other fractions (by difference): {protein_remaining:.2f} kg")
    else:
        st.info("Protein recovery % needs both feed protein and recovered-fraction protein entered above.")

    st.markdown("#### Mass balance reconciliation")
    total_in = (wet_feed or 0) + (water_added or 0)
    total_out = sum(x or 0 for x in [protein_fraction_mass, oil_recovered, other_coproducts, water_out, solid_waste])
    if total_in > 0:
        unaccounted = total_in - total_out
        st.write(f"Total input mass: **{total_in:.1f} kg** (wet feed + process water)")
        st.write(f"Total measured output mass: **{total_out:.1f} kg** (sum of all output streams above)")
        if abs(unaccounted) < 0.01:
            st.success("Balance closes: input mass = output mass.")
        else:
            st.warning(
                f"Unaccounted mass: **{unaccounted:.1f} kg** ({abs(unaccounted) / total_in * 100:.1f}% of input). "
                "This is not assumed to be product — it reflects unmeasured losses, moisture evaporation, "
                "or streams not yet entered."
            )
    else:
        st.info("Enter wet feed mass to see the overall balance.")

    if missing:
        st.error("Missing inputs needed for a full balance: " + ", ".join(missing))

    with st.expander("How this is calculated"):
        st.markdown(
            "- **Dry matter** = wet feed × (1 − moisture%)\n"
            "- **Protein entering process** = dry matter × feed protein%\n"
            "- **Protein recovered** = recovered-fraction mass × its protein%\n"
            "- **Protein recovery %** = protein recovered ÷ protein entering × 100\n"
            "- **Mass balance** = (wet feed + water added) vs. (sum of all recovered/output streams)\n"
            "- No percentage is inferred from another; every number above comes directly from what you entered."
        )

    return {
        "wet_feed_kg": wet_feed or None,
        "dry_matter_kg": dry_matter,
        "protein_in_kg": protein_in,
        "protein_recovered_kg": protein_recovered,
        "missing_inputs": missing,
    }
