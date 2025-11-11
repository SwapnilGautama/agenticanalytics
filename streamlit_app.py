
import streamlit as st
import pandas as pd
from app.orchestrator import run_pipeline
from app.tools.data_loader import load_frames
from app.tools.kpi_wrappers import rev_cost

st.set_page_config(page_title="HALO — Agentic", layout="wide")
st.title("HALO — Agentic Analytics (GitHub + Streamlit)")

tabs = st.tabs(["Ask HALO", "Download Aggregates", "Dashboard: Margin by BU"])

with tabs[0]:
    query = st.text_input("Ask HALO", placeholder="e.g., BU-wise revenue and cost (USD) for last month")
    go = st.button("Run", key="ask_run")
    if go and query.strip():
        with st.spinner("Agents at work..."):
            story = run_pipeline({
                "goal": query,
                "context": {"user_id": "swap"},
                "constraints": {"privacy": "no_raw_pii"},
                "history": st.session_state.get("history", [])
            })
        st.markdown(story["text"])
        arts = story.get("artifacts", {})
        if "table" in arts:
            st.subheader("Table")
            st.dataframe(arts["table"])
        if "chart" in arts:
            st.subheader("Chart")
            st.altair_chart(arts["chart"], use_container_width=True)
        st.session_state.setdefault("history", []).append({"q": query, "a": story["text"]})

with tabs[1]:
    st.subheader("Download Aggregates")
    by = st.selectbox("Group by", ["Segment", "BU", "DU"], index=0)
    include_margin = st.checkbox("Include Margin (USD and %)", value=True)
    if st.button("Generate Aggregates", key="gen_agg"):
        with st.spinner("Aggregating from Excel..."):
            ctx = load_frames()
            result = rev_cost.run(ctx, by=by, include_margin=include_margin)
            df = result["table"]
            st.dataframe(df)
            # Downloads
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", data=csv_bytes, file_name=f"aggregates_{by.lower()}.csv", mime="text/csv")
            # Excel
            import io
            bio = io.BytesIO()
            with pd.ExcelWriter(bio, engine="openpyxl") as xw:
                df.to_excel(xw, index=False, sheet_name="data")
            st.download_button("Download Excel", data=bio.getvalue(), file_name=f"aggregates_{by.lower()}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with tabs[2]:
    st.subheader("Dashboard — Margin by BU")
    st.caption("Revenue, Cost, Margin using 'Amount in USD' from LnTPnL.xlsx")
    if st.button("Build Dashboard", key="dash_btn"):
        with st.spinner("Building charts..."):
            ctx = load_frames()
            result = rev_cost.run(ctx, by="BU", include_margin=True)
            df = result["table"].copy()

            # Simple KPI tiles
            total_rev = float(df["Revenue"].sum()) if "Revenue" in df.columns else 0.0
            total_cost = float(df["Cost"].sum()) if "Cost" in df.columns else 0.0
            total_margin = float(df["Margin (USD)"].sum()) if "Margin (USD)" in df.columns else (total_rev - total_cost)

            k1, k2, k3 = st.columns(3)
            k1.metric("Total Revenue (USD)", f"{total_rev:,.0f}")
            k2.metric("Total Cost (USD)", f"{total_cost:,.0f}")
            k3.metric("Total Margin (USD)", f"{total_margin:,.0f}")

            import altair as alt
            # Bar chart: Margin by BU
            if "Margin (USD)" in df.columns:
                c1 = (alt.Chart(df)
                       .mark_bar()
                       .encode(x=alt.X("BU:N", sort="-y"), y="Margin (USD):Q", tooltip=list(df.columns))
                       .properties(height=340))
                st.altair_chart(c1, use_container_width=True)

            # Table with sorting
            st.dataframe(df.sort_values("Margin (USD)", ascending=False) if "Margin (USD)" in df.columns else df)
