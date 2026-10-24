"""
Evidence loading + badge rendering helpers for ByProduct2Protein.

Badge vocabulary (must be used on every number shown in the app):
  published        - from a published paper/review (e.g. Tan et al. 2023)
  measured         - entered by the user from their own lab result
  assumed          - a default/benchmark the user can edit, not from a lab test
  synthetic        - generated placeholder data (demo model only)
  needs_lab_test   - no source exists yet; value must not be shown as a number
"""
import json
import os

import streamlit as st

DATA_DIR = "data"

BADGE_STYLES = {
    "published": ("📘 Published", "#1b5e20", "#e8f5e9"),
    "given": ("📘 Published", "#1b5e20", "#e8f5e9"),
    "measured": ("🧪 Measured", "#0d47a1", "#e3f2fd"),
    "assumed": ("⚠️ Assumed", "#e65100", "#fff3e0"),
    "synthetic": ("🧬 Synthetic", "#b71c1c", "#ffebee"),
    "needs_lab_test": ("🔬 Not measured yet", "#424242", "#eeeeee"),
}


def badge(status: str) -> str:
    """Return an HTML span styled as a badge for the given data_status."""
    label, fg, bg = BADGE_STYLES.get(status, (status, "#424242", "#eeeeee"))
    return (
        f'<span style="background-color:{bg};color:{fg};padding:2px 8px;'
        f'border-radius:10px;font-size:0.75em;font-weight:600;white-space:nowrap;">'
        f"{label}</span>"
    )


def metric_with_badge(label: str, value, status: str, suffix: str = ""):
    """Render a metric-like block that always carries a data-status badge.

    If status is 'needs_lab_test' (or value is None), show 'Not measured yet'
    instead of a number, per the no-silent-number rule.
    """
    if status == "needs_lab_test" or value is None:
        st.markdown(
            f"**{label}**<br>Not measured yet {badge('needs_lab_test')}",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"**{label}**<br><span style='font-size:1.4em;font-weight:700;'>{value}{suffix}</span> "
            f"{badge(status)}",
            unsafe_allow_html=True,
        )


LEGEND_ORDER = ["published", "measured", "assumed", "synthetic", "needs_lab_test"]


def badge_legend():
    """Render the legend of all badge types, meant for the top of the app."""
    cols = st.columns(len(LEGEND_ORDER))
    for col, status in zip(cols, LEGEND_ORDER):
        with col:
            st.markdown(badge(status), unsafe_allow_html=True)


@st.cache_data
def load_json(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def get_evidence_by_id(evidence_list, evidence_id):
    for item in evidence_list:
        if item["id"] == evidence_id:
            return item
    return None


def source_expander(evidence_item: dict):
    """Render an expander with full source details for one evidence row."""
    with st.expander(f"Source: {evidence_item['id']} — {evidence_item['parameter']}"):
        st.markdown(f"**Evidence:** {evidence_item['evidence']}")
        st.markdown(f"**Why it matters:** {evidence_item['why_it_matters']}")
        st.markdown(f"**Measurement/intervention:** {evidence_item['intervention_or_measurement']}")
        st.markdown(f"**Data status:** {badge(evidence_item['data_status'])}", unsafe_allow_html=True)
        st.markdown(f"**Source:** {evidence_item['source_url']}")


def paper_fact_expander(fact_item: dict, citation: str, sources: dict = None):
    """Render an expander for one paper fact.

    If `sources` is provided and the fact has a `source` key, the citation
    shown is looked up from `sources[fact_item['source']]` instead of the
    single default `citation` (used when facts come from multiple sources).
    """
    fact_citation = citation
    if sources and fact_item.get("source"):
        fact_citation = sources.get(fact_item["source"], citation)
    with st.expander(f"{fact_item['id']} ({fact_item['section']})"):
        st.markdown(fact_item["fact"])
        if fact_item.get("note"):
            st.caption(f"Note: {fact_item['note']}")
        st.markdown(badge(fact_item["data_status"]), unsafe_allow_html=True)
        st.caption(fact_citation)


def range_note(fact_a: dict, fact_b: dict, note: str):
    """Render two overlapping facts side by side as a range, never merged."""
    st.markdown(
        f"**{fact_a['id']}:** {fact_a['fact']} {badge(fact_a['data_status'])}",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"**{fact_b['id']}:** {fact_b['fact']} {badge(fact_b['data_status'])}",
        unsafe_allow_html=True,
    )
    st.caption(f"⚠️ {note}")
