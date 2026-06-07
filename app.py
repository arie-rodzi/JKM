import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from io import BytesIO
from datetime import datetime
import textwrap
import re

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Dashboard Psikologi Kaunseling JKM",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin2026"

DEFAULT_FILE = "JKM_7Sheet_Full_Simulation_Raw_Data(2).xlsx"

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
[data-testid="stSidebar"] {display:none;}
[data-testid="collapsedControl"] {display:none;}

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

.stApp {
    background:
    radial-gradient(circle at top left, rgba(255, 168, 76, .18), transparent 32%),
    radial-gradient(circle at top right, rgba(0, 184, 217, .20), transparent 35%),
    linear-gradient(135deg, #08111f 0%, #102542 38%, #231942 100%);
    color: white;
}

.block-container {
    padding-top: 1.3rem;
    max-width: 1500px;
}

.hero {
    padding: 34px 36px;
    border-radius: 30px;
    background:
    linear-gradient(135deg, rgba(255,255,255,.17), rgba(255,255,255,.06)),
    linear-gradient(120deg, rgba(255,183,3,.22), rgba(33,158,188,.18));
    border: 1px solid rgba(255,255,255,.20);
    box-shadow: 0 25px 80px rgba(0,0,0,.35);
    margin-bottom: 18px;
}

.hero h1 {
    font-size: 2.35rem;
    line-height: 1.12;
    margin: 0;
    color: #ffffff;
    letter-spacing: -.5px;
}

.hero p {
    font-size: 1.03rem;
    color: #dce8ff;
    max-width: 1050px;
    margin-top: 10px;
}

.filter-card {
    padding: 20px;
    border-radius: 24px;
    background: rgba(255,255,255,.10);
    border: 1px solid rgba(255,255,255,.18);
    box-shadow: 0 18px 45px rgba(0,0,0,.25);
    margin-bottom: 18px;
}

.kpi {
    padding: 22px;
    border-radius: 24px;
    min-height: 132px;
    background: linear-gradient(135deg, rgba(255,255,255,.18), rgba(255,255,255,.07));
    border: 1px solid rgba(255,255,255,.20);
    box-shadow: 0 18px 55px rgba(0,0,0,.25);
}

.kpi .label {
    color: #dbeafe;
    font-size: .86rem;
    letter-spacing: .6px;
    text-transform: uppercase;
}

.kpi .value {
    color: #ffffff;
    font-size: 2.35rem;
    font-weight: 900;
    margin-top: 8px;
}

.kpi .sub {
    color: #ffd166;
    font-size: .86rem;
    margin-top: 4px;
}

.section {
    padding: 24px;
    border-radius: 26px;
    background: rgba(255,255,255,.09);
    border: 1px solid rgba(255,255,255,.16);
    box-shadow: 0 20px 60px rgba(0,0,0,.25);
    margin-top: 18px;
}

.section h2, .section h3 {
    color: white;
    margin-top: 0;
}

.audit {
    margin-top: 9px;
    padding: 14px 16px;
    border-radius: 16px;
    background: rgba(255, 209, 102, .12);
    border-left: 5px solid #ffd166;
    color: #fff6d8;
    font-size: .92rem;
    line-height: 1.45;
}

.intervention {
    padding: 18px;
    border-radius: 20px;
    background: linear-gradient(135deg, rgba(255,107,107,.18), rgba(72,149,239,.15));
    border: 1px solid rgba(255,255,255,.17);
    margin-bottom: 12px;
}

.good {
    color: #6ee7b7;
    font-weight: 800;
}

.warn {
    color: #ffd166;
    font-weight: 800;
}

.bad {
    color: #ff8fab;
    font-weight: 800;
}

div[data-testid="stMetricValue"] {
    color: white;
}

.stButton button, .stDownloadButton button {
    border-radius: 15px;
    border: 0;
    background: linear-gradient(135deg, #ffb703, #fb8500);
    color: #111827;
    font-weight: 900;
    padding: .75rem 1.1rem;
}

.stSelectbox label, .stFileUploader label, .stTextInput label {
    color: #ffffff !important;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# BASIC FUNCTIONS
# ============================================================

def safe_mean(df, cols):
    cols = [c for c in cols if c in df.columns]
    if not cols:
        return pd.Series(np.nan, index=df.index)
    return df[cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)

def cronbach_alpha(df_items):
    df_items = df_items.apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all")
    if df_items.shape[1] < 2:
        return np.nan
    df_items = df_items.fillna(df_items.mean())
    item_var = df_items.var(axis=0, ddof=1).sum()
    total_var = df_items.sum(axis=1).var(ddof=1)
    k = df_items.shape[1]
    if total_var == 0 or np.isnan(total_var):
        return np.nan
    return (k / (k - 1)) * (1 - item_var / total_var)

def get_item_cols(df):
    return [
        c for c in df.columns
        if re.match(r"^(K\d+[A-Z]\d+|SQ\d+|B\d+|T2_\d+|T3_\d+|K1O\d+)$", str(c))
    ]

def group_dimension_columns(df):
    item_cols = get_item_cols(df)
    groups = {}

    for c in item_cols:
        c = str(c)

        if c.startswith("K1O"):
            key = "Outcome / Perubahan Klien"
        elif c.startswith("SQ"):
            key = "Kepuasan Sistem"
        elif c.startswith("T2_"):
            key = "Proses Susulan T2"
        elif c.startswith("T3_"):
            key = "Kelestarian T3"
        elif re.match(r"^B\d+", c):
            key = "Outcome Teras T1"
        else:
            m = re.match(r"^(K\d+[A-Z])", c)
            key = m.group(1) if m else c[:3]

        groups.setdefault(key, []).append(c)

    label_map = {
        "K2A": "Akses & Kebolehcapaian",
        "K2B": "Komunikasi Perkhidmatan",
        "K2C": "Hubungan Terapeutik",
        "K2D": "Hak, Etika & Keselamatan",
        "K2E": "Kesesuaian Intervensi",
        "K2F": "Kesan & Perubahan Klien",
        "K3A": "Keberkesanan Intervensi Pegawai",
        "K3B": "Kapasiti & Kompetensi Pegawai",
        "K3C": "Pengurusan Kes Pegawai",
        "K4A": "SOP & Tadbir Urus",
        "K4B": "Kolaborasi Dalaman",
        "K4C": "Kualiti Penyampaian",
        "K4D": "Kesedaran Peranan",
        "K4E": "Sokongan Organisasi",
        "K4F": "Pematuhan Etika",
        "K4G": "Koordinasi Sistem",
        "K4H": "Data & Dashboard",
        "K5A": "Keperluan Penambahbaikan Pegawai",
        "K5B": "Keperluan Penambahbaikan Warga JKM"
    }

    return {label_map.get(k, k): v for k, v in groups.items()}

def classify_score(x):
    if pd.isna(x):
        return "Tiada data"
    if x >= 4.0:
        return "Kuat"
    if x >= 3.4:
        return "Sederhana"
    return "Perlu Intervensi"

def status_color(x):
    if pd.isna(x):
        return "#94a3b8"
    if x >= 4.0:
        return "#06d6a0"
    if x >= 3.4:
        return "#ffd166"
    return "#ef476f"

def wrap_text(text, width=95):
    return "\n".join(textwrap.wrap(str(text), width=width))

# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(show_spinner=False)
def load_excel(file):
    xls = pd.ExcelFile(file)
    sheets = {s: pd.read_excel(file, sheet_name=s) for s in xls.sheet_names}
    return sheets

def standardise_quant(sheets):
    frames = []

    mapping = {
        "S1_Quant_Raw": "Klien",
        "S2_Quant_Raw": "Pegawai",
        "S3_Quant_Raw": "Warga JKM",
        "T123_Pilot_Raw": "Klien"
    }

    for sheet, respondent_type in mapping.items():
        if sheet in sheets:
            df = sheets[sheet].copy()
            df["Jenis Responden"] = respondent_type
            df["Sumber Data"] = sheet
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True, sort=False)

def standardise_qual(sheets):
    frames = []

    mapping = {
        "Q1_Client_Raw": "Klien",
        "Q2_Officer_Raw": "Pegawai",
        "Q3_System_Raw": "Warga JKM"
    }

    for sheet, respondent_type in mapping.items():
        if sheet in sheets:
            df = sheets[sheet].copy()
            df["Jenis Responden"] = respondent_type
            df["Sumber Data"] = sheet
            frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True, sort=False)

# ============================================================
# ADMIN LOGIN ONLY
# ============================================================

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "uploaded_excel" not in st.session_state:
    st.session_state.uploaded_excel = None

st.markdown("""
<div class="hero">
<h1>Dashboard Penilaian Perkhidmatan Psikologi dan Kaunseling JKM</h1>
<p>
Sistem analitik bersepadu untuk menilai dapatan kuantitatif, kualitatif, SEM ringkas,
RE-AIM, CMO, simulasi impak dan cadangan intervensi berdasarkan filter Zon, Negeri dan Jenis Responden.
</p>
</div>
""", unsafe_allow_html=True)

with st.expander("🔐 Admin sahaja: login untuk upload data"):
    if not st.session_state.admin_logged:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            username = st.text_input("Username admin")
        with c2:
            password = st.text_input("Password admin", type="password")
        with c3:
            st.write("")
            st.write("")
            if st.button("Login Admin"):
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.admin_logged = True
                    st.success("Admin berjaya login. Modul upload data dibuka.")
                    st.rerun()
                else:
                    st.error("Username atau password salah.")
    else:
        st.success("Admin aktif. Upload data dibenarkan.")
        uploaded_file = st.file_uploader(
            "Upload fail Excel data JKM",
            type=["xlsx"],
            help="Hanya admin boleh upload atau tukar data."
        )
        if uploaded_file is not None:
            st.session_state.uploaded_excel = uploaded_file
            st.success("Fail berjaya dimuat naik. Dashboard menggunakan data baharu.")

        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Reset data kepada fail asal"):
                st.session_state.uploaded_excel = None
                st.success("Data telah direset.")
                st.rerun()
        with c2:
            if st.button("Logout Admin"):
                st.session_state.admin_logged = False
                st.rerun()

# ============================================================
# LOAD DATA
# ============================================================

try:
    data_source = st.session_state.uploaded_excel if st.session_state.uploaded_excel is not None else DEFAULT_FILE
    sheets = load_excel(data_source)
except Exception:
    st.error("Data belum tersedia. Sila login admin dan upload fail Excel.")
    st.stop()

df_all = standardise_quant(sheets)
df_qual_all = standardise_qual(sheets)

if df_all.empty:
    st.error("Tiada data kuantitatif dikesan.")
    st.stop()

# ============================================================
# FILTER ONLY THREE DROPDOWNS
# ============================================================

st.markdown('<div class="filter-card">', unsafe_allow_html=True)
st.markdown("### 🎛️ Filter Analisis Utama")

f1, f2, f3 = st.columns(3)

zone_values = ["Semua"] + sorted([x for x in df_all["Zone"].dropna().unique()])
with f1:
    selected_zone = st.selectbox("Zon", zone_values)

df_zone = df_all.copy()
if selected_zone != "Semua":
    df_zone = df_zone[df_zone["Zone"] == selected_zone]

state_values = ["Semua"] + sorted([x for x in df_zone["State"].dropna().unique()])
with f2:
    selected_state = st.selectbox("Negeri", state_values)

respondent_values = ["Semua"] + sorted([x for x in df_all["Jenis Responden"].dropna().unique()])
with f3:
    selected_type = st.selectbox("Jenis Responden", respondent_values)

st.markdown('</div>', unsafe_allow_html=True)

df = df_all.copy()
if selected_zone != "Semua":
    df = df[df["Zone"] == selected_zone]
if selected_state != "Semua":
    df = df[df["State"] == selected_state]
if selected_type != "Semua":
    df = df[df["Jenis Responden"] == selected_type]

df_qual = df_qual_all.copy()
if not df_qual.empty:
    if selected_zone != "Semua" and "Zone" in df_qual.columns:
        df_qual = df_qual[df_qual["Zone"] == selected_zone]
    if selected_state != "Semua" and "State" in df_qual.columns:
        df_qual = df_qual[df_qual["State"] == selected_state]
    if selected_type != "Semua" and "Jenis Responden" in df_qual.columns:
        df_qual = df_qual[df_qual["Jenis Responden"] == selected_type]

if df.empty:
    st.warning("Tiada data untuk kombinasi filter ini.")
    st.stop()

item_cols = get_item_cols(df)
dim_groups = group_dimension_columns(df)

for dim, cols in dim_groups.items():
    df[dim] = safe_mean(df, cols)

dimension_cols = list(dim_groups.keys())
df["Skor Keseluruhan"] = safe_mean(df, dimension_cols)

# ============================================================
# KPI BOX
# ============================================================

n = len(df)
overall = df["Skor Keseluruhan"].mean()
high_pct = (df["Skor Keseluruhan"] >= 4.0).mean() * 100
risk_pct = (df["Skor Keseluruhan"] < 3.4).mean() * 100
alpha = cronbach_alpha(df[item_cols]) if item_cols else np.nan

st.markdown("### 📌 Ringkasan KPI Berdasarkan Filter Semasa")
k1, k2, k3, k4, k5 = st.columns(5)

kpis = [
    ("Bil. Responden", f"{n:,}", "Selepas filter aktif"),
    ("Skor Purata", f"{overall:.2f}", classify_score(overall)),
    ("% Skor Kuat", f"{high_pct:.1f}%", "Skor ≥ 4.00"),
    ("% Perlu Intervensi", f"{risk_pct:.1f}%", "Skor < 3.40"),
    ("Cronbach Alpha", f"{alpha:.3f}" if not pd.isna(alpha) else "NA", "Reliability keseluruhan")
]

for col, (label, value, sub) in zip([k1, k2, k3, k4, k5], kpis):
    with col:
        st.markdown(f"""
        <div class="kpi">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div class="audit">
<b>Bagaimana KPI ini diperoleh:</b>
Sistem menapis data menggunakan tiga dropdown sahaja iaitu Zon, Negeri dan Jenis Responden.
Semua item Likert yang dikesan dalam fail Excel digabungkan mengikut konstruk/dimensi.
Skor purata ialah min bagi semua dimensi yang tersedia. Peratus skor kuat dikira berdasarkan responden
dengan skor keseluruhan ≥ 4.00, manakala kategori perlu intervensi ialah skor < 3.40.
Cronbach Alpha dikira menggunakan item-item Likert bagi menilai konsistensi dalaman instrumen.
</div>
""", unsafe_allow_html=True)

# ============================================================
# CHART HELPERS
# ============================================================

def make_bar_chart(data, x, y, title, ylabel="Skor Purata", color="#ffd166"):
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.bar(data[x].astype(str), data[y], color=color, edgecolor="white", linewidth=1.2)
    ax.set_title(title, fontsize=15, fontweight="bold")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, 5)
    ax.grid(axis="y", alpha=.25)
    ax.tick_params(axis="x", rotation=35)
    for i, v in enumerate(data[y]):
        if pd.notna(v):
            ax.text(i, v + .05, f"{v:.2f}", ha="center", fontsize=9, fontweight="bold")
    fig.tight_layout()
    return fig

def make_horizontal_bar(data, x, y, title):
    fig, ax = plt.subplots(figsize=(11, 6))
    colors = [status_color(v) for v in data[y]]
    ax.barh(data[x].astype(str), data[y], color=colors, edgecolor="white")
    ax.set_title(title, fontsize=15, fontweight="bold")
    ax.set_xlabel("Skor Purata")
    ax.set_xlim(0, 5)
    ax.grid(axis="x", alpha=.25)
    for i, v in enumerate(data[y]):
        if pd.notna(v):
            ax.text(v + .04, i, f"{v:.2f}", va="center", fontsize=9, fontweight="bold")
    fig.tight_layout()
    return fig

def show_chart_with_audit(fig, audit_text):
    st.pyplot(fig, use_container_width=True)
    st.markdown(f"""
    <div class="audit">
    <b>Bagaimana dapatan graf ini diperoleh:</b><br>{audit_text}
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# DASHBOARD ANALYSIS
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 📊 Analisis Dimensi Utama")

dim_summary = (
    df[dimension_cols]
    .mean()
    .reset_index()
    .rename(columns={"index": "Dimensi", 0: "Skor Purata"})
    .sort_values("Skor Purata", ascending=True)
)

fig_dim = make_horizontal_bar(dim_summary, "Dimensi", "Skor Purata", "Skor Purata Mengikut Dimensi")
show_chart_with_audit(
    fig_dim,
    "Setiap bar mewakili purata item Likert dalam dimensi tersebut. "
    "Contohnya, dimensi Akses & Kebolehcapaian dikira sebagai purata item-item berkaitan akses. "
    "Graf disusun daripada skor terendah kepada tertinggi supaya dimensi yang memerlukan intervensi dapat dikenal pasti dahulu."
)

st.dataframe(dim_summary, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# GROUP COMPARISON
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🧭 Perbandingan Mengikut Zon, Negeri dan Jenis Responden")

group_choice = st.selectbox(
    "Pilih pecahan perbandingan",
    ["Zone", "State", "Jenis Responden"],
    format_func=lambda x: {"Zone": "Zon", "State": "Negeri", "Jenis Responden": "Jenis Responden"}[x]
)

group_df = (
    df.groupby(group_choice, dropna=False)["Skor Keseluruhan"]
    .mean()
    .reset_index()
    .rename(columns={group_choice: "Kategori", "Skor Keseluruhan": "Skor Purata"})
    .sort_values("Skor Purata", ascending=False)
)

fig_group = make_bar_chart(
    group_df,
    "Kategori",
    "Skor Purata",
    f"Perbandingan Skor Purata Mengikut {group_choice}",
    color="#4cc9f0"
)

show_chart_with_audit(
    fig_group,
    f"Graf ini dikira dengan mengumpulkan responden berdasarkan {group_choice}. "
    "Bagi setiap kumpulan, sistem mengambil purata Skor Keseluruhan selepas filter aktif. "
    "Tujuannya ialah mengenal pasti kumpulan yang menunjukkan pencapaian lebih baik atau lebih rendah."
)

st.dataframe(group_df, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# SEM MODEL
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🔗 Model SEM Ringkas / Path Model")

sem_df = df[dimension_cols].copy()
sem_df = sem_df.dropna(axis=1, how="all")

if sem_df.shape[1] >= 3:
    target = "Skor Keseluruhan"
    predictors = dimension_cols[:]
    sem_work = df[predictors + [target]].dropna()

    if len(sem_work) >= 5:
        X = sem_work[predictors].apply(pd.to_numeric, errors="coerce")
        y = sem_work[target].apply(pd.to_numeric, errors="coerce")

        Xz = (X - X.mean()) / X.std(ddof=0)
        yz = (y - y.mean()) / y.std(ddof=0)

        path_rows = []
        for col in predictors:
            if Xz[col].std(ddof=0) > 0:
                beta = np.corrcoef(Xz[col], yz)[0, 1]
            else:
                beta = np.nan
            path_rows.append({
                "Konstruk Eksogen": col,
                "Konstruk Endogen": "Skor Keseluruhan",
                "Path Coefficient Anggaran": beta,
                "Kekuatan": "Tinggi" if abs(beta) >= .70 else "Sederhana" if abs(beta) >= .40 else "Rendah"
            })

        path_df = pd.DataFrame(path_rows).sort_values("Path Coefficient Anggaran", ascending=False)

        fig_sem, ax = plt.subplots(figsize=(12, 6))
        ax.axis("off")
        ax.set_title("Model SEM Ringkas: Dimensi → Skor Keseluruhan", fontsize=16, fontweight="bold")

        top_paths = path_df.head(6)
        y_positions = np.linspace(.82, .18, len(top_paths))

        for ypos, (_, row) in zip(y_positions, top_paths.iterrows()):
            ax.text(.05, ypos, row["Konstruk Eksogen"], bbox=dict(boxstyle="round,pad=.5", fc="#118ab2", ec="white"), color="white", fontsize=10)
            ax.annotate("", xy=(.70, .50), xytext=(.38, ypos), arrowprops=dict(arrowstyle="->", lw=2, color="#ffd166"))
            ax.text(.43, ypos + .035, f"β={row['Path Coefficient Anggaran']:.2f}", color="#111827",
                    bbox=dict(boxstyle="round,pad=.25", fc="#ffd166", ec="none"), fontsize=9)

        ax.text(.72, .47, "Skor Keseluruhan", bbox=dict(boxstyle="round,pad=.7", fc="#ef476f", ec="white"), color="white", fontsize=13, fontweight="bold")

        st.pyplot(fig_sem, use_container_width=True)

        st.markdown("""
        <div class="audit">
        <b>Bagaimana model SEM ini diperoleh:</b><br>
        Model ini ialah SEM ringkas berbentuk path model eksploratori. Setiap dimensi dijadikan konstruk eksogen,
        manakala Skor Keseluruhan dijadikan konstruk endogen. Path coefficient dianggarkan menggunakan korelasi
        piawai antara skor dimensi dengan skor keseluruhan. Nilai β yang lebih tinggi menunjukkan dimensi tersebut
        lebih kuat berkaitan dengan pencapaian keseluruhan. Ini bukan pengganti SEM penuh seperti SmartPLS/AMOS,
        tetapi cukup untuk dashboard operasi awal bagi mengenal pasti konstruk pemacu utama.
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(path_df, use_container_width=True)
    else:
        st.warning("Data tidak mencukupi untuk model SEM.")
else:
    st.warning("Dimensi tidak mencukupi untuk model SEM.")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# RE-AIM
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🎯 Kerangka RE-AIM")

reaim_map = {
    "Reach": ["Akses & Kebolehcapaian", "Outcome Teras T1"],
    "Effectiveness": ["Kesan & Perubahan Klien", "Outcome / Perubahan Klien", "Keberkesanan Intervensi Pegawai"],
    "Adoption": ["Kolaborasi Dalaman", "Kesedaran Peranan", "Sokongan Organisasi"],
    "Implementation": ["SOP & Tadbir Urus", "Kualiti Penyampaian", "Pematuhan Etika", "Pengurusan Kes Pegawai"],
    "Maintenance": ["Kelestarian T3", "Keperluan Penambahbaikan Pegawai", "Keperluan Penambahbaikan Warga JKM"]
}

reaim_rows = []
for domain, dims in reaim_map.items():
    available = [d for d in dims if d in df.columns]
    score = df[available].mean(axis=1).mean() if available else np.nan
    reaim_rows.append({
        "Domain RE-AIM": domain,
        "Skor": score,
        "Status": classify_score(score),
        "Dimensi Digunakan": ", ".join(available) if available else "Tiada dimensi sepadan"
    })

reaim_df = pd.DataFrame(reaim_rows)

fig_reaim = make_bar_chart(reaim_df, "Domain RE-AIM", "Skor", "Skor Mengikut Domain RE-AIM", color="#06d6a0")
show_chart_with_audit(
    fig_reaim,
    "Setiap domain RE-AIM dibina dengan memadankan dimensi kuantitatif kepada lima komponen: Reach, Effectiveness, Adoption, Implementation dan Maintenance. "
    "Skor domain ialah purata dimensi yang tersedia dalam dataset selepas filter aktif."
)

st.dataframe(reaim_df, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# QUALITATIVE CMO
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🧩 Analisis Kualitatif CMO")

if df_qual.empty:
    st.info("Tiada data kualitatif untuk filter semasa.")
else:
    cmo_cols = [c for c in ["CMO_Context", "CMO_Mechanism", "CMO_Outcome", "RE_AIM_Tag"] if c in df_qual.columns]

    if cmo_cols:
        for c in cmo_cols:
            st.markdown(f"### {c}")
            counts = df_qual[c].dropna().astype(str).value_counts().head(10).reset_index()
            counts.columns = ["Tema", "Bilangan"]
            if not counts.empty:
                fig_cmo = make_bar_chart(counts, "Tema", "Bilangan", f"Taburan Tema {c}", ylabel="Bilangan", color="#f72585")
                show_chart_with_audit(
                    fig_cmo,
                    f"Graf ini dikira melalui kiraan kekerapan tema dalam kolum {c}. "
                    "Tema yang paling kerap muncul menunjukkan isu, mekanisme atau outcome yang dominan dalam data kualitatif."
                )
                st.dataframe(counts, use_container_width=True)
    else:
        st.info("Kolum CMO tidak dikesan dalam data kualitatif.")

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# INTERVENTION AND SIMULATION
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🛠️ Cadangan Intervensi Mengikut Zon, Negeri dan Jenis Responden")

weak_dims = dim_summary.sort_values("Skor Purata", ascending=True).head(5)

def intervention_text(dim, score):
    if score < 3.4:
        level = "Intervensi Intensif"
        action = (
            "Laksanakan pelan pemulihan segera melalui semakan SOP, latihan pegawai, pemantauan mingguan, "
            "sesi libat urus klien/pegawai dan penetapan KPI mikro selama 3 bulan."
        )
    elif score < 4.0:
        level = "Intervensi Pengukuhan"
        action = (
            "Laksanakan penambahbaikan bersasar melalui bengkel kecil, coaching pegawai, pemurnian proses kerja, "
            "dan pemantauan bulanan sehingga skor mencapai sekurang-kurangnya 4.00."
        )
    else:
        level = "Kekalkan dan Replikasi"
        action = (
            "Kekalkan amalan semasa dan dokumentasikan sebagai amalan baik untuk direplikasi kepada zon/negeri/kumpulan responden lain."
        )

    return level, action

filter_sentence = f"Zon: {selected_zone} | Negeri: {selected_state} | Jenis Responden: {selected_type}"
st.markdown(f"**Filter semasa:** {filter_sentence}")

for _, row in weak_dims.iterrows():
    dim = row["Dimensi"]
    score = row["Skor Purata"]
    level, action = intervention_text(dim, score)

    st.markdown(f"""
    <div class="intervention">
    <h3>{dim}</h3>
    <p><b>Skor semasa:</b> {score:.2f} &nbsp; | &nbsp; <b>Tahap:</b> {level}</p>
    <p><b>Cadangan intervensi:</b> {action}</p>
    <p><b>Rasional:</b> Dimensi ini berada antara skor terendah selepas filter aktif. Oleh itu,
    intervensi dicadangkan khusus kepada kumpulan terpilih berdasarkan Zon, Negeri dan Jenis Responden,
    bukan cadangan umum seluruh negara.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 🔮 Simulasi Impak Intervensi")
increase = st.slider("Andaian peningkatan skor selepas intervensi (%)", 1, 30, 10)

sim_df = weak_dims.copy()
sim_df["Skor Selepas Simulasi"] = np.minimum(5, sim_df["Skor Purata"] * (1 + increase / 100))
sim_df["Perubahan"] = sim_df["Skor Selepas Simulasi"] - sim_df["Skor Purata"]
sim_df["Status Baharu"] = sim_df["Skor Selepas Simulasi"].apply(classify_score)

fig_sim, ax = plt.subplots(figsize=(11, 5.8))
x = np.arange(len(sim_df))
w = .36
ax.bar(x - w/2, sim_df["Skor Purata"], width=w, label="Sebelum", color="#ef476f")
ax.bar(x + w/2, sim_df["Skor Selepas Simulasi"], width=w, label="Selepas", color="#06d6a0")
ax.set_xticks(x)
ax.set_xticklabels(sim_df["Dimensi"], rotation=30, ha="right")
ax.set_ylim(0, 5)
ax.set_ylabel("Skor")
ax.set_title("Simulasi Kesan Intervensi Terhadap Dimensi Terendah", fontweight="bold")
ax.legend()
ax.grid(axis="y", alpha=.25)
fig_sim.tight_layout()

show_chart_with_audit(
    fig_sim,
    f"Simulasi ini mengambil lima dimensi terendah dan menaikkan skor mengikut andaian peningkatan {increase}%. "
    "Skor selepas simulasi dihadkan maksimum 5.00 kerana skala Likert ialah 1 hingga 5. "
    "Tujuannya ialah menunjukkan potensi impak sekiranya intervensi berjaya meningkatkan skor dimensi bermasalah."
)

st.dataframe(sim_df, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PDF REPORT
# ============================================================

def add_text_page(pdf, title, lines):
    fig = plt.figure(figsize=(8.27, 11.69))
    plt.axis("off")
    y = .95
    plt.text(.05, y, title, fontsize=18, fontweight="bold", color="#102542")
    y -= .045
    plt.text(.05, y, f"Dijana pada: {datetime.now().strftime('%d/%m/%Y %H:%M')}", fontsize=9)
    y -= .035
    for line in lines:
        wrapped = textwrap.wrap(str(line), width=92)
        for wline in wrapped:
            if y < .06:
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)
                fig = plt.figure(figsize=(8.27, 11.69))
                plt.axis("off")
                y = .95
            plt.text(.05, y, wline, fontsize=10, color="#111827")
            y -= .024
        y -= .012
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)

def generate_pdf_report():
    buffer = BytesIO()

    with PdfPages(buffer) as pdf:
        add_text_page(pdf, "Laporan Dashboard Psikologi dan Kaunseling JKM", [
            f"Filter laporan: {filter_sentence}",
            f"Bilangan responden: {n}",
            f"Skor purata keseluruhan: {overall:.3f}",
            f"Peratus skor kuat: {high_pct:.1f}%",
            f"Peratus perlu intervensi: {risk_pct:.1f}%",
            f"Cronbach Alpha: {alpha:.3f}" if not pd.isna(alpha) else "Cronbach Alpha: NA",
            "",
            "Penerangan metodologi:",
            "Laporan ini dijana berdasarkan filter aktif di dashboard. Semua dapatan kuantitatif dikira daripada item Likert yang dikenal pasti dalam data Excel. Skor dimensi ialah purata item bagi konstruk berkaitan. Skor keseluruhan ialah purata semua dimensi yang tersedia.",
            "Kategori interpretasi: skor ≥ 4.00 dianggap kuat, skor 3.40 hingga 3.99 dianggap sederhana, manakala skor < 3.40 dianggap memerlukan intervensi."
        ])

        pdf.savefig(fig_dim, bbox_inches="tight")
        pdf.savefig(fig_group, bbox_inches="tight")
        pdf.savefig(fig_reaim, bbox_inches="tight")
        pdf.savefig(fig_sim, bbox_inches="tight")

        add_text_page(pdf, "Dapatan Dimensi dan Intervensi", [
            "Dimensi terendah yang memerlukan perhatian:",
            *[
                f"{r['Dimensi']}: skor {r['Skor Purata']:.2f}. Cadangan: {intervention_text(r['Dimensi'], r['Skor Purata'])[1]}"
                for _, r in weak_dims.iterrows()
            ],
            "",
            "Audit trail:",
            "Setiap graf dalam dashboard disertakan penerangan cara pengiraan. Prinsip yang sama digunakan dalam laporan PDF ini. Graf dimensi menunjukkan purata setiap konstruk; graf perbandingan menunjukkan purata skor keseluruhan mengikut kategori; graf RE-AIM memetakan konstruk kepada lima domain RE-AIM; graf simulasi menunjukkan perubahan skor andaian selepas intervensi."
        ])

        if 'path_df' in globals():
            add_text_page(pdf, "Model SEM Ringkas", [
                "Model SEM ringkas dibina sebagai path model eksploratori. Konstruk eksogen ialah dimensi penilaian. Konstruk endogen ialah Skor Keseluruhan.",
                "Path coefficient dianggarkan menggunakan korelasi piawai antara dimensi dengan skor keseluruhan.",
                "",
                *[
                    f"{r['Konstruk Eksogen']} → Skor Keseluruhan: β = {r['Path Coefficient Anggaran']:.3f}, kekuatan {r['Kekuatan']}"
                    for _, r in path_df.head(10).iterrows()
                ]
            ])

        add_text_page(pdf, "RE-AIM, CMO dan Simulasi", [
            "RE-AIM digunakan untuk menterjemahkan dapatan kepada lima domain operasi: Reach, Effectiveness, Adoption, Implementation dan Maintenance.",
            "CMO digunakan untuk memahami Context, Mechanism dan Outcome daripada data kualitatif.",
            f"Simulasi intervensi menggunakan andaian peningkatan {increase}% bagi dimensi terendah.",
            "Laporan ini boleh dicetak terus melalui butang download PDF dan fungsi print pada PDF viewer."
        ])

    buffer.seek(0)
    return buffer

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🖨️ Laporan PDF Lengkap Berdasarkan Filter Semasa")

st.markdown("""
<div class="audit">
<b>Kandungan PDF:</b>
KPI, graf dimensi, graf perbandingan, audit trail, penerangan formula,
model SEM ringkas, RE-AIM, CMO, simulasi dan intervensi mengikut filter aktif.
Selepas download, buka PDF dan tekan Ctrl+P untuk print.
</div>
""", unsafe_allow_html=True)

pdf_buffer = generate_pdf_report()

st.download_button(
    label="📄 Download / Print Laporan PDF Lengkap",
    data=pdf_buffer,
    file_name=f"Laporan_JKM_{selected_zone}_{selected_state}_{selected_type}.pdf".replace(" ", "_"),
    mime="application/pdf"
)

st.markdown('</div>', unsafe_allow_html=True)
