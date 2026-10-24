import streamlit as st

from evidence_utils import source_expander, paper_fact_expander, range_note, get_evidence_by_id


def render(rb_evidence, paper_facts):
    st.subheader("Rice bran evidence table (RB01–RB13)")
    st.caption("Each row is used directly by the Diagnosis tab's candidate-cause logic.")
    for ev in rb_evidence:
        source_expander(ev)

    st.divider()
    st.subheader("Paper facts")
    sources = paper_facts.get("sources", {})
    st.caption(paper_facts["citation"])
    if sources.get("irri"):
        st.caption(sources["irri"])

    facts_by_id = {f["id"]: f for f in paper_facts["facts"]}
    overlap_ids = {"PF02", "PF03", "PF26", "PF01", "PF29"}

    st.markdown("**Overlapping measurements (shown as ranges, never merged):**")
    if "PF02" in facts_by_id and "PF26" in facts_by_id:
        range_note(
            facts_by_id["PF02"], facts_by_id["PF26"],
            "Bran share of paddy/grain differs by mill, variety and milling degree; measure your lot.",
        )
    if "PF03" in facts_by_id and "PF26" in facts_by_id:
        range_note(
            facts_by_id["PF03"], facts_by_id["PF26"],
            "Bran share of paddy differs by mill, variety and milling degree; measure your lot.",
        )
    if "PF01" in facts_by_id and "PF29" in facts_by_id:
        range_note(
            facts_by_id["PF01"], facts_by_id["PF29"],
            "Oil share differs by mill, variety and milling degree; measure your lot.",
        )

    st.markdown("**All facts:**")
    for fact in paper_facts["facts"]:
        if fact["id"] in overlap_ids:
            continue
        paper_fact_expander(fact, paper_facts["citation"], sources)

    with st.expander("Overlapping facts (also shown above as ranges)"):
        for fid in ["PF01", "PF02", "PF03", "PF26", "PF29"]:
            if fid in facts_by_id:
                paper_fact_expander(facts_by_id[fid], paper_facts["citation"], sources)

    st.divider()
    st.subheader("References")
    st.markdown(f"- {paper_facts['citation']}")
    if sources.get("irri"):
        st.markdown(f"- {sources['irri']}")
    if rb_evidence:
        rb12 = get_evidence_by_id(rb_evidence, "RB12")
        if rb12:
            st.markdown(f"- RB evidence sources: see individual expanders above (e.g. {rb12['source_url']})")
