# JKM PsyCounsel SEM Impact Intelligence

Revised Streamlit demo aligned to TOR for Kajian Penilaian Keberkesanan Perkhidmatan Psikologi dan Kaunseling JKM.

## Main revisions
- Uses SEM as the main quantitative analysis dashboard.
- Uses TOR-aligned sample assumptions: 600 quantitative respondents and 85 qualitative informants.
- Replaces DASS-focused KPI with WHODAS, Wellbeing/WHOQOL proxy, WAI Alliance, CSQ-8, and PCL-5 selective trauma outcome.
- Adds Measurement Model, Structural Model, HTMT, R², CMO, RE-AIM, policy actions and scenario simulator.
- Simulation data is clearly labelled as demonstration only.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data upload
Upload an Excel file with sheets:
- `questionnaire`
- `interview`

The app can also generate a TOR-aligned Excel template from the Data & Template tab.
