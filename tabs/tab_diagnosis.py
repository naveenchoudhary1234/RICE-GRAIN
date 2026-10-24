import os
from datetime import date

import streamlit as st

from diagnosis import rank_causes, ffa_flag, recommend_route, ROUTES
from evidence_utils import badge, get_evidence_by_id, source_expander, metric_with_badge


def render(rb_evidence, byproducts):
    st.subheader("Step 1 — Lot details")
    c1, c2, c3 = st.columns(3)
    with c1:
        mill = st.text_input("Mill name/ID", key="diag_mill")
        variety = st.text_input("Rice variety (if known)", key="diag_variety")
    with c2:
        lot_date = st.date_input("Lot date", value=date.today(), key="diag_date")
        storage = st.selectbox("Storage history", ["Fresh (<48h)", "Cold-stored", "Ambient, days", "Ambient, weeks+", "Unknown"], key="diag_storage")
    with c3:
        bran_type = st.selectbox(
            "Bran type",
            ["coarse bran", "fine bran", "polish/meal", "mixed", "unknown"],
            index=4,
            key="diag_bran_type",
        )
        st.caption("Evidence: RB01 — batch composition varies by variety, milling and storage.")
        source_expander(get_evidence_by_id(rb_evidence, "RB01"))
    st.caption(
        "Composition (oil %, bran yield %) differs by stream (coarse/fine/polish) and must be "
        "measured on your own lot (PF26–PF29, IRRI Rice Knowledge Bank)."
    )

    st.markdown("**Optional lab values** (leave blank if not measured yet — shown as *Not measured yet*, not a fake number)")
    l1, l2, l3, l4, l5 = st.columns(5)
    with l1:
        protein_pct = st.number_input("Protein (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="diag_protein")
    with l2:
        moisture_pct = st.number_input("Moisture (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="diag_moisture")
    with l3:
        water_activity = st.number_input("Water activity (aw)", min_value=0.0, max_value=1.0, value=0.0, step=0.01, key="diag_aw")
    with l4:
        ffa_pct = st.number_input("Free fatty acids (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key="diag_ffa")
    with l5:
        peroxide_value = st.number_input("Peroxide value (meq O2/kg)", min_value=0.0, value=0.0, step=0.1, key="diag_pv")

    st.divider()
    st.subheader("Step 2 — Observed defect")
    defect = st.selectbox("What defect is observed?", ["Rancid or soapy", "Bitter", "Astringent", "Beany", "None / no defect"], key="diag_defect")

    st.divider()
    st.subheader("Step 3 — Candidate causes (ranked)")
    causes = rank_causes(defect)
    if not causes:
        st.info("No defect selected — no candidate causes to diagnose.")
    for rank, (ev_id, plausibility, test) in enumerate(causes, start=1):
        ev = get_evidence_by_id(rb_evidence, ev_id)
        with st.container(border=True):
            st.markdown(f"**#{rank}. {ev['parameter']}** &nbsp; {badge(ev['data_status'])}", unsafe_allow_html=True)
            st.write(plausibility)
            st.markdown(f"✅ **Confirming test:** {test}")
            source_expander(ev)

    st.divider()
    st.subheader("Step 4 — Route recommendation")
    route_notes = recommend_route(defect, ffa_pct if ffa_pct > 0 else None)
    rcol1, rcol2 = st.columns(2)
    for col, (route_name, route) in zip((rcol1, rcol2), ROUTES.items()):
        with col:
            st.markdown(f"**{route_name}**")
            st.caption(f"Evidence: {route['evidence_id']}")
            st.write(route["description"])
            st.markdown("**Pros:** " + "; ".join(route["pros"]))
            st.markdown("**Cons:** " + "; ".join(route["cons"]))
    if route_notes:
        for n in route_notes:
            st.warning(n)

    st.divider()
    st.subheader("Step 5 — Next best measurement")
    next_test = None
    if ffa_pct == 0.0 and defect in ("Rancid or soapy", "Bitter"):
        next_test = "Free fatty acids (FFA) / acid value test — not yet entered, and most diagnostic for this defect (RB03)."
    elif moisture_pct == 0.0 or water_activity == 0.0:
        next_test = "Moisture % and water activity (aw) — foundational for any stability/shelf-life decision (RB09)."
    elif defect in ("Bitter", "Astringent"):
        next_test = "Sensory panel + phenolic/phytate assay to confirm cause before treating (RB05, RB06, RB07)."
    else:
        next_test = "Sensory panel to establish a baseline before any treatment trial (RB07)."
    st.success(f"🔬 **Next best measurement:** {next_test}")

    st.divider()
    st.subheader("Free fatty acid screening (published thresholds)")
    if ffa_pct > 0:
        status, msg = ffa_flag(ffa_pct)
        metric_with_badge("Measured FFA", f"{ffa_pct:.1f}", "measured", suffix="%")
        if status == "unfit":
            st.error(msg)
        elif status == "desirable":
            st.success(msg)
        else:
            st.warning(msg)
    else:
        metric_with_badge("FFA", None, "needs_lab_test")
        st.caption("Thresholds (PF10, published): >10% unfit for food use; <5% desirable.")

    st.divider()
    st.subheader("🛡️ Safety and Regulatory panel")
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("**Safety / contaminants** " + badge("given"), unsafe_allow_html=True)
        source_expander(get_evidence_by_id(rb_evidence, "RB12"))
    with sc2:
        st.markdown("**Regulatory status (FSSAI)** " + badge("given"), unsafe_allow_html=True)
        source_expander(get_evidence_by_id(rb_evidence, "RB13"))

    diag_results = {
        "mill": mill, "variety": variety, "lot_date": str(lot_date), "storage": storage,
        "bran_type": bran_type,
        "protein_pct": protein_pct or None, "moisture_pct": moisture_pct or None,
        "water_activity": water_activity or None, "ffa_pct": ffa_pct or None,
        "peroxide_value": peroxide_value or None, "defect": defect,
        "causes": [{"id": c[0], "test": c[2]} for c in causes],
        "next_test": next_test,
    }
    st.session_state["diag_results"] = diag_results

    st.divider()
    _render_explain_section(diag_results, rb_evidence)
    return diag_results


def _render_explain_section(diag_results, rb_evidence):
    st.subheader("🧠 Explain these results")
    st.caption(
        "Powered by Groq — reads only this app's own evidence/results. It is instructed not to "
        "add numbers or claims, and to say what test is needed for missing data."
    )

    if st.button("Explain", key="diag_explain_btn"):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            st.error("No Groq API key configured. Set GROQ_API_KEY in the .env file.")
            return
        try:
            import requests
            import json as _json

            cost_results = st.session_state.get("cost_results")
            evidence_used = [
                {"id": c["id"], "parameter": next((e["parameter"] for e in rb_evidence if e["id"] == c["id"]), c["id"])}
                for c in diag_results["causes"]
            ]
            payload_data = {
                "diagnosis": diag_results,
                "evidence_used": evidence_used,
                "cost_results": cost_results,
            }
            model_name = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
            system_prompt = (
                "Use only the provided data. Do not add numbers or claims. "
                "If data is missing, say what test is needed."
            )
            with st.spinner("Asking Groq..."):
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": _json.dumps(payload_data, default=str)},
                        ],
                        "max_tokens": 500,
                    },
                    timeout=30,
                )
            if resp.status_code == 429:
                st.warning("Rate limit reached — please wait a few seconds and try again.")
                return
            if resp.status_code != 200:
                st.error(f"Groq API request error (status {resp.status_code}): {resp.text}")
                return
            explanation = resp.json()["choices"][0]["message"]["content"]
            st.success("Explanation generated")
            st.write(explanation)
            used_ids = ", ".join(c["id"] for c in diag_results["causes"]) or "none"
            st.caption(f"Source IDs referenced in this analysis: {used_ids}")
        except ImportError:
            st.error("The `requests` package is not installed. Run `pip install -r requirements.txt`.")
        except Exception as e:
            st.error(f"Could not get explanation: {e}")
