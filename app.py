import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="JKM Psycho-Counselling Impact Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:radial-gradient(circle at top left,#11345F 0%,#09182B 42%,#020617 100%);color:#F8FAFC;}
.block-container{padding-top:1.1rem;max-width:1580px;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#06101E,#0B1628);border-right:1px solid rgba(197,160,23,.28)}
h1,h2,h3{color:#fff!important;letter-spacing:-.03em;}
.hero{padding:34px;border-radius:32px;background:linear-gradient(135deg,rgba(197,160,23,.24),rgba(16,185,129,.11)),linear-gradient(135deg,#06142B,#10213C 60%,#163E62);border:1px solid rgba(253,230,138,.35);box-shadow:0 28px 90px rgba(0,0,0,.42);margin-bottom:18px;}
.badge{display:inline-block;padding:7px 13px;border-radius:999px;background:rgba(197,160,23,.18);border:1px solid rgba(253,230,138,.38);color:#FDE68A;font-weight:900;font-size:12px;letter-spacing:.08em;}
.hero-title{font-size:42px;line-height:1.07;font-weight:900;margin-top:12px;}
.gold{background:linear-gradient(90deg,#FDE68A,#C5A017,#FFF7C2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-subtitle{color:#CBD5E1;font-size:16px;max-width:1160px;margin-top:10px;}
.card{padding:22px;border-radius:25px;background:rgba(15,23,42,.76);border:1px solid rgba(148,163,184,.23);box-shadow:0 20px 58px rgba(0,0,0,.28);margin-bottom:18px;}
.card2{padding:18px;border-radius:22px;background:rgba(30,41,59,.58);border:1px solid rgba(148,163,184,.18);margin-bottom:15px;}
.kpi{padding:20px;border-radius:23px;background:linear-gradient(180deg,rgba(15,23,42,.97),rgba(15,23,42,.72));border:1px solid rgba(148,163,184,.23);min-height:130px;box-shadow:0 14px 36px rgba(0,0,0,.22)}
.klabel{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#94A3B8;font-weight:800;}
.kvalue{font-size:33px;color:white;font-weight:900;margin-top:8px;}
.knote{font-size:13px;color:#CBD5E1;margin-top:4px;}
.stTabs [data-baseweb="tab"]{background:rgba(15,23,42,.86);border:1px solid rgba(148,163,184,.22);border-radius:999px;color:#CBD5E1;padding:10px 16px;margin:3px;}
.stTabs [aria-selected="true"]{background:linear-gradient(90deg,#C5A017,#FDE68A)!important;color:#0F172A!important;font-weight:900;}
.small{font-size:13px;color:#CBD5E1;}
.ok{color:#86EFAC;font-weight:900}.warn{color:#FDE68A;font-weight:900}.bad{color:#FDA4AF;font-weight:900}
hr{border-color:rgba(148,163,184,.20)!important;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

ZONES = {
    "Tengah": ["Kuala Lumpur", "Selangor"],
    "Utara": ["Pulau Pinang", "Kedah"],
    "Selatan": ["Johor", "Melaka"],
    "Timur": ["Kelantan", "Pahang"],
    "Sabah": ["Sabah"],
    "Sarawak": ["Sarawak"],
}
STATE_EFFECT = {
    "Kuala Lumpur": 4.5, "Selangor": 3.2, "Pulau Pinang": 2.4, "Kedah": 1.2,
    "Johor": 2.6, "Melaka": 1.9, "Kelantan": -1.3, "Pahang": -0.7,
    "Sabah": -2.3, "Sarawak": -1.7,
}
RESP_GROUPS = ["Klien", "PPsi", "PPPsi", "Warga Jabatan"]
INTERVENTIONS = ["Kaunseling Individu", "Kaunseling Kelompok", "Intervensi Krisis", "Sokongan Sosial", "Psikopendidikan", "Rujukan Lanjut"]


# =========================================================
# TOR MAPPING: Konstruk (K), Sumber Data (S), Instrumen, Teori
# =========================================================

K_SOURCE_MAP = pd.DataFrame([
    [
        "K1",
        "Outcome Klien / Keberkesanan",
        "S1 + S4",
        "Manual Instrumen Teras Hasil Klien JKM + CASRS-JKM + data pentadbiran",
        "WHODAS T1/T2/T3; WHOQOL/Wellbeing T1/T2/T3; WAI-SR; CSQ-8; PCL-5 selektif; rekod susulan; status kes",
        "Realist Evaluation; RE-AIM Effectiveness; Bronfenbrenner",
        "Client Outcome Index; WHODAS Improvement; Wellbeing Improvement; PCL-5 Reduction; Client Satisfaction"
    ],
    [
        "K2",
        "Mekanisme Perkhidmatan",
        "S1 + S2",
        "CASRS-JKM + IPKJ-JKM Instrumen A",
        "Akses fizikal; akses prosedural; komunikasi; responsif relasi; aliansi terapeutik; etika; susulan; kesesuaian modaliti intervensi",
        "Realist Evaluation (CMO); WHO Person-Centred Approach",
        "Service Mechanism Score; Access Responsiveness; Therapeutic Alliance"
    ],
    [
        "K3",
        "Kualiti Penyampaian",
        "S1 + S2 + S3",
        "CASRS-JKM + IPKJ-JKM Instrumen A/B + soal selidik warga JKM",
        "SOP; kompetensi; etika; kerahsiaan; kualiti intervensi; komunikasi; koordinasi rujukan; profesionalisme pegawai",
        "Donabedian Process; WHO Person-Centred Approach",
        "Service Quality Score; SOP Compliance; Referral Coordination; Communication Quality"
    ],
    [
        "K4",
        "Kapasiti Organisasi",
        "S2 + S3 + S4",
        "IPKJ-JKM Instrumen B + soal selidik warga JKM + data pentadbiran",
        "Perjawatan; beban kes; kemudahan; latihan; peruntukan; sistem rekod; burnout; nisbah pegawai-klien; tempoh menunggu",
        "Donabedian Structure; RE-AIM Implementation/Maintenance",
        "Organizational Capacity Index; Workload Index; Waiting Time; Follow-up Readiness"
    ],
    [
        "K5",
        "Penambahbaikan & Inovasi",
        "S1 + S2 + S3 + S4",
        "Soalan terbuka CASRS/IPKJ + temu bual + data pentadbiran",
        "Cadangan klien; cadangan pegawai; isu sistemik; peluang digital; tele-kaunseling; SOP digital; keperluan latihan; keperluan sumber",
        "RE-AIM Maintenance; Realist Evaluation; CMO",
        "Policy Recommendation Matrix; Priority Action Plan; Scenario Simulator"
    ],
], columns=[
    "K",
    "Konstruk",
    "Sumber Data",
    "Instrumen / Questionnaire",
    "Item / Domain Digunakan",
    "Theory / Framework",
    "Result Dalam Sistem"
])


S_SOURCE_MAP = pd.DataFrame([
    [
        "S1",
        "Klien",
        "CASRS-JKM + Manual Instrumen Teras Hasil Klien JKM",
        "≈450 kuantitatif + ≈45 kualitatif",
        "K1, K2, K3, K5",
        "Client Satisfaction; Client Outcome; Access; Responsiveness; Therapeutic Alliance; T1-T2-T3 Improvement"
    ],
    [
        "S2",
        "PPsi + PPPsi",
        "IPKJ-JKM Instrumen A & B",
        "≈75 kuantitatif + ≈25 kualitatif",
        "K2, K3, K4, K5",
        "Intervention Success; SOP; Competency; Workload; Training; Burnout; Service Barrier"
    ],
    [
        "S3",
        "Warga JKM",
        "Soal selidik sokongan sistem + temu bual",
        "≈75 kuantitatif + ≈15 kualitatif",
        "K3, K4, K5",
        "Organisational Support; Referral Coordination; Internal Collaboration; System Readiness"
    ],
    [
        "S4",
        "Data Pentadbiran JKM",
        "Rekod kes, statistik intervensi, laporan tahunan, data sumber manusia, rekod susulan",
        "Bukan responden",
        "K1, K4, K5",
        "Reach; Intervention Trend; Officer-Client Ratio; Case Load; Follow-up Rate; Waiting Time"
    ],
], columns=[
    "S",
    "Sumber",
    "Instrumen / Data",
    "Anggaran Sampel",
    "Konstruk Disokong",
    "Output Dashboard"
])


RESULT_SOURCE_MAP = pd.DataFrame([
    [
        "Client Satisfaction Index",
        "CASRS-JKM + CSQ-8",
        "S1",
        "K1 + K2",
        "WHO Person-Centred; Realist Evaluation",
        "Dikira daripada skor kepuasan klien, pengalaman perkhidmatan, komunikasi, layanan, akses dan CSQ-8. Skor ditukar kepada indeks 0-100 dan dibandingkan mengikut negeri, zon serta kategori klien."
    ],
    [
        "National Effectiveness Index",
        "CASRS-JKM + Manual Outcome Klien + IPKJ-JKM + Warga JKM + data pentadbiran",
        "S1 + S2 + S3 + S4",
        "K1 + K2 + K3 + K4 + K5",
        "Realist Evaluation; Donabedian; RE-AIM",
        "Indeks komposit nasional yang menggabungkan outcome klien, mekanisme perkhidmatan, kualiti penyampaian, kapasiti organisasi dan data prestasi pentadbiran. Ini bukan daripada satu questionnaire sahaja."
    ],
    [
        "Client Outcome Index",
        "WHODAS, WHOQOL/Wellbeing, WAI-SR, CSQ-8, PCL-5 selektif, rekod susulan",
        "S1 + S4",
        "K1",
        "RE-AIM Effectiveness; Realist CMO",
        "Dikira melalui perubahan T1-T2-T3: WHODAS menurun dianggap baik, Wellbeing meningkat dianggap baik, PCL-5 menurun dianggap baik, manakala WAI-SR dan CSQ-8 yang tinggi menunjukkan outcome positif."
    ],
    [
        "Service Mechanism Score",
        "CASRS-JKM + IPKJ-JKM Instrumen A",
        "S1 + S2",
        "K2",
        "Realist Evaluation CMO; WHO Person-Centred",
        "Dikira daripada akses, prosedur, komunikasi, responsif relasi, aliansi terapeutik, susulan dan kesesuaian modaliti intervensi."
    ],
    [
        "Service Quality Score",
        "CASRS-JKM + IPKJ-JKM + soal selidik warga JKM",
        "S1 + S2 + S3",
        "K3",
        "Donabedian Process; WHO Person-Centred",
        "Dikira daripada SOP, kompetensi, etika, kerahsiaan, kualiti intervensi, komunikasi dan koordinasi rujukan."
    ],
    [
        "Organizational Capacity Index",
        "IPKJ-JKM Instrumen B + warga JKM + data pentadbiran",
        "S2 + S3 + S4",
        "K4",
        "Donabedian Structure; RE-AIM Implementation",
        "Dikira daripada beban kes, perjawatan, kemudahan, latihan, sistem rekod, peruntukan, burnout, nisbah pegawai-klien dan tempoh menunggu."
    ],
    [
        "SEM Path Coefficient",
        "Skor konstruk teragregat daripada CASRS, IPKJ, outcome longitudinal dan data pentadbiran",
        "S1 + S2 + S3 + S4",
        "K1-K4",
        "Realist CMO + Donabedian",
        "Menguji hubungan Capacity → Quality → Mechanism → Outcome. Model ini menggabungkan pelbagai sumber data dan bukan bergantung kepada satu set questionnaire sahaja."
    ],
    [
        "RE-AIM Score",
        "Data pentadbiran + outcome klien + IPKJ + temu bual",
        "S1 + S2 + S3 + S4",
        "K1-K5",
        "RE-AIM",
        "Reach daripada rekod pentadbiran; Effectiveness daripada outcome klien; Adoption daripada pegawai/warga JKM; Implementation daripada IPKJ; Maintenance daripada susulan dan dapatan kualitatif."
    ],
    [
        "CMO Finding",
        "Temu bual, soalan terbuka CASRS/IPKJ dan data sokongan sistem",
        "S1 + S2 + S3",
        "K2 + K5",
        "Realist Evaluation",
        "Menjawab: dalam konteks apa, melalui mekanisme apa, outcome apa berlaku. Digunakan untuk menjana dapatan kualitatif dan cadangan penambahbaikan."
    ],
], columns=[
    "Result Sistem",
    "Questionnaire / Data Digunakan",
    "Sumber",
    "Konstruk",
    "Theory",
    "Bagaimana Sistem Kira / Jana Result"
])


def zone_from_state(s):
    for z, states in ZONES.items():
        if s in states:
            return z
    return "Unknown"

@st.cache_data(show_spinner=False)
def simulate_questionnaire(n=600, seed=2026):
    rng = np.random.default_rng(seed)
    states = list(STATE_EFFECT.keys())
    # equal-ish by six TOR zones, then split within states
    zone_list = np.repeat(list(ZONES.keys()), n // 6)
    if len(zone_list) < n:
        zone_list = np.concatenate([zone_list, rng.choice(list(ZONES.keys()), n - len(zone_list))])
    rng.shuffle(zone_list)
    rows = []
    for i, z in enumerate(zone_list, 1):
        state = rng.choice(ZONES[z])
        eff = STATE_EFFECT[state]
        group = rng.choice(RESP_GROUPS, p=[0.75, 0.105, 0.045, 0.10])
        age = int(np.clip(rng.normal(38, 13), 16, 75))
        capacity = np.clip(rng.normal(70 + eff, 9), 35, 97)
        quality = np.clip(0.62 * capacity + rng.normal(29 + eff, 7), 35, 99)
        mechanism = np.clip(0.60 * quality + rng.normal(31, 7), 35, 99)
        wai = np.clip(mechanism + rng.normal(1.5, 7), 35, 99)
        csq8 = np.clip(0.55 * mechanism + 0.30 * quality + rng.normal(14, 6), 35, 100)
        access = np.clip(rng.normal(72 + eff, 10), 30, 98)
        rights = np.clip(rng.normal(80 + eff, 8), 45, 100)
        sop = np.clip(rng.normal(74 + eff, 9), 35, 98)
        referral = np.clip(rng.normal(68 + eff, 11), 28, 97)
        whodas_t1 = np.clip(rng.normal(48, 11), 12, 86)
        wellbeing_t1 = np.clip(rng.normal(52, 10), 15, 88)
        pcl5_t1 = np.clip(rng.normal(44, 13), 5, 82)
        improvement = np.clip((mechanism + quality + access) / 10 + rng.normal(0, 4), 5, 33)
        whodas_t2 = np.clip(whodas_t1 - improvement * 0.55 + rng.normal(0, 3), 4, 78)
        whodas_t3 = np.clip(whodas_t2 - rng.normal(2.2, 3), 3, 75)
        wellbeing_t2 = np.clip(wellbeing_t1 + improvement * 0.60 + rng.normal(0, 3), 15, 98)
        wellbeing_t3 = np.clip(wellbeing_t2 + rng.normal(2, 3), 15, 99)
        pcl5_t2 = np.clip(pcl5_t1 - improvement * 0.65 + rng.normal(0, 4), 2, 80)
        pcl5_t3 = np.clip(pcl5_t2 - rng.normal(2.5, 3), 2, 78)
        outcome = np.clip(0.23 * (100 - whodas_t3) + 0.24 * wellbeing_t3 + 0.19 * csq8 + 0.18 * wai + 0.16 * (100 - pcl5_t3), 0, 100)
        rows.append({
            "respondent_id": f"Q{i:04d}", "zone": z, "state": state, "respondent_group": group,
            "gender": rng.choice(["Lelaki", "Perempuan"], p=[.42, .58]),
            "age": age, "age_group": "16-24" if age < 25 else "25-34" if age < 35 else "35-44" if age < 45 else "45-54" if age < 55 else "55+",
            "intervention_type": rng.choice(INTERVENTIONS, p=[.34,.15,.17,.13,.12,.09]),
            "waiting_days": int(np.clip(rng.normal(9 - eff/3, 4), 1, 30)),
            "sessions_completed": int(np.clip(rng.poisson(4)+1, 1, 12)),
            "dropout_status": "Ya" if rng.random() < .12 + max(0, 65 - access) / 220 else "Tidak",
            "followup_status": "Lengkap" if rng.random() < .75 else "Tidak lengkap",
            "Organizational_Capacity": round(capacity, 1), "Service_Quality": round(quality, 1), "Service_Mechanism": round(mechanism, 1),
            "Access_Responsiveness": round(access, 1), "Rights_Based_Experience": round(rights, 1),
            "SOP_Compliance": round(sop, 1), "Referral_Coordination": round(referral, 1),
            "WHODAS_T1": round(whodas_t1, 1), "WHODAS_T2": round(whodas_t2, 1), "WHODAS_T3": round(whodas_t3, 1),
            "Wellbeing_T1": round(wellbeing_t1, 1), "Wellbeing_T2": round(wellbeing_t2, 1), "Wellbeing_T3": round(wellbeing_t3, 1),
            "PCL5_T1": round(pcl5_t1, 1), "PCL5_T2": round(pcl5_t2, 1), "PCL5_T3": round(pcl5_t3, 1),
            "WAI_Alliance": round(wai, 1), "CSQ8_Satisfaction": round(csq8, 1), "Client_Outcome_Index": round(outcome, 1)
        })
    return pd.DataFrame(rows)

@st.cache_data(show_spinner=False)
def simulate_interviews(n=85, seed=2027):
    rng = np.random.default_rng(seed)
    zone_list = np.repeat(list(ZONES.keys()), n // 6)
    if len(zone_list) < n:
        zone_list = np.concatenate([zone_list, rng.choice(list(ZONES.keys()), n - len(zone_list))])
    rng.shuffle(zone_list)
    themes = ["Akses dan masa menunggu", "Hubungan terapeutik", "Kerahsiaan dan rasa selamat", "Kesesuaian budaya/bahasa", "Susulan kes", "Kapasiti pegawai", "Rujukan antara agensi", "Tele-kaunseling", "Pemulihan trauma", "SOP dan dokumentasi"]
    rows = []
    for i, z in enumerate(zone_list, 1):
        rows.append({
            "interview_id": f"I{i:03d}", "zone": z, "state": rng.choice(ZONES[z]),
            "respondent_group": rng.choice(["Klien", "PPsi", "PPPsi", "Warga Jabatan", "Pemegang Taruh"], p=[.53,.20,.09,.10,.08]),
            "CMO_context": rng.choice(["Luar bandar", "Bandar", "Beban kes tinggi", "Kes krisis", "Kumpulan rentan", "Capaian digital rendah"]),
            "CMO_mechanism": rng.choice(["Kepercayaan", "Rasa selamat", "Pemerkasaan", "Kefahaman matlamat sesi", "Sokongan sosial", "Privasi"]),
            "CMO_outcome": rng.choice(["Pengurangan tekanan", "Peningkatan fungsi sosial", "Kepuasan tinggi", "Kekal hadir sesi", "Rujukan berjaya", "Keciciran rendah"]),
            "main_theme": rng.choice(themes),
            "sentiment": rng.choice(["Positif", "Campuran", "Negatif"], p=[.58,.30,.12]),
            "priority": rng.choice(["Tinggi", "Sederhana", "Rendah"], p=[.45,.38,.17]),
            "quote": "Petikan ilustrasi simulasi; akan diganti dengan transkrip sebenar selepas kerja lapangan."
        })
    return pd.DataFrame(rows)


def fig_style(fig, h=430):
    fig.update_layout(
        height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,.18)",
        font=dict(color="#E5E7EB", family="Inter"), margin=dict(l=25, r=25, t=62, b=35),
        legend=dict(orientation="h", y=1.08, x=1, xanchor="right"), title_font=dict(size=20, color="#fff"),
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,.18)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,.18)")
    return fig


def kpi(label, value, note=""):
    st.markdown(f"<div class='kpi'><div class='klabel'>{label}</div><div class='kvalue'>{value}</div><div class='knote'>{note}</div></div>", unsafe_allow_html=True)


def sem_tables():
    measurement = pd.DataFrame([
        ["Organizational Capacity", .931, .949, .755, "Pass"], ["Service Quality", .944, .959, .786, "Pass"],
        ["Service Mechanism", .928, .946, .744, "Pass"], ["Client Outcome", .918, .940, .724, "Pass"]
    ], columns=["Construct", "Cronbach Alpha", "Composite Reliability", "AVE", "Decision"])
    paths = pd.DataFrame([
        ["Organizational Capacity → Service Quality", .81, 22.4, "<0.001", "Supported"],
        ["Service Quality → Service Mechanism", .76, 18.9, "<0.001", "Supported"],
        ["Service Mechanism → Client Outcome", .73, 16.8, "<0.001", "Supported"],
        ["Service Quality → Client Outcome", .24, 5.2, "<0.001", "Supported"],
        ["Organizational Capacity → Client Outcome", .11, 2.1, "0.035", "Weak / indirect dominant"],
    ], columns=["SEM Path", "Beta", "t-value", "p-value", "Decision"])
    r2 = pd.DataFrame([["Service Quality", .66, "Substantial"], ["Service Mechanism", .58, "Moderate-high"], ["Client Outcome", .71, "Substantial"]], columns=["Endogenous Construct", "R²", "Interpretation"])
    htmt = pd.DataFrame(np.array([[1,.74,.69,.62],[.74,1,.77,.70],[.69,.77,1,.73],[.62,.70,.73,1]]), columns=["Capacity","Quality","Mechanism","Outcome"], index=["Capacity","Quality","Mechanism","Outcome"])
    mediation = pd.DataFrame([
        ["Capacity → Quality → Outcome", .194, "<0.001", "Partial mediation"],
        ["Quality → Mechanism → Outcome", .555, "<0.001", "Strong mediation"],
        ["Capacity → Quality → Mechanism → Outcome", .449, "<0.001", "Sequential mediation"],
    ], columns=["Indirect Effect", "Beta", "p-value", "Interpretation"])
    fit = pd.DataFrame([["SRMR", .047, "Good"], ["NFI", .923, "Acceptable"], ["Q² Predict", .381, "Predictive relevance"], ["GoF", .642, "High"]], columns=["Model Fit / Predictive Metric", "Value", "Interpretation"])
    return measurement, paths, r2, htmt, mediation, fit


def model_results(qdf):
    corr = qdf[["Organizational_Capacity","Service_Quality","Service_Mechanism","Client_Outcome_Index","CSQ8_Satisfaction","WAI_Alliance","Access_Responsiveness"]].corr().round(2)
    # simple OLS using numpy for illustrative model table, no statsmodels dependency
    y = qdf["Client_Outcome_Index"].values
    Xcols = ["Organizational_Capacity","Service_Quality","Service_Mechanism","CSQ8_Satisfaction","WAI_Alliance","Access_Responsiveness"]
    X = qdf[Xcols].values
    Xs = (X - X.mean(axis=0)) / X.std(axis=0)
    ys = (y - y.mean()) / y.std()
    beta = np.linalg.lstsq(np.c_[np.ones(len(Xs)), Xs], ys, rcond=None)[0][1:]
    pred = np.c_[np.ones(len(Xs)), Xs].dot(np.r_[0,beta])
    r2 = 1 - np.sum((ys - pred)**2) / np.sum((ys - ys.mean())**2)
    reg = pd.DataFrame({"Predictor": Xcols, "Standardized Beta": beta.round(3), "Role": ["Context", "Process", "Mechanism", "Outcome perception", "Therapeutic alliance", "Access"]})
    reg.loc[len(reg)] = ["Model R²", round(r2,3), "Diagnostic only"]
    return corr, reg


def create_sem_diagram():
    nodes = pd.DataFrame({
        "node": ["Organizational\nCapacity", "Service\nQuality", "Service\nMechanism", "Client\nOutcome"],
        "x": [0, 1, 2, 3], "y": [0, .35, 0, .35]
    })
    edges = [(0,1,"β=.81"), (1,2,"β=.76"), (2,3,"β=.73"), (1,3,"β=.24")]
    fig = go.Figure()
    for a,b,label in edges:
        x0,y0 = nodes.loc[a,["x","y"]]
        x1,y1 = nodes.loc[b,["x","y"]]
        fig.add_trace(go.Scatter(x=[x0,x1], y=[y0,y1], mode="lines", line=dict(width=5 if label != "β=.24" else 3, color="#FDE68A" if label != "β=.24" else "#38BDF8"), hoverinfo="skip", showlegend=False))
        fig.add_annotation(x=(x0+x1)/2, y=(y0+y1)/2+.12, text=label, showarrow=False, font=dict(size=16, color="#FDE68A"))
    fig.add_trace(go.Scatter(x=nodes.x, y=nodes.y, mode="markers+text", text=nodes.node, textposition="middle center", marker=dict(size=110, color="#0F766E", line=dict(color="#FDE68A", width=3)), textfont=dict(size=14, color="white", family="Inter"), showlegend=False))
    fig.update_xaxes(visible=False, range=[-.35,3.35])
    fig.update_yaxes(visible=False, range=[-.42,.82])
    fig.update_layout(title="SEM Path Model: Capacity → Quality → Mechanism → Outcome", height=430, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=10,r=10,t=60,b=10))
    return fig


def make_template(qdf, idf):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        qdf.head(30).to_excel(writer, index=False, sheet_name="questionnaire")
        idf.head(30).to_excel(writer, index=False, sheet_name="interview")
        pd.DataFrame({"Note": ["TOR aligned: 600 quantitative and 85 qualitative.", "Replace simulation rows with actual field data.", "SEM coefficients shown in dashboard are illustrative until recalculated using actual data."]}).to_excel(writer, index=False, sheet_name="README")
    return output.getvalue()

# Sidebar / data
qdf_demo = simulate_questionnaire()
idf_demo = simulate_interviews()
st.sidebar.markdown("## 🧠 JKM Intelligence")
st.sidebar.caption("Simulation data aligned to TOR. Upload real Excel to replace demo data.")
data_mode = st.sidebar.radio("Data source", ["Simulation: TOR-aligned demo", "Upload Excel template"], index=0)
if data_mode.startswith("Upload"):
    up = st.sidebar.file_uploader("Upload Excel with questionnaire + interview sheets", type=["xlsx"])
    if up:
        qdf = pd.read_excel(up, sheet_name="questionnaire")
        try:
            idf = pd.read_excel(up, sheet_name="interview")
        except Exception:
            idf = idf_demo.copy()
    else:
        qdf = qdf_demo.copy(); idf = idf_demo.copy()
else:
    qdf = qdf_demo.copy(); idf = idf_demo.copy()

# Safety columns
for col in ["state","zone","Client_Outcome_Index","Service_Quality","Service_Mechanism","Organizational_Capacity"]:
    if col not in qdf.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

avg_out = qdf["Client_Outcome_Index"].mean()
dropout = qdf["dropout_status"].eq("Ya").mean()*100 if "dropout_status" in qdf else 0
follow = qdf["followup_status"].eq("Lengkap").mean()*100 if "followup_status" in qdf else 0

st.markdown("""
<div class='hero'>
  <span class='badge'>TOR-ALIGNED • SEM-BASED • SIMULATION DEMO</span>
  <div class='hero-title'>Kajian Penilaian Keberkesanan <span class='gold'>Perkhidmatan Psikologi & Kaunseling JKM</span></div>
  <div class='hero-subtitle'>Premium Streamlit dashboard untuk demonstrasi tender: analisis negeri/zon, outcome longitudinal T1–T2–T3, SEM, model sokongan, RE-AIM, CMO, polisi dan simulasi senario. Semua nilai dalam demo ialah data simulasi dan perlu diganti dengan data lapangan sebenar.</div>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: kpi("Kuantitatif", f"{len(qdf):,}", "TOR target: 600")
with c2: kpi("Kualitatif", f"{len(idf):,}", "TOR target: 85")
with c3: kpi("Overall Satisfaction", f"{qdf['CSQ8_Satisfaction'].mean():.1f}", "S1 Klien • CASRS/CSQ-8 • K1-K2")
with c4: kpi("Outcome Index", f"{avg_out:.1f}", "S1+S4 • WHODAS/WHOQOL/WAI/CSQ/PCL")
with c5: kpi("Dropout", f"{dropout:.1f}%", "S4 admin + S1 follow-up")
with c6: kpi("T3 Follow-up", f"{follow:.1f}%", "RE-AIM Maintenance")

tabs = st.tabs(["01 Overview", "02 Mapping K-S-Theory", "03 Negeri & Zon", "04 T1-T2-T3 Outcomes", "05 SEM", "06 Model Results", "07 RE-AIM + CMO", "08 Kualitatif", "09 Policy", "10 Scenario", "11 Data"])

with tabs[0]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Executive Dashboard")
    a,b = st.columns([1.05,1])
    with a:
        state_summary = qdf.groupby("state", as_index=False).agg(Respondents=("respondent_id","count"), Outcome=("Client_Outcome_Index","mean"), Quality=("Service_Quality","mean"), Mechanism=("Service_Mechanism","mean"), Capacity=("Organizational_Capacity","mean"), Waiting_Days=("waiting_days","mean"))
        st.plotly_chart(fig_style(px.bar(state_summary.sort_values("Outcome"), x="Outcome", y="state", orientation="h", text="Outcome", title="Ranking Outcome Mengikut Negeri")), use_container_width=True)
    with b:
        zone_summary = qdf.groupby("zone", as_index=False).agg(Outcome=("Client_Outcome_Index","mean"), Quality=("Service_Quality","mean"), Respondents=("respondent_id","count"))
        st.plotly_chart(fig_style(px.scatter(zone_summary, x="Quality", y="Outcome", size="Respondents", color="zone", text="zone", title="Zone Performance Bubble")), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


with tabs[1]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Mapping Result Sistem: Konstruk K, Sumber S, Questionnaire dan Theory")
    st.info("Bahagian ini menjawab soalan panel: result dalam dashboard datang daripada questionnaire mana, responden mana, sumber data mana dan teori mana. Jadi sistem ini bukan bergantung kepada satu questionnaire sahaja.")

    a,b = st.columns([1,1])
    with a:
        st.markdown("### 1) Sumber Data S1–S4")
        st.dataframe(S_SOURCE_MAP, use_container_width=True, hide_index=True)
    with b:
        st.markdown("### 2) Konstruk K1–K5")
        st.dataframe(K_SOURCE_MAP[["K","Konstruk","Sumber Data","Theory / Framework","Result Dalam Sistem"]], use_container_width=True, hide_index=True)

    st.markdown("### 3) Result Dashboard: Dapat Daripada Mana?")
    st.dataframe(RESULT_SOURCE_MAP, use_container_width=True, hide_index=True)

    st.markdown("### 4) Logik Pengiraan Dalam Sistem")
    st.markdown("""
    <div class='card2'>
    <b>Overall Satisfaction</b> dikira daripada skor kepuasan klien, iaitu <b>S1 Klien</b> melalui CASRS/CSQ-8. Ini menyokong <b>K1 Outcome Klien</b> dan <b>K2 Mekanisme Perkhidmatan</b> kerana kepuasan klien bergantung kepada pengalaman akses, komunikasi, hubungan terapeutik, etika dan susulan.<br><br>
    <b>Client Outcome Index</b> bukan satu item soal selidik. Ia ialah indeks gabungan daripada outcome longitudinal <b>T1, T2 dan T3</b>: WHODAS menurun, Wellbeing meningkat, PCL-5 menurun, WAI tinggi dan CSQ-8 tinggi. Ini datang daripada <b>S1 Klien</b> dan disahkan dengan <b>S4 data pentadbiran</b> seperti susulan dan keciciran.<br><br>
    <b>SEM Model</b> menggunakan skor konstruk teragregat, bukan raw item semata-mata. Konstruk <b>K4 Capacity</b> datang terutama daripada IPKJ dan data pentadbiran; <b>K3 Quality</b> daripada IPKJ/CASRS; <b>K2 Mechanism</b> daripada CASRS/WAI; dan <b>K1 Outcome</b> daripada outcome klien T1-T2-T3. Maka model ialah triangulasi S1, S2, S3 dan S4.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 5) Mini Data Dictionary Untuk Upload Excel")
    dictionary = pd.DataFrame([
        ["CSQ8_Satisfaction", "S1 Klien", "K1/K2", "Kepuasan keseluruhan klien terhadap perkhidmatan"],
        ["WHODAS_T1/T2/T3", "S1 Klien", "K1", "Fungsi harian/disability; skor menurun bermaksud bertambah baik"],
        ["Wellbeing_T1/T2/T3", "S1 Klien", "K1", "Kesejahteraan/kualiti hidup; skor meningkat bermaksud bertambah baik"],
        ["PCL5_T1/T2/T3", "S1 Klien selektif", "K1", "Simptom trauma; skor menurun bermaksud bertambah baik"],
        ["WAI_Alliance", "S1 Klien", "K2", "Aliansi terapeutik / hubungan klien-pegawai"],
        ["Service_Quality", "S2/S3 + S1", "K3", "Kualiti penyampaian: SOP, kompetensi, etika, rujukan"],
        ["Organizational_Capacity", "S2/S3/S4", "K4", "Kapasiti organisasi: beban kes, latihan, kemudahan, perjawatan"],
        ["main_theme / CMO_context", "S1/S2/S3 kualitatif", "K5/K2", "Tema temu bual untuk cadangan penambahbaikan dan CMO"],
    ], columns=["Nama Column Dalam App", "Sumber", "Konstruk", "Maksud"])
    st.dataframe(dictionary, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[2]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Statistik Setiap Negeri dan Perbandingan Zon")
    metrics = ["CSQ8_Satisfaction", "Client_Outcome_Index", "Service_Quality", "Service_Mechanism", "Organizational_Capacity", "Access_Responsiveness", "WAI_Alliance", "waiting_days"]
    selected_metric = st.selectbox("Pilih indikator untuk perbandingan", metrics, index=0)
    summary = qdf.groupby(["zone","state"], as_index=False).agg(
        Respondents=("respondent_id","count"),
        Outcome=("Client_Outcome_Index","mean"), Quality=("Service_Quality","mean"), Mechanism=("Service_Mechanism","mean"),
        Capacity=("Organizational_Capacity","mean"), Access=("Access_Responsiveness","mean"), Satisfaction=("CSQ8_Satisfaction","mean"), Alliance=("WAI_Alliance","mean"), Waiting_Days=("waiting_days","mean")
    ).round(2)
    a,b = st.columns(2)
    with a:
        st.plotly_chart(fig_style(px.bar(qdf.groupby("state", as_index=False)[selected_metric].mean().sort_values(selected_metric), x=selected_metric, y="state", orientation="h", color=selected_metric, title=f"Perbandingan Negeri: {selected_metric}", color_continuous_scale="Cividis")), use_container_width=True)
    with b:
        pivot = qdf.pivot_table(index="state", columns="respondent_group", values=selected_metric, aggfunc="mean").round(1)
        st.plotly_chart(fig_style(px.imshow(pivot, text_auto=True, aspect="auto", color_continuous_scale="Cividis", title=f"Heatmap Negeri × Kumpulan Responden: {selected_metric}")), use_container_width=True)
    st.dataframe(summary, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[3]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Outcome Longitudinal T1, T2, T3")
    time_df = pd.DataFrame({
        "Instrument": ["WHODAS"]*3 + ["Wellbeing"]*3 + ["PCL-5"]*3,
        "Time": ["T1 Intake", "T2 Closure", "T3 Follow-up"]*3,
        "Score": [qdf.WHODAS_T1.mean(), qdf.WHODAS_T2.mean(), qdf.WHODAS_T3.mean(), qdf.Wellbeing_T1.mean(), qdf.Wellbeing_T2.mean(), qdf.Wellbeing_T3.mean(), qdf.PCL5_T1.mean(), qdf.PCL5_T2.mean(), qdf.PCL5_T3.mean()]
    })
    st.plotly_chart(fig_style(px.line(time_df, x="Time", y="Score", color="Instrument", markers=True, title="Purata Perubahan Outcome Klien")), use_container_width=True)
    a,b = st.columns(2)
    with a:
        change_state = qdf.assign(WHODAS_Improvement=qdf.WHODAS_T1-qdf.WHODAS_T3, Wellbeing_Improvement=qdf.Wellbeing_T3-qdf.Wellbeing_T1, PCL5_Improvement=qdf.PCL5_T1-qdf.PCL5_T3).groupby("state", as_index=False)[["WHODAS_Improvement","Wellbeing_Improvement","PCL5_Improvement"]].mean()
        st.plotly_chart(fig_style(px.bar(change_state, x="state", y=["WHODAS_Improvement","Wellbeing_Improvement","PCL5_Improvement"], barmode="group", title="Improvement T1 ke T3 Mengikut Negeri")), use_container_width=True)
    with b:
        st.plotly_chart(fig_style(px.box(qdf, x="zone", y="Client_Outcome_Index", color="zone", title="Distribution Outcome Mengikut Zon")), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[4]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("SEM: Measurement Model + Structural Model")
    measurement, paths, r2tab, htmt, mediation, fit = sem_tables()
    a,b = st.columns([1.1,1])
    with a:
        st.markdown("**Measurement Model: Reliability & Validity**")
        st.dataframe(measurement, use_container_width=True)
        st.markdown("**Structural Model: Path Coefficients**")
        st.dataframe(paths, use_container_width=True)
    with b:
        st.markdown("**HTMT Discriminant Validity**")
        st.dataframe(htmt.round(2), use_container_width=True)
        st.markdown("**R² and Model Fit**")
        st.dataframe(r2tab, use_container_width=True)
        st.dataframe(fit, use_container_width=True)
    st.plotly_chart(create_sem_diagram(), use_container_width=True)
    st.markdown("**Mediation / Indirect Effects**")
    st.dataframe(mediation, use_container_width=True)
    st.caption("Nota: Nilai SEM ini ialah nilai simulasi untuk demonstrasi app. Untuk laporan sebenar, pekali perlu dijana daripada AMOS/SmartPLS/R-lavaan menggunakan data lapangan.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[5]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Result Model Lain: CFA, Diagnostic Correlation, Regression Support, Group Comparison")
    corr, reg = model_results(qdf)
    a,b = st.columns(2)
    with a:
        st.markdown("**Correlation Matrix — Diagnostic Sahaja**")
        st.plotly_chart(fig_style(px.imshow(corr, text_auto=True, color_continuous_scale="Cividis", title="Correlation Diagnostic")), use_container_width=True)
    with b:
        st.markdown("**Supportive Regression Diagnostic — Bukan Analisis Utama**")
        st.dataframe(reg, use_container_width=True)
    cfa = pd.DataFrame([
        ["Capacity", "CAP1-CAP6", .78, .91, "Retain"], ["Quality", "QUAL1-QUAL8", .81, .93, "Retain"], ["Mechanism", "MECH1-MECH7", .76, .90, "Retain"], ["Outcome", "OUT1-OUT5", .74, .89, "Retain"]
    ], columns=["Latent Construct", "Indicators", "Min Loading", "Max Loading", "Decision"])
    group = qdf.groupby("zone", as_index=False).agg(Mean_Outcome=("Client_Outcome_Index","mean"), SD_Outcome=("Client_Outcome_Index","std"), N=("respondent_id","count")).round(2)
    a,b = st.columns(2)
    with a:
        st.markdown("**CFA / Indicator Loading Summary**")
        st.dataframe(cfa, use_container_width=True)
    with b:
        st.markdown("**Group Comparison Summary**")
        st.dataframe(group, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[6]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("RE-AIM + Realist CMO")
    reaim = pd.DataFrame({
        "Dimension": ["Reach", "Effectiveness", "Adoption", "Implementation", "Maintenance"],
        "Score": [min(100, len(qdf)/600*100), avg_out, qdf.Access_Responsiveness.mean(), (qdf.Rights_Based_Experience.mean()+qdf.Service_Quality.mean())/2, 100-dropout]
    })
    fig = go.Figure(go.Scatterpolar(r=reaim.Score, theta=reaim.Dimension, fill="toself", line=dict(color="#FDE68A", width=3), name="RE-AIM"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])), title="RE-AIM Radar")
    a,b = st.columns([.9,1.1])
    with a: st.plotly_chart(fig_style(fig, 500), use_container_width=True)
    with b:
        st.dataframe(reaim.round(1), use_container_width=True)
        cmo = idf.groupby(["CMO_context","CMO_mechanism","CMO_outcome"], as_index=False).size().sort_values("size", ascending=False).head(12)
        st.dataframe(cmo, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[7]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Qualitative Analytics: 85 Informants")
    a,b = st.columns(2)
    with a:
        theme = idf.main_theme.value_counts().reset_index(); theme.columns=["Theme","Count"]
        st.plotly_chart(fig_style(px.bar(theme, x="Count", y="Theme", orientation="h", title="Theme Frequency")), use_container_width=True)
    with b:
        sent = idf.groupby(["zone","sentiment"], as_index=False).size()
        st.plotly_chart(fig_style(px.bar(sent, x="zone", y="size", color="sentiment", barmode="group", title="Sentiment by Zone")), use_container_width=True)
    st.dataframe(idf, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[8]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Policy Action Dashboard")
    recs = pd.DataFrame([
        ["High", "Capacity & workload", "Tambah kapasiti PPsi/PPPsi atau susun semula triage bagi lokasi beban kes tinggi.", "Capacity → Quality path"],
        ["High", "Service quality", "Latihan trauma-informed care, therapeutic alliance dan standard dokumentasi kes.", "Quality → Mechanism path"],
        ["High", "Outcome monitoring", "Mandatkan T1/T2/T3 bagi WHODAS, Wellbeing, WAI, CSQ-8 dan PCL-5 selektif.", "Effectiveness evidence"],
        ["Medium", "Digital follow-up", "Automated reminder dan follow-up dashboard untuk T3.", "Maintenance / dropout"],
        ["Medium", "Referral coordination", "Standard rujukan antara JKM, KKM, PDRM, NGO dan sokongan komuniti.", "Continuity of care"],
    ], columns=["Priority", "Domain", "Recommended Action", "Evidence Logic"])
    st.dataframe(recs, use_container_width=True)
    st.plotly_chart(fig_style(px.treemap(recs, path=["Priority","Domain"], title="Policy Priority Map"), 500), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[9]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Scenario Simulator")
    ppsi = st.slider("Tambahan kapasiti PPsi/PPPsi (%)", 0, 50, 15)
    training = st.slider("Peningkatan latihan & supervision (%)", 0, 50, 20)
    digital = st.slider("Digital triage & T3 follow-up adoption (%)", 0, 50, 20)
    uplift = 0.18*ppsi + 0.22*training + 0.16*digital
    pred = min(100, avg_out + uplift/3)
    c1,c2,c3 = st.columns(3)
    c1.metric("Current Outcome", f"{avg_out:.1f}")
    c2.metric("Projected Outcome", f"{pred:.1f}", f"+{pred-avg_out:.1f}")
    c3.metric("Estimated Dropout", f"{max(2, dropout-(ppsi+digital)/12):.1f}%")
    sim = pd.DataFrame({"Scenario": ["Current", "After intervention"], "Outcome": [avg_out, pred], "Dropout": [dropout, max(2, dropout-(ppsi+digital)/12)]})
    st.plotly_chart(fig_style(px.bar(sim, x="Scenario", y="Outcome", text="Outcome", title="Projected Outcome")), use_container_width=True)
    st.caption("Scenario values are illustrative; final parameters must be calibrated using actual SEM coefficients and administrative records.")
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[10]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Data, Template and Download")
    st.download_button("Download TOR-aligned Excel template", make_template(qdf_demo, idf_demo), "JKM_SEM_TOR_Aligned_Template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Download current questionnaire CSV", qdf.to_csv(index=False).encode("utf-8"), "questionnaire_current.csv", "text/csv")
    st.download_button("Download current interview CSV", idf.to_csv(index=False).encode("utf-8"), "interview_current.csv", "text/csv")
    st.markdown("**Questionnaire data**")
    st.dataframe(qdf, use_container_width=True)
    st.markdown("**Interview data**")
    st.dataframe(idf, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption("JKM Psycho-Counselling Impact Intelligence | TOR-aligned simulation dashboard | SEM outputs illustrative until recalculated using actual field-data model estimates")
