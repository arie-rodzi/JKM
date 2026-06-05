import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dashboard Kajian Psikologi & Kaunseling JKM",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# GAYA PAPARAN PREMIUM
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(253, 230, 138, 0.20), transparent 32%),
        radial-gradient(circle at top right, rgba(34, 197, 94, 0.18), transparent 30%),
        linear-gradient(135deg, #030712 0%, #071526 38%, #0B2545 72%, #123C69 100%);
    color: white;
}

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

.hero-box {
    padding: 34px 38px;
    border-radius: 32px;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.18), rgba(255,255,255,0.06)),
        linear-gradient(90deg, rgba(253,230,138,0.16), rgba(14,165,233,0.08));
    border: 1px solid rgba(255,255,255,0.25);
    box-shadow: 0 28px 80px rgba(0,0,0,0.42);
    margin-bottom: 26px;
}

.main-title {
    font-size: 44px;
    line-height: 1.1;
    font-weight: 950;
    letter-spacing: -1.2px;
    color: #FDE68A;
    text-shadow: 0 0 30px rgba(253,230,138,0.28);
}

.sub-title {
    font-size: 17px;
    color: #DDEBFF;
    margin-top: 12px;
    max-width: 980px;
}

.badge-row {
    margin-top: 22px;
}

.badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.58);
    border: 1px solid rgba(253,230,138,0.38);
    color: #FDE68A;
    font-weight: 700;
    font-size: 13px;
    margin-right: 8px;
    margin-bottom: 8px;
}

.kpi-card {
    min-height: 150px;
    padding: 22px 22px 20px 22px;
    border-radius: 28px;
    background:
        linear-gradient(145deg, rgba(255,255,255,0.20), rgba(255,255,255,0.055)),
        radial-gradient(circle at top right, rgba(253,230,138,0.23), transparent 38%);
    border: 1px solid rgba(255,255,255,0.24);
    box-shadow:
        0 22px 48px rgba(0,0,0,0.34),
        inset 0 1px 0 rgba(255,255,255,0.22);
    transition: all 0.25s ease;
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 28px 65px rgba(0,0,0,0.42);
    border-color: rgba(253,230,138,0.55);
}

.kpi-label {
    color: #E0F2FE;
    font-size: 13px;
    font-weight: 750;
    text-transform: uppercase;
    letter-spacing: .55px;
}

.kpi-value {
    color: #FDE68A;
    font-size: 39px;
    font-weight: 950;
    margin-top: 10px;
    line-height: 1;
}

.kpi-note {
    color: #BBF7D0;
    font-size: 13px;
    font-weight: 650;
    margin-top: 12px;
}

.info-box {
    padding: 20px 24px;
    border-radius: 24px;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.14), rgba(255,255,255,0.055));
    border: 1px solid rgba(255,255,255,0.20);
    border-left: 6px solid #FDE68A;
    box-shadow: 0 18px 38px rgba(0,0,0,0.26);
    margin: 16px 0 22px 0;
    color: #EAF6FF;
}

.section-card {
    padding: 24px;
    border-radius: 26px;
    background: rgba(255,255,255,0.09);
    border: 1px solid rgba(255,255,255,0.18);
    box-shadow: 0 18px 45px rgba(0,0,0,0.28);
    margin-bottom: 20px;
}

h1, h2, h3 {
    color: #FDE68A !important;
    font-weight: 900 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    padding: 10px 18px;
    background: rgba(255,255,255,0.08);
    color: #E0F2FE;
    border: 1px solid rgba(255,255,255,0.14);
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FDE68A, #F59E0B) !important;
    color: #111827 !important;
    font-weight: 900;
}

[data-testid="stMetricValue"] {
    color: #FDE68A;
}

.stDataFrame {
    border-radius: 18px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATA SIMULASI SELARAS TOR
# =========================================================
@st.cache_data
def jana_data():
    np.random.seed(42)

    negeri_zon = {
        "Kuala Lumpur": "Zon Tengah",
        "Selangor": "Zon Tengah",
        "Pulau Pinang": "Zon Utara",
        "Kedah": "Zon Utara",
        "Johor": "Zon Selatan",
        "Melaka": "Zon Selatan",
        "Kelantan": "Zon Timur",
        "Pahang": "Zon Timur",
        "Sabah": "Sabah",
        "Sarawak": "Sarawak",
    }

    negeri = list(negeri_zon.keys())
    rows = []

    for i in range(600):
        n = np.random.choice(negeri)
        z = negeri_zon[n]

        s1 = np.clip(np.random.normal(82, 7), 55, 98)
        s2 = np.clip(np.random.normal(78, 8), 50, 97)
        s3 = np.clip(np.random.normal(76, 8), 50, 95)
        s4 = np.clip(np.random.normal(74, 9), 45, 96)

        whodas_t1 = np.clip(np.random.normal(58, 10), 25, 90)
        whodas_t2 = np.clip(whodas_t1 - np.random.normal(15, 5), 15, 85)
        whodas_t3 = np.clip(whodas_t2 + np.random.normal(3, 4), 15, 85)

        wellbeing_t1 = np.clip(np.random.normal(52, 10), 20, 85)
        wellbeing_t2 = np.clip(wellbeing_t1 + np.random.normal(18, 6), 25, 98)
        wellbeing_t3 = np.clip(wellbeing_t2 - np.random.normal(2, 4), 25, 98)

        satisfaction = np.clip(s1 + np.random.normal(2, 5), 45, 100)
        quality = np.clip((s1 * 0.25) + (s2 * 0.40) + (s3 * 0.35), 40, 100)
        capacity = np.clip((s2 * 0.35) + (s3 * 0.30) + (s4 * 0.35), 40, 100)
        mechanism = np.clip((s1 * 0.55) + (s2 * 0.45), 40, 100)
        outcome = np.clip(
            ((100 - whodas_t2) * 0.35) +
            (wellbeing_t2 * 0.35) +
            (satisfaction * 0.20) +
            (mechanism * 0.10), 40, 100
        )

        integrated = np.clip(
            (outcome * 0.30) +
            (mechanism * 0.20) +
            (quality * 0.20) +
            (capacity * 0.20) +
            (s4 * 0.10), 40, 100
        )

        rows.append([
            i + 1, n, z,
            s1, s2, s3, s4,
            satisfaction, outcome, mechanism, quality, capacity, integrated,
            whodas_t1, whodas_t2, whodas_t3,
            wellbeing_t1, wellbeing_t2, wellbeing_t3
        ])

    return pd.DataFrame(rows, columns=[
        "ID", "Negeri", "Zon",
        "S1_Klien", "S2_PPsi_PPPsi", "S3_Warga_JKM", "S4_Data_Pentadbiran",
        "Indeks_Kepuasan_Klien", "Indeks_Outcome_Klien", "Mekanisme_Perkhidmatan",
        "Kualiti_Penyampaian", "Kapasiti_Organisasi", "Indeks_Keberkesanan_Bersepadu",
        "WHODAS_T1", "WHODAS_T2", "WHODAS_T3",
        "Wellbeing_T1", "Wellbeing_T2", "Wellbeing_T3"
    ])


df = jana_data()


# =========================================================
# PEMETAAN TOR
# =========================================================
K_SOURCE_MAP = pd.DataFrame([
    ["K1", "Outcome Klien / Keberkesanan", "S1 + S4", "Manual Outcome Klien + CASRS-JKM + data pentadbiran", "WHODAS T1/T2/T3, Wellbeing T1/T2/T3, WAI-SR, CSQ-8, PCL-5 selektif, rekod susulan", "Realist Evaluation, RE-AIM, Bronfenbrenner", "Indeks Outcome Klien"],
    ["K2", "Mekanisme Perkhidmatan", "S1 + S2", "CASRS-JKM + IPKJ-JKM", "Akses, komunikasi, hubungan terapeutik, etika, susulan, modaliti intervensi", "Realist Evaluation CMO, WHO Person-Centred", "Skor Mekanisme Perkhidmatan"],
    ["K3", "Kualiti Penyampaian", "S1 + S2 + S3", "CASRS-JKM + IPKJ-JKM + soal selidik warga JKM", "SOP, kompetensi, etika, kerahsiaan, koordinasi rujukan, komunikasi", "Donabedian Model, WHO Person-Centred", "Skor Kualiti Penyampaian"],
    ["K4", "Kapasiti Organisasi", "S2 + S3 + S4", "IPKJ-JKM Instrumen B + warga JKM + data pentadbiran", "Perjawatan, beban kes, latihan, kemudahan, sistem rekod, burnout, nisbah pegawai-klien", "Donabedian Structure, RE-AIM Implementation", "Indeks Kapasiti Organisasi"],
    ["K5", "Penambahbaikan & Inovasi", "S1 + S2 + S3 + S4", "Soalan terbuka CASRS/IPKJ + temu bual + data pentadbiran", "Cadangan klien, cadangan pegawai, isu sistemik, tele-kaunseling, SOP digital", "RE-AIM Maintenance, Realist Evaluation CMO", "Matriks Cadangan Dasar"],
], columns=["K", "Konstruk", "Sumber Data", "Instrumen / Questionnaire", "Item / Domain Digunakan", "Teori / Kerangka", "Result Dalam Sistem"])

RESULT_SOURCE_MAP = pd.DataFrame([
    ["Indeks Kepuasan Klien", "CASRS-JKM + CSQ-8", "S1", "K1 + K2", "WHO Person-Centred; Realist Evaluation", "Purata skor kepuasan klien ditukar kepada indeks 0-100."],
    ["Indeks Keberkesanan Bersepadu", "CASRS + Manual Outcome + IPKJ + Warga JKM + data pentadbiran", "S1 + S2 + S3 + S4", "K1-K5", "Realist Evaluation; Donabedian; RE-AIM", "Indeks komposit nasional merangkumi outcome, mekanisme, kualiti, kapasiti dan prestasi pentadbiran."],
    ["Indeks Outcome Klien", "WHODAS, Wellbeing, WAI-SR, CSQ-8, PCL-5 selektif", "S1 + S4", "K1", "RE-AIM Effectiveness; Realist CMO", "Perubahan T1-T2-T3. WHODAS menurun = baik; Wellbeing meningkat = baik."],
    ["Skor Kualiti Penyampaian", "CASRS-JKM + IPKJ-JKM + Warga JKM", "S1 + S2 + S3", "K3", "Donabedian Process", "Gabungan SOP, kompetensi, etika, komunikasi dan koordinasi rujukan."],
    ["Indeks Kapasiti Organisasi", "IPKJ-JKM + Warga JKM + data pentadbiran", "S2 + S3 + S4", "K4", "Donabedian Structure", "Gabungan beban kes, perjawatan, latihan, kemudahan dan data pentadbiran."],
    ["SEM", "Skor konstruk teragregat", "S1 + S2 + S3 + S4", "K1-K4", "Realist CMO + Donabedian", "Menguji hubungan Kapasiti → Kualiti → Mekanisme → Outcome."],
    ["RE-AIM", "Data pentadbiran + outcome + IPKJ + temu bual", "S1 + S2 + S3 + S4", "K1-K5", "RE-AIM", "Reach, Effectiveness, Adoption, Implementation dan Maintenance."],
], columns=["Result Sistem", "Questionnaire / Data Digunakan", "Sumber", "Konstruk", "Teori", "Bagaimana Sistem Kira / Jana Result"])


# =========================================================
# FUNGSI BANTUAN
# =========================================================
def kpi(label, value, note=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def ringkas(series):
    return float(series.mean())


def pilih_data(df):
    col1, col2 = st.columns(2)
    with col1:
        zon = st.selectbox("Pilih Zon", ["Semua Zon"] + sorted(df["Zon"].unique()))
    with col2:
        if zon == "Semua Zon":
            negeri_list = sorted(df["Negeri"].unique())
        else:
            negeri_list = sorted(df[df["Zon"] == zon]["Negeri"].unique())
        negeri = st.selectbox("Pilih Negeri", ["Semua Negeri"] + negeri_list)

    dff = df.copy()
    if zon != "Semua Zon":
        dff = dff[dff["Zon"] == zon]
    if negeri != "Semua Negeri":
        dff = dff[dff["Negeri"] == negeri]

    return dff, zon, negeri


def plot_bar(data, x, y, title):
    fig = px.bar(data, x=x, y=y, text_auto=".1f", title=title)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        title_font=dict(size=20)
    )
    return fig


def plot_line(data, x, y, title):
    fig = px.line(data, x=x, y=y, markers=True, title=title)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    return fig


# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="main-title">Dashboard Kajian Penilaian Keberkesanan Perkhidmatan Psikologi dan Kaunseling JKM</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Sistem Analitik Simulasi Berasaskan TOR: Konstruk K1-K5, Sumber Data S1-S4, SEM, RE-AIM dan CMO</div>', unsafe_allow_html=True)

dff, zon_pilih, negeri_pilih = pilih_data(df)

st.markdown(f"""
<div class="info-box">
<b>Nota:</b> Paparan ini menggunakan data simulasi untuk demonstrasi cadangan teknikal. 
Semua analisis di bawah berubah mengikut penapis yang dipilih: <b>{zon_pilih}</b> dan <b>{negeri_pilih}</b>.
</div>
""", unsafe_allow_html=True)


# =========================================================
# KPI BOX WAJIB
# =========================================================
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi("Indeks Keberkesanan Bersepadu", f"{ringkas(dff['Indeks_Keberkesanan_Bersepadu']):.1f}%", "S1 + S2 + S3 + S4")
with c2:
    kpi("Indeks Kepuasan Klien", f"{ringkas(dff['Indeks_Kepuasan_Klien']):.1f}%", "S1: Klien")
with c3:
    kpi("Indeks Outcome Klien", f"{ringkas(dff['Indeks_Outcome_Klien']):.1f}%", "K1: Outcome")
with c4:
    kpi("Kualiti Penyampaian", f"{ringkas(dff['Kualiti_Penyampaian']):.1f}%", "K3: Kualiti")

c5, c6, c7, c8 = st.columns(4)
with c5:
    kpi("Kapasiti Organisasi", f"{ringkas(dff['Kapasiti_Organisasi']):.1f}%", "K4: Kapasiti")
with c6:
    kpi("Mekanisme Perkhidmatan", f"{ringkas(dff['Mekanisme_Perkhidmatan']):.1f}%", "K2: Mekanisme")
with c7:
    kpi("Jumlah Responden Kuantitatif", f"{len(dff):,}", "Sampel simulasi")
with c8:
    kpi("Jumlah Temu Bual Kualitatif", "85", "Selaras TOR")


# =========================================================
# TAB ANALISIS
# =========================================================
tabs = st.tabs([
    "Ringkasan Eksekutif",
    "Analisis Negeri dan Zon",
    "Outcome T1-T2-T3",
    "SEM",
    "RE-AIM",
    "CMO",
    "Pemetaan K-S-Teori",
    "Simulasi Dasar"
])


# =========================================================
# RINGKASAN EKSEKUTIF
# =========================================================
with tabs[0]:
    st.subheader("Ringkasan Eksekutif")

    st.markdown(f"""
    <div class="info-box">
    Berdasarkan data simulasi bagi pilihan semasa, Indeks Keberkesanan Bersepadu ialah 
    <b>{ringkas(dff['Indeks_Keberkesanan_Bersepadu']):.1f}%</b>. 
    Indeks ini tidak bergantung kepada satu questionnaire sahaja, tetapi menggabungkan 
    <b>S1 Klien, S2 PPsi/PPPsi, S3 Warga JKM dan S4 Data Pentadbiran</b>.
    </div>
    """, unsafe_allow_html=True)

    summary = pd.DataFrame({
        "Komponen": [
            "S1 Klien",
            "S2 PPsi/PPPsi",
            "S3 Warga JKM",
            "S4 Data Pentadbiran",
            "Indeks Kepuasan Klien",
            "Indeks Keberkesanan Bersepadu"
        ],
        "Skor Purata": [
            ringkas(dff["S1_Klien"]),
            ringkas(dff["S2_PPsi_PPPsi"]),
            ringkas(dff["S3_Warga_JKM"]),
            ringkas(dff["S4_Data_Pentadbiran"]),
            ringkas(dff["Indeks_Kepuasan_Klien"]),
            ringkas(dff["Indeks_Keberkesanan_Bersepadu"])
        ]
    })

    st.plotly_chart(plot_bar(summary, "Komponen", "Skor Purata", "Ringkasan Skor Utama"), use_container_width=True)
    st.dataframe(summary, use_container_width=True)


# =========================================================
# NEGERI DAN ZON
# =========================================================
with tabs[1]:
    st.subheader("Analisis Perbandingan Negeri dan Zon")

    by_state = dff.groupby("Negeri", as_index=False)[[
        "Indeks_Keberkesanan_Bersepadu",
        "Indeks_Kepuasan_Klien",
        "Kualiti_Penyampaian",
        "Kapasiti_Organisasi"
    ]].mean()

    by_zone = dff.groupby("Zon", as_index=False)[[
        "Indeks_Keberkesanan_Bersepadu",
        "Indeks_Kepuasan_Klien",
        "Kualiti_Penyampaian",
        "Kapasiti_Organisasi"
    ]].mean()

    st.plotly_chart(plot_bar(by_state, "Negeri", "Indeks_Keberkesanan_Bersepadu", "Indeks Keberkesanan Mengikut Negeri"), use_container_width=True)
    st.plotly_chart(plot_bar(by_zone, "Zon", "Indeks_Keberkesanan_Bersepadu", "Indeks Keberkesanan Mengikut Zon"), use_container_width=True)

    st.dataframe(by_state.round(2), use_container_width=True)
    st.dataframe(by_zone.round(2), use_container_width=True)


# =========================================================
# OUTCOME T1-T2-T3
# =========================================================
with tabs[2]:
    st.subheader("Analisis Outcome Longitudinal T1-T2-T3")

    t_data = pd.DataFrame({
        "Masa": ["T1", "T2", "T3"],
        "WHODAS": [
            ringkas(dff["WHODAS_T1"]),
            ringkas(dff["WHODAS_T2"]),
            ringkas(dff["WHODAS_T3"])
        ],
        "Wellbeing": [
            ringkas(dff["Wellbeing_T1"]),
            ringkas(dff["Wellbeing_T2"]),
            ringkas(dff["Wellbeing_T3"])
        ]
    })

    st.markdown("""
    <div class="info-box">
    WHODAS yang menurun menunjukkan kefungsian klien bertambah baik. 
    Wellbeing yang meningkat menunjukkan kesejahteraan klien bertambah baik.
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(plot_line(t_data, "Masa", "WHODAS", "Trend WHODAS T1-T2-T3"), use_container_width=True)
    st.plotly_chart(plot_line(t_data, "Masa", "Wellbeing", "Trend Wellbeing T1-T2-T3"), use_container_width=True)
    st.dataframe(t_data.round(2), use_container_width=True)


# =========================================================
# SEM
# =========================================================
with tabs[3]:
    st.subheader("Analisis SEM: Kapasiti → Kualiti → Mekanisme → Outcome")

    cap = ringkas(dff["Kapasiti_Organisasi"]) / 100
    qua = ringkas(dff["Kualiti_Penyampaian"]) / 100
    mec = ringkas(dff["Mekanisme_Perkhidmatan"]) / 100
    out = ringkas(dff["Indeks_Outcome_Klien"]) / 100

    beta1 = np.clip(0.45 + cap * 0.35, 0.50, 0.88)
    beta2 = np.clip(0.42 + qua * 0.35, 0.50, 0.88)
    beta3 = np.clip(0.40 + mec * 0.35, 0.50, 0.88)

    sem_table = pd.DataFrame({
        "Hubungan SEM": [
            "Kapasiti Organisasi → Kualiti Penyampaian",
            "Kualiti Penyampaian → Mekanisme Perkhidmatan",
            "Mekanisme Perkhidmatan → Outcome Klien"
        ],
        "Beta": [beta1, beta2, beta3],
        "Nilai-p": ["<0.001", "<0.001", "<0.001"],
        "Interpretasi": [
            "Kapasiti organisasi menyokong kualiti penyampaian.",
            "Kualiti penyampaian mengukuhkan mekanisme perkhidmatan.",
            "Mekanisme perkhidmatan meningkatkan outcome klien."
        ]
    })

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("R² Kualiti", f"{beta1**2:.2f}", "K4 → K3")
    with c2:
        kpi("R² Mekanisme", f"{beta2**2:.2f}", "K3 → K2")
    with c3:
        kpi("R² Outcome", f"{beta3**2:.2f}", "K2 → K1")

    fig = go.Figure()
    nodes = ["Kapasiti Organisasi", "Kualiti Penyampaian", "Mekanisme Perkhidmatan", "Outcome Klien"]
    xs = [0.1, 0.38, 0.66, 0.92]
    ys = [0.5, 0.5, 0.5, 0.5]

    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="markers+text",
        marker=dict(size=65),
        text=nodes,
        textposition="bottom center",
        hovertext=nodes,
        hoverinfo="text"
    ))

    for i, b in enumerate([beta1, beta2, beta3]):
        fig.add_trace(go.Scatter(
            x=[xs[i], xs[i+1]],
            y=[ys[i], ys[i+1]],
            mode="lines+text",
            line=dict(width=5),
            text=["", f"β={b:.2f}"],
            textposition="top center",
            hoverinfo="skip"
        ))

    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[0.2, 0.8])
    fig.update_layout(
        height=380,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title="Model SEM Simulasi"
    )

    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(sem_table.round(3), use_container_width=True)


# =========================================================
# RE-AIM
# =========================================================
with tabs[4]:
    st.subheader("Analisis RE-AIM")

    reaim = pd.DataFrame({
        "Domain RE-AIM": ["Reach", "Effectiveness", "Adoption", "Implementation", "Maintenance"],
        "Sumber Data": ["S4", "S1 + S4", "S2 + S3", "S2 + S3 + S4", "S1 + S2 + S3 + S4"],
        "Skor": [
            ringkas(dff["S4_Data_Pentadbiran"]),
            ringkas(dff["Indeks_Outcome_Klien"]),
            ringkas(dff["S2_PPsi_PPPsi"]),
            ringkas(dff["Kapasiti_Organisasi"]),
            ringkas(dff["Indeks_Keberkesanan_Bersepadu"])
        ],
        "Maksud": [
            "Liputan capaian perkhidmatan berdasarkan rekod pentadbiran.",
            "Perubahan outcome klien selepas intervensi.",
            "Penerimaan dan penggunaan perkhidmatan oleh pegawai dan sistem.",
            "Kualiti pelaksanaan, SOP, sumber dan kapasiti.",
            "Kelestarian susulan, pemindahan ilmu dan penambahbaikan."
        ]
    })

    st.plotly_chart(plot_bar(reaim, "Domain RE-AIM", "Skor", "Skor RE-AIM Mengikut Pilihan Semasa"), use_container_width=True)
    st.dataframe(reaim.round(2), use_container_width=True)


# =========================================================
# CMO
# =========================================================
with tabs[5]:
    st.subheader("Analisis CMO: Context–Mechanism–Outcome")

    cmo = pd.DataFrame([
        ["Beban kes tinggi", "Kapasiti pegawai terhad dan masa menunggu meningkat", "Outcome klien lebih perlahan", "K4 → K1", "S2 + S4"],
        ["Akses lokasi mencabar", "Keperluan tele-kaunseling dan susulan digital", "Reach boleh meningkat", "K2 + K5", "S1 + S4"],
        ["SOP dan rujukan jelas", "Koordinasi antara agensi lebih lancar", "Kualiti penyampaian meningkat", "K3", "S2 + S3"],
        ["Hubungan terapeutik baik", "Klien lebih percaya dan kekal dalam sesi", "Kepuasan dan outcome meningkat", "K2 → K1", "S1"],
    ], columns=["Konteks", "Mekanisme", "Outcome", "Konstruk", "Sumber Data"])

    st.dataframe(cmo, use_container_width=True)


# =========================================================
# PEMETAAN K-S-TEORI
# =========================================================
with tabs[6]:
    st.subheader("Pemetaan Konstruk, Sumber Data, Instrumen dan Teori")

    st.markdown("### Pemetaan Konstruk K1-K5")
    st.dataframe(K_SOURCE_MAP, use_container_width=True)

    st.markdown("### Pemetaan Result Sistem kepada Questionnaire, Sumber, Konstruk dan Teori")
    st.dataframe(RESULT_SOURCE_MAP, use_container_width=True)


# =========================================================
# SIMULASI DASAR
# =========================================================
with tabs[7]:
    st.subheader("Simulasi Dasar dan Penambahbaikan")

    tambah_pegawai = st.slider("Simulasi penambahan kapasiti pegawai (%)", 0, 30, 10)
    tambah_latihan = st.slider("Simulasi peningkatan latihan dan kompetensi (%)", 0, 30, 10)
    tambah_digital = st.slider("Simulasi pendigitalan susulan / tele-kaunseling (%)", 0, 30, 10)

    base = ringkas(dff["Indeks_Keberkesanan_Bersepadu"])
    simulated = np.clip(base + tambah_pegawai * 0.20 + tambah_latihan * 0.25 + tambah_digital * 0.18, 0, 100)

    c1, c2 = st.columns(2)
    with c1:
        kpi("Indeks Semasa", f"{base:.1f}%", "Berdasarkan data simulasi")
    with c2:
        kpi("Indeks Selepas Simulasi", f"{simulated:.1f}%", "Anggaran impak dasar")

    policy = pd.DataFrame({
        "Cadangan": [
            "Menambah kapasiti PPsi/PPPsi di negeri berkeperluan tinggi",
            "Memperkukuh latihan kompetensi dan penyeliaan klinikal",
            "Membangunkan sistem susulan digital dan tele-kaunseling",
            "Memperkemas SOP rujukan antara agensi",
        ],
        "Keutamaan": ["Tinggi", "Tinggi", "Sederhana", "Sederhana"],
        "Sumber Data Menyokong": ["S2 + S4", "S2 + S3", "S1 + S4", "S2 + S3"],
        "Konstruk": ["K4", "K3 + K4", "K2 + K5", "K3"],
    })

    st.dataframe(policy, use_container_width=True)
