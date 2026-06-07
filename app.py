import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from io import BytesIO
from datetime import datetime
import re
import textwrap
import base64
import html

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="JKM Psychological Services DSS-IIS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin2026"

DEFAULT_FILE = "JKM_7Sheet_Full_Simulation_Raw_Data(2).xlsx"

# ============================================================
# PREMIUM STYLE
# ============================================================

st.markdown("""
<style>
[data-testid="stSidebar"] {display:none;}
[data-testid="collapsedControl"] {display:none;}

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}

.stApp {
    background:
    radial-gradient(circle at 8% 8%, rgba(255, 184, 0, .28), transparent 28%),
    radial-gradient(circle at 92% 8%, rgba(0, 180, 216, .30), transparent 32%),
    radial-gradient(circle at 50% 100%, rgba(247, 37, 133, .18), transparent 35%),
    linear-gradient(135deg, #061826 0%, #102542 42%, #231942 100%);
    color: #ffffff;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 4rem;
    max-width: 1550px;
}

.hero {
    padding: 34px 38px;
    border-radius: 30px;
    background:
        linear-gradient(135deg, rgba(255,255,255,.19), rgba(255,255,255,.06)),
        linear-gradient(120deg, rgba(255,183,3,.21), rgba(33,158,188,.17), rgba(247,37,133,.13));
    border: 1px solid rgba(255,255,255,.22);
    box-shadow: 0 28px 90px rgba(0,0,0,.38);
    margin-bottom: 20px;
}

.hero h1 {
    font-size: 2.25rem;
    line-height: 1.12;
    margin: 0;
    color: #ffffff;
    letter-spacing: -.6px;
}

.hero p {
    font-size: 1.02rem;
    color: #dbeafe;
    max-width: 1120px;
    margin-top: 12px;
    line-height: 1.55;
}

.card {
    padding: 22px;
    border-radius: 25px;
    background: rgba(255,255,255,.095);
    border: 1px solid rgba(255,255,255,.17);
    box-shadow: 0 22px 60px rgba(0,0,0,.28);
    margin-bottom: 18px;
}

.filter-card {
    padding: 22px;
    border-radius: 26px;
    background:
        linear-gradient(135deg, rgba(255,255,255,.14), rgba(255,255,255,.055));
    border: 1px solid rgba(255,255,255,.19);
    box-shadow: 0 20px 55px rgba(0,0,0,.28);
    margin-bottom: 18px;
}

.kpi {
    padding: 22px;
    border-radius: 24px;
    min-height: 140px;
    background:
        linear-gradient(135deg, rgba(255,255,255,.19), rgba(255,255,255,.07));
    border: 1px solid rgba(255,255,255,.20);
    box-shadow: 0 18px 55px rgba(0,0,0,.30);
    position: relative;
    overflow: hidden;
}

.kpi:before {
    content: "";
    position: absolute;
    top: -40px;
    right: -40px;
    width: 115px;
    height: 115px;
    background: rgba(255, 183, 3, .22);
    border-radius: 50%;
}

.kpi .label {
    color: #dbeafe;
    font-size: .78rem;
    letter-spacing: .8px;
    text-transform: uppercase;
    font-weight: 900;
}

.kpi .value {
    color: #ffffff;
    font-size: 2.25rem;
    font-weight: 950;
    margin-top: 8px;
}

.kpi .sub {
    color: #ffd166;
    font-size: .88rem;
    margin-top: 4px;
    font-weight: 700;
}

.section {
    padding: 25px;
    border-radius: 28px;
    background:
        linear-gradient(135deg, rgba(255,255,255,.105), rgba(255,255,255,.048));
    border: 1px solid rgba(255,255,255,.17);
    box-shadow: 0 22px 70px rgba(0,0,0,.30);
    margin-top: 18px;
}

.section h2, .section h3, .section h4 {
    color: #ffffff;
}

.audit {
    margin-top: 10px;
    padding: 15px 17px;
    border-radius: 17px;
    background: rgba(255, 209, 102, .125);
    border-left: 5px solid #ffd166;
    color: #fff7d6;
    font-size: .93rem;
    line-height: 1.55;
}

.note-blue {
    margin-top: 10px;
    padding: 15px 17px;
    border-radius: 17px;
    background: rgba(76, 201, 240, .13);
    border-left: 5px solid #4cc9f0;
    color: #e0f7ff;
    font-size: .93rem;
    line-height: 1.55;
}

.warning-box {
    margin-top: 10px;
    padding: 15px 17px;
    border-radius: 17px;
    background: rgba(239, 71, 111, .13);
    border-left: 5px solid #ef476f;
    color: #ffe1e8;
    font-size: .93rem;
    line-height: 1.55;
}

.intervention {
    padding: 19px;
    border-radius: 22px;
    background:
        linear-gradient(135deg, rgba(239,71,111,.20), rgba(76,201,240,.14));
    border: 1px solid rgba(255,255,255,.18);
    box-shadow: 0 16px 38px rgba(0,0,0,.20);
    margin-bottom: 14px;
}

.intervention h3 {
    margin-top: 0;
}

.bad {color:#ff8fab;font-weight:900;}
.warn {color:#ffd166;font-weight:900;}
.good {color:#6ee7b7;font-weight:900;}

.stButton button, .stDownloadButton button {
    border-radius: 15px;
    border: 0;
    background: linear-gradient(135deg, #ffb703, #fb8500);
    color: #111827;
    font-weight: 950;
    padding: .75rem 1.15rem;
}

.stSelectbox label, .stFileUploader label, .stTextInput label, .stSlider label {
    color: #ffffff !important;
    font-weight: 900;
}

div[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
}

hr {
    border-color: rgba(255,255,255,.18);
}

@media print {
    .stButton, .stDownloadButton, header, footer, [data-testid="stToolbar"] {
        display: none !important;
    }
    .stApp {
        background: white !important;
        color: black !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def clean_label(x):
    return str(x).replace("_", " ").strip()

def safe_numeric(s):
    return pd.to_numeric(s, errors="coerce")

def safe_mean(df, cols):
    cols = [c for c in cols if c in df.columns]
    if not cols:
        return pd.Series(np.nan, index=df.index)
    return df[cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)

def cronbach_alpha(df_items):
    df_items = df_items.apply(pd.to_numeric, errors="coerce")
    df_items = df_items.dropna(axis=1, how="all")
    if df_items.shape[1] < 2:
        return np.nan
    df_items = df_items.fillna(df_items.mean(numeric_only=True))
    item_var = df_items.var(axis=0, ddof=1).sum()
    total_var = df_items.sum(axis=1).var(ddof=1)
    k = df_items.shape[1]
    if total_var == 0 or pd.isna(total_var):
        return np.nan
    return (k / (k - 1)) * (1 - item_var / total_var)

def classify_score(score):
    if pd.isna(score):
        return "Tiada Data"
    if score >= 4.0:
        return "Baik / Kuat"
    if score >= 3.4:
        return "Sederhana / Perlu Pengukuhan"
    return "Rendah / Perlu Intervensi"

def classify_html(score):
    status = classify_score(score)
    if pd.isna(score):
        return f"<span>{status}</span>"
    if score >= 4.0:
        return f"<span class='good'>{status}</span>"
    if score >= 3.4:
        return f"<span class='warn'>{status}</span>"
    return f"<span class='bad'>{status}</span>"

def score_color(score):
    if pd.isna(score):
        return "#94a3b8"
    if score >= 4.0:
        return "#06d6a0"
    if score >= 3.4:
        return "#ffd166"
    return "#ef476f"

def detect_col(df, candidates):
    lower_map = {str(c).lower().strip(): c for c in df.columns}
    for cand in candidates:
        if cand.lower().strip() in lower_map:
            return lower_map[cand.lower().strip()]
    for c in df.columns:
        cl = str(c).lower()
        for cand in candidates:
            if cand.lower() in cl:
                return c
    return None

def get_item_cols(df):
    item_cols = []
    for c in df.columns:
        cs = str(c).strip()
        if re.match(r"^(K\d+[A-Z]\d+|K\d+[A-Z]_\d+|SQ\d+|B\d+|T2_\d+|T3_\d+|K1O\d+)$", cs):
            item_cols.append(c)
    return item_cols

def get_cols_start(df, prefixes):
    out = []
    for c in df.columns:
        cs = str(c)
        if any(cs.startswith(p) for p in prefixes):
            out.append(c)
    return out

def format_cols(cols):
    if not cols:
        return "Tiada item dikesan"
    return ", ".join([str(c) for c in cols])

def formula_text(name, cols):
    if not cols:
        return f"{name}: tiada item dikesan."
    return f"{name} = ({' + '.join([str(c) for c in cols])}) / {len(cols)}"

def html_escape(x):
    return html.escape(str(x))

# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(show_spinner=False)
def load_excel(file):
    xls = pd.ExcelFile(file)
    return {s: pd.read_excel(file, sheet_name=s) for s in xls.sheet_names}

def standardise_quant(sheets):
    frames = []
    sheet_map = {
        "S1_Quant_Raw": "Klien",
        "S2_Quant_Raw": "Pegawai",
        "S3_Quant_Raw": "Warga JKM",
        "T123_Pilot_Raw": "Klien"
    }

    for sheet_name, jenis in sheet_map.items():
        if sheet_name in sheets:
            temp = sheets[sheet_name].copy()
            temp["Jenis Responden"] = jenis
            temp["Kod Borang"] = {
                "Klien": "S1",
                "Pegawai": "S2",
                "Warga JKM": "S3"
            }.get(jenis, "NA")
            temp["Sumber Data"] = sheet_name
            frames.append(temp)

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True, sort=False)

    zone_col = detect_col(df, ["Zone", "Zon"])
    state_col = detect_col(df, ["State", "Negeri"])

    if zone_col and zone_col != "Zone":
        df["Zone"] = df[zone_col]
    if state_col and state_col != "State":
        df["State"] = df[state_col]

    if "Zone" not in df.columns:
        df["Zone"] = "Tidak Dinyatakan"
    if "State" not in df.columns:
        df["State"] = "Tidak Dinyatakan"

    return df

def standardise_qual(sheets):
    frames = []
    sheet_map = {
        "Q1_Client_Raw": "Klien",
        "Q2_Officer_Raw": "Pegawai",
        "Q3_System_Raw": "Warga JKM"
    }

    for sheet_name, jenis in sheet_map.items():
        if sheet_name in sheets:
            temp = sheets[sheet_name].copy()
            temp["Jenis Responden"] = jenis
            temp["Kod Borang"] = {
                "Klien": "S1",
                "Pegawai": "S2",
                "Warga JKM": "S3"
            }.get(jenis, "NA")
            temp["Sumber Data"] = sheet_name
            frames.append(temp)

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True, sort=False)

    zone_col = detect_col(df, ["Zone", "Zon"])
    state_col = detect_col(df, ["State", "Negeri"])

    if zone_col and zone_col != "Zone":
        df["Zone"] = df[zone_col]
    if state_col and state_col != "State":
        df["State"] = df[state_col]

    if "Zone" not in df.columns:
        df["Zone"] = "Tidak Dinyatakan"
    if "State" not in df.columns:
        df["State"] = "Tidak Dinyatakan"

    return df

# ============================================================
# CONSTRUCT MAP
# ============================================================

def build_construct_map(df, selected_type):
    cols = list(df.columns)

    if selected_type == "Klien":
        return {
            "Akses & Kebolehcapaian": get_cols_start(df, ["K2A"]),
            "Komunikasi Perkhidmatan": get_cols_start(df, ["K2B"]),
            "Hubungan Terapeutik": get_cols_start(df, ["K2C"]),
            "Hak, Etika & Keselamatan": get_cols_start(df, ["K2D"]),
            "Kesesuaian Intervensi": get_cols_start(df, ["K2E"]),
            "Kesan & Perubahan Klien": get_cols_start(df, ["K2F"]),
            "Outcome Klien": get_cols_start(df, ["K1O"])
        }

    if selected_type == "Pegawai":
        return {
            "Keberkesanan Intervensi Pegawai": get_cols_start(df, ["K3A"]),
            "Kompetensi & Kapasiti Pegawai": get_cols_start(df, ["K3B"]),
            "Pengurusan Kes": get_cols_start(df, ["K3C"]),
            "SOP & Tadbir Urus": get_cols_start(df, ["K4A"]),
            "Kolaborasi Dalaman": get_cols_start(df, ["K4B"]),
            "Kualiti Penyampaian": get_cols_start(df, ["K4C"]),
            "Keperluan Penambahbaikan Pegawai": get_cols_start(df, ["K5A"])
        }

    if selected_type == "Warga JKM":
        return {
            "Kesedaran Peranan": get_cols_start(df, ["K4D"]),
            "Sokongan Organisasi": get_cols_start(df, ["K4E"]),
            "Pematuhan Etika": get_cols_start(df, ["K4F"]),
            "Koordinasi Sistem": get_cols_start(df, ["K4G"]),
            "Data & Dashboard": get_cols_start(df, ["K4H"]),
            "Keperluan Penambahbaikan Warga JKM": get_cols_start(df, ["K5B"])
        }

    # Semua responden: hanya konstruk yang boleh wujud bersama, tetapi tak semestinya sah untuk SEM
    general = {}
    for label, prefixes in {
        "Akses & Kebolehcapaian": ["K2A"],
        "Komunikasi Perkhidmatan": ["K2B"],
        "Hubungan Terapeutik": ["K2C"],
        "Hak, Etika & Keselamatan": ["K2D"],
        "Kesesuaian Intervensi": ["K2E"],
        "Kesan & Perubahan Klien": ["K2F"],
        "Keberkesanan Intervensi Pegawai": ["K3A"],
        "Kompetensi & Kapasiti Pegawai": ["K3B"],
        "Pengurusan Kes": ["K3C"],
        "SOP & Tadbir Urus": ["K4A"],
        "Kolaborasi Dalaman": ["K4B"],
        "Kualiti Penyampaian": ["K4C"],
        "Kesedaran Peranan": ["K4D"],
        "Sokongan Organisasi": ["K4E"],
        "Pematuhan Etika": ["K4F"],
        "Koordinasi Sistem": ["K4G"],
        "Data & Dashboard": ["K4H"],
        "Keperluan Penambahbaikan Pegawai": ["K5A"],
        "Keperluan Penambahbaikan Warga JKM": ["K5B"],
        "Outcome Klien": ["K1O"],
        "Kepuasan Sistem": ["SQ"],
        "Outcome Teras": ["B"],
        "Susulan T2": ["T2_"],
        "Kelestarian T3": ["T3_"]
    }.items():
        c = get_cols_start(df, prefixes)
        if c:
            general[label] = c
    return general

def add_construct_scores(df, construct_map):
    temp = df.copy()
    valid_constructs = {}
    for name, cols in construct_map.items():
        cols = [c for c in cols if c in temp.columns]
        if cols:
            temp[name] = safe_mean(temp, cols)
            if temp[name].notna().sum() > 0:
                valid_constructs[name] = cols
    if valid_constructs:
        temp["Skor Keseluruhan"] = safe_mean(temp, list(valid_constructs.keys()))
    else:
        temp["Skor Keseluruhan"] = np.nan
    return temp, valid_constructs

# ============================================================
# CHART FUNCTIONS
# ============================================================

def alt_bar(df, x, y, title, sort="-y", height=420):
    data = df.copy()
    data["Warna Status"] = data[y].apply(
        lambda v: "Baik" if v >= 4 else "Sederhana" if v >= 3.4 else "Intervensi"
    )

    chart = alt.Chart(data).mark_bar(
        cornerRadiusTopLeft=8,
        cornerRadiusTopRight=8
    ).encode(
        x=alt.X(f"{x}:N", sort=sort, title=None, axis=alt.Axis(labelAngle=-25)),
        y=alt.Y(f"{y}:Q", title="Skor / Nilai"),
        color=alt.Color(
            "Warna Status:N",
            scale=alt.Scale(
                domain=["Baik", "Sederhana", "Intervensi"],
                range=["#06d6a0", "#ffd166", "#ef476f"]
            ),
            legend=alt.Legend(title="Status")
        ),
        tooltip=[
            alt.Tooltip(f"{x}:N", title=x),
            alt.Tooltip(f"{y}:Q", title=y, format=".3f")
        ]
    ).properties(
        title=title,
        height=height
    )

    text = alt.Chart(data).mark_text(
        dy=-8,
        color="white",
        fontWeight="bold"
    ).encode(
        x=alt.X(f"{x}:N", sort=sort),
        y=alt.Y(f"{y}:Q"),
        text=alt.Text(f"{y}:Q", format=".2f")
    )

    return (chart + text).configure_axis(
        labelColor="white",
        titleColor="white",
        gridColor="rgba(255,255,255,0.16)"
    ).configure_title(
        color="white",
        fontSize=17,
        fontWeight="bold"
    ).configure_legend(
        labelColor="white",
        titleColor="white"
    ).configure_view(
        strokeOpacity=0
    )

def alt_horizontal_bar(df, x, y, title, height=520):
    data = df.copy()
    data["Status"] = data[y].apply(
        lambda v: "Baik" if v >= 4 else "Sederhana" if v >= 3.4 else "Intervensi"
    )

    chart = alt.Chart(data).mark_bar(cornerRadius=8).encode(
        y=alt.Y(f"{x}:N", sort=alt.SortField(y, order="ascending"), title=None),
        x=alt.X(f"{y}:Q", title="Skor Purata", scale=alt.Scale(domain=[0, 5])),
        color=alt.Color(
            "Status:N",
            scale=alt.Scale(
                domain=["Baik", "Sederhana", "Intervensi"],
                range=["#06d6a0", "#ffd166", "#ef476f"]
            )
        ),
        tooltip=[
            alt.Tooltip(f"{x}:N", title=x),
            alt.Tooltip(f"{y}:Q", title=y, format=".3f"),
            alt.Tooltip("Status:N")
        ]
    ).properties(title=title, height=height)

    text = alt.Chart(data).mark_text(
        align="left",
        dx=6,
        color="white",
        fontWeight="bold"
    ).encode(
        y=alt.Y(f"{x}:N", sort=alt.SortField(y, order="ascending")),
        x=alt.X(f"{y}:Q"),
        text=alt.Text(f"{y}:Q", format=".2f")
    )

    return (chart + text).configure_axis(
        labelColor="white",
        titleColor="white",
        gridColor="rgba(255,255,255,0.16)"
    ).configure_title(
        color="white",
        fontSize=17,
        fontWeight="bold"
    ).configure_legend(
        labelColor="white",
        titleColor="white"
    ).configure_view(
        strokeOpacity=0
    )

def show_audit(title, body):
    st.markdown(f"""
    <div class="audit">
    <b>{html_escape(title)}</b><br>
    {body}
    </div>
    """, unsafe_allow_html=True)

def show_note(title, body):
    st.markdown(f"""
    <div class="note-blue">
    <b>{html_escape(title)}</b><br>
    {body}
    </div>
    """, unsafe_allow_html=True)

def show_warning_box(title, body):
    st.markdown(f"""
    <div class="warning-box">
    <b>{html_escape(title)}</b><br>
    {body}
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# REPORT INTRO FUNCTIONS
# ============================================================

def build_report_intro(df_all, df_filtered, selected_zone, selected_state, selected_type):
    total_n = len(df_all)
    filtered_n = len(df_filtered)

    zone_count = df_all["Zone"].nunique(dropna=True) if "Zone" in df_all.columns else 0
    state_count = df_all["State"].nunique(dropna=True) if "State" in df_all.columns else 0

    resp_dist = (
        df_all["Jenis Responden"]
        .value_counts(dropna=False)
        .reset_index()
    )
    resp_dist.columns = ["Jenis Responden", "Bilangan"]

    zone_phrase = "semua zon" if selected_zone == "Semua" else f"Zon {selected_zone}"
    state_phrase = "semua negeri" if selected_state == "Semua" else f"Negeri {selected_state}"
    type_phrase = "semua jenis responden" if selected_type == "Semua" else f"responden {selected_type}"

    intro = f"""
    Laporan analitik ini dijana oleh JKM Psychological Services Decision Support & Intervention Intelligence System (DSS-IIS).
    Sistem ini bertujuan menilai dapatan perkhidmatan psikologi dan kaunseling berdasarkan data kuantitatif,
    data kualitatif, model RE-AIM, CMO, SEM eksploratori, simulasi impak dan cadangan intervensi bersasar.

    Secara keseluruhan, pangkalan data mengandungi {total_n:,} rekod responden yang merangkumi {zone_count}
    zon dan {state_count} negeri. Responden terdiri daripada tiga kategori utama, iaitu Klien (S1),
    Pegawai (S2) dan Warga JKM (S3). Walau bagaimanapun, struktur item dan konstruk adalah berbeza mengikut
    jenis responden. Oleh itu, tidak semua analisis boleh dijalankan secara serentak untuk semua kategori responden.

    Bagi laporan semasa, penapisan data adalah berdasarkan {zone_phrase}, {state_phrase} dan {type_phrase}.
    Selepas filter digunakan, sebanyak {filtered_n:,} rekod responden dianalisis. Semua KPI, graf, RE-AIM,
    CMO, SEM, simulasi dan intervensi dalam laporan ini adalah berdasarkan data yang telah ditapis sahaja.
    """

    return intro.strip(), resp_dist

def location_text(selected_zone, selected_state, selected_type):
    parts = []
    if selected_zone != "Semua":
        parts.append(f"Zon {selected_zone}")
    if selected_state != "Semua":
        parts.append(f"Negeri {selected_state}")
    if selected_type != "Semua":
        parts.append(f"kumpulan responden {selected_type}")
    return ", ".join(parts) if parts else "semua zon, semua negeri dan semua jenis responden"

# ============================================================
# ADMIN LOGIN ONLY
# ============================================================

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "uploaded_excel" not in st.session_state:
    st.session_state.uploaded_excel = None

st.markdown("""
<div class="hero">
<h1>JKM Psychological Services Decision Support & Intervention Intelligence System</h1>
<p>
Sistem ini bukan sekadar dashboard. Ia dibina sebagai DSS untuk membantu JKM membaca data,
menjelaskan jalan kira, mengenal pasti isu mengikut Zon, Negeri dan Jenis Responden,
mencadangkan intervensi bersasar, mensimulasikan impak, serta menjana laporan pelaporan pengurusan.
</p>
</div>
""", unsafe_allow_html=True)

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
            if st.button("Reset kepada fail asal"):
                st.session_state.uploaded_excel = None
                st.success("Data direset kepada fail asal.")
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
except Exception as e:
    st.error("Data belum tersedia atau fail default tidak ditemui. Login admin dan upload fail Excel.")
    st.stop()

df_all_raw = standardise_quant(sheets)
df_qual_all = standardise_qual(sheets)

if df_all_raw.empty:
    st.error("Tiada sheet kuantitatif dikesan. Pastikan sheet S1_Quant_Raw, S2_Quant_Raw atau S3_Quant_Raw wujud.")
    st.stop()

# ============================================================
# FILTERS: ONLY THREE DROPDOWNS
# ============================================================

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

# ============================================================
# INTRO REPORT
# ============================================================

intro_text, respondent_dist = build_report_intro(
    df_all_raw, df, selected_zone, selected_state, selected_type
)

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 📘 Pengenalan Pelaporan Automatik")
st.markdown(f"""
<div class="note-blue">
{html_escape(intro_text).replace(chr(10), "<br>")}
</div>
""", unsafe_allow_html=True)

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

show_audit(
    "Jalan kira pengenalan laporan",
    f"""
    Sistem membaca keseluruhan data dahulu, kemudian mengira jumlah rekod keseluruhan, bilangan zon,
    bilangan negeri dan komposisi responden. Selepas itu, sistem menggunakan tiga filter utama:
    <b>Zon = {html_escape(selected_zone)}</b>, <b>Negeri = {html_escape(selected_state)}</b> dan
    <b>Jenis Responden = {html_escape(selected_type)}</b>. Semua analisis selepas ini hanya menggunakan
    <b>{len(df):,}</b> rekod yang melepasi filter tersebut.
    """
)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# KPI
# ============================================================

n = len(df)
overall = df["Skor Keseluruhan"].mean()
high_pct = (df["Skor Keseluruhan"] >= 4.0).mean() * 100
moderate_pct = ((df["Skor Keseluruhan"] >= 3.4) & (df["Skor Keseluruhan"] < 4.0)).mean() * 100
risk_pct = (df["Skor Keseluruhan"] < 3.4).mean() * 100
alpha = cronbach_alpha(df_filtered_raw[item_cols]) if item_cols else np.nan

st.markdown("## 📌 KPI Utama")
k1, k2, k3, k4, k5 = st.columns(5)

kpis = [
    ("Bil. Responden", f"{n:,}", "Data selepas filter"),
    ("Skor Keseluruhan", f"{overall:.2f}", classify_score(overall)),
    ("% Baik", f"{high_pct:.1f}%", "Skor ≥ 4.00"),
    ("% Perlu Intervensi", f"{risk_pct:.1f}%", "Skor < 3.40"),
    ("Cronbach Alpha", f"{alpha:.3f}" if not pd.isna(alpha) else "NA", "Konsistensi dalaman")
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

show_audit(
    "Jalan kira KPI",
    f"""
    <b>Bilangan Responden</b> = jumlah baris data selepas filter = {n:,}.<br>
    <b>Skor Keseluruhan</b> = purata semua skor konstruk yang sah untuk jenis responden dipilih.
    Dalam filter ini, konstruk yang digunakan ialah: {html_escape(", ".join(dimension_cols))}.<br>
    <b>% Baik</b> = bilangan responden dengan skor keseluruhan ≥ 4.00 / {n:,} × 100 = {high_pct:.1f}%.<br>
    <b>% Perlu Intervensi</b> = bilangan responden dengan skor keseluruhan < 3.40 / {n:,} × 100 = {risk_pct:.1f}%.<br>
    <b>Cronbach Alpha</b> dikira daripada item Likert yang dikesan dalam data filter semasa. Nilai ini menunjukkan
    tahap konsistensi dalaman instrumen, bukan ukuran keberkesanan program secara langsung.
    """
)

# ============================================================
# DIMENSION ANALYSIS
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 📊 Analisis Dimensi / Konstruk")

dim_summary = (
    df[dimension_cols]
    .mean()
    .reset_index()
    .rename(columns={"index": "Dimensi", 0: "Skor Purata"})
)
dim_summary["Status"] = dim_summary["Skor Purata"].apply(classify_score)
dim_summary = dim_summary.sort_values("Skor Purata", ascending=True)

chart_dim = alt_horizontal_bar(
    dim_summary,
    "Dimensi",
    "Skor Purata",
    "Skor Purata Mengikut Dimensi / Konstruk"
)
st.altair_chart(chart_dim, use_container_width=True)

lowest_dim = dim_summary.iloc[0]["Dimensi"]
lowest_score = dim_summary.iloc[0]["Skor Purata"]
highest_dim = dim_summary.iloc[-1]["Dimensi"]
highest_score = dim_summary.iloc[-1]["Skor Purata"]

show_audit(
    "Jalan kira graf dimensi",
    f"""
    Setiap bar mewakili skor purata bagi satu konstruk. Contohnya, jika konstruk mempunyai 5 item,
    sistem mengira purata item tersebut untuk setiap responden, kemudian mengambil purata keseluruhan responden.
    Konstruk terendah bagi filter ini ialah <b>{html_escape(lowest_dim)}</b> dengan skor <b>{lowest_score:.2f}</b>,
    manakala konstruk tertinggi ialah <b>{html_escape(highest_dim)}</b> dengan skor <b>{highest_score:.2f}</b>.<br><br>
    <b>Contoh formula konstruk terendah:</b><br>
    {html_escape(formula_text(lowest_dim, valid_constructs.get(lowest_dim, [])))}<br><br>
    <b>Interpretasi:</b> {html_escape(lowest_dim)} berada pada status {classify_html(lowest_score)}.
    """
)

st.dataframe(dim_summary, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# GROUP COMPARISON
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🧭 Perbandingan Mengikut Kategori")

group_choice_label = st.selectbox(
    "Pilih kategori perbandingan",
    ["Zon", "Negeri", "Jenis Responden"],
    index=0
)

group_col_map = {
    "Zon": "Zone",
    "Negeri": "State",
    "Jenis Responden": "Jenis Responden"
}
group_col = group_col_map[group_choice_label]

group_df = (
    df.groupby(group_col, dropna=False)["Skor Keseluruhan"]
    .agg(["mean", "count"])
    .reset_index()
    .rename(columns={group_col: "Kategori", "mean": "Skor Purata", "count": "Bilangan"})
    .sort_values("Skor Purata", ascending=False)
)

chart_group = alt_bar(
    group_df,
    "Kategori",
    "Skor Purata",
    f"Perbandingan Skor Keseluruhan Mengikut {group_choice_label}",
    sort="-y"
)
st.altair_chart(chart_group, use_container_width=True)

best_row = group_df.iloc[0]
weak_row = group_df.iloc[-1]

show_audit(
    "Jalan kira graf perbandingan kategori",
    f"""
    Sistem mengumpulkan data berdasarkan <b>{html_escape(group_choice_label)}</b>.
    Bagi setiap kategori, skor dikira sebagai purata <b>Skor Keseluruhan</b> responden dalam kategori tersebut.
    Kategori tertinggi ialah <b>{html_escape(best_row['Kategori'])}</b> dengan skor <b>{best_row['Skor Purata']:.2f}</b>
    berdasarkan <b>{int(best_row['Bilangan'])}</b> responden.
    Kategori terendah ialah <b>{html_escape(weak_row['Kategori'])}</b> dengan skor <b>{weak_row['Skor Purata']:.2f}</b>
    berdasarkan <b>{int(weak_row['Bilangan'])}</b> responden.
    """
)

st.dataframe(group_df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# RE-AIM
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🎯 Analisis RE-AIM")

reaim_map = {
    "Reach": ["Akses & Kebolehcapaian", "Outcome Teras", "Kepuasan Sistem"],
    "Effectiveness": ["Kesan & Perubahan Klien", "Outcome Klien", "Keberkesanan Intervensi Pegawai"],
    "Adoption": ["Kolaborasi Dalaman", "Kesedaran Peranan", "Sokongan Organisasi"],
    "Implementation": ["SOP & Tadbir Urus", "Kualiti Penyampaian", "Pematuhan Etika", "Pengurusan Kes"],
    "Maintenance": ["Kelestarian T3", "Keperluan Penambahbaikan Pegawai", "Keperluan Penambahbaikan Warga JKM"]
}

reaim_rows = []
for domain, dims in reaim_map.items():
    available = [d for d in dims if d in df.columns and df[d].notna().sum() > 0]
    score = df[available].mean(axis=1).mean() if available else np.nan
    reaim_rows.append({
        "Domain RE-AIM": domain,
        "Skor": score,
        "Status": classify_score(score),
        "Dimensi Digunakan": ", ".join(available) if available else "Tiada dimensi sepadan untuk filter ini"
    })

reaim_df = pd.DataFrame(reaim_rows)

chart_reaim = alt_bar(
    reaim_df.dropna(subset=["Skor"]),
    "Domain RE-AIM",
    "Skor",
    "Skor Mengikut Domain RE-AIM",
    sort=None
)
st.altair_chart(chart_reaim, use_container_width=True)

show_audit(
    "Jalan kira RE-AIM",
    """
    RE-AIM dipetakan secara automatik kepada konstruk yang wujud dalam dataset selepas filter.
    Reach merujuk capaian perkhidmatan; Effectiveness merujuk keberkesanan/outcome;
    Adoption merujuk penerimaan dan sokongan organisasi; Implementation merujuk pelaksanaan SOP,
    kualiti dan pengurusan; Maintenance merujuk kelestarian dan keperluan penambahbaikan.
    Jika sesuatu domain tidak mempunyai konstruk yang sah untuk jenis responden dipilih, sistem tidak memaksa pengiraan.
    """
)

for _, r in reaim_df.iterrows():
    if pd.notna(r["Skor"]):
        st.markdown(f"""
        <div class="note-blue">
        <b>{html_escape(r['Domain RE-AIM'])}</b>: Skor {r['Skor']:.2f} ({html_escape(r['Status'])}).<br>
        Domain ini dikira menggunakan dimensi: {html_escape(r['Dimensi Digunakan'])}.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="warning-box">
        <b>{html_escape(r['Domain RE-AIM'])}</b>: Tidak dikira kerana tiada konstruk sepadan untuk filter semasa.
        </div>
        """, unsafe_allow_html=True)

st.dataframe(reaim_df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# CMO QUALITATIVE
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🧩 Analisis Kualitatif CMO")

if df_qual.empty:
    show_warning_box(
        "Tiada data kualitatif",
        "Tiada data kualitatif dikesan untuk filter semasa. Analisis CMO tidak dipaparkan."
    )
else:
    cmo_cols = [c for c in ["CMO_Context", "CMO_Mechanism", "CMO_Outcome", "RE_AIM_Tag"] if c in df_qual.columns]

    if not cmo_cols:
        show_warning_box(
            "Kolum CMO tidak ditemui",
            "Data kualitatif wujud, tetapi kolum CMO_Context, CMO_Mechanism, CMO_Outcome atau RE_AIM_Tag tidak ditemui."
        )
    else:
        for c in cmo_cols:
            counts = (
                df_qual[c]
                .dropna()
                .astype(str)
                .value_counts()
                .head(10)
                .reset_index()
            )
            counts.columns = ["Tema", "Bilangan"]

            if counts.empty:
                continue

            st.markdown(f"### {clean_label(c)}")
            chart_cmo = alt.Chart(counts).mark_bar(cornerRadiusTopLeft=7, cornerRadiusTopRight=7).encode(
                x=alt.X("Tema:N", sort="-y", title=None, axis=alt.Axis(labelAngle=-25)),
                y=alt.Y("Bilangan:Q", title="Bilangan"),
                color=alt.Color("Tema:N", legend=None),
                tooltip=["Tema:N", "Bilangan:Q"]
            ).properties(
                title=f"Taburan Tema {clean_label(c)}",
                height=380
            ).configure_axis(
                labelColor="white",
                titleColor="white",
                gridColor="rgba(255,255,255,0.16)"
            ).configure_title(
                color="white",
                fontSize=16,
                fontWeight="bold"
            ).configure_view(
                strokeOpacity=0
            )

            st.altair_chart(chart_cmo, use_container_width=True)

            top_theme = counts.iloc[0]["Tema"]
            top_count = counts.iloc[0]["Bilangan"]

            show_audit(
                f"Jalan kira tema {clean_label(c)}",
                f"""
                Sistem mengira kekerapan setiap tema dalam kolum <b>{html_escape(c)}</b>.
                Tema tertinggi ialah <b>{html_escape(top_theme)}</b> dengan <b>{int(top_count)}</b> sebutan.
                Kekerapan tema digunakan untuk mengenal pasti konteks, mekanisme atau outcome dominan
                dalam data kualitatif bagi filter semasa.
                """
            )

            st.dataframe(counts, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# SEM / PATH MODEL
# ============================================================

def get_sem_spec(df, selected_type):
    if selected_type == "Semua":
        return None, None, (
            "SEM tidak dijalankan kerana Jenis Responden = Semua. "
            "Instrumen S1, S2 dan S3 mempunyai konstruk dan DV berbeza. "
            "Sila pilih Klien, Pegawai atau Warga JKM untuk SEM khusus."
        )

    if selected_type == "Klien":
        iv = {
            "Akses & Kebolehcapaian": get_cols_start(df, ["K2A"]),
            "Komunikasi Perkhidmatan": get_cols_start(df, ["K2B"]),
            "Hubungan Terapeutik": get_cols_start(df, ["K2C"]),
            "Hak, Etika & Keselamatan": get_cols_start(df, ["K2D"]),
            "Kesesuaian Intervensi": get_cols_start(df, ["K2E"])
        }
        dv = get_cols_start(df, ["K1O"])
        if not dv:
            possible = [c for c in ["Score_Core_Outcome", "Score_Overall", "Score_T1_Outcome"] if c in df.columns]
            dv = possible

    elif selected_type == "Pegawai":
        iv = {
            "Kompetensi & Kapasiti Pegawai": get_cols_start(df, ["K3B"]),
            "Pengurusan Kes": get_cols_start(df, ["K3C"]),
            "SOP & Tadbir Urus": get_cols_start(df, ["K4A"]),
            "Kolaborasi Dalaman": get_cols_start(df, ["K4B"]),
            "Kualiti Penyampaian": get_cols_start(df, ["K4C"])
        }
        dv = [c for c in ["Score_K3A_Success", "Score_Overall"] if c in df.columns]
        if not dv:
            dv = get_cols_start(df, ["K3A"])

    elif selected_type == "Warga JKM":
        iv = {
            "Kesedaran Peranan": get_cols_start(df, ["K4D"]),
            "Sokongan Organisasi": get_cols_start(df, ["K4E"]),
            "Pematuhan Etika": get_cols_start(df, ["K4F"]),
            "Koordinasi Sistem": get_cols_start(df, ["K4G"]),
            "Data & Dashboard": get_cols_start(df, ["K4H"])
        }
        dv = [c for c in ["Score_K5B_Improvement", "Score_Overall"] if c in df.columns]
        if not dv:
            dv = get_cols_start(df, ["K5B"])

    else:
        return None, None, "Jenis responden tidak dikenali untuk model SEM."

    iv = {k: v for k, v in iv.items() if v}
    if not iv:
        return None, None, "SEM tidak dapat dijalankan kerana tiada konstruk IV yang sah dikesan."

    if not dv:
        return iv, None, (
            "SEM tidak dapat dijalankan kerana pemboleh ubah bersandar atau DV tidak ditemui. "
            "Untuk Klien, DV sesuai ialah K1O atau outcome klien. Untuk Pegawai, DV sesuai ialah "
            "Score_K3A_Success atau K3A. Untuk Warga JKM, DV sesuai ialah Score_K5B_Improvement, "
            "Score_Overall atau K5B."
        )

    return iv, dv, None

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🔗 Model SEM / Path Model Mengikut Jenis Responden")

iv_spec, dv_cols, sem_warning = get_sem_spec(df_filtered_raw, selected_type)

if sem_warning:
    show_warning_box(
        "SEM tidak dipaparkan",
        html_escape(sem_warning)
    )
else:
    sem_data = pd.DataFrame(index=df_filtered_raw.index)
    for name, cols in iv_spec.items():
        sem_data[name] = safe_mean(df_filtered_raw, cols)
    sem_data["Outcome / DV"] = safe_mean(df_filtered_raw, dv_cols)
    sem_data = sem_data.dropna()

    valid_n_sem = len(sem_data)

    if valid_n_sem < 30:
        show_warning_box(
            "SEM tidak cukup data sah",
            f"""
            Data sah selepas filter dan selepas membuang nilai kosong hanya <b>{valid_n_sem}</b> responden.
            Sistem mencadangkan sekurang-kurangnya <b>30 responden</b> untuk path model eksploratori dashboard,
            dan lebih tinggi untuk SEM penuh seperti SmartPLS/AMOS. DV yang digunakan ialah:
            <b>{html_escape(format_cols(dv_cols))}</b>.
            """
        )
    else:
        rows = []
        for col in sem_data.columns:
            if col == "Outcome / DV":
                continue
            beta = sem_data[col].corr(sem_data["Outcome / DV"])
            rows.append({
                "Laluan SEM": f"{col} → Outcome / DV",
                "Konstruk IV": col,
                "Path Coefficient β": beta,
                "Kekuatan": "Kuat" if abs(beta) >= .70 else "Sederhana" if abs(beta) >= .40 else "Rendah"
            })

        sem_result = pd.DataFrame(rows).sort_values("Path Coefficient β", ascending=False)
        chart_sem = alt_bar(
            sem_result,
            "Konstruk IV",
            "Path Coefficient β",
            f"Path Coefficient SEM: {selected_type} → Outcome",
            sort="-y"
        )
        st.altair_chart(chart_sem, use_container_width=True)

        show_audit(
            "Jalan kira SEM / path model",
            f"""
            SEM ini hanya dijalankan kerana Jenis Responden dipilih sebagai <b>{html_escape(selected_type)}</b>.
            Setiap konstruk IV dikira sebagai purata item-item dalam konstruk tersebut. DV dikira menggunakan:
            <b>{html_escape(format_cols(dv_cols))}</b>.<br><br>
            Path coefficient β dianggarkan menggunakan korelasi piawai antara skor konstruk IV dan skor DV.
            Ini ialah <b>path model eksploratori untuk dashboard</b>, bukan SEM penuh menggantikan SmartPLS/AMOS.
            Sampel sah untuk SEM selepas filter ialah <b>{valid_n_sem}</b> responden.
            """
        )

        st.dataframe(sem_result, use_container_width=True, hide_index=True)

        top_sem = sem_result.iloc[0]
        show_note(
            "Interpretasi SEM utama",
            f"""
            Laluan paling dominan ialah <b>{html_escape(top_sem['Laluan SEM'])}</b> dengan β =
            <b>{top_sem['Path Coefficient β']:.3f}</b>. Ini menunjukkan konstruk tersebut mempunyai
            hubungan paling kuat dengan outcome bagi filter semasa. Jika nilai β positif, peningkatan konstruk
            tersebut dijangka berkait dengan peningkatan outcome. Jika nilai β rendah, konstruk tersebut kurang
            berperanan sebagai pemacu outcome dalam data semasa.
            """
        )

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# INTERVENTION
# ============================================================

def detailed_intervention(zone, state, respondent_type, dim, score):
    lokasi = location_text(zone, state, respondent_type)

    if score < 3.4:
        tahap = "Kritikal / Perlu Intervensi Segera"
        tempoh = "3 bulan"
        sasaran = min(5, score + 0.50)
        cadangan = [
            "Laksanakan audit ringkas terhadap punca skor rendah melalui semakan item yang membentuk dimensi ini.",
            "Adakan sesi coaching atau klinik intervensi kepada pegawai/unit berkaitan.",
            "Tetapkan pemantauan mingguan terhadap kes atau proses kerja yang berkaitan dengan dimensi ini.",
            "Laksanakan sesi maklum balas berstruktur bersama kumpulan responden sasaran.",
            "Wujudkan KPI mikro supaya skor dimensi meningkat secara berperingkat dalam tempoh 3 bulan."
        ]
        rasional = (
            f"Skor {score:.2f} berada di bawah 3.40. Ini menunjukkan dimensi ini berisiko menjejaskan "
            f"keberkesanan perkhidmatan bagi {lokasi}."
        )

    elif score < 4.0:
        tahap = "Sederhana / Perlu Pengukuhan"
        tempoh = "2 hingga 3 bulan"
        sasaran = min(5, score + 0.30)
        cadangan = [
            "Laksanakan latihan mikro bersasar berdasarkan item yang paling rendah dalam dimensi ini.",
            "Perkukuh komunikasi dan penyelarasan dalaman melibatkan pegawai atau unit berkaitan.",
            "Pantau skor secara bulanan untuk melihat sama ada perubahan proses kerja memberi kesan.",
            "Dokumentasikan amalan baik daripada lokasi atau kumpulan yang mencatat skor lebih tinggi.",
            "Gunakan sesi refleksi kes untuk mengenal pasti halangan pelaksanaan."
        ]
        rasional = (
            f"Skor {score:.2f} berada pada tahap sederhana. Dimensi ini tidak kritikal tetapi masih belum "
            f"mencapai tahap kukuh 4.00."
        )

    else:
        tahap = "Baik / Kekalkan dan Replikasi"
        tempoh = "Pemantauan berkala"
        sasaran = min(5, score + 0.10)
        cadangan = [
            "Kekalkan amalan sedia ada kerana skor telah melepasi tahap 4.00.",
            "Dokumentasikan amalan terbaik sebagai rujukan kepada zon/negeri/kumpulan lain.",
            "Gunakan dimensi ini sebagai penanda aras dalaman.",
            "Laksanakan pemantauan berkala supaya prestasi tidak menurun.",
            "Replikasi pendekatan yang berjaya kepada dimensi yang lebih rendah."
        ]
        rasional = (
            f"Skor {score:.2f} menunjukkan dimensi ini berada pada tahap baik bagi {lokasi}."
        )

    return {
        "Lokasi / Sasaran": lokasi,
        "Dimensi": dim,
        "Skor Semasa": score,
        "Tahap": tahap,
        "Tempoh": tempoh,
        "Sasaran Skor": sasaran,
        "Rasional": rasional,
        "Cadangan": cadangan
    }

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🛠️ Intervensi Bersasar Mengikut Filter")

weak_dims = dim_summary.sort_values("Skor Purata", ascending=True).head(5)
interventions = []

for _, r in weak_dims.iterrows():
    interventions.append(
        detailed_intervention(
            selected_zone,
            selected_state,
            selected_type,
            r["Dimensi"],
            r["Skor Purata"]
        )
    )

for item in interventions:
    st.markdown(f"""
    <div class="intervention">
    <h3>{html_escape(item['Dimensi'])}</h3>
    <p><b>Lokasi / sasaran:</b> {html_escape(item['Lokasi / Sasaran'])}</p>
    <p><b>Skor semasa:</b> {item['Skor Semasa']:.2f} | <b>Tahap:</b> {html_escape(item['Tahap'])} |
    <b>Sasaran:</b> {item['Skor Semasa']:.2f} → {item['Sasaran Skor']:.2f} |
    <b>Tempoh:</b> {html_escape(item['Tempoh'])}</p>
    <p><b>Rasional:</b> {html_escape(item['Rasional'])}</p>
    <ol>
    {''.join([f"<li>{html_escape(x)}</li>" for x in item['Cadangan']])}
    </ol>
    </div>
    """, unsafe_allow_html=True)

show_audit(
    "Jalan kira intervensi",
    f"""
    Sistem memilih lima dimensi dengan skor purata terendah selepas filter. Bagi setiap dimensi,
    tahap intervensi ditentukan menggunakan ambang: skor < 3.40 = intervensi segera,
    3.40 hingga 3.99 = pengukuhan, dan ≥ 4.00 = kekalkan/replikasi. Lokasi intervensi pula
    dibina berdasarkan filter aktif: <b>{html_escape(location_text(selected_zone, selected_state, selected_type))}</b>.
    """
)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# SIMULATION
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🔮 Simulasi Impak Intervensi")

increase = st.slider("Andaian peningkatan skor dimensi selepas intervensi (%)", 1, 30, 10)

sim_df = weak_dims[["Dimensi", "Skor Purata"]].copy()
sim_df["Skor Selepas Intervensi"] = np.minimum(5, sim_df["Skor Purata"] * (1 + increase / 100))
sim_df["Perubahan Skor"] = sim_df["Skor Selepas Intervensi"] - sim_df["Skor Purata"]
sim_df["Status Selepas"] = sim_df["Skor Selepas Intervensi"].apply(classify_score)

sim_long = sim_df.melt(
    id_vars=["Dimensi"],
    value_vars=["Skor Purata", "Skor Selepas Intervensi"],
    var_name="Senario",
    value_name="Skor"
)

chart_sim = alt.Chart(sim_long).mark_bar(cornerRadiusTopLeft=7, cornerRadiusTopRight=7).encode(
    x=alt.X("Dimensi:N", title=None, axis=alt.Axis(labelAngle=-25)),
    y=alt.Y("Skor:Q", title="Skor", scale=alt.Scale(domain=[0, 5])),
    color=alt.Color(
        "Senario:N",
        scale=alt.Scale(
            domain=["Skor Purata", "Skor Selepas Intervensi"],
            range=["#ef476f", "#06d6a0"]
        )
    ),
    xOffset="Senario:N",
    tooltip=["Dimensi:N", "Senario:N", alt.Tooltip("Skor:Q", format=".3f")]
).properties(
    title="Simulasi Sebelum dan Selepas Intervensi",
    height=430
).configure_axis(
    labelColor="white",
    titleColor="white",
    gridColor="rgba(255,255,255,0.16)"
).configure_title(
    color="white",
    fontSize=17,
    fontWeight="bold"
).configure_legend(
    labelColor="white",
    titleColor="white"
).configure_view(
    strokeOpacity=0
)

st.altair_chart(chart_sim, use_container_width=True)

show_audit(
    "Jalan kira simulasi",
    f"""
    Simulasi menggunakan lima dimensi terendah. Formula simulasi ialah:
    <b>Skor Selepas = min(5.00, Skor Semasa × (1 + {increase}/100))</b>.
    Nilai maksimum dihadkan kepada 5.00 kerana skala Likert maksimum ialah 5.
    Simulasi ini menunjukkan potensi peningkatan sekiranya intervensi berjaya menaikkan skor sebanyak {increase}%.
    """
)

st.dataframe(sim_df, use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# MANAGEMENT SUMMARY
# ============================================================

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🧾 Rumusan Pengurusan Automatik")

top3 = weak_dims.head(3)

summary_text = f"""
Berdasarkan analisis semasa bagi {location_text(selected_zone, selected_state, selected_type)},
sebanyak {n:,} responden telah dianalisis. Skor keseluruhan ialah {overall:.2f}, iaitu pada tahap
{classify_score(overall)}. Tiga dimensi yang memerlukan perhatian utama ialah
{top3.iloc[0]['Dimensi']} ({top3.iloc[0]['Skor Purata']:.2f}),
{top3.iloc[1]['Dimensi']} ({top3.iloc[1]['Skor Purata']:.2f}) dan
{top3.iloc[2]['Dimensi']} ({top3.iloc[2]['Skor Purata']:.2f}).
Intervensi bersasar dicadangkan kepada kumpulan/lokasi ini dengan fokus kepada dimensi terendah,
diikuti pemantauan berkala dan simulasi peningkatan skor.
"""

st.markdown(f"""
<div class="note-blue">
{html_escape(summary_text)}
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# HTML / PDF REPORT GENERATION
# ============================================================

def dataframe_to_html_table(df_table):
    return df_table.to_html(index=False, border=0, classes="report-table", escape=True)

def build_html_report():
    respondent_html = dataframe_to_html_table(respondent_dist)
    dim_html = dataframe_to_html_table(dim_summary)
    reaim_html = dataframe_to_html_table(reaim_df)
    group_html = dataframe_to_html_table(group_df)
    sim_html = dataframe_to_html_table(sim_df)

    intervention_html = ""
    for item in interventions:
        intervention_html += f"""
        <div class="box">
            <h3>{html_escape(item['Dimensi'])}</h3>
            <p><b>Lokasi/Sasaran:</b> {html_escape(item['Lokasi / Sasaran'])}</p>
            <p><b>Skor Semasa:</b> {item['Skor Semasa']:.2f} |
            <b>Tahap:</b> {html_escape(item['Tahap'])} |
            <b>Sasaran:</b> {item['Skor Semasa']:.2f} → {item['Sasaran Skor']:.2f}</p>
            <p><b>Rasional:</b> {html_escape(item['Rasional'])}</p>
            <ol>
                {''.join([f"<li>{html_escape(x)}</li>" for x in item['Cadangan']])}
            </ol>
        </div>
        """

    sem_html = ""
    if "sem_result" in globals():
        sem_html = dataframe_to_html_table(sem_result)
    else:
        sem_html = "<p>SEM tidak dipaparkan kerana Jenis Responden = Semua, DV tidak wujud, atau data sah tidak mencukupi.</p>"

    report = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Laporan JKM DSS-IIS</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 34px;
            color: #111827;
            line-height: 1.48;
        }}
        h1 {{
            color: #102542;
            border-bottom: 5px solid #ffb703;
            padding-bottom: 12px;
        }}
        h2 {{
            margin-top: 32px;
            color: #102542;
            border-left: 8px solid #118ab2;
            padding-left: 12px;
        }}
        .meta {{
            background: #eef6ff;
            padding: 16px;
            border-radius: 12px;
            border-left: 6px solid #118ab2;
        }}
        .box {{
            background: #f8fafc;
            padding: 16px;
            border-radius: 12px;
            border-left: 6px solid #ffb703;
            margin: 14px 0;
        }}
        .kpi {{
            display: inline-block;
            width: 18%;
            margin: 6px;
            padding: 14px;
            background: #102542;
            color: white;
            border-radius: 14px;
            vertical-align: top;
        }}
        .kpi b {{
            font-size: 22px;
            color: #ffd166;
        }}
        table.report-table {{
            border-collapse: collapse;
            width: 100%;
            margin-top: 10px;
            font-size: 12px;
        }}
        table.report-table th {{
            background: #102542;
            color: white;
            padding: 8px;
            border: 1px solid #e5e7eb;
        }}
        table.report-table td {{
            padding: 7px;
            border: 1px solid #e5e7eb;
        }}
        .audit {{
            background: #fff7d6;
            padding: 14px;
            border-left: 6px solid #ffb703;
            border-radius: 10px;
            margin-top: 10px;
        }}
        @media print {{
            body {{ margin: 18mm; }}
            button {{ display:none; }}
        }}
    </style>
    </head>
    <body>
        <button onclick="window.print()" style="padding:12px 18px;background:#ffb703;border:0;border-radius:10px;font-weight:bold;">
            Print / Save as PDF
        </button>

        <h1>Laporan JKM Psychological Services DSS-IIS</h1>
        <div class="meta">
            <b>Dijana pada:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br>
            <b>Filter:</b> Zon = {html_escape(selected_zone)}, Negeri = {html_escape(selected_state)}, Jenis Responden = {html_escape(selected_type)}
        </div>

        <h2>1. Pengenalan</h2>
        <p>{html_escape(intro_text).replace(chr(10), '<br>')}</p>

        <h2>2. Profil Responden</h2>
        {respondent_html}

        <h2>3. KPI Utama</h2>
        <div class="kpi">Bil. Responden<br><b>{n:,}</b></div>
        <div class="kpi">Skor Keseluruhan<br><b>{overall:.2f}</b></div>
        <div class="kpi">% Baik<br><b>{high_pct:.1f}%</b></div>
        <div class="kpi">% Intervensi<br><b>{risk_pct:.1f}%</b></div>
        <div class="kpi">Cronbach Alpha<br><b>{alpha:.3f if not pd.isna(alpha) else 'NA'}</b></div>

        <div class="audit">
        <b>Jalan kira KPI:</b> Skor keseluruhan dikira sebagai purata konstruk sah. % Baik ialah skor ≥ 4.00.
        % Intervensi ialah skor < 3.40.
        </div>

        <h2>4. Analisis Dimensi</h2>
        {dim_html}
        <div class="audit">
        <b>Jalan kira dimensi:</b> Setiap konstruk dikira sebagai purata item yang membentuk konstruk tersebut.
        Konstruk terendah ialah {html_escape(lowest_dim)} dengan skor {lowest_score:.2f}.
        </div>

        <h2>5. Analisis Perbandingan Kategori</h2>
        {group_html}

        <h2>6. RE-AIM</h2>
        {reaim_html}

        <h2>7. CMO</h2>
        <p>Analisis CMO dipaparkan dalam sistem berdasarkan tema kualitatif yang wujud selepas filter.</p>

        <h2>8. SEM / Path Model</h2>
        {sem_html}
        <div class="audit">
        <b>Nota SEM:</b> SEM hanya sah dipaparkan apabila satu jenis responden dipilih dan DV yang sesuai wujud.
        Jika semua responden digabungkan, SEM tidak dijalankan kerana S1, S2 dan S3 mempunyai konstruk berbeza.
        </div>

        <h2>9. Intervensi Bersasar</h2>
        {intervention_html}

        <h2>10. Simulasi Impak</h2>
        {sim_html}
        <div class="audit">
        Simulasi menggunakan andaian peningkatan {increase}% terhadap dimensi terendah.
        Formula: Skor Selepas = min(5.00, Skor Semasa × (1 + {increase}/100)).
        </div>

        <h2>11. Rumusan Pengurusan</h2>
        <div class="box">{html_escape(summary_text)}</div>
    </body>
    </html>
    """
    return report

def make_downloadable_html(html_string):
    return html_string.encode("utf-8")

def make_pdf_if_reportlab_available(report_text):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name="MalayBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12
        ))
        styles.add(ParagraphStyle(
            name="MalayHeading",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=colors.HexColor("#102542")
        ))

        story = []

        def p(txt):
            story.append(Paragraph(html_escape(str(txt)).replace("\n", "<br/>"), styles["MalayBody"]))
            story.append(Spacer(1, 8))

        def h(txt):
            story.append(Paragraph(str(txt), styles["MalayHeading"]))
            story.append(Spacer(1, 8))

        def table_from_df(dfx, max_rows=20):
            dfx = dfx.head(max_rows).copy()
            data = [list(dfx.columns)] + dfx.astype(str).values.tolist()
            tbl = Table(data, repeatRows=1)
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#102542")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 10))

        story.append(Paragraph("Laporan JKM Psychological Services DSS-IIS", styles["Title"]))
        p(f"Dijana pada: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        p(f"Filter: Zon={selected_zone}, Negeri={selected_state}, Jenis Responden={selected_type}")

        h("1. Pengenalan")
        p(intro_text)

        h("2. Profil Responden")
        table_from_df(respondent_dist)

        h("3. KPI Utama")
        kpi_df = pd.DataFrame({
            "KPI": ["Bil. Responden", "Skor Keseluruhan", "% Baik", "% Perlu Intervensi", "Cronbach Alpha"],
            "Nilai": [f"{n:,}", f"{overall:.2f}", f"{high_pct:.1f}%", f"{risk_pct:.1f}%", f"{alpha:.3f}" if not pd.isna(alpha) else "NA"]
        })
        table_from_df(kpi_df)

        h("4. Analisis Dimensi")
        table_from_df(dim_summary, max_rows=30)
        p(f"Dimensi terendah ialah {lowest_dim} dengan skor {lowest_score:.2f}. Formula: {formula_text(lowest_dim, valid_constructs.get(lowest_dim, []))}")

        h("5. RE-AIM")
        table_from_df(reaim_df)

        h("6. SEM / Path Model")
        if "sem_result" in globals():
            table_from_df(sem_result)
        else:
            p("SEM tidak dipaparkan kerana Jenis Responden = Semua, DV tidak wujud, atau data sah tidak mencukupi.")

        h("7. Intervensi Bersasar")
        for item in interventions:
            p(f"{item['Dimensi']} | Skor {item['Skor Semasa']:.2f} | {item['Tahap']} | Sasaran {item['Sasaran Skor']:.2f}")
            p(item["Rasional"])
            for idx, cad in enumerate(item["Cadangan"], 1):
                p(f"{idx}. {cad}")

        h("8. Simulasi Impak")
        table_from_df(sim_df)

        h("9. Rumusan Pengurusan")
        p(summary_text)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    except Exception:
        return None

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown("## 🖨️ Laporan Lengkap: Download / Print")

report_html = build_html_report()
html_bytes = make_downloadable_html(report_html)
pdf_bytes = make_pdf_if_reportlab_available(report_html)

show_audit(
    "Kandungan laporan",
    """
    Laporan merangkumi pengenalan automatik, profil responden, KPI, jalan kira, analisis dimensi,
    perbandingan kategori, RE-AIM, CMO, SEM/path model, intervensi bersasar, simulasi dan rumusan pengurusan.
    Jika PDF tidak tersedia kerana library <b>reportlab</b> belum dipasang, sistem tetap menyediakan laporan HTML
    yang boleh dibuka dan dicetak sebagai PDF melalui browser.
    """
)

c1, c2 = st.columns(2)

with c1:
    st.download_button(
        "📄 Download Laporan HTML untuk Print",
        data=html_bytes,
        file_name=f"Laporan_JKM_DSS_{selected_zone}_{selected_state}_{selected_type}.html".replace(" ", "_"),
        mime="text/html"
    )

with c2:
    if pdf_bytes is not None:
        st.download_button(
            "📕 Download PDF Lengkap",
            data=pdf_bytes,
            file_name=f"Laporan_JKM_DSS_{selected_zone}_{selected_state}_{selected_type}.pdf".replace(" ", "_"),
            mime="application/pdf"
        )
    else:
        st.warning("PDF sebenar perlukan reportlab dalam requirements.txt. HTML report masih boleh print sebagai PDF.")

st.markdown("""
<div class="note-blue">
<b>Untuk print:</b> Download laporan HTML, buka fail tersebut dalam browser, kemudian tekan Ctrl+P dan pilih
Save as PDF. Untuk PDF terus dari sistem, tambah <b>reportlab</b> dalam requirements.txt.
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
