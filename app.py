import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="Sistem Analitik Psikologi dan Kaunseling JKM",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
.block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
.main-title {
    background: linear-gradient(135deg,#061B3A,#123C69,#0E7C7B);
    padding: 35px;
    border-radius: 24px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}
.card {
    background: white;
    padding: 22px;
    border-radius: 18px;
    box-shadow: 0 6px 22px rgba(0,0,0,0.08);
    border: 1px solid #edf0f5;
}
.kpi {
    background: linear-gradient(135deg,#EAF4FF,#FFFFFF);
    padding: 22px;
    border-radius: 18px;
    border-left: 7px solid #123C69;
    box-shadow: 0 5px 16px rgba(0,0,0,0.07);
}
.kpi h2 {margin:0; color:#0B1F3A;}
.kpi p {margin:0; color:#566;}
.adminbox {
    background: linear-gradient(135deg,#FFF7D6,#FFFFFF);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid #C9A227;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# LOGIN
# =====================================================
ADMIN_USER = "admin"
ADMIN_PASS = "jkm2026"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "data" not in st.session_state:
    st.session_state.data = {}

def login_page():
    st.markdown("""
    <div class="main-title">
        <h1>SISTEM ANALITIK PSIKOLOGI DAN KAUNSELING JKM MALAYSIA</h1>
        <h4>Dashboard Kuantitatif, Kualitatif, CMO, RE-AIM, Donabedian dan T1–T2–T3</h4>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1.2,1])
    with c2:
        st.markdown('<div class="adminbox">', unsafe_allow_html=True)
        st.subheader("Log Masuk Admin")
        username = st.text_input("Nama Pengguna")
        password = st.text_input("Kata Laluan", type="password")
        if st.button("Masuk Sistem", use_container_width=True):
            if username == ADMIN_USER and password == ADMIN_PASS:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Nama pengguna atau kata laluan tidak tepat.")
        st.caption("Default: admin / jkm2026")
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_page()
    st.stop()

# =====================================================
# HELPERS
# =====================================================
def safe_mean(df, cols):
    valid = [c for c in cols if c in df.columns]
    if not valid:
        return np.nan
    return df[valid].apply(pd.to_numeric, errors="coerce").mean(axis=1)

def percent_score(series):
    return (series.mean() / 5) * 100 if len(series.dropna()) else np.nan

def cronbach_alpha(df_items):
    df_items = df_items.apply(pd.to_numeric, errors="coerce").dropna()
    k = df_items.shape[1]
    if k <= 1 or df_items.empty:
        return np.nan
    item_var = df_items.var(axis=0, ddof=1).sum()
    total_var = df_items.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return np.nan
    return (k / (k - 1)) * (1 - item_var / total_var)

def kpi_card(title, value, note=""):
    st.markdown(f"""
    <div class="kpi">
        <p>{title}</p>
        <h2>{value}</h2>
        <small>{note}</small>
    </div>
    """, unsafe_allow_html=True)

def read_excel(uploaded_file):
    xls = pd.ExcelFile(uploaded_file)
    return {sheet: pd.read_excel(uploaded_file, sheet_name=sheet) for sheet in xls.sheet_names}

def find_sheet(data, possible_names):
    for name in possible_names:
        if name in data:
            return data[name]
    return pd.DataFrame()

def filter_df(df):
    if df.empty:
        return df

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        negeri_col = "Negeri" if "Negeri" in df.columns else None
        negeri = st.selectbox(
            "Negeri",
            ["Semua"] + sorted(df[negeri_col].dropna().unique().tolist()) if negeri_col else ["Semua"]
        )

    with c2:
        zon_col = "Zon" if "Zon" in df.columns else None
        zon = st.selectbox(
            "Zon",
            ["Semua"] + sorted(df[zon_col].dropna().unique().tolist()) if zon_col else ["Semua"]
        )

    with c3:
        client_col = None
        for col in ["Jenis Klien", "Kategori Klien", "Kategori Klien JKM"]:
            if col in df.columns:
                client_col = col
                break
        jenis_klien = st.selectbox(
            "Jenis Klien",
            ["Semua"] + sorted(df[client_col].dropna().unique().tolist()) if client_col else ["Semua"]
        )

    with c4:
        respondent_col = None
        for col in ["Jenis Responden", "Responden Type", "Kategori Responden", "Jawatan"]:
            if col in df.columns:
                respondent_col = col
                break
        jenis_responden = st.selectbox(
            "Jenis Responden",
            ["Semua"] + sorted(df[respondent_col].dropna().unique().tolist()) if respondent_col else ["Semua"]
        )

    out = df.copy()
    if negeri_col and negeri != "Semua":
        out = out[out[negeri_col] == negeri]
    if zon_col and zon != "Semua":
        out = out[out[zon_col] == zon]
    if client_col and jenis_klien != "Semua":
        out = out[out[client_col] == jenis_klien]
    if respondent_col and jenis_responden != "Semua":
        out = out[out[respondent_col] == jenis_responden]
    return out

# =====================================================
# MAPPING ITEM
# =====================================================
S1_MAP = {
    "K2A Akses dan Rujukan": [f"K2A{i}" for i in range(1,7)],
    "K2B Komunikasi": [f"K2B{i}" for i in range(1,7)],
    "K2C Hubungan Terapeutik": [f"K2C{i}" for i in range(1,8)],
    "K2D Budaya dan Hak": [f"K2D{i}" for i in range(1,8)],
    "K2E Kesinambungan": [f"K2E{i}" for i in range(1,7)],
    "K2F Pemerkasaan": [f"K2F{i}" for i in range(1,8)],
    "K1 Outcome Klien": [f"K1O{i}" for i in range(1,8)]
}

S2_MAP = {
    "K3A Faktor Kejayaan": [f"K3A{i}" for i in range(1,7)],
    "K3B Halangan Keberkesanan": [f"K3B{i}" for i in range(1,7)],
    "K3C Keciciran": [f"K3C{i}" for i in range(1,7)],
    "K4A Perjawatan dan Beban Kerja": [f"K4A{i}" for i in range(1,7)],
    "K4B Capaian dan Ekuiti": [f"K4B{i}" for i in range(1,7)],
    "K4C Kapasiti Institusi": [f"K4C{i}" for i in range(1,7)],
    "K5 Penambahbaikan": [f"K5A{i}" for i in range(1,7)]
}

S3_MAP = {
    "K4D Kefahaman Peranan": [f"K4D{i}" for i in range(1,7)],
    "K4E Kesiapsiagaan Rujukan": [f"K4E{i}" for i in range(1,7)],
    "K4F Koordinasi Antara Unit": [f"K4F{i}" for i in range(1,7)],
    "K4G Sokongan Organisasi": [f"K4G{i}" for i in range(1,7)],
    "K4H Etika dan Kerahsiaan": [f"K4H{i}" for i in range(1,7)],
    "K5B Penambahbaikan Sistem": [f"K5B{i}" for i in range(1,7)]
}

QUESTION_TEXT = {
    "K2A1": "Saya mudah mendapatkan maklumat mengenai perkhidmatan ini.",
    "K2A2": "Proses mendapatkan temu janji adalah mudah.",
    "K2A3": "Tempoh menunggu adalah munasabah.",
    "K2A4": "Lokasi perkhidmatan mudah diakses.",
    "K2A5": "Masa temu janji sesuai.",
    "K2A6": "Kemudahan membantu saya hadir sesi.",
}

THEORY_MAP = {
    "K2A Akses dan Rujukan": ["RE-AIM: Reach", "Donabedian: Structure", "CMO: Context"],
    "K2B Komunikasi": ["WHO Person-Centred Care", "CMO: Mechanism"],
    "K2C Hubungan Terapeutik": ["Realist Evaluation", "CMO: Mechanism"],
    "K2D Budaya dan Hak": ["WHO Rights-Based", "Bronfenbrenner", "CMO: Context/Mechanism"],
    "K2E Kesinambungan": ["RE-AIM: Maintenance", "Donabedian: Process"],
    "K2F Pemerkasaan": ["WHO Recovery-Oriented", "CMO: Mechanism"],
    "K1 Outcome Klien": ["Realist Evaluation: Outcome", "Donabedian: Outcome"]
}

# =====================================================
# ANALYSIS
# =====================================================
def construct_scores(df, mapping):
    result = pd.DataFrame(index=df.index)
    for construct, cols in mapping.items():
        result[construct] = safe_mean(df, cols)
    result["Overall Index"] = result.mean(axis=1)
    return result

def show_quant_dashboard(df, mapping, title):
    st.subheader(title)

    if df.empty:
        st.warning("Tiada data dijumpai.")
        return

    df = filter_df(df)
    scores = construct_scores(df, mapping)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Bilangan Responden", f"{len(df)}", "Selepas filter")
    with c2:
        kpi_card("Overall Index", f"{percent_score(scores['Overall Index']):.1f}%", "Purata semua konstruk")
    with c3:
        best = scores.mean().drop("Overall Index").idxmax()
        kpi_card("Konstruk Tertinggi", best, f"{percent_score(scores[best]):.1f}%")
    with c4:
        low = scores.mean().drop("Overall Index").idxmin()
        kpi_card("Konstruk Terendah", low, f"{percent_score(scores[low]):.1f}%")

    mean_scores = scores.drop(columns=["Overall Index"]).mean().reset_index()
    mean_scores.columns = ["Konstruk", "Skor Min"]

    fig = px.bar(
        mean_scores,
        x="Skor Min",
        y="Konstruk",
        orientation="h",
        title="Purata Skor Konstruk",
        text=mean_scores["Skor Min"].round(2)
    )
    fig.update_layout(height=480)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Bagaimana keputusan ini dikira?"):
        st.markdown("""
        **Langkah kiraan:**

        1. Setiap item menggunakan skala 1 hingga 5.  
        2. Skor konstruk dikira melalui purata item dalam konstruk tersebut.  
        3. Overall Index ialah purata semua konstruk.  
        4. Skor peratus dikira sebagai:

        \\[
        Skor(\\%) = \\frac{Skor\\ Min}{5} \\times 100
        \\]
        """)

        selected_construct = st.selectbox("Pilih konstruk untuk audit trail", list(mapping.keys()))
        cols = mapping[selected_construct]
        valid_cols = [c for c in cols if c in df.columns]

        st.write("**Item digunakan:**", valid_cols)
        st.write("**Teori / Kerangka:**", THEORY_MAP.get(selected_construct, ["Kerangka berkaitan dalam sistem"]))

        q_table = pd.DataFrame({
            "Kod Item": valid_cols,
            "Soalan": [QUESTION_TEXT.get(c, "Soalan berdasarkan kod item dalam instrumen.") for c in valid_cols]
        })
        st.dataframe(q_table, use_container_width=True)

        alpha = cronbach_alpha(df[valid_cols]) if valid_cols else np.nan
        st.metric("Cronbach Alpha", f"{alpha:.3f}" if not np.isnan(alpha) else "Tidak mencukupi")

    with st.expander("Maksud graph"):
        st.markdown("""
        Graph bar menunjukkan purata skor bagi setiap konstruk.  
        Bar yang lebih panjang bermaksud konstruk tersebut mempunyai skor yang lebih tinggi.  
        Konstruk paling rendah perlu diberi perhatian untuk cadangan intervensi.
        """)

    st.markdown("### Jadual Skor Konstruk")
    st.dataframe(scores.round(3), use_container_width=True)

def show_framework_dashboard(s1, s2, s3):
    st.subheader("Kerangka Keseluruhan: CMO, RE-AIM dan Donabedian")

    values = []

    if not s1.empty:
        s1s = construct_scores(s1, S1_MAP)
        context = np.nanmean([s1s.get("K2A Akses dan Rujukan", pd.Series()).mean(),
                              s1s.get("K2D Budaya dan Hak", pd.Series()).mean()])
        mechanism = np.nanmean([s1s.get("K2B Komunikasi", pd.Series()).mean(),
                                s1s.get("K2C Hubungan Terapeutik", pd.Series()).mean(),
                                s1s.get("K2F Pemerkasaan", pd.Series()).mean()])
        outcome = s1s.get("K1 Outcome Klien", pd.Series()).mean()
        values += [
            {"Kerangka": "CMO", "Komponen": "Context", "Skor": context},
            {"Kerangka": "CMO", "Komponen": "Mechanism", "Skor": mechanism},
            {"Kerangka": "CMO", "Komponen": "Outcome", "Skor": outcome},
        ]

    if not s1.empty:
        s1s = construct_scores(s1, S1_MAP)
        values += [
            {"Kerangka": "RE-AIM", "Komponen": "Reach", "Skor": s1s["K2A Akses dan Rujukan"].mean()},
            {"Kerangka": "RE-AIM", "Komponen": "Effectiveness", "Skor": s1s["K1 Outcome Klien"].mean()},
            {"Kerangka": "RE-AIM", "Komponen": "Implementation", "Skor": s1s[["K2B Komunikasi","K2C Hubungan Terapeutik"]].mean(axis=1).mean()},
            {"Kerangka": "RE-AIM", "Komponen": "Maintenance", "Skor": s1s["K2E Kesinambungan"].mean()},
        ]

    if not s2.empty:
        s2s = construct_scores(s2, S2_MAP)
        values += [
            {"Kerangka": "Donabedian", "Komponen": "Structure", "Skor": s2s[["K4A Perjawatan dan Beban Kerja","K4C Kapasiti Institusi"]].mean(axis=1).mean()},
            {"Kerangka": "Donabedian", "Komponen": "Process", "Skor": s2s[["K3A Faktor Kejayaan","K3B Halangan Keberkesanan"]].mean(axis=1).mean()},
        ]

    if not values:
        st.warning("Tiada data untuk kerangka.")
        return

    fw = pd.DataFrame(values)
    fw["Skor %"] = fw["Skor"] / 5 * 100

    fig = px.bar(
        fw,
        x="Komponen",
        y="Skor %",
        color="Kerangka",
        barmode="group",
        title="Skor Keseluruhan Mengikut Kerangka"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(fw.round(2), use_container_width=True)

    with st.expander("Audit Trail Kerangka"):
        st.markdown("""
        **CMO**
        - Context: latar klien, akses, budaya, jenis kes.
        - Mechanism: komunikasi, hubungan terapeutik, pemerkasaan.
        - Outcome: perubahan klien.

        **RE-AIM**
        - Reach: capaian perkhidmatan.
        - Effectiveness: perubahan outcome.
        - Implementation: pelaksanaan perkhidmatan.
        - Maintenance: kesinambungan dan susulan.

        **Donabedian**
        - Structure: sumber, perjawatan, ruang, sistem.
        - Process: proses intervensi, SOP, rujukan.
        - Outcome: hasil perkhidmatan.
        """)

def show_t123(df):
    st.subheader("Analisis Pilot T1–T2–T3")

    if df.empty:
        st.warning("Tiada data T1–T2–T3.")
        return

    core = [f"B{i}" for i in range(1,11)]
    if not set(core).issubset(df.columns):
        st.warning("Kolum B1 hingga B10 tidak lengkap.")
        return

    id_col = "Kod Responden" if "Kod Responden" in df.columns else df.columns[0]
    t_col = "Titik Masa" if "Titik Masa" in df.columns else "T"

    df["Outcome"] = safe_mean(df, core)

    counts = df[t_col].value_counts().to_dict()
    c1, c2, c3 = st.columns(3)
    c1.metric("T1", counts.get("T1", 0))
    c2.metric("T2", counts.get("T2", 0))
    c3.metric("T3", counts.get("T3", 0))

    trend = df.groupby(t_col)["Outcome"].mean().reset_index()
    fig = px.line(trend, x=t_col, y="Outcome", markers=True, title="Trend Outcome T1–T2–T3")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Bagaimana T1–T2–T3 dikira?"):
        st.markdown("""
        Item B1 hingga B10 digunakan sama pada T1, T2 dan T3.

        \\[
        Outcome_T = \\frac{B1+B2+...+B10}{10}
        \\]

        Perubahan dikira sebagai:

        \\[
        \\Delta_{T2-T1}=Outcome_{T2}-Outcome_{T1}
        \\]
        """)

def show_qual(df, title):
    st.subheader(title)
    if df.empty:
        st.warning("Tiada data kualitatif.")
        return

    text_cols = [c for c in df.columns if c.lower().startswith("q") or c.lower().startswith("sq")]
    if not text_cols:
        text_cols = df.select_dtypes(include="object").columns.tolist()

    all_text = " ".join(df[text_cols].astype(str).values.flatten()).lower()
    words = pd.Series(all_text.split())
    stop = {"dan","yang","di","ke","dalam","ini","itu","saya","kami","untuk","dengan","ada","tidak","lebih"}
    words = words[~words.isin(stop)]
    freq = words.value_counts().head(20).reset_index()
    freq.columns = ["Kata Kunci", "Kekerapan"]

    fig = px.bar(freq, x="Kekerapan", y="Kata Kunci", orientation="h", title="Kekerapan Kata Kunci")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Bagaimana analisis kualitatif ini dibuat?"):
        st.markdown("""
        Sistem menggabungkan jawapan terbuka, membersihkan perkataan umum,
        kemudian mengira kekerapan kata kunci utama.

        Dapatan ini digunakan sebagai petunjuk awal tema, bukan menggantikan analisis tematik manual/NVivo.
        """)

    st.dataframe(df, use_container_width=True)

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<div class="main-title">
    <h1>SISTEM ANALITIK PSIKOLOGI DAN KAUNSELING JKM MALAYSIA</h1>
    <h4>Admin Upload • Analitik Kuantitatif • Kualitatif • CMO • RE-AIM • Donabedian • Audit Trail</h4>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs([
    "Muat Naik Data",
    "Dashboard Utama",
    "S1 Klien",
    "S2 Pegawai",
    "S3 Warga JKM",
    "Kualitatif",
    "T1–T2–T3",
    "Audit Trail & Formula"
])

# =====================================================
# TAB UPLOAD
# =====================================================
with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Muat Naik Dataset Excel 7 Sheet")

    uploaded = st.file_uploader(
        "Pilih fail Excel (.xlsx)",
        type=["xlsx"],
        help="Pastikan Excel mengandungi sheet S1_Quant, S2_Quant, S3_Quant, Q1_Qual, Q2_Qual, Q3_Qual dan T123_Pilot."
    )

    if uploaded:
        try:
            st.session_state.data = read_excel(uploaded)
            st.success("Fail berjaya dimuat naik dan dibaca.")
            st.write("Sheet dijumpai:", list(st.session_state.data.keys()))
        except Exception as e:
            st.error(f"Ralat membaca fail: {e}")

    st.markdown("""
    **Nama sheet yang disyorkan:**
    - S1_Quant
    - S2_Quant
    - S3_Quant
    - Q1_Qual
    - Q2_Qual
    - Q3_Qual
    - T123_Pilot
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# GET SHEETS
# =====================================================
data = st.session_state.data
s1 = find_sheet(data, ["S1_Quant", "S1", "S1 Quant"])
s2 = find_sheet(data, ["S2_Quant", "S2", "S2 Quant"])
s3 = find_sheet(data, ["S3_Quant", "S3", "S3 Quant"])
q1 = find_sheet(data, ["Q1_Qual", "Q1", "S1_Qual"])
q2 = find_sheet(data, ["Q2_Qual", "Q2", "S2_Qual"])
q3 = find_sheet(data, ["Q3_Qual", "Q3", "S3_Qual"])
t123 = find_sheet(data, ["T123_Pilot", "T1T2T3", "T123"])

# =====================================================
# DASHBOARD
# =====================================================
with tabs[1]:
    show_framework_dashboard(s1, s2, s3)

with tabs[2]:
    show_quant_dashboard(s1, S1_MAP, "S1: Analitik Klien")

with tabs[3]:
    show_quant_dashboard(s2, S2_MAP, "S2: Analitik Pegawai PPsi / PPPsi")

with tabs[4]:
    show_quant_dashboard(s3, S3_MAP, "S3: Analitik Warga JKM")

with tabs[5]:
    qtab1, qtab2, qtab3 = st.tabs(["Q1 Klien", "Q2 Pegawai", "Q3 Warga JKM"])
    with qtab1:
        show_qual(q1, "Q1 Kualitatif Klien")
    with qtab2:
        show_qual(q2, "Q2 Kualitatif Pegawai")
    with qtab3:
        show_qual(q3, "Q3 Kualitatif Warga JKM")

with tabs[6]:
    show_t123(t123)

with tabs[7]:
    st.subheader("Audit Trail & Formula")

    st.markdown("""
    Sistem ini menggunakan aliran:

    **Set Soalan → Konstruk → Teori → Kerangka → Formula → Skor → Interpretasi → Cadangan Intervensi**

    ### Contoh:
    **K2A Akses dan Rujukan**
    - Sumber: S1 Klien
    - Item: K2A1 hingga K2A6
    - Teori: RE-AIM Reach, Donabedian Structure, CMO Context
    - Formula:

    \\[
    K2A = \\frac{K2A1+K2A2+K2A3+K2A4+K2A5+K2A6}{6}
    \\]

    - Skor peratus:

    \\[
    K2A(\\%) = \\frac{K2A}{5}\\times100
    \\]

    ### Interpretasi:
    - 1.00–2.00 = Rendah
    - 2.01–3.00 = Sederhana rendah
    - 3.01–4.00 = Sederhana tinggi
    - 4.01–5.00 = Tinggi
    """)

    st.info("Semua graf dalam sistem ini boleh ditafsir berdasarkan konstruk, item, teori dan kerangka yang dipetakan.")
