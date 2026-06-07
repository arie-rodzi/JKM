import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime
import html
import re
from pathlib import Path

st.set_page_config(
    page_title="JKM Psychological Services DSS-IIS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin2026"
DEFAULT_FILES = [
    "JKM_7Sheet_Full_Simulation_Raw_Data(1).xlsx",
    "JKM_7Sheet_Full_Simulation_Raw_Data(2).xlsx",
    "JKM_7Sheet_Full_Simulation_Raw_Data.xlsx",
]

# =====================================================
# CSS PREMIUM + HIDE SIDEBAR + TRANSPARENT CHART
# =====================================================
st.markdown("""
<style>
[data-testid="stSidebar"] {display:none !important;}
[data-testid="collapsedControl"] {display:none !important;}
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.stApp {
    background:
    radial-gradient(circle at 8% 8%, rgba(255, 184, 0, .32), transparent 28%),
    radial-gradient(circle at 92% 8%, rgba(0, 245, 212, .28), transparent 32%),
    radial-gradient(circle at 50% 100%, rgba(255, 77, 109, .22), transparent 35%),
    linear-gradient(135deg, #061826 0%, #102542 42%, #231942 100%);
    color: #ffffff;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 3rem;
    max-width: 1550px;
}

.hero, .section, .filter-card, .soft-card {
    border-radius: 28px;
    background: linear-gradient(135deg, rgba(255,255,255,.15), rgba(255,255,255,.055));
    border: 1px solid rgba(255,255,255,.20);
    box-shadow: 0 22px 70px rgba(0,0,0,.32);
    margin-bottom: 18px;
    backdrop-filter: blur(18px);
}

.hero {padding: 34px 38px;}
.section, .filter-card, .soft-card {padding: 24px;}

.hero h1 {
    font-size: 2.25rem;
    margin: 0;
    color: #ffffff;
    letter-spacing: -.5px;
}
.hero p {
    color: #dbeafe;
    font-size: 1.02rem;
    max-width: 1150px;
    line-height: 1.55;
}

.kpi {
    padding: 22px;
    border-radius: 24px;
    min-height: 138px;
    background: linear-gradient(135deg, rgba(255,255,255,.20), rgba(255,255,255,.07));
    border: 1px solid rgba(255,255,255,.22);
    box-shadow: 0 18px 45px rgba(0,0,0,.22);
}
.kpi .label {color:#cbd5e1; font-size:.86rem; font-weight:800; text-transform:uppercase; letter-spacing:.5px;}
.kpi .value {color:#ffffff; font-size:2rem; font-weight:950; margin-top:8px;}
.kpi .sub {color:#dbeafe; font-size:.82rem; margin-top:6px;}

.note-blue, .audit-box, .intervention-box {
    padding: 18px 20px;
    border-radius: 20px;
    color: #e0f2fe;
    line-height: 1.55;
    margin-top: 12px;
}
.note-blue {background:rgba(14,165,233,.13); border:1px solid rgba(125,211,252,.35);}
.audit-box {background:rgba(255,209,102,.12); border:1px solid rgba(255,209,102,.35); color:#fff7d6;}
.intervention-box {background:rgba(0,245,212,.10); border:1px solid rgba(0,245,212,.30); color:#d9fffb;}

/* Remove white chart background */
div[data-testid="stAltairChart"],
div[data-testid="stAltairChart"] > div,
div[data-testid="stVegaLiteChart"],
div[data-testid="stVegaLiteChart"] > div,
canvas, iframe {
    background: transparent !important;
}
.vega-embed, .vega-embed canvas, .vega-embed svg {
    background: transparent !important;
}

[data-testid="stDataFrame"] {
    background: rgba(255,255,255,.06) !important;
    border-radius: 18px;
}

h1, h2, h3, h4, p, label, span, div {color: inherit;}
.stSelectbox label, .stTextInput label, .stFileUploader label {color:#ffffff !important; font-weight:700;}
.stButton button, .stDownloadButton button {
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,.25) !important;
    background: linear-gradient(135deg, #00f5d4, #ffd166) !important;
    color: #07131f !important;
    font-weight: 900 !important;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def html_escape(x):
    return html.escape(str(x))

@st.cache_data(show_spinner=False)
def load_excel_cached(file_bytes, file_name):
    return pd.read_excel(file_bytes, sheet_name=None)

def load_excel(source):
    if hasattr(source, "read"):
        source.seek(0)
        return load_excel_cached(source.getvalue(), source.name)
    return pd.read_excel(source, sheet_name=None)


def find_default_excel():
    for file_name in DEFAULT_FILES:
        if Path(file_name).exists():
            return file_name
    return None

def clean_col(c):
    c = str(c).strip()
    c = re.sub(r"\s+", " ", c)
    return c

def find_col(df, candidates):
    lower_map = {str(c).strip().lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    for c in df.columns:
        cl = str(c).strip().lower()
        for cand in candidates:
            if cand.lower() in cl:
                return c
    return None

def standardise_quant(sheets):
    frames = []
    for sheet_name, raw in sheets.items():
        if raw is None or raw.empty:
            continue
        df = raw.copy()
        df.columns = [clean_col(c) for c in df.columns]

        numeric_cols = []
        for c in df.columns:
            s = pd.to_numeric(df[c], errors="coerce")
            if s.notna().sum() >= max(3, int(0.2 * len(df))):
                if s.dropna().between(1, 5).mean() >= 0.60:
                    numeric_cols.append(c)
        if len(numeric_cols) < 2:
            continue

        zone_col = find_col(df, ["Zone", "Zon", "Wilayah"])
        state_col = find_col(df, ["State", "Negeri", "Negeri Responden"])
        type_col = find_col(df, ["Jenis Responden", "Type of Respondent", "Respondent Type", "Kategori Responden", "Jenis"])

        if zone_col is None:
            df["Zone"] = "Tidak dinyatakan"
        else:
            df["Zone"] = df[zone_col].fillna("Tidak dinyatakan").astype(str)

        if state_col is None:
            df["State"] = "Tidak dinyatakan"
        else:
            df["State"] = df[state_col].fillna("Tidak dinyatakan").astype(str)

        if type_col is None:
            df["Jenis Responden"] = sheet_name
        else:
            df["Jenis Responden"] = df[type_col].fillna(sheet_name).astype(str)

        for c in numeric_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df["Nama Sheet"] = sheet_name
        frames.append(df)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False)

def standardise_qual(sheets):
    frames = []
    for sheet_name, raw in sheets.items():
        if raw is None or raw.empty:
            continue
        df = raw.copy()
        df.columns = [clean_col(c) for c in df.columns]
        text_cols = []
        for c in df.columns:
            if df[c].dtype == "object":
                avg_len = df[c].dropna().astype(str).str.len().mean()
                if pd.notna(avg_len) and avg_len > 20:
                    text_cols.append(c)
        if not text_cols:
            continue
        zone_col = find_col(df, ["Zone", "Zon", "Wilayah"])
        state_col = find_col(df, ["State", "Negeri"])
        type_col = find_col(df, ["Jenis Responden", "Respondent Type", "Kategori Responden", "Jenis"])
        out = pd.DataFrame()
        out["Zone"] = df[zone_col].fillna("Tidak dinyatakan").astype(str) if zone_col else "Tidak dinyatakan"
        out["State"] = df[state_col].fillna("Tidak dinyatakan").astype(str) if state_col else "Tidak dinyatakan"
        out["Jenis Responden"] = df[type_col].fillna(sheet_name).astype(str) if type_col else sheet_name
        out["Sumber Sheet"] = sheet_name
        out["Teks"] = df[text_cols].astype(str).agg(" | ".join, axis=1)
        frames.append(out)
    return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()

def get_item_cols(df):
    exclude = {"Zone", "State", "Jenis Responden", "Nama Sheet"}
    item_cols = []
    for c in df.columns:
        if c in exclude:
            continue
        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().sum() >= max(3, int(0.2 * len(df))):
            if s.dropna().between(1, 5).mean() >= 0.60:
                item_cols.append(c)
    return item_cols

def build_construct_map(df, selected_type="Semua"):
    item_cols = get_item_cols(df)
    if not item_cols:
        return {}

    groups = {}
    for c in item_cols:
        name = str(c).strip()
        prefix = None
        m = re.match(r"^([A-Za-z]+\s*\d*|[A-Za-z]+)[\._\-\s]*\d+", name)
        if m:
            prefix = m.group(1).strip().upper()
        else:
            parts = re.split(r"[\._\-\s]+", name)
            prefix = parts[0].strip().upper() if parts else "ITEM"
        groups.setdefault(prefix, []).append(c)

    # If too many tiny groups, use balanced automatic dimensions.
    if len(groups) > 12 or any(len(v) == 1 for v in groups.values()):
        chunks = np.array_split(item_cols, min(6, max(1, len(item_cols))))
        groups = {f"Dimensi {i+1}": list(chunk) for i, chunk in enumerate(chunks) if len(chunk) > 0}

    return groups

def add_construct_scores(df_raw, construct_map):
    df = df_raw.copy()
    valid = {}
    for construct, cols in construct_map.items():
        existing = [c for c in cols if c in df.columns]
        if not existing:
            continue
        score_col = str(construct)
        df[score_col] = df[existing].apply(pd.to_numeric, errors="coerce").mean(axis=1)
        if df[score_col].notna().sum() > 0:
            valid[score_col] = existing
    if valid:
        df["Skor Keseluruhan"] = df[list(valid.keys())].mean(axis=1)
    return df, valid

def classify_score(v):
    if pd.isna(v):
        return "Tiada Data"
    if v >= 4.0:
        return "Baik"
    if v >= 3.4:
        return "Sederhana"
    return "Perlu Intervensi"

def cronbach_alpha(df_items):
    data = df_items.apply(pd.to_numeric, errors="coerce").dropna(axis=1, how="all")
    data = data.dropna(axis=0, how="any")
    k = data.shape[1]
    if k < 2 or data.shape[0] < 3:
        return np.nan
    variances = data.var(axis=0, ddof=1)
    total_var = data.sum(axis=1).var(ddof=1)
    if total_var == 0 or pd.isna(total_var):
        return np.nan
    return (k / (k - 1)) * (1 - variances.sum() / total_var)

def alt_horizontal_bar(df_chart, x, y, title, sort="-x", height=430):
    data = df_chart.copy()
    if "Status" not in data.columns:
        data["Status"] = data[y].apply(classify_score)
    chart = (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopRight=12, cornerRadiusBottomRight=12)
        .encode(
            y=alt.Y(f"{x}:N", sort=sort, title=None, axis=alt.Axis(labelColor="white", labelFontSize=13, labelLimit=420)),
            x=alt.X(f"{y}:Q", title="Skor Purata", scale=alt.Scale(domain=[0, 5]), axis=alt.Axis(labelColor="white", titleColor="white", gridColor="rgba(255,255,255,0.12)")),
            color=alt.Color("Status:N", scale=alt.Scale(domain=["Baik", "Sederhana", "Perlu Intervensi", "Tiada Data"], range=["#00F5D4", "#FFD166", "#EF476F", "#94A3B8"]), legend=alt.Legend(title=None, labelColor="white", orient="top")),
            tooltip=[alt.Tooltip(f"{x}:N", title=x), alt.Tooltip(f"{y}:Q", title="Skor Purata", format=".2f"), alt.Tooltip("Status:N", title="Status")]
        )
        .properties(title=alt.TitleParams(text=title, color="white", fontSize=18, anchor="start"), height=height, background="transparent")
        .configure_view(strokeWidth=0, fill="transparent")
        .configure_axis(domainColor="rgba(255,255,255,0.25)", tickColor="rgba(255,255,255,0.25)")
        .configure_legend(labelColor="white", titleColor="white")
    )
    return chart

def alt_column_bar(df_chart, x, y, title, height=360):
    data = df_chart.copy()
    return (
        alt.Chart(data)
        .mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10)
        .encode(
            x=alt.X(f"{x}:N", title=None, sort="-y", axis=alt.Axis(labelColor="white", labelFontSize=12, labelAngle=-25, labelLimit=160)),
            y=alt.Y(f"{y}:Q", title="Bilangan", axis=alt.Axis(labelColor="white", titleColor="white", gridColor="rgba(255,255,255,0.12)")),
            tooltip=[alt.Tooltip(f"{x}:N", title=x), alt.Tooltip(f"{y}:Q", title=y, format=",.0f")]
        )
        .properties(title=alt.TitleParams(text=title, color="white", fontSize=18, anchor="start"), height=height, background="transparent")
        .configure_mark(color="#00F5D4")
        .configure_view(strokeWidth=0, fill="transparent")
        .configure_axis(domainColor="rgba(255,255,255,0.25)", tickColor="rgba(255,255,255,0.25)")
    )

def show_audit(title, body):
    with st.expander(f"🧮 {title}"):
        st.markdown(f'<div class="audit-box">{body}</div>', unsafe_allow_html=True)

def lowest_analysis(df, group_col, group_label):
    if group_col not in df.columns:
        return f"Analisis {group_label} tidak boleh dibuat kerana kolum {group_col} tiada dalam data."
    temp = (
        df.groupby(group_col, dropna=False)["Skor Keseluruhan"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={group_col: group_label, "mean": "Skor Purata", "count": "Bilangan"})
        .sort_values("Skor Purata", ascending=True)
    )
    if temp.empty:
        return f"Tiada data untuk analisis {group_label}."
    lowest = temp.iloc[0]
    highest = temp.iloc[-1]
    return (
        f"Berdasarkan filter semasa, {group_label} paling rendah ialah {lowest[group_label]} "
        f"dengan skor purata {lowest['Skor Purata']:.2f} melibatkan {int(lowest['Bilangan'])} responden. "
        f"{group_label} paling tinggi ialah {highest[group_label]} dengan skor purata {highest['Skor Purata']:.2f}. "
        f"Keutamaan intervensi perlu diberi kepada {lowest[group_label]}."
    )

def build_report_intro(df_all, df_filtered, zone, state, rtype):
    total = len(df_all)
    filtered = len(df_filtered)
    zones = df_all["Zone"].nunique() if "Zone" in df_all.columns else 0
    states = df_all["State"].nunique() if "State" in df_all.columns else 0
    types = df_all["Jenis Responden"].nunique() if "Jenis Responden" in df_all.columns else 0
    text = (
        f"Laporan ini dijana secara automatik berdasarkan {filtered:,} rekod selepas filter daripada jumlah keseluruhan {total:,} rekod. "
        f"Data merangkumi {zones} zon, {states} negeri dan {types} jenis responden. "
        f"Filter semasa ialah Zon: {zone}, Negeri: {state}, Jenis Responden: {rtype}. "
        f"Semua skor dikira menggunakan purata item Likert yang sah dan diringkaskan kepada konstruk, skor keseluruhan, status prestasi serta cadangan intervensi."
    )
    dist = df_all["Jenis Responden"].value_counts(dropna=False).reset_index()
    dist.columns = ["Jenis Responden", "Bilangan"]
    dist["Peratus"] = dist["Bilangan"] / dist["Bilangan"].sum() * 100
    dist["Peratus"] = dist["Peratus"].round(1)
    return text, dist

def make_group_summary(df, group_col):
    if group_col not in df.columns:
        return pd.DataFrame()
    out = df.groupby(group_col, dropna=False)["Skor Keseluruhan"].agg(["mean", "count"]).reset_index()
    out.columns = [group_col, "Skor Purata", "Bilangan"]
    out["Status"] = out["Skor Purata"].apply(classify_score)
    return out.sort_values("Skor Purata", ascending=True)

def intervention_text(score, dimension="keseluruhan"):
    if pd.isna(score):
        return "Data tidak mencukupi untuk menjana intervensi."
    if score < 3.4:
        return f"Intervensi segera diperlukan untuk {dimension}: audit isu utama, sesi libat urus, modul sokongan psikososial, pemantauan kes berisiko dan pelaporan mingguan."
    if score < 4.0:
        return f"Intervensi penambahbaikan dicadangkan untuk {dimension}: bimbingan bersasar, klinik sokongan, pemantauan bulanan dan pengukuhan komunikasi perkhidmatan."
    return f"{dimension} berada pada tahap baik. Fokus kepada pengekalan kualiti, dokumentasi amalan terbaik dan peluasan kepada lokasi lain."

def simple_theme_summary(df_qual):
    if df_qual.empty:
        return pd.DataFrame(), "Tiada data kualitatif dikesan dalam fail."
    keywords = {
        "Akses Perkhidmatan": ["akses", "mudah", "sukar", "jauh", "temujanji", "appointment"],
        "Kualiti Kaunseling": ["kaunseling", "psikologi", "sesi", "pegawai", "membantu"],
        "Masa Menunggu": ["tunggu", "lambat", "cepat", "masa"],
        "Komunikasi": ["maklum", "komunikasi", "jelas", "penerangan", "info"],
        "Kemudahan": ["bilik", "selesa", "kemudahan", "ruang", "privasi"]
    }
    rows = []
    text_series = df_qual["Teks"].fillna("").astype(str).str.lower()
    for theme, keys in keywords.items():
        count = sum(text_series.str.contains(k, regex=False).sum() for k in keys)
        rows.append({"Tema": theme, "Kekerapan Petunjuk": int(count)})
    theme_df = pd.DataFrame(rows).sort_values("Kekerapan Petunjuk", ascending=False)
    top = theme_df.iloc[0]
    story = f"Tema kualitatif paling dominan ialah {top['Tema']} dengan {int(top['Kekerapan Petunjuk'])} petunjuk kata kunci."
    return theme_df, story

def to_html_table(df):
    if df is None or df.empty:
        return "<p>Tiada data.</p>"
    return df.to_html(index=False, border=0, classes="tbl")

def build_html_report(title, intro, respondent_dist, kpis, dim_summary, zone_sum, state_sum, resp_sum, theme_df, summary_text):
    css = """
    <style>
    body{font-family:Arial,sans-serif;background:#081827;color:#0f172a;margin:30px;}
    .page{background:white;border-radius:20px;padding:30px;}
    h1{color:#102542;} h2{color:#231942;border-bottom:2px solid #ffd166;padding-bottom:6px;}
    .kpi{display:inline-block;width:18%;margin:1%;padding:14px;border-radius:14px;background:#eef6ff;vertical-align:top;}
    .box{padding:16px;border-radius:14px;background:#f8fafc;border:1px solid #e2e8f0;margin:10px 0;}
    table{border-collapse:collapse;width:100%;font-size:12px;} th{background:#102542;color:white;} th,td{border:1px solid #dbe3ef;padding:7px;text-align:left;}
    </style>
    """
    kpi_html = "".join([f"<div class='kpi'><b>{a}</b><br><span style='font-size:24px;font-weight:800'>{b}</span><br>{c}</div>" for a,b,c in kpis])
    return f"""
    <html><head><meta charset='utf-8'>{css}<title>{html_escape(title)}</title></head>
    <body><div class='page'>
    <h1>{html_escape(title)}</h1>
    <div class='box'>{html_escape(intro)}</div>
    <h2>1. Profil Responden</h2>{to_html_table(respondent_dist)}
    <h2>2. KPI Utama</h2>{kpi_html}
    <h2>3. Analisis Dimensi</h2>{to_html_table(dim_summary)}
    <h2>4. Analisis Zon</h2>{to_html_table(zone_sum)}
    <h2>5. Analisis Negeri</h2>{to_html_table(state_sum)}
    <h2>6. Analisis Jenis Responden</h2>{to_html_table(resp_sum)}
    <h2>7. Tema Kualitatif</h2>{to_html_table(theme_df)}
    <h2>8. Rumusan Pengurusan</h2><div class='box'>{html_escape(summary_text)}</div>
    </div></body></html>
    """

# =====================================================
# SESSION STATE
# =====================================================
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "uploaded_excel" not in st.session_state:
    st.session_state.uploaded_excel = None

# =====================================================
# HERO
# =====================================================
st.markdown("""
<div class="hero">
<h1>JKM Psychological Services Decision Support & Intervention Intelligence System</h1>
<p>
Sistem ini membaca data, menjelaskan jalan kira, mengenal pasti isu mengikut Zon, Negeri dan Jenis Responden,
mencadangkan intervensi bersasar, mensimulasikan impak, serta menjana laporan pengurusan. Semua graf menggunakan latar transparent tanpa kotak putih.
</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# ADMIN UPLOAD
# =====================================================
with st.expander("🔐 Admin sahaja: login untuk upload / reset data"):
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
        st.caption("User biasa tidak perlu login. Login hanya untuk admin upload atau reset data.")
    else:
        st.success("Admin aktif. Upload data dibenarkan.")
        uploaded_file = st.file_uploader("Upload fail Excel data JKM", type=["xlsx"])
        if uploaded_file is not None:
            st.session_state.uploaded_excel = uploaded_file
            st.success("Fail berjaya dimuat naik. Dashboard menggunakan data baharu.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Reset data upload"):
                st.session_state.uploaded_excel = None
                st.success("Data upload telah dikosongkan. Upload semula fail Excel jika tiada fail default dalam folder app.")
                st.rerun()
        with c2:
            if st.button("Logout Admin"):
                st.session_state.admin_logged = False
                st.rerun()

# =====================================================
# DATA LOAD
# =====================================================
data_source = st.session_state.uploaded_excel

if data_source is None:
    default_path = find_default_excel()
    if default_path is not None:
        data_source = default_path

if data_source is None:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.warning("Tiada fail Excel dikesan. Sila login admin dan upload fail Excel JKM terlebih dahulu.")
    st.markdown("""
    **Nota penting:** App ini tidak lagi bergantung kepada satu nama fail sahaja.  
    Admin boleh upload terus fail `.xlsx`, atau letakkan salah satu fail ini dalam folder GitHub yang sama dengan `app.py`:

    `JKM_7Sheet_Full_Simulation_Raw_Data(1).xlsx`  
    `JKM_7Sheet_Full_Simulation_Raw_Data(2).xlsx`  
    `JKM_7Sheet_Full_Simulation_Raw_Data.xlsx`
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

try:
    sheets = load_excel(data_source)
except Exception as e:
    st.error("Fail Excel tidak dapat dibaca. Sila upload semula fail Excel yang betul.")
    st.caption(f"Info teknikal: {e}")
    st.stop()

df_all_raw = standardise_quant(sheets)
df_qual_all = standardise_qual(sheets)

if df_all_raw.empty:
    st.error("Tiada sheet kuantitatif dikesan. Pastikan fail Excel ada item Likert skala 1 hingga 5.")
    st.stop()

# =====================================================
# FILTERS
# =====================================================
st.markdown('<div class="filter-card">', unsafe_allow_html=True)
st.markdown("### 🎛️ Filter Pelaporan Utama")
f1, f2, f3 = st.columns(3)

zone_values = ["Semua"] + sorted([str(x) for x in df_all_raw["Zone"].dropna().unique()])
with f1:
    selected_zone = st.selectbox("Zon", zone_values)

df_zone = df_all_raw.copy()
if selected_zone != "Semua":
    df_zone = df_zone[df_zone["Zone"].astype(str) == str(selected_zone)]

state_values = ["Semua"] + sorted([str(x) for x in df_zone["State"].dropna().unique()])
with f2:
    selected_state = st.selectbox("Negeri", state_values)

respondent_values = ["Semua"] + sorted([str(x) for x in df_all_raw["Jenis Responden"].dropna().unique()])
with f3:
    selected_type = st.selectbox("Jenis Responden", respondent_values)
st.markdown('</div>', unsafe_allow_html=True)

df_filtered_raw = df_all_raw.copy()
if selected_zone != "Semua":
    df_filtered_raw = df_filtered_raw[df_filtered_raw["Zone"].astype(str) == str(selected_zone)]
if selected_state != "Semua":
    df_filtered_raw = df_filtered_raw[df_filtered_raw["State"].astype(str) == str(selected_state)]
if selected_type != "Semua":
    df_filtered_raw = df_filtered_raw[df_filtered_raw["Jenis Responden"].astype(str) == str(selected_type)]

df_qual = df_qual_all.copy()
if not df_qual.empty:
    if selected_zone != "Semua":
        df_qual = df_qual[df_qual["Zone"].astype(str) == str(selected_zone)]
    if selected_state != "Semua":
        df_qual = df_qual[df_qual["State"].astype(str) == str(selected_state)]
    if selected_type != "Semua":
        df_qual = df_qual[df_qual["Jenis Responden"].astype(str) == str(selected_type)]

if df_filtered_raw.empty:
    st.warning("Tiada data untuk kombinasi filter ini.")
    st.stop()

construct_map = build_construct_map(df_filtered_raw, selected_type)
df, valid_constructs = add_construct_scores(df_filtered_raw, construct_map)

if not valid_constructs:
    st.error("Tiada konstruk boleh dikira daripada data filter semasa.")
    st.stop()

dimension_cols = list(valid_constructs.keys())
item_cols = get_item_cols(df_filtered_raw)
intro_text, respondent_dist = build_report_intro(df_all_raw, df, selected_zone, selected_state, selected_type)

# =====================================================
# INTRO
# =====================================================
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 📘 Pengenalan Pelaporan Automatik")
st.markdown(f'<div class="note-blue">{html_escape(intro_text)}</div>', unsafe_allow_html=True)

c1, c2 = st.columns([1, 1])
with c1:
    st.markdown("### Komposisi Responden Keseluruhan")
    st.dataframe(respondent_dist, use_container_width=True, hide_index=True)
with c2:
    filter_summary = pd.DataFrame({
        "Perkara": ["Zon dipilih", "Negeri dipilih", "Jenis responden dipilih", "Bilangan data selepas filter"],
        "Nilai": [selected_zone, selected_state, selected_type, f"{len(df):,}"]
    })
    st.markdown("### Ringkasan Filter Laporan")
    st.dataframe(filter_summary, use_container_width=True, hide_index=True)

show_audit("Jalan kira pengenalan laporan", f"Sistem membaca keseluruhan data, kemudian menapis data mengikut Zon = <b>{html_escape(selected_zone)}</b>, Negeri = <b>{html_escape(selected_state)}</b>, dan Jenis Responden = <b>{html_escape(selected_type)}</b>. Analisis selepas ini menggunakan <b>{len(df):,}</b> rekod.")
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# KPI
# =====================================================
n = len(df)
overall = df["Skor Keseluruhan"].mean()
high_pct = (df["Skor Keseluruhan"] >= 4.0).mean() * 100
risk_pct = (df["Skor Keseluruhan"] < 3.4).mean() * 100
alpha = cronbach_alpha(df_filtered_raw[item_cols]) if item_cols else np.nan
alpha_display = f"{alpha:.3f}" if not pd.isna(alpha) else "NA"
overall_display = f"{overall:.2f}" if not pd.isna(overall) else "NA"

st.markdown("## 📌 KPI Utama")
k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    ("Bil. Responden", f"{n:,}", "Data selepas filter"),
    ("Skor Keseluruhan", overall_display, classify_score(overall)),
    ("% Baik", f"{high_pct:.1f}%", "Skor ≥ 4.00"),
    ("% Perlu Intervensi", f"{risk_pct:.1f}%", "Skor < 3.40"),
    ("Cronbach Alpha", alpha_display, "Konsistensi dalaman")
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

show_audit("Jalan kira KPI", f"<b>Bilangan Responden</b> = {n:,}.<br><b>Skor Keseluruhan</b> = purata semua konstruk sah: {html_escape(', '.join(dimension_cols))}.<br><b>% Baik</b> = responden skor ≥ 4.00 / {n:,} × 100 = {high_pct:.1f}%.<br><b>% Perlu Intervensi</b> = responden skor < 3.40 / {n:,} × 100 = {risk_pct:.1f}%.<br><b>Cronbach Alpha</b> dikira daripada item Likert yang dikesan.")

# =====================================================
# DIMENSION ANALYSIS
# =====================================================
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 📊 Analisis Dimensi / Konstruk")
dim_summary = df[dimension_cols].mean().reset_index().rename(columns={"index": "Dimensi", 0: "Skor Purata"})
dim_summary["Status"] = dim_summary["Skor Purata"].apply(classify_score)
dim_summary = dim_summary.sort_values("Skor Purata", ascending=True)

st.altair_chart(alt_horizontal_bar(dim_summary, "Dimensi", "Skor Purata", "Skor Purata Mengikut Dimensi / Konstruk"), use_container_width=True, theme=None)
st.dataframe(dim_summary, use_container_width=True, hide_index=True)

lowest_dim = dim_summary.iloc[0]["Dimensi"]
lowest_score = dim_summary.iloc[0]["Skor Purata"]
highest_dim = dim_summary.iloc[-1]["Dimensi"]
highest_score = dim_summary.iloc[-1]["Skor Purata"]
st.markdown(f'<div class="intervention-box"><b>Dapatan utama:</b> Dimensi paling rendah ialah <b>{html_escape(lowest_dim)}</b> ({lowest_score:.2f}), manakala dimensi paling tinggi ialah <b>{html_escape(highest_dim)}</b> ({highest_score:.2f}).<br><br><b>Cadangan:</b> {html_escape(intervention_text(lowest_score, lowest_dim))}</div>', unsafe_allow_html=True)
show_audit("Jalan kira graf dimensi", "Setiap bar mewakili skor purata bagi satu konstruk. Skor konstruk = purata item dalam konstruk tersebut. Status: Baik ≥ 4.00, Sederhana 3.40–3.99, Perlu Intervensi < 3.40.")
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# GROUP COMPARISON
# =====================================================
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🌍 Analisis Mengikut Zon, Negeri dan Jenis Responden")
zone_sum = make_group_summary(df, "Zone")
state_sum = make_group_summary(df, "State")
resp_sum = make_group_summary(df, "Jenis Responden")

t1, t2, t3 = st.tabs(["Zon", "Negeri", "Jenis Responden"])
with t1:
    if not zone_sum.empty:
        st.altair_chart(alt_horizontal_bar(zone_sum, "Zone", "Skor Purata", "Skor Purata Mengikut Zon", height=360), use_container_width=True, theme=None)
        st.dataframe(zone_sum, use_container_width=True, hide_index=True)
        st.info(lowest_analysis(df, "Zone", "Zon"))
with t2:
    if not state_sum.empty:
        st.altair_chart(alt_horizontal_bar(state_sum, "State", "Skor Purata", "Skor Purata Mengikut Negeri", height=520), use_container_width=True, theme=None)
        st.dataframe(state_sum, use_container_width=True, hide_index=True)
        st.info(lowest_analysis(df, "State", "Negeri"))
with t3:
    if not resp_sum.empty:
        st.altair_chart(alt_horizontal_bar(resp_sum, "Jenis Responden", "Skor Purata", "Skor Purata Mengikut Jenis Responden", height=360), use_container_width=True, theme=None)
        st.dataframe(resp_sum, use_container_width=True, hide_index=True)
        st.info(lowest_analysis(df, "Jenis Responden", "Jenis Responden"))
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# QUALITATIVE
# =====================================================
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🗣️ Analisis Kualitatif Ringkas")
theme_df, theme_story = simple_theme_summary(df_qual)
if not theme_df.empty:
    st.altair_chart(alt_horizontal_bar(theme_df, "Tema", "Kekerapan Petunjuk", "Kekerapan Tema Kualitatif", sort="-x", height=360), use_container_width=True, theme=None)
    st.dataframe(theme_df, use_container_width=True, hide_index=True)
st.markdown(f'<div class="note-blue">{html_escape(theme_story)}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# INTERVENTION + SIMULATION
# =====================================================
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🎯 Intervensi Bersasar dan Simulasi Impak")
boost = st.slider("Simulasi peningkatan skor intervensi", min_value=0.05, max_value=0.80, value=0.20, step=0.05)
sim_df = dim_summary.copy()
sim_df["Skor Selepas Intervensi"] = (sim_df["Skor Purata"] + boost).clip(upper=5)
sim_long = sim_df.melt(id_vars=["Dimensi"], value_vars=["Skor Purata", "Skor Selepas Intervensi"], var_name="Senario", value_name="Skor")
chart_sim = (
    alt.Chart(sim_long)
    .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
    .encode(
        x=alt.X("Dimensi:N", title=None, axis=alt.Axis(labelColor="white", labelAngle=-25, labelLimit=160)),
        y=alt.Y("Skor:Q", title="Skor", scale=alt.Scale(domain=[0,5]), axis=alt.Axis(labelColor="white", titleColor="white", gridColor="rgba(255,255,255,0.12)")),
        color=alt.Color("Senario:N", legend=alt.Legend(title=None, labelColor="white", orient="top")),
        xOffset="Senario:N",
        tooltip=["Dimensi:N", "Senario:N", alt.Tooltip("Skor:Q", format=".2f")]
    )
    .properties(title=alt.TitleParams(text="Simulasi Sebelum dan Selepas Intervensi", color="white", fontSize=18, anchor="start"), height=430, background="transparent")
    .configure_view(strokeWidth=0, fill="transparent")
    .configure_axis(domainColor="rgba(255,255,255,0.25)", tickColor="rgba(255,255,255,0.25)")
    .configure_legend(labelColor="white", titleColor="white")
)
st.altair_chart(chart_sim, use_container_width=True, theme=None)
st.markdown(f'<div class="intervention-box"><b>Cadangan automatik:</b> {html_escape(intervention_text(lowest_score, lowest_dim))}<br><br><b>Simulasi:</b> Jika intervensi menaikkan skor sebanyak {boost:.2f}, dimensi terendah dijangka meningkat daripada {lowest_score:.2f} kepada {min(lowest_score + boost, 5):.2f}.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# REPORT DOWNLOAD
# =====================================================
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🖨️ Laporan Lengkap: Download / Print")
summary_text = (
    f"Secara keseluruhan, skor purata sistem ialah {overall_display} dan diklasifikasikan sebagai {classify_score(overall)}. "
    f"Dimensi paling memerlukan perhatian ialah {lowest_dim} dengan skor {lowest_score:.2f}. "
    f"Cadangan utama ialah melaksanakan intervensi bersasar berdasarkan zon, negeri dan jenis responden yang menunjukkan skor paling rendah."
)
report_html = build_html_report(
    "Laporan JKM Psychological Services DSS-IIS",
    intro_text,
    respondent_dist,
    kpis,
    dim_summary,
    zone_sum,
    state_sum,
    resp_sum,
    theme_df,
    summary_text
)
st.markdown(f'<div class="note-blue">{html_escape(summary_text)}</div>', unsafe_allow_html=True)
st.download_button(
    "📄 Download Laporan HTML untuk Print / Save as PDF",
    data=report_html.encode("utf-8"),
    file_name=f"Laporan_JKM_DSS_{selected_zone}_{selected_state}_{selected_type}.html".replace(" ", "_"),
    mime="text/html"
)
st.markdown('</div>', unsafe_allow_html=True)
