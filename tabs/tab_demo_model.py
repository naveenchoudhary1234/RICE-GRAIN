import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import xgboost as xgb
from sklearn.preprocessing import OneHotEncoder

DATA_DIR = "data"


@st.cache_data
def _load_literature():
    return pd.read_csv(os.path.join(DATA_DIR, "literature_data.csv"))


@st.cache_resource
def _train_models(df: pd.DataFrame):
    feature_cols_cat = ["by_product", "treatment"]
    feature_cols_num = ["temp", "time", "enzyme_dose", "protein_before", "bitterness_before"]

    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    cat_encoded = encoder.fit_transform(df[feature_cols_cat])
    X = np.hstack([cat_encoded, df[feature_cols_num].values])

    y_protein = df["protein_after"].values
    y_bitter = df["bitterness_after"].values

    model_protein = xgb.XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.08, random_state=42)
    model_protein.fit(X, y_protein)
    model_bitter = xgb.XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.08, random_state=42)
    model_bitter.fit(X, y_bitter)

    return encoder, model_protein, model_bitter, feature_cols_cat, feature_cols_num


def _predict(encoder, model_protein, model_bitter, cat_cols, num_cols, row):
    cat_df = pd.DataFrame([{c: row[c] for c in cat_cols}])
    cat_encoded = encoder.transform(cat_df)
    num_vals = np.array([[row[c] for c in num_cols]])
    X = np.hstack([cat_encoded, num_vals])
    return float(model_protein.predict(X)[0]), float(model_bitter.predict(X)[0])


def render(byproducts, treatments_db):
    st.error(
        "🚫 **SYNTHETIC DATA — NOT FOR DECISIONS.** This tab's training data "
        "(data/literature_data.csv) is machine-generated with a simple heuristic formula, "
        "not real experimental results. It does NOT feed the Diagnosis tab's recommendations. "
        "Use it only to see how an XGBoost model *could* be wired up once real lot-level data exists."
    )

    literature_df = _load_literature()
    encoder, model_protein, model_bitter, cat_cols, num_cols = _train_models(literature_df)

    bp_names = [k for k in byproducts if not k.startswith("_")]
    selected_bp = st.selectbox("By-product", bp_names, key="demo_bp")
    bp_info = byproducts[selected_bp]

    all_treatments = sorted({
        o["treatment"]
        for key, opts in treatments_db.items()
        if not key.startswith("_")
        for o in opts
    })
    selected_treatment = st.selectbox("Treatment", all_treatments, key="demo_treatment")
    temp = st.slider("Temperature (°C)", 20, 140, 80, key="demo_temp")
    time_min = st.slider("Time (min)", 5, 200, 60, key="demo_time")
    enzyme_dose = st.slider("Enzyme dose (% w/w)", 0.0, 3.0, 0.5, step=0.1, key="demo_enzyme")
    protein_before = st.number_input("Protein before (%)", value=float(bp_info["protein_pct"]), key="demo_protein_before")
    bitterness_before = st.slider("Bitterness before (0-10)", 0.0, 10.0, 7.0, step=0.1, key="demo_bitter_before")

    row = {
        "by_product": selected_bp, "treatment": selected_treatment, "temp": temp, "time": time_min,
        "enzyme_dose": enzyme_dose, "protein_before": protein_before, "bitterness_before": bitterness_before,
    }
    protein_after, bitterness_after = _predict(encoder, model_protein, model_bitter, cat_cols, num_cols, row)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Predicted protein after (synthetic)", f"{protein_after:.1f}%", delta=f"{protein_after - protein_before:+.1f} pts")
    with c2:
        st.metric("Predicted bitterness after (synthetic)", f"{bitterness_after:.1f}/10", delta=f"{bitterness_after - bitterness_before:+.1f}", delta_color="inverse")

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Before", x=["Protein %", "Bitterness"], y=[protein_before, bitterness_before], marker_color="#90a4ae"))
    fig.add_trace(go.Bar(name="After (synthetic prediction)", x=["Protein %", "Bitterness"], y=[protein_after, bitterness_after], marker_color="#b71c1c"))
    fig.update_layout(barmode="group", height=380)
    st.plotly_chart(fig, width="stretch")
    st.caption("Red = synthetic model output. Replace data/literature_data.csv with real trial data before trusting these numbers.")
