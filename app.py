
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="JKM PsyCounsel Impact Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# PREMIUM CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: radial-gradient(circle at top left, #1B2A4A 0%, #07111F 38%, #030712 100%);
    color: #F8FAFC;
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #06101E 0%, #0B1628 100%);
    border-right: 1px solid rgba(197,160,23,0.25);
}
h1, h2, h3 {
    color: #FFFFFF !important;
    letter-spacing: -0.03em;
}
.hero {
    padding: 28px 34px;
    border-radius: 28px;
    background:
      linear-gradient(135deg, rgba(197,160,23,0.20), rgba(255,255,255,0.05)),
      linear-gradient(135deg, #0B1730 0%, #111E38 60%, #1B2A4A 100%);
    border: 1px solid rgba(197,160,23,0.32);
    box-shadow: 0 24px 80px rgba(0,0,0,0.40);
    margin-bottom: 18px;
}
.hero-title {
    font-size: 42px;
    font-weight: 900;
    line-height: 1.05;
    color: #FFFFFF;
}
.hero-subtitle {
    margin-top: 8px;
    color: #CBD5E1;
    font-size: 16px;
    max-width: 1050px;
}
.gold {
    background: linear-gradient(90deg, #FDE68A, #C5A017, #FFF7C2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.kpi-card {
    padding: 20px 20px;
    border-radius: 22px;
    background: linear-gradient(180deg, rgba(15,23,42,0.94), rgba(15,23,42,0.66));
    border: 1px solid rgba(148,163,184,0.22);
    box-shadow: 0 18px 45px rgba(0,0,0,0.25);
    min-height: 130px;
}
.kpi-label {
    color: #94A3B8;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
}
.kpi-value {
    font-size: 34px;
    font-weight: 900;
    color: #FFFFFF;
    margin-top: 8px;
}
.kpi-note {
    color: #CBD5E1;
    font-size: 13px;
    margin-top: 4px;
}
.section-card {
    padding: 22px;
    border-radius: 24px;
    background: rgba(15,23,42,0.72);
    border: 1px solid rgba(148,163,184,0.20);
    box-shadow: 0 20px 50px rgba(0,0,0,0.28);
    margin-bottom: 18px;
}
.badge {
    display:inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(197,160,23,0.14);
    color: #FDE68A;
    border: 1px solid rgba(197,160,23,0.35);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: .05em;
}
.metric-good { color:#86EFAC; font-weight:800; }
.metric-warn { color:#FDE68A; font-weight:800; }
.metric-bad { color:#FDA4AF; font-weight:800; }
div[data-testid="stMetric"] {
    background: rgba(15,23,42,0.72);
    border: 1px solid rgba(148,163,184,0.18);
    padding: 16px;
    border-radius: 18px;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(15,23,42,0.85);
    border-radius: 999px;
    border: 1px solid rgba(148,163,184,0.22);
    padding: 10px 18px;
    color: #CBD5E1;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #C5A017, #FDE68A) !important;
    color: #0F172A !important;
    font-weight: 900;
}
[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}
hr {
    border-color: rgba(148,163,184,0.25);
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA GENERATION / LOADER
# ============================================================
ZONES = {
    "Tengah": ["Kuala Lumpur", "Selangor"],
    "Utara": ["Pulau Pinang", "Kedah"],
    "Selatan": ["Johor", "Melaka"],
    "Timur": ["Kelantan", "Pahang"],
    "Sabah": ["Kota Kinabalu"],
    "Sarawak": ["Kuching"]
}

CLIENT_TYPES = [
    "Klien individu", "Warga Jabatan", "PPsi", "PPPsi", "Klien keluarga",
    "Mangsa keganasan rumah tangga", "OKU", "Warga emas", "Kanak-kanak / remaja"
]
INTERVENTION_TYPES = ["Kaunseling Individu", "Kaunseling Kelompok", "Intervensi Krisis", "Sokongan Sosial", "Psikopendidikan", "Rujukan Lanjut"]

@st.cache_data
def generate_questionnaire(n=600, seed=2027):
    rng = np.random.default_rng(seed)
    zones = np.repeat(list(ZONES.keys()), n // 6)
    if len(zones) < n:
        zones = np.concatenate([zones, rng.choice(list(ZONES.keys()), n-len(zones))])
    rng.shuffle(zones)

    rows = []
    for i, zone in enumerate(zones, start=1):
        age = int(np.clip(rng.normal(38, 13), 16, 75))
        gender = rng.choice(["Lelaki", "Perempuan"], p=[0.42, 0.58])
        client_type = rng.choice(CLIENT_TYPES, p=[.25,.15,.13,.10,.10,.08,.07,.06,.06])
        intervention = rng.choice(INTERVENTION_TYPES, p=[.34,.15,.17,.13,.12,.09])
        location = rng.choice(ZONES[zone])

        # baseline severity and improvement
        base = rng.normal(62, 12)
        zone_effect = {"Tengah": 4, "Utara": 2, "Selatan": 3, "Timur": -1, "Sabah": -2, "Sarawak": -1}[zone]
        access = np.clip(rng.normal(73 + zone_effect, 10), 35, 98)
        alliance = np.clip(rng.normal(77 + zone_effect, 9), 40, 99)
        rights = np.clip(rng.normal(80 + zone_effect, 8), 45, 99)
        satisfaction = np.clip(rng.normal(78 + zone_effect, 9), 35, 100)

        t1_dass = np.clip(base + rng.normal(0, 7), 20, 95)
        improvement = np.clip((access + alliance + rights)/9 + rng.normal(0, 5), 6, 32)
        t2_dass = np.clip(t1_dass - improvement, 5, 85)
        t3_dass = np.clip(t2_dass - rng.normal(3, 5), 5, 80)

        t1_whodas = np.clip(rng.normal(48, 11), 10, 85)
        t2_whodas = np.clip(t1_whodas - improvement*0.55 + rng.normal(0,4), 5, 75)
        t3_whodas = np.clip(t2_whodas - rng.normal(2,3), 5, 70)

        wellbeing_t1 = np.clip(rng.normal(52, 10), 10, 90)
        wellbeing_t2 = np.clip(wellbeing_t1 + improvement*0.62 + rng.normal(0,4), 15, 98)
        wellbeing_t3 = np.clip(wellbeing_t2 + rng.normal(2,4), 15, 99)

        wait_days = int(np.clip(rng.normal(9 - zone_effect/2, 4), 1, 28))
        sessions = int(np.clip(rng.poisson(4) + 1, 1, 12))
        dropout = "Ya" if rng.random() < (0.13 + max(0, 65-access)/200) else "Tidak"
        followup = "Lengkap" if rng.random() < 0.75 else "Tidak lengkap"

        effectiveness = np.clip(
            0.28*(t1_dass-t3_dass)*3 + 0.20*(t1_whodas-t3_whodas)*2 + 
            0.20*(wellbeing_t3-wellbeing_t1)*2 + 0.16*satisfaction + 
            0.16*alliance, 0, 100
        )

        rows.append({
            "respondent_id": f"Q{i:04d}",
            "zone": zone,
            "state_location": location,
            "gender": gender,
            "age": age,
            "age_group": "16-24" if age<25 else "25-34" if age<35 else "35-44" if age<45 else "45-54" if age<55 else "55+",
            "respondent_group": client_type,
            "intervention_type": intervention,
            "waiting_days": wait_days,
            "sessions_completed": sessions,
            "dropout_status": dropout,
            "followup_status": followup,
            "DASS21_T1": round(t1_dass,1),
            "DASS21_T2": round(t2_dass,1),
            "DASS21_T3": round(t3_dass,1),
            "WHODAS_T1": round(t1_whodas,1),
            "WHODAS_T2": round(t2_whodas,1),
            "WHODAS_T3": round(t3_whodas,1),
            "Wellbeing_T1": round(wellbeing_t1,1),
            "Wellbeing_T2": round(wellbeing_t2,1),
            "Wellbeing_T3": round(wellbeing_t3,1),
            "WAI_Alliance": round(alliance,1),
            "CSQ8_Satisfaction": round(satisfaction,1),
            "Access_Responsiveness": round(access,1),
            "Rights_Based_Experience": round(rights,1),
            "Effectiveness_Index": round(effectiveness,1)
        })
    return pd.DataFrame(rows)

@st.cache_data
def generate_interviews(n=90, seed=2028):
    rng = np.random.default_rng(seed)
    zones = np.repeat(list(ZONES.keys()), n // 6)
    if len(zones) < n:
        zones = np.concatenate([zones, rng.choice(list(ZONES.keys()), n-len(zones))])
    rng.shuffle(zones)
    themes = [
        "Akses dan masa menunggu", "Hubungan terapeutik", "Kerahsiaan dan rasa selamat",
        "Kesesuaian budaya/bahasa", "Susulan kes", "Kapasiti pegawai",
        "Rujukan antara agensi", "Tele-kaunseling", "Pemulihan trauma", "SOP dan dokumentasi"
    ]
    sentiment = ["Positif", "Campuran", "Negatif"]
    quotes = {
        "Akses dan masa menunggu": "Masa menunggu masih menjadi isu utama bagi klien tertentu.",
        "Hubungan terapeutik": "Klien lebih yakin apabila pegawai memberi ruang untuk bercakap dengan selamat.",
        "Kerahsiaan dan rasa selamat": "Kepercayaan meningkat apabila aspek kerahsiaan diterangkan dengan jelas.",
        "Kesesuaian budaya/bahasa": "Bahasa dan kefahaman budaya membantu klien lebih terbuka.",
        "Susulan kes": "Susulan yang konsisten membantu klien kekal dalam proses pemulihan.",
        "Kapasiti pegawai": "Beban kes yang tinggi boleh menjejaskan kekerapan sesi.",
        "Rujukan antara agensi": "Rujukan perlu lebih tersusun supaya klien tidak tercicir.",
        "Tele-kaunseling": "Tele-kaunseling membantu capaian tetapi tidak sesuai untuk semua kes.",
        "Pemulihan trauma": "Klien berisiko memerlukan pendekatan berinformasi trauma.",
        "SOP dan dokumentasi": "SOP yang jelas membantu konsistensi perkhidmatan antara lokasi."
    }
    rows=[]
    for i, zone in enumerate(zones, start=1):
        theme = rng.choice(themes)
        rows.append({
            "interview_id": f"I{i:03d}",
            "zone": zone,
            "respondent_group": rng.choice(["Klien", "Pegawai Psikologi", "Penolong Pegawai Psikologi", "Pengurusan JKM", "Pemegang Taruh Luar"],
                                           p=[.40,.22,.16,.12,.10]),
            "CMO_context": rng.choice(["Luar bandar", "Bandar", "Beban kes tinggi", "Kes krisis", "Kumpulan rentan", "Capaian digital rendah"]),
            "CMO_mechanism": rng.choice(["Kepercayaan", "Rasa selamat", "Pemerkasaan", "Kefahaman matlamat sesi", "Sokongan sosial", "Privasi"]),
            "CMO_outcome": rng.choice(["Pengurangan tekanan", "Peningkatan fungsi sosial", "Kepuasan tinggi", "Kekal hadir sesi", "Rujukan berjaya", "Keciciran rendah"]),
            "main_theme": theme,
            "sentiment": rng.choice(sentiment, p=[.58,.30,.12]),
            "illustrative_quote": quotes[theme],
            "recommendation_priority": rng.choice(["Tinggi", "Sederhana", "Rendah"], p=[.45,.38,.17])
        })
    return pd.DataFrame(rows)

def normalize_columns(df):
    df.columns = [str(c).strip() for c in df.columns]
    return df

def load_uploaded_excel(uploaded):
    if uploaded is None:
        return None, None
    xls = pd.ExcelFile(uploaded)
    qdf, idf = None, None
    if "questionnaire" in xls.sheet_names:
        qdf = pd.read_excel(uploaded, sheet_name="questionnaire")
    else:
        qdf = pd.read_excel(uploaded, sheet_name=xls.sheet_names[0])
    if "interview" in xls.sheet_names:
        idf = pd.read_excel(uploaded, sheet_name="interview")
    elif len(xls.sheet_names) > 1:
        idf = pd.read_excel(uploaded, sheet_name=xls.sheet_names[1])
    return normalize_columns(qdf), normalize_columns(idf) if idf is not None else None

def status_badge(score):
    if score >= 75:
        return "Sangat Baik"
    if score >= 65:
        return "Baik"
    if score >= 55:
        return "Sederhana"
    return "Perlu Intervensi"

def kpi_card(label, value, note=""):
    st.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)

def premium_fig(fig, height=410):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.25)",
        font=dict(color="#E5E7EB", family="Inter"),
        margin=dict(l=24,r=24,t=60,b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        title_font=dict(size=20, color="#FFFFFF")
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.18)", zerolinecolor="rgba(148,163,184,0.22)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.18)", zerolinecolor="rgba(148,163,184,0.22)")
    return fig

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown("## 🧠 JKM Impact Intelligence")
st.sidebar.markdown("**Mode data**")
data_mode = st.sidebar.radio(
    "Pilih sumber data",
    ["Demo penuh 600 responden + 90 interview", "Upload Excel sebenar"],
    label_visibility="collapsed"
)

uploaded_excel = None
if data_mode == "Upload Excel sebenar":
    uploaded_excel = st.sidebar.file_uploader(
        "Upload Excel sebenar JKM (.xlsx)",
        type=["xlsx"],
        help="Sheet 1: questionnaire, Sheet 2: interview. Upload optional; app tetap boleh buka."
    )

qdf_demo = generate_questionnaire()
idf_demo = generate_interviews()

qdf, idf = qdf_demo, idf_demo
if uploaded_excel is not None:
    try:
        qdf_upload, idf_upload = load_uploaded_excel(uploaded_excel)
        if qdf_upload is not None and len(qdf_upload) > 0:
            qdf = qdf_upload
        if idf_upload is not None and len(idf_upload) > 0:
            idf = idf_upload
        st.sidebar.success("Excel sebenar berjaya dimuat naik.")
    except Exception as e:
        st.sidebar.error(f"Gagal baca Excel: {e}")
else:
    if data_mode == "Upload Excel sebenar":
        st.sidebar.info("Belum upload Excel. Demo result masih dipaparkan supaya panel boleh lihat sistem.")

zone_filter = st.sidebar.multiselect("Filter zon", sorted(qdf["zone"].dropna().unique()), default=sorted(qdf["zone"].dropna().unique()))
group_filter = st.sidebar.multiselect("Filter kumpulan responden", sorted(qdf["respondent_group"].dropna().unique()), default=sorted(qdf["respondent_group"].dropna().unique()))
qdf_f = qdf[qdf["zone"].isin(zone_filter) & qdf["respondent_group"].isin(group_filter)].copy()
idf_f = idf[idf["zone"].isin(zone_filter)].copy() if idf is not None and "zone" in idf.columns else idf

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero">
  <div class="badge">PREMIUM RESEARCH IMPACT DASHBOARD</div>
  <div class="hero-title">JKM <span class="gold">PsyCounsel Impact Intelligence</span></div>
  <div class="hero-subtitle">
  Sistem pintar untuk memvisualkan expected result kajian: demografi, keberkesanan intervensi, RE-AIM, CMO,
  instrumen psikologi, dapatan kualitatif dan cadangan penambahbaikan berasaskan bukti.
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# KPI SUMMARY
# ============================================================
total_resp = len(qdf_f)
total_interview = len(idf_f) if idf_f is not None else 0
avg_eff = qdf_f["Effectiveness_Index"].mean() if "Effectiveness_Index" in qdf_f else np.nan
avg_sat = qdf_f["CSQ8_Satisfaction"].mean() if "CSQ8_Satisfaction" in qdf_f else np.nan
dass_change = (qdf_f["DASS21_T1"].mean() - qdf_f["DASS21_T3"].mean()) if {"DASS21_T1","DASS21_T3"}.issubset(qdf_f.columns) else np.nan

c1,c2,c3,c4,c5 = st.columns(5)
with c1: kpi_card("Responden kuantitatif", f"{total_resp:,}", "sasaran penuh: 600")
with c2: kpi_card("Interview kualitatif", f"{total_interview:,}", "sasaran: 90 informan")
with c3: kpi_card("Effectiveness Index", f"{avg_eff:.1f}" if not np.isnan(avg_eff) else "-", status_badge(avg_eff) if not np.isnan(avg_eff) else "")
with c4: kpi_card("Kepuasan CSQ-8", f"{avg_sat:.1f}" if not np.isnan(avg_sat) else "-", "pengalaman perkhidmatan")
with c5: kpi_card("Pengurangan DASS", f"{dass_change:.1f}" if not np.isnan(dass_change) else "-", "T1 ke T3")

tabs = st.tabs([
    "Executive Result",
    "Demografi",
    "Keberkesanan T1-T2-T3",
    "RE-AIM",
    "CMO Realist",
    "Instrumen",
    "Interview 90",
    "Zon Drilldown",
    "Cadangan",
    "Data"
])

# ============================================================
# EXECUTIVE
# ============================================================
with tabs[0]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Ringkasan Expected Result Keseluruhan")
    zone_summary = qdf_f.groupby("zone", as_index=False).agg(
        respondents=("respondent_id","count"),
        effectiveness=("Effectiveness_Index","mean"),
        satisfaction=("CSQ8_Satisfaction","mean"),
        access=("Access_Responsiveness","mean"),
        alliance=("WAI_Alliance","mean"),
        rights=("Rights_Based_Experience","mean"),
        dass_reduction=("DASS21_T1", "mean")
    )
    zone_summary["dass_reduction"] = qdf_f.groupby("zone").apply(lambda x: x["DASS21_T1"].mean()-x["DASS21_T3"].mean()).values
    zone_summary["status"] = zone_summary["effectiveness"].apply(status_badge)
    st.dataframe(zone_summary.round(1), use_container_width=True)

    fig = px.bar(zone_summary.sort_values("effectiveness", ascending=False), x="zone", y="effectiveness",
                 text="effectiveness", title="Effectiveness Index Mengikut Zon", color="effectiveness",
                 color_continuous_scale=["#7F1D1D","#C5A017","#22C55E"])
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    st.plotly_chart(premium_fig(fig), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# DEMOGRAPHICS
# ============================================================
with tabs[1]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Visualisasi Demografi Responden")
    a,b = st.columns(2)
    with a:
        fig = px.histogram(qdf_f, x="zone", color="gender", barmode="group", title="Taburan Responden Mengikut Zon dan Jantina")
        st.plotly_chart(premium_fig(fig), use_container_width=True)
    with b:
        fig = px.histogram(qdf_f, x="age_group", color="respondent_group", title="Taburan Umur Mengikut Kumpulan Responden")
        st.plotly_chart(premium_fig(fig), use_container_width=True)

    a,b = st.columns(2)
    with a:
        fig = px.pie(qdf_f, names="respondent_group", title="Komposisi Kumpulan Responden", hole=0.58)
        st.plotly_chart(premium_fig(fig), use_container_width=True)
    with b:
        fig = px.box(qdf_f, x="zone", y="age", color="zone", title="Profil Umur Mengikut Zon")
        st.plotly_chart(premium_fig(fig), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# EFFECTIVENESS
# ============================================================
with tabs[2]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Keberkesanan Pra-Pasca-Susulan: T1, T2, T3")
    time_means = pd.DataFrame({
        "Measure": ["DASS-21", "DASS-21", "DASS-21", "WHODAS", "WHODAS", "WHODAS", "Wellbeing", "Wellbeing", "Wellbeing"],
        "Time": ["T1 Intake", "T2 Penutupan Kes", "T3 Susulan"]*3,
        "Score": [
            qdf_f["DASS21_T1"].mean(), qdf_f["DASS21_T2"].mean(), qdf_f["DASS21_T3"].mean(),
            qdf_f["WHODAS_T1"].mean(), qdf_f["WHODAS_T2"].mean(), qdf_f["WHODAS_T3"].mean(),
            qdf_f["Wellbeing_T1"].mean(), qdf_f["Wellbeing_T2"].mean(), qdf_f["Wellbeing_T3"].mean()
        ]
    })
    fig = px.line(time_means, x="Time", y="Score", color="Measure", markers=True,
                  title="Trend Perubahan Skor Klien Dari T1 ke T3")
    st.plotly_chart(premium_fig(fig), use_container_width=True)

    a,b = st.columns(2)
    with a:
        fig = px.scatter(qdf_f, x="WAI_Alliance", y="Effectiveness_Index", color="zone",
                         size="sessions_completed", hover_data=["respondent_group","intervention_type"],
                         title="Hubungan Aliansi Terapeutik dengan Keberkesanan")
        st.plotly_chart(premium_fig(fig), use_container_width=True)
    with b:
        fig = px.violin(qdf_f, x="intervention_type", y="Effectiveness_Index", color="intervention_type",
                        box=True, title="Keberkesanan Mengikut Jenis Intervensi")
        fig.update_xaxes(tickangle=-25)
        st.plotly_chart(premium_fig(fig), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# RE-AIM
# ============================================================
with tabs[3]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("RE-AIM Result Framework")
    reaim = pd.DataFrame({
        "Dimension": ["Reach", "Effectiveness", "Adoption", "Implementation", "Maintenance"],
        "Score": [
            min(100, len(qdf_f)/600*100),
            qdf_f["Effectiveness_Index"].mean(),
            qdf_f["Access_Responsiveness"].mean(),
            (qdf_f["Rights_Based_Experience"].mean()+qdf_f["WAI_Alliance"].mean())/2,
            100 - (qdf_f["dropout_status"].eq("Ya").mean()*100)
        ],
        "Interpretation": [
            "Liputan sampel dan capaian zon",
            "Perubahan psikologi, fungsi dan kesejahteraan",
            "Penerimaan dan kebolehcapaian perkhidmatan",
            "Konsistensi SOP, etika dan pengalaman hak klien",
            "Susulan, retention dan kelestarian hasil"
        ]
    })
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=reaim["Score"], theta=reaim["Dimension"], fill="toself",
        name="RE-AIM Score", line=dict(color="#FDE68A", width=3)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,100], gridcolor="rgba(148,163,184,.25)")),
        title="Radar RE-AIM Keseluruhan"
    )
    st.plotly_chart(premium_fig(fig, height=520), use_container_width=True)
    st.dataframe(reaim.round(1), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# CMO
# ============================================================
with tabs[4]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Realist Evaluation: Context–Mechanism–Outcome")
    if idf_f is not None:
        a,b,c = st.columns(3)
        with a:
            cm = idf_f["CMO_context"].value_counts().reset_index()
            cm.columns = ["Context", "Count"]
            fig = px.bar(cm, x="Count", y="Context", orientation="h", title="Context Utama")
            st.plotly_chart(premium_fig(fig), use_container_width=True)
        with b:
            mm = idf_f["CMO_mechanism"].value_counts().reset_index()
            mm.columns = ["Mechanism", "Count"]
            fig = px.bar(mm, x="Count", y="Mechanism", orientation="h", title="Mechanism Utama")
            st.plotly_chart(premium_fig(fig), use_container_width=True)
        with c:
            oo = idf_f["CMO_outcome"].value_counts().reset_index()
            oo.columns = ["Outcome", "Count"]
            fig = px.bar(oo, x="Count", y="Outcome", orientation="h", title="Outcome Utama")
            st.plotly_chart(premium_fig(fig), use_container_width=True)
        st.dataframe(idf_f[["interview_id","zone","respondent_group","CMO_context","CMO_mechanism","CMO_outcome","main_theme"]], use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# INSTRUMENTS
# ============================================================
with tabs[5]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Analisis Instrumen Psikologi dan Pengalaman Perkhidmatan")
    instrument_cols = ["DASS21_T1","DASS21_T2","DASS21_T3","WHODAS_T1","WHODAS_T2","WHODAS_T3","Wellbeing_T1","Wellbeing_T2","Wellbeing_T3","WAI_Alliance","CSQ8_Satisfaction","Access_Responsiveness","Rights_Based_Experience"]
    inst = qdf_f[instrument_cols].mean().reset_index()
    inst.columns = ["Instrument", "Average Score"]
    fig = px.bar(inst, x="Instrument", y="Average Score", title="Purata Skor Instrumen / Konstruk")
    fig.update_xaxes(tickangle=-35)
    st.plotly_chart(premium_fig(fig), use_container_width=True)

    corr_cols = ["Effectiveness_Index","WAI_Alliance","CSQ8_Satisfaction","Access_Responsiveness","Rights_Based_Experience","sessions_completed","waiting_days"]
    corr = qdf_f[corr_cols].corr(numeric_only=True)
    fig = px.imshow(corr, text_auto=".2f", title="Correlation Heatmap: Faktor Berkait Keberkesanan", color_continuous_scale="Cividis")
    st.plotly_chart(premium_fig(fig, height=560), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# INTERVIEW
# ============================================================
with tabs[6]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Dapatan Kualitatif: 90 Interview / FGD")
    if idf_f is not None:
        a,b = st.columns(2)
        with a:
            fig = px.histogram(idf_f, x="zone", color="sentiment", barmode="group", title="Sentimen Dapatan Mengikut Zon")
            st.plotly_chart(premium_fig(fig), use_container_width=True)
        with b:
            th = idf_f["main_theme"].value_counts().reset_index()
            th.columns=["Theme","Count"]
            fig = px.bar(th, x="Count", y="Theme", orientation="h", title="Tema Utama Interview")
            st.plotly_chart(premium_fig(fig), use_container_width=True)
        st.dataframe(idf_f, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# ZONE DRILLDOWN
# ============================================================
with tabs[7]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Drilldown Zon")
    selected_zone = st.selectbox("Pilih zon", sorted(qdf_f["zone"].unique()))
    zd = qdf_f[qdf_f["zone"] == selected_zone]
    z1,z2,z3,z4 = st.columns(4)
    z1.metric("Responden", len(zd))
    z2.metric("Effectiveness", f"{zd['Effectiveness_Index'].mean():.1f}")
    z3.metric("DASS Reduction", f"{(zd['DASS21_T1'].mean()-zd['DASS21_T3'].mean()):.1f}")
    z4.metric("Dropout", f"{zd['dropout_status'].eq('Ya').mean()*100:.1f}%")
    fig = px.histogram(zd, x="respondent_group", color="intervention_type", title=f"Profil Kes dan Intervensi: Zon {selected_zone}")
    fig.update_xaxes(tickangle=-25)
    st.plotly_chart(premium_fig(fig), use_container_width=True)
    st.dataframe(zd, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# RECOMMENDATIONS
# ============================================================
with tabs[8]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Cadangan Penambahbaikan Berasaskan Bukti")
    recs = pd.DataFrame([
        ["Akses & Responsif", "Kurangkan masa menunggu melalui triage digital dan slot intervensi krisis.", "Tinggi"],
        ["Outcome Monitoring", "Laksana pengukuran T1, T2 dan T3 secara rutin untuk DASS-21, WHODAS dan Wellbeing.", "Tinggi"],
        ["Kualiti Intervensi", "Perkukuh latihan aliansi terapeutik, trauma-informed care dan person-centred practice.", "Tinggi"],
        ["Data & Dashboard", "Bangunkan pangkalan data bersepadu untuk sesi, rujukan, keciciran, susulan dan status penutupan kes.", "Tinggi"],
        ["Kelestarian", "Tetapkan KPI RE-AIM tahunan bagi Reach, Effectiveness, Adoption, Implementation dan Maintenance.", "Sederhana"],
        ["Ekuiti Zon", "Laksana pelan khusus untuk zon dengan capaian rendah atau beban kes tinggi.", "Sederhana"],
    ], columns=["Domain", "Cadangan", "Keutamaan"])
    st.dataframe(recs, use_container_width=True)

    fig = px.treemap(recs, path=["Keutamaan","Domain"], title="Peta Keutamaan Cadangan Strategik")
    st.plotly_chart(premium_fig(fig, height=520), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# DATA
# ============================================================
with tabs[9]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Data Preview dan Download")
    st.caption("Demo ini menggunakan 600 data simulasi + 90 interview. Bila data sebenar diupload, jadual ini akan diganti.")
    st.download_button(
        "Download questionnaire result CSV",
        data=qdf_f.to_csv(index=False).encode("utf-8"),
        file_name="questionnaire_result_current.csv",
        mime="text/csv"
    )
    if idf_f is not None:
        st.download_button(
            "Download interview result CSV",
            data=idf_f.to_csv(index=False).encode("utf-8"),
            file_name="interview_result_current.csv",
            mime="text/csv"
        )
    st.dataframe(qdf_f, use_container_width=True)
    if idf_f is not None:
        st.dataframe(idf_f, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("JKM PsyCounsel Impact Intelligence | Realist Evaluation + RE-AIM + Mixed Method Result Visualisation")
