
# HALO — Agentic (GitHub + Streamlit only)

This codepack converts HALO into a lightweight agentic system that runs entirely on Streamlit + your GitHub repo.
It is pre-wired for your uploaded schemas:

- **LnTPnL.xlsx** → cost & revenue by project. Uses **Amount in USD** for all financial aggregations.
  Expected fields (subset): `Segment`, `BU`, `DU`, `Type` (Cost/Revenue), `Amount in USD`, `Month` (optional).
- **LNTData.xlsx** → utilization hours. Aggregates **Billable** and **Productive** hours by Segment/BU/DU.
  Expected fields (subset): `Segment`, `BU`, `DU`, `TotalBillableHours`, `ProductiveHours`, `NetAvailableHours`, `Month` (optional).
- **KPInOtherDetails.xlsx** → optional lookups (not required for v1).

## How to run (Streamlit Cloud or Codespaces)
1. Put `LnTPnL.xlsx`, `LNTData.xlsx`, `KPInOtherDetails.xlsx` in repo root or a `data/` folder.
2. `pip install -r requirements.txt`
3. `streamlit run streamlit_app.py`
4. Ask:
   - "Revenue and cost by Segment last month"
   - "Show DU-level billable vs productive hours"
   - "BU-wise margin with Revenue and Cost (USD)"
   
## Outputs
- Agent orchestrates: Router → KPI Agent → Narrative → Compliance → Return.
- Aggregates at **Segment**, **BU**, **DU** levels.
- Uses **Amount in USD** for revenue & cost. Computes **Margin (USD)** and optional **Margin %**.
- Hours tables: Billable & Productive (and NetAvailableHours if present).

## Notes
- Excel loading can be heavy. Use the `ROW_LIMIT` and `COLUMNS` filters in `data_loader.py` for quick tests.
- For large data, consider converting xlsx to parquet in Git LFS for performance.


---

## Create a new GitHub repo named `agenticanalytics` and push

```bash
# 1) Create repo on GitHub (UI): New → Repository name: agenticanalytics → Public/Private → Create
# 2) Locally (or in Codespaces):
git init
git remote add origin https://github.com/<your-org-or-username>/agenticanalytics.git
git branch -M main
git add .
git commit -m "init: HALO Agentic (Streamlit + GitHub only)"
git push -u origin main
```

### Deploy on Streamlit Cloud
1. Click "New app" → point to `agenticanalytics` repo.
2. Main file: `streamlit_app.py`
3. Python version: 3.11+ (recommended), add the `requirements.txt` path.
4. Set Secrets if you plan to write back to GitHub (not required for read-only).

### Data placement
- Put `LnTPnL.xlsx` and `LNTData.xlsx` in the repo root or `data/` folder.
- Large files → consider Git LFS.

### Usage highlights
- **Ask HALO**: freeform questions (router → KPI tools).
- **Download Aggregates**: export Segment/BU/DU tables as CSV/Excel.
- **Dashboard**: one-click Margin by BU with KPIs and chart.
