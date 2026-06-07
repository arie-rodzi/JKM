import io
from pathlib import Path
import re
from collections import Counter

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="JKM PsyCounsel National Analytics",
    page_icon="🇲🇾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:radial-gradient(circle at top left,#1D4ED8 0%,#0B1F3A 38%,#020617 100%);color:#F8FAFC;}
.block-container{padding-top:1rem;max-width:1700px;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#06101E,#0B1628);border-right:1px solid rgba(197,160,23,.28)}
h1,h2,h3{color:#fff!important;letter-spacing:-.03em;}
.hero{padding:34px;border-radius:32px;background:linear-gradient(135deg,rgba(197,160,23,.26),rgba(14,124,123,.12)),linear-gradient(135deg,#06142B,#10213C 58%,#0E4A6B);border:1px solid rgba(253,230,138,.38);box-shadow:0 28px 90px rgba(0,0,0,.42);margin-bottom:18px;}
.badge{display:inline-block;padding:7px 13px;border-radius:999px;background:rgba(197,160,23,.20);border:1px solid rgba(253,230,138,.40);color:#FDE68A;font-weight:900;font-size:12px;letter-spacing:.08em;}
.hero-title{font-size:42px;line-height:1.07;font-weight:900;margin-top:12px;}
.gold{background:linear-gradient(90deg,#FDE68A,#C5A017,#FFF7C2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-subtitle{color:#CBD5E1;font-size:16px;max-width:1160px;margin-top:10px;}
.card{padding:22px;border-radius:25px;background:rgba(15,23,42,.78);border:1px solid rgba(148,163,184,.24);box-shadow:0 20px 58px rgba(0,0,0,.28);margin-bottom:18px;}
.card2{padding:18px;border-radius:22px;background:rgba(30,41,59,.60);border:1px solid rgba(148,163,184,.18);margin-bottom:15px;}
.kpi{padding:20px;border-radius:23px;background:linear-gradient(180deg,rgba(15,23,42,.97),rgba(15,23,42,.72));border:1px solid rgba(148,163,184,.25);min-height:128px;box-shadow:0 14px 36px rgba(0,0,0,.22)}
.klabel{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#94A3B8;font-weight:800;}
.kvalue{font-size:30px;color:white;font-weight:900;margin-top:8px;}
.knote{font-size:13px;color:#CBD5E1;margin-top:4px;}
.stTabs [data-baseweb="tab"]{background:rgba(15,23,42,.86);border:1px solid rgba(148,163,184,.22);border-radius:999px;color:#CBD5E1;padding:10px 16px;margin:3px;}
.stTabs [aria-selected="true"]{background:linear-gradient(90deg,#C5A017,#FDE68A)!important;color:#0F172A!important;font-weight:900;}
.small{font-size:13px;color:#CBD5E1;}
.ok{color:#86EFAC;font-weight:900}.warn{color:#FDE68A;font-weight:900}.bad{color:#FDA4AF;font-weight:900}
hr{border-color:rgba(148,163,184,.20)!important;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

DEFAULT_EXCEL = Path("data/JKM_7Sheet_Full_Simulation_Raw_Data.xlsx")
REQUIRED_SHEETS = [
    "S1_Quant_Raw", "S2_Quant_Raw", "S3_Quant_Raw",
    "Q1_Client_Raw", "Q2_Officer_Raw", "Q3_System_Raw", "T123_Pilot_Raw"
]

# -------------------------------------------------------------------
# Admin login
# -------------------------------------------------------------------
def get_secret(name: str, default: str) -> str:
    try:
        return str(st.secrets.get(name, default))
    except Exception:
        return default

ADMIN_USERNAME = get_secret("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = get_secret("ADMIN_PASSWORD", "jkm2026")

for key, default in {"authenticated": False, "workbook_bytes": None, "workbook_name": "Default simulation workbook"}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<div class="hero">
<span class="badge">ADMIN EXCEL ANALYTICS • 7 SHEETS • FULL CALCULATION ENGINE</span>
<div class="hero-title">JKM PsyCounsel <span class="gold">National Analytics System</span></div>
<div class="hero-subtitle">Admin upload Excel, sistem terus jana S1, S2, S3, Q1, Q2, Q3, T1--T2--T3, reliability, correlation, CMO, RE-AIM, overall framework score, gap ranking dan intervention recommendation.</div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login = st.button("Login Admin", use_container_width=True)
        st.caption("Default demo login: username `admin`, password `jkm2026`. Ubah melalui Streamlit secrets untuk production.")
        st.markdown('</div>', unsafe_allow_html=True)
        if login:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Username atau password tidak tepat.")
    st.stop()

# -------------------------------------------------------------------
# Loader and helpers
# -------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def read_excel_from_bytes(content: bytes) -> dict:
    xl = pd.ExcelFile(io.BytesIO(content), engine="openpyxl")
    return {s: pd.read_excel(xl, sheet_name=s) for s in xl.sheet_names}

@st.cache_data(show_spinner=False)
def read_excel_from_path(path: str) -> dict:
    xl = pd.ExcelFile(path, engine="openpyxl")
    return {s: pd.read_excel(xl, sheet_name=s) for s in xl.sheet_names}

def load_default() -> dict:
    if DEFAULT_EXCEL.exists():
        return read_excel_from_path(str(DEFAULT_EXCEL))
    return {}

def num_series(s):
    return pd.to_numeric(s, errors="coerce")

def mean_col(df: pd.DataFrame, col: str) -> float:
    if df.empty or col not in df.columns:
        return np.nan
    return float(num_series(df[col]).mean())

def pct(x):
    if pd.isna(x):
        return "-"
    return f"{x:.2f}"

def scale100(x):
    if pd.isna(x):
        return np.nan
    return max(0, min(100, (x - 1) / 4 * 100))

def kpi(label, value, note=""):
    st.markdown(f'<div class="kpi"><div class="klabel">{label}</div><div class="kvalue">{value}</div><div class="knote">{note}</div></div>', unsafe_allow_html=True)

def filter_df(df: pd.DataFrame, zone: str, state: str) -> pd.DataFrame:
    out = df.copy()
    if zone != "Semua Zon" and "Zone" in out.columns:
        out = out[out["Zone"].astype(str).eq(zone)]
    if state != "Semua Negeri" and "State" in out.columns:
        out = out[out["State"].astype(str).eq(state)]
    return out

def cols_start(df, prefixes):
    if isinstance(prefixes, str):
        prefixes = [prefixes]
    return [c for c in df.columns if any(str(c).startswith(p) for p in prefixes) and pd.api.types.is_numeric_dtype(df[c])]

def score_cols(df):
    return [c for c in df.columns if str(c).startswith("Score_") and pd.api.types.is_numeric_dtype(df[c])]

def score_summary(df):
    rows = []
    for c in score_cols(df):
        if c == "Score_Overall":
            label = "OVERALL"
        else:
            label = c.replace("Score_", "")
        rows.append({"Construct": label, "Mean_1_5": mean_col(df, c), "Score_100": scale100(mean_col(df, c)), "N": int(df[c].notna().sum())})
    return pd.DataFrame(rows).sort_values("Score_100", ascending=False) if rows else pd.DataFrame()

def item_summary(df, prefixes):
    rows = []
    for c in cols_start(df, prefixes):
        x = num_series(df[c])
        rows.append({"Item": c, "Mean_1_5": float(x.mean()), "Score_100": scale100(float(x.mean())), "Low_%_1_2": float((x <= 2).mean() * 100), "N": int(x.notna().sum())})
    return pd.DataFrame(rows).sort_values("Mean_1_5") if rows else pd.DataFrame()

def cronbach_alpha(df, cols):
    cols = [c for c in cols if c in df.columns]
    if len(cols) < 2 or df.empty:
        return np.nan
    data = df[cols].apply(pd.to_numeric, errors="coerce").dropna()
    if len(data) < 3:
        return np.nan
    k = len(cols)
    item_vars = data.var(axis=0, ddof=1)
    total_var = data.sum(axis=1).var(ddof=1)
    if total_var == 0 or pd.isna(total_var):
        return np.nan
    return float((k / (k - 1)) * (1 - item_vars.sum() / total_var))

def reliability_table(df, construct_map):
    rows = []
    for construct, prefixes in construct_map.items():
        cols = []
        for p in prefixes:
            cols += cols_start(df, p)
        alpha = cronbach_alpha(df, cols)
        mean = float(df[cols].mean(numeric_only=True).mean()) if cols else np.nan
        rows.append({"Construct": construct, "Items": len(cols), "Mean_1_5": mean, "Score_100": scale100(mean), "Cronbach_Alpha": alpha, "Status": alpha_status(alpha)})
    return pd.DataFrame(rows)

def alpha_status(a):
    if pd.isna(a): return "Insufficient"
    if a >= .90: return "Excellent"
    if a >= .80: return "Good"
    if a >= .70: return "Acceptable"
    if a >= .60: return "Questionable"
    return "Review"

def interpret_score(score100):
    if pd.isna(score100): return "No data"
    if score100 >= 80: return "High / Strong"
    if score100 >= 65: return "Moderate High"
    if score100 >= 50: return "Moderate / Watch"
    return "Priority Gap"

def qualitative_theme_counts(df, source_name):
    if df.empty: return pd.DataFrame()
    text_cols = [c for c in df.columns if c not in ["Interview_ID", "FGD_KII_ID", "Zone", "State", "Client_Category", "Position", "Setting", "Participant_Group", "CMO_Context", "CMO_Mechanism", "CMO_Outcome", "RE_AIM_Tag"]]
    rows=[]
    for c in text_cols:
        rows.append({"Source": source_name, "Section": c, "Mentions": int(df[c].notna().sum())})
    return pd.DataFrame(rows).sort_values("Mentions", ascending=False)

def keyword_frequency(df, max_words=25):
    stop = set("dan yang untuk dalam dengan kepada daripada serta atau pada ini itu adalah sebagai oleh ke di dari telah akan tidak boleh perlu paling secara klien pegawai jkm perkhidmatan psikologi kaunseling tuan puan".split())
    text_cols = [c for c in df.columns if df[c].dtype == object and not c.endswith("ID") and c not in ["Zone", "State"]]
    text = " ".join(df[text_cols].astype(str).fillna("").values.ravel()).lower()
    words = re.findall(r"[a-zA-ZÀ-ÿ]{4,}", text)
    words = [w for w in words if w not in stop and w != "nan"]
    cnt = Counter(words).most_common(max_words)
    return pd.DataFrame(cnt, columns=["Keyword", "Frequency"])

def recommendations_from_scores(summary_df, label):
    if summary_df.empty: return []
    low = summary_df[summary_df["Construct"] != "OVERALL"].sort_values("Score_100").head(3)
    recs=[]
    for _, r in low.iterrows():
        c = r["Construct"]
        sc = r["Score_100"]
        if sc >= 70:
            continue
        if "Access" in c or "Referral" in c:
            recs.append(f"{label}: Perkukuh laluan rujukan, masa menunggu, komunikasi awal dan akses klien bagi konstruk {c}.")
        elif "Communication" in c:
            recs.append(f"{label}: Standardkan skrip penerangan, semakan kefahaman dan bahan maklumat mudah faham bagi konstruk {c}.")
        elif "Relationship" in c:
            recs.append(f"{label}: Tambah latihan therapeutic alliance, non-judgemental practice dan trauma-informed communication bagi konstruk {c}.")
        elif "Workload" in c or "Capacity" in c or "OrgSupport" in c:
            recs.append(f"{label}: Semak beban kerja, perjawatan, ruang sesi, SOP dan sistem data bagi konstruk {c}.")
        elif "Coordination" in c:
            recs.append(f"{label}: Wujudkan case conference berkala, referral feedback loop dan SOP koordinasi antara unit bagi konstruk {c}.")
        elif "Ethics" in c or "Stigma" in c:
            recs.append(f"{label}: Perkukuh latihan kerahsiaan, anti-stigma dan rights-based practice bagi konstruk {c}.")
        else:
            recs.append(f"{label}: Fokus intervensi penambahbaikan kepada konstruk {c} yang mencatat skor {sc:.1f}/100.")
    return recs

# -------------------------------------------------------------------
# Admin upload panel
# -------------------------------------------------------------------
with st.sidebar:
    st.success("Logged in as Admin")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.workbook_bytes = None
        st.rerun()
    st.markdown("---")
    st.subheader("Upload Excel")
    uploaded = st.file_uploader("Upload workbook 7 sheet (.xlsx)", type=["xlsx"])
    if uploaded is not None:
        st.session_state.workbook_bytes = uploaded.getvalue()
        st.session_state.workbook_name = uploaded.name
        st.success(f"Excel dimuat naik: {uploaded.name}")
    if st.button("Reset guna default Excel"):
        st.session_state.workbook_bytes = None
        st.session_state.workbook_name = "Default simulation workbook"
        st.rerun()

if st.session_state.workbook_bytes:
    sheets = read_excel_from_bytes(st.session_state.workbook_bytes)
else:
    sheets = load_default()

missing = [s for s in REQUIRED_SHEETS if s not in sheets]
if missing:
    st.error("Excel tidak lengkap. Sheet yang hilang: " + ", ".join(missing))
    st.info("Pastikan workbook mengandungi 7 sheet: " + ", ".join(REQUIRED_SHEETS))
    st.stop()

s1, s2, s3 = sheets["S1_Quant_Raw"], sheets["S2_Quant_Raw"], sheets["S3_Quant_Raw"]
q1, q2, q3 = sheets["Q1_Client_Raw"], sheets["Q2_Officer_Raw"], sheets["Q3_System_Raw"]
t123 = sheets["T123_Pilot_Raw"]

all_zones = sorted(set(pd.concat([df.get("Zone", pd.Series(dtype=str)).dropna().astype(str) for df in [s1,s2,s3,q1,q2,q3,t123]], ignore_index=True)))
all_states = sorted(set(pd.concat([df.get("State", pd.Series(dtype=str)).dropna().astype(str) for df in [s1,s2,s3,q1,q2,q3,t123]], ignore_index=True)))

st.markdown(f'<div class="card"><b>Workbook aktif:</b> {st.session_state.workbook_name} &nbsp; | &nbsp; <b>Sheet lengkap:</b> 7/7 &nbsp; | &nbsp; <b>Mode:</b> Full Calculation Engine</div>', unsafe_allow_html=True)

c1,c2,c3 = st.columns([1,1,1])
with c1:
    zone_pick = st.selectbox("Filter Zon", ["Semua Zon"] + all_zones)
with c2:
    state_options = all_states
    if zone_pick != "Semua Zon":
        chunks=[]
        for df in [s1,s2,s3,q1,q2,q3,t123]:
            if "Zone" in df.columns and "State" in df.columns:
                chunks.append(df[df["Zone"].astype(str).eq(zone_pick)]["State"].dropna().astype(str))
        state_options = sorted(set(pd.concat(chunks, ignore_index=True))) if chunks else []
    state_pick = st.selectbox("Filter Negeri", ["Semua Negeri"] + state_options)
with c3:
    st.info("Semua result ikut filter ini.")

fs1, fs2, fs3, fq1, fq2, fq3, ft123 = [filter_df(df, zone_pick, state_pick) for df in [s1,s2,s3,q1,q2,q3,t123]]

# Construct maps
S1_MAP = {
    "K2A Access": ["K2A"], "K2B Communication": ["K2B"], "K2C Relationship": ["K2C"],
    "K2D Cultural & Rights": ["K2D"], "K2E Continuity": ["K2E"], "K2F Empowerment": ["K2F"], "K1 Outcome": ["K1O"]
}
S2_MAP = {
    "K3A Success": ["K3A"], "K3B Barriers": ["K3B"], "K3C Dropout": ["K3C"],
    "K4A Workload": ["K4A"], "K4B Access Equity": ["K4B"], "K4C Capacity": ["K4C"], "K5 Improvement": ["K5A"]
}
S3_MAP = {
    "K4D Awareness": ["K4D"], "K4E Referral": ["K4E"], "K4F Coordination": ["K4F"],
    "K4G Org Support": ["K4G"], "K4H Ethics Stigma": ["K4H"], "K5B Improvement": ["K5B"]
}



# -------------------------------------------------------------------
# Audit trail: theory -> set -> question -> formula -> framework -> result
# -------------------------------------------------------------------
QUESTION_TEXT = {
    "S1": {
        "K2A": {
            "construct": "K2A Access and Referral", "set": "A", "theory": "RE-AIM Reach; Donabedian Structure; Realist Evaluation Context",
            "framework": {"CMO": "Context", "RE-AIM": "Reach", "Donabedian": "Structure"},
            "items": {
                "K2A1": "Saya mudah mendapatkan maklumat mengenai perkhidmatan ini.",
                "K2A2": "Proses mendapatkan temu janji adalah mudah.",
                "K2A3": "Tempoh menunggu untuk mendapatkan perkhidmatan adalah munasabah.",
                "K2A4": "Lokasi perkhidmatan mudah diakses.",
                "K2A5": "Masa temu janji sesuai dengan jadual harian saya.",
                "K2A6": "Kemudahan yang disediakan membantu saya menghadiri sesi."
            }
        },
        "K2B": {"construct":"K2B Communication Responsiveness","set":"B","theory":"WHO Person-Centred Care; Realist Evaluation Mechanism","framework":{"CMO":"Mechanism","RE-AIM":"Implementation","Donabedian":"Process"},"items":{
            "K2B1":"Tujuan perkhidmatan diterangkan dengan jelas.","K2B2":"Pegawai menggunakan bahasa yang mudah difahami.","K2B3":"Saya memahami matlamat sesi yang dijalankan.","K2B4":"Saya diberi peluang untuk bertanya soalan.","K2B5":"Pegawai memastikan saya memahami penerangan yang diberikan.","K2B6":"Maklumat yang diberikan membantu saya memahami situasi saya."}},
        "K2C": {"construct":"K2C Therapeutic Relationship","set":"C","theory":"Working Alliance; Realist Evaluation Mechanism; WHO Person-Centred Care","framework":{"CMO":"Mechanism","RE-AIM":"Implementation","Donabedian":"Process"},"items":{
            "K2C1":"Pegawai mendengar masalah saya dengan teliti.","K2C2":"Saya berasa selamat untuk berkongsi perkara peribadi.","K2C3":"Saya dilayan dengan hormat.","K2C4":"Perbincangan dalam sesi berkaitan dengan keperluan saya.","K2C5":"Saya dan pegawai mempunyai matlamat yang jelas.","K2C6":"Saya tidak berasa dihakimi semasa sesi.","K2C7":"Pendekatan yang digunakan sesuai dengan keadaan saya."}},
        "K2D": {"construct":"K2D Cultural and Rights Responsiveness","set":"D","theory":"WHO Rights-Based Care; Bronfenbrenner Ecological Systems Theory","framework":{"CMO":"Context + Mechanism","RE-AIM":"Implementation","Donabedian":"Process"},"items":{
            "K2D1":"Latar belakang budaya saya dihormati.","K2D2":"Kepercayaan agama atau nilai hidup saya dihormati.","K2D3":"Keadaan keluarga saya diambil kira.","K2D4":"Pegawai memahami cabaran kehidupan harian saya.","K2D5":"Kerahsiaan maklumat saya dijaga dengan baik.","K2D6":"Saya diberi peluang membuat keputusan berkaitan bantuan yang diterima.","K2D7":"Saya dilayan secara adil tanpa diskriminasi."}},
        "K2E": {"construct":"K2E Continuity and Coordination","set":"E","theory":"RE-AIM Maintenance; Donabedian Process","framework":{"CMO":"Mechanism","RE-AIM":"Maintenance","Donabedian":"Process"},"items":{
            "K2E1":"Saya mendapat maklumat yang jelas mengenai sesi susulan.","K2E2":"Pegawai membantu merancang tindakan selepas sesi.","K2E3":"Saya tahu kepada siapa perlu dirujuk jika memerlukan bantuan tambahan.","K2E4":"Perkhidmatan yang diterima adalah konsisten.","K2E5":"Saya mudah menghubungi pihak berkaitan apabila diperlukan.","K2E6":"Sokongan selepas sesi membantu saya meneruskan perubahan positif."}},
        "K2F": {"construct":"K2F Empowerment and Engagement","set":"F","theory":"Recovery-Oriented Practice; WHO Empowerment; Realist Mechanism","framework":{"CMO":"Mechanism","RE-AIM":"Adoption + Maintenance","Donabedian":"Outcome support"},"items":{
            "K2F1":"Saya lebih memahami masalah yang saya hadapi.","K2F2":"Saya lebih yakin menguruskan cabaran hidup.","K2F3":"Saya lebih yakin membuat keputusan.","K2F4":"Saya berasa lebih bermotivasi selepas menerima perkhidmatan.","K2F5":"Saya terlibat secara aktif sepanjang sesi.","K2F6":"Saya bersedia mendapatkan bantuan lagi jika diperlukan.","K2F7":"Saya akan mengesyorkan perkhidmatan ini kepada orang lain yang memerlukan."}},
        "K1O": {"construct":"K1 Client Outcome","set":"O","theory":"Realist Evaluation Outcome; Donabedian Outcome; Outcome Monitoring","framework":{"CMO":"Outcome","RE-AIM":"Effectiveness","Donabedian":"Outcome"},"items":{
            "K1O1":"Tahap tekanan emosi saya berkurangan.","K1O2":"Saya lebih mampu menguruskan masalah harian.","K1O3":"Hubungan saya dengan orang sekeliling bertambah baik.","K1O4":"Saya lebih yakin terhadap masa depan.","K1O5":"Kesejahteraan hidup saya bertambah baik.","K1O6":"Perkhidmatan ini membantu saya mencapai perubahan yang positif.","K1O7":"Secara keseluruhannya saya berpuas hati dengan perkhidmatan yang diterima."}}
    },
    "S2": {
        "K3A": {"construct":"K3A Intervention Success Factors","set":"A","theory":"Realist Evaluation Mechanism; Working Alliance; Ecological Support","framework":{"CMO":"Mechanism","RE-AIM":"Effectiveness","Donabedian":"Process"},"items":{"K3A1":"Kesediaan klien untuk hadir dan berbincang membantu keberkesanan intervensi.","K3A2":"Hubungan terapeutik yang baik meningkatkan peluang perubahan positif.","K3A3":"Pendekatan intervensi yang sesuai membantu keberkesanan perkhidmatan.","K3A4":"Sokongan keluarga atau penjaga membantu klien mengekalkan perubahan positif.","K3A5":"Sokongan agensi lain membantu memperkukuh outcome klien.","K3A6":"Bilangan sesi yang mencukupi penting untuk perubahan bermakna."}},
        "K3B": {"construct":"K3B Barriers to Effectiveness","set":"B","theory":"Realist Evaluation Context/Barrier; Ecological Systems","framework":{"CMO":"Context + Mechanism barrier","RE-AIM":"Effectiveness","Donabedian":"Process risk"},"items":{"K3B1":"Motivasi klien yang rendah menjadi cabaran utama.","K3B2":"Stigma terhadap kaunseling menghalang penglibatan aktif.","K3B3":"Masalah keluarga atau komuniti menyukarkan perubahan positif.","K3B4":"Masalah akses menjejaskan kehadiran klien.","K3B5":"Kekangan masa pegawai menjejaskan kualiti susulan kes.","K3B6":"Kekurangan koordinasi antara agensi menyukarkan kes kompleks."}},
        "K3C": {"construct":"K3C Dropout and Non-Attendance","set":"C","theory":"RE-AIM Maintenance; Disengagement/Retention Logic","framework":{"CMO":"Outcome risk","RE-AIM":"Maintenance","Donabedian":"Outcome risk"},"items":{"K3C1":"Ketidakhadiran berkait dengan kekangan praktikal.","K3C2":"Klien berhenti awal kerana belum bersedia secara emosi.","K3C3":"Klien tercicir apabila tidak memahami proses intervensi.","K3C4":"Sistem peringatan temu janji lemah menyumbang ketidakhadiran.","K3C5":"Ketiadaan pelan susulan meningkatkan risiko keciciran.","K3C6":"Klien yang tidak merasai manfaat awal lebih cenderung tidak meneruskan sesi."}},
        "K4A": {"construct":"K4A Staffing, Caseload and Workload","set":"D","theory":"Donabedian Structure; Workload-Capacity Logic","framework":{"CMO":"Context","RE-AIM":"Implementation","Donabedian":"Structure"},"items":{"K4A1":"Bilangan pegawai mencukupi berbanding permintaan.","K4A2":"Beban kes terkawal untuk mengekalkan kualiti.","K4A3":"Masa persediaan sebelum sesi mencukupi.","K4A4":"Masa dokumentasi selepas sesi mencukupi.","K4A5":"Kerja pentadbiran tidak mengganggu masa intervensi secara berlebihan.","K4A6":"Peranan saya dalam perkhidmatan adalah jelas."}},
        "K4B": {"construct":"K4B Access and Equity","set":"E","theory":"RE-AIM Reach; Equity Access","framework":{"CMO":"Context","RE-AIM":"Reach","Donabedian":"Structure"},"items":{"K4B1":"Perkhidmatan dicapai bandar dan luar bandar secara adil.","K4B2":"Perkhidmatan sesuai untuk pelbagai kumpulan sasar JKM.","K4B3":"Keperluan bahasa dan budaya ditangani dengan baik.","K4B4":"Perkhidmatan jarak jauh membantu meningkatkan capaian.","K4B5":"Perkhidmatan responsif kepada OKU, warga emas dan kumpulan rentan.","K4B6":"Mekanisme rujukan membantu klien menerima bantuan sesuai."}},
        "K4C": {"construct":"K4C Institutional Capacity and Service System","set":"F","theory":"Donabedian Structure/Process; Systems Theory","framework":{"CMO":"Context + Mechanism","RE-AIM":"Implementation","Donabedian":"Structure + Process"},"items":{"K4C1":"Ruang sesi sesuai dari aspek privasi dan keselamatan.","K4C2":"SOP pelaksanaan jelas dan praktikal.","K4C3":"Sistem dokumentasi membantu pemantauan perkhidmatan.","K4C4":"Data perkhidmatan mencukupi untuk pemantauan dan penambahbaikan.","K4C5":"Koordinasi pejabat, institusi dan agensi rujukan berjalan baik.","K4C6":"Latihan sedia ada mencukupi untuk intervensi berkualiti."}},
        "K5A": {"construct":"K5 Improvement and Innovation","set":"G","theory":"RE-AIM Maintenance; Continuous Quality Improvement","framework":{"CMO":"Outcome improvement","RE-AIM":"Adoption + Maintenance","Donabedian":"Outcome improvement"},"items":{"K5A1":"Latihan berkala diperlukan.","K5A2":"SOP perlu diperkukuh.","K5A3":"Sistem digital atau dashboard diperlukan.","K5A4":"Mekanisme susulan perlu diperkukuh.","K5A5":"Perkhidmatan memerlukan lebih sumber untuk kes kompleks.","K5A6":"Amalan terbaik antara negeri/zon perlu dikongsi."}}
    },
    "S3": {
        "K4D": {"construct":"K4D Service Awareness and Role Clarity","set":"A","theory":"Role Theory; RE-AIM Adoption; Systems Theory","framework":{"CMO":"Mechanism","RE-AIM":"Adoption","Donabedian":"Process"},"items":{"K4D1":"Saya memahami fungsi utama perkhidmatan.","K4D2":"Saya mengetahui jenis kes yang sesuai dirujuk.","K4D3":"Saya memahami peranan saya menyokong perkhidmatan.","K4D4":"Saya memahami perbezaan sokongan kebajikan, pengurusan kes dan intervensi psikologi.","K4D5":"Maklumat perkhidmatan mudah diperoleh.","K4D6":"Peranan pegawai psikologi jelas kepada warga jabatan."}},
        "K4E": {"construct":"K4E Referral Readiness and Pathway Clarity","set":"B","theory":"RE-AIM Reach; Donabedian Process","framework":{"CMO":"Mechanism","RE-AIM":"Reach + Implementation","Donabedian":"Process"},"items":{"K4E1":"Saya tahu langkah merujuk klien.","K4E2":"Laluan rujukan jelas.","K4E3":"Saya yakin mengenal pasti klien yang memerlukan sokongan.","K4E4":"Prosedur rujukan mudah dilaksanakan.","K4E5":"Maklumat yang diperlukan untuk rujukan jelas.","K4E6":"Rujukan dapat dibuat dalam tempoh sesuai."}},
        "K4F": {"construct":"K4F Inter-Unit Coordination","set":"C","theory":"Systems Theory; Donabedian Process","framework":{"CMO":"Mechanism","RE-AIM":"Implementation","Donabedian":"Process"},"items":{"K4F1":"Komunikasi antara unit dan pegawai psikologi berjalan baik.","K4F2":"Perkongsian maklumat kes dibuat sesuai dan beretika.","K4F3":"Koordinasi membantu kelancaran pengurusan klien.","K4F4":"Tindakan susulan selepas rujukan dapat dipantau.","K4F5":"Perbincangan kes membantu kes kompleks.","K4F6":"Koordinasi dengan agensi luar memenuhi keperluan klien."}},
        "K4G": {"construct":"K4G Organisational Support and Resources","set":"D","theory":"Organisational Support Theory; Donabedian Structure","framework":{"CMO":"Context","RE-AIM":"Maintenance","Donabedian":"Structure"},"items":{"K4G1":"Pengurusan memberi sokongan mencukupi.","K4G2":"Kemudahan fizikal sesuai.","K4G3":"Warga JKM diberi pendedahan mencukupi.","K4G4":"Latihan pengesanan awal isu psikososial perlu diperkukuh.","K4G5":"Sistem rekod/data perlu membantu koordinasi.","K4G6":"Perkhidmatan wajar diberi keutamaan dalam pengurusan kes JKM."}},
        "K4H": {"construct":"K4H Ethics, Stigma and Confidentiality","set":"E","theory":"WHO Rights-Based Care; Labelling/Stigma Lens","framework":{"CMO":"Context + Mechanism","RE-AIM":"Implementation","Donabedian":"Process"},"items":{"K4H1":"Saya memahami kepentingan kerahsiaan maklumat klien.","K4H2":"Stigma menghalang klien mendapatkan bantuan.","K4H3":"Warga JKM perlu mengelakkan label negatif.","K4H4":"Klien perlu dilayan dengan maruah dan hormat.","K4H5":"Perkongsian maklumat klien perlu beretika.","K4H6":"Keselamatan emosi klien perlu diambil kira."}},
        "K5B": {"construct":"K5B System Improvement and Innovation","set":"F","theory":"Continuous Quality Improvement; RE-AIM Maintenance; Systems Theory","framework":{"CMO":"Outcome improvement","RE-AIM":"Maintenance","Donabedian":"Outcome improvement"},"items":{"K5B1":"SOP rujukan perlu diperkukuh.","K5B2":"Latihan pengesanan awal perlu berkala.","K5B3":"Sistem digital/dashboard membantu pemantauan.","K5B4":"Perbincangan kes perlu lebih tersusun.","K5B5":"Maklumat perkhidmatan perlu disebarkan lebih jelas.","K5B6":"Mekanisme maklum balas perlu ditambah baik."}}
    }
}

T123_META = {
    "core": {"construct":"Core Outcome Items", "set":"T", "theory":"Outcome Monitoring; RE-AIM Effectiveness; Donabedian Outcome", "items":{
        "B1":"Saya dapat mengurus tekanan emosi dengan baik.","B2":"Saya berasa lebih tenang dalam kehidupan harian.","B3":"Saya memahami masalah yang saya hadapi.","B4":"Saya memahami pilihan yang ada untuk membantu diri saya.","B5":"Saya yakin membuat keputusan berkaitan masalah saya.","B6":"Saya yakin menghadapi cabaran semasa.","B7":"Saya dapat menjalankan aktiviti harian dengan baik.","B8":"Saya dapat berfungsi dengan baik dalam keluarga, pekerjaan atau pembelajaran.","B9":"Saya mempunyai harapan terhadap masa depan.","B10":"Secara keseluruhan, saya berasa lebih baik."}},
    "process": {"construct":"T2 Process Items", "set":"P", "theory":"Realist Mechanism; RE-AIM Adoption/Implementation", "items":{"T2_11":"Sesi membantu memahami masalah.","T2_12":"Hubungan dengan pegawai membantu perubahan.","T2_13":"Saya ingin meneruskan sesi/bantuan."}},
    "sustainability": {"construct":"T3 Sustainability Items", "set":"S", "theory":"RE-AIM Maintenance; Outcome Sustainability", "items":{"T3_11":"Perubahan positif masih dapat dikekalkan.","T3_12":"Masih menggunakan kemahiran/strategi dipelajari.","T3_13":"Mampu mengurus cabaran masa depan."}}
}

QUAL_META = {
    "Q1": {"source":"Client interview", "theory":"Realist Evaluation + RE-AIM + WHO rights-based + Bronfenbrenner", "sections":{"B_Access":"Access / Reach / Context", "C_Communication":"Communication / Mechanism", "D_Therapeutic_Relationship":"Therapeutic relationship / Mechanism", "E_Cultural_Context":"Ecological context", "F_Rights_Based":"Rights and safety", "G_Outcome_Change":"Outcome", "J_Dropout_If_Relevant":"Dropout / Maintenance risk"}},
    "Q2": {"source":"Officer interview", "theory":"Realist Evaluation + Donabedian + RE-AIM", "sections":{"B_Success_Factors":"Success mechanism", "C_Barriers":"Barrier", "D_Limited_Impact":"Limited outcome", "E_Dropout":"Dropout", "F_Staffing_Workload":"Structure", "I_SOP_Referral_Coordination":"Process coordination", "K_Improvement":"Improvement outcome"}},
    "Q3": {"source":"System / Warga JKM / stakeholder FGD-KII", "theory":"Donabedian + Systems Theory + RE-AIM + Realist Evaluation", "sections":{"A_Role_Awareness":"Role clarity / Adoption", "B_Referral_Pathway":"Referral / Reach", "C_InterUnit_Coordination":"Coordination / Implementation", "D_Organisational_Support":"Structure", "E_Ethics_Confidentiality_Stigma":"Rights and stigma", "F_Data_Dashboard":"Data system", "G_Training_Competency":"Capacity building", "H_System_Improvement":"System improvement"}}
}

def set_formula_text(prefix, n_items):
    return f"{prefix} = (" + " + ".join([f"{prefix}{i}" for i in range(1, n_items+1)]) + f") / {n_items}"

def render_construct_explainer(dataset_key, prefix, df=None, title_suffix=""):
    meta = QUESTION_TEXT.get(dataset_key, {}).get(prefix)
    if not meta:
        return
    items = list(meta["items"].keys())
    n = len(items)
    with st.expander(f"How this result is calculated • {meta['construct']} {title_suffix}"):
        st.markdown(f"""
        **1. Result source:** Dataset **{dataset_key}** → Construct **{meta['construct']}** → Set **{meta['set']}**.  
        **2. Theory source:** {meta['theory']}.  
        **3. Framework mapping:** CMO = **{meta['framework'].get('CMO','-')}**, RE-AIM = **{meta['framework'].get('RE-AIM','-')}**, Donabedian/System = **{meta['framework'].get('Donabedian','-')}**.  
        **4. Formula:** `{set_formula_text(prefix, n)}`.  
        **5. Conversion to 0–100:** `(Mean - 1) / 4 × 100`.  
        **6. Interpretation:** higher score means stronger performance for this construct; low item means targeted intervention is required.
        """)
        qdf = pd.DataFrame([{"Item": k, "Question / Indicator": v} for k, v in meta["items"].items()])
        if df is not None and not df.empty:
            qdf["Mean_1_5"] = [mean_col(df, k) if k in df.columns else np.nan for k in qdf["Item"]]
            qdf["Score_100"] = qdf["Mean_1_5"].apply(scale100)
        st.dataframe(qdf, use_container_width=True)

def render_overall_explainer(name, components, values):
    with st.expander(f"How overall {name} is calculated"):
        rows=[]
        for c, v in zip(components, values):
            rows.append({"Component": c, "Mean_1_5": v, "Score_100": scale100(v), "Interpretation": interpret_score(scale100(v))})
        df=pd.DataFrame(rows)
        st.markdown(f"**Formula:** {name} = average of all available component means. Each component is first based on Likert mean 1–5, then displayed as 0–100 using `(Mean - 1) / 4 × 100`.")
        st.dataframe(df, use_container_width=True)

def render_set_theory_overview(dataset_key):
    rows=[]
    for prefix, meta in QUESTION_TEXT.get(dataset_key, {}).items():
        rows.append({
            "Set": meta["set"], "Prefix": prefix, "Construct": meta["construct"],
            "Items": ", ".join(meta["items"].keys()), "Theory": meta["theory"],
            "CMO": meta["framework"].get("CMO","-"), "RE-AIM": meta["framework"].get("RE-AIM","-"), "Donabedian/System": meta["framework"].get("Donabedian","-")
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

def render_graph_explainer(graph_name, data_source, x_axis, y_axis, meaning):
    with st.expander(f"Explain graph • {graph_name}"):
        st.markdown(f"""
        **Data source:** {data_source}  
        **X-axis:** {x_axis}  
        **Y-axis / value:** {y_axis}  
        **How it is obtained:** the system groups the uploaded Excel data according to the x-axis, calculates the mean or count required by the y-axis, then displays it as a bar, line, radar or heatmap.  
        **How to read:** {meaning}
        """)

# KPIs
s1_overall = mean_col(fs1, "Score_Overall")
s2_overall = mean_col(fs2, "Score_Overall")
s3_overall = mean_col(fs3, "Score_Overall")
t123_core = mean_col(ft123, "Score_Core_Outcome")
integrated = np.nanmean([s1_overall, s2_overall, s3_overall, t123_core])

# Framework scores
CMO_context = np.nanmean([mean_col(fs1,"Score_K2A_Access"), mean_col(fs2,"Score_K4B_Access_Equity"), mean_col(fs3,"Score_K4G_OrgSupport")])
CMO_mechanism = np.nanmean([mean_col(fs1,"Score_K2B_Communication"), mean_col(fs1,"Score_K2C_Relationship"), mean_col(fs1,"Score_K2F_Empowerment"), mean_col(fs2,"Score_K3A_Success"), mean_col(fs3,"Score_K4F_Coordination")])
CMO_outcome = np.nanmean([mean_col(fs1,"Score_K1_Outcome"), t123_core, mean_col(fs2,"Score_K5_Improvement"), mean_col(fs3,"Score_K5B_Improvement")])
CMO_overall = np.nanmean([CMO_context, CMO_mechanism, CMO_outcome])

RE_reach = np.nanmean([mean_col(fs1,"Score_K2A_Access"), mean_col(fs2,"Score_K4B_Access_Equity"), mean_col(fs3,"Score_K4E_Referral")])
RE_effectiveness = np.nanmean([mean_col(fs1,"Score_K1_Outcome"), mean_col(fs2,"Score_K3A_Success"), t123_core])
RE_adoption = np.nanmean([mean_col(fs2,"Score_K5_Improvement"), mean_col(fs3,"Score_K4D_Awareness")])
RE_implementation = np.nanmean([mean_col(fs1,"Score_K2E_Continuity"), mean_col(fs2,"Score_K4C_Capacity"), mean_col(fs3,"Score_K4F_Coordination")])
RE_maintenance = np.nanmean([mean_col(fs1,"Score_K2E_Continuity"), mean_col(ft123,"Score_T3_Sustainability"), mean_col(fs3,"Score_K5B_Improvement")])
RE_overall = np.nanmean([RE_reach, RE_effectiveness, RE_adoption, RE_implementation, RE_maintenance])

D_structure = np.nanmean([mean_col(fs1,"Score_K2A_Access"), mean_col(fs2,"Score_K4A_Workload"), mean_col(fs2,"Score_K4C_Capacity"), mean_col(fs3,"Score_K4G_OrgSupport")])
D_process = np.nanmean([mean_col(fs1,"Score_K2B_Communication"), mean_col(fs1,"Score_K2C_Relationship"), mean_col(fs2,"Score_K4C_Capacity"), mean_col(fs3,"Score_K4F_Coordination")])
D_outcome = np.nanmean([mean_col(fs1,"Score_K1_Outcome"), t123_core, mean_col(fs2,"Score_K5_Improvement"), mean_col(fs3,"Score_K5B_Improvement")])
D_overall = np.nanmean([D_structure, D_process, D_outcome])

# Tabs
tabs = st.tabs([
    "Admin & Overall", "Reliability", "S1 Quant", "S2 Quant", "S3 Quant",
    "Q1 Client", "Q2 Officer", "Q3 System", "T1-T2-T3",
    "CMO", "RE-AIM", "Donabedian/System", "Intervention Engine", "Audit Trail & Formula", "Raw Data"
])

with tabs[0]:
    st.subheader("Ringkasan Eksekutif dan Overall Framework")
    a,b,c,d,e = st.columns(5)
    with a: kpi("S1 Klien", f"{scale100(s1_overall):.1f}%" if not pd.isna(s1_overall) else "-", f"N={len(fs1):,} | Mean {pct(s1_overall)}/5")
    with b: kpi("S2 Pegawai", f"{scale100(s2_overall):.1f}%" if not pd.isna(s2_overall) else "-", f"N={len(fs2):,} | Mean {pct(s2_overall)}/5")
    with c: kpi("S3 Warga", f"{scale100(s3_overall):.1f}%" if not pd.isna(s3_overall) else "-", f"N={len(fs3):,} | Mean {pct(s3_overall)}/5")
    with d: kpi("T123 Outcome", f"{scale100(t123_core):.1f}%" if not pd.isna(t123_core) else "-", f"Rows={len(ft123):,} | Mean {pct(t123_core)}/5")
    with e: kpi("Integrated", f"{scale100(integrated):.1f}%" if not pd.isna(integrated) else "-", interpret_score(scale100(integrated)))

    f1,f2,f3 = st.columns(3)
    with f1: kpi("CMO Overall", f"{scale100(CMO_overall):.1f}%" if not pd.isna(CMO_overall) else "-", "Context + Mechanism + Outcome")
    with f2: kpi("RE-AIM Overall", f"{scale100(RE_overall):.1f}%" if not pd.isna(RE_overall) else "-", "Reach + Effectiveness + Adoption + Implementation + Maintenance")
    with f3: kpi("Donabedian Overall", f"{scale100(D_overall):.1f}%" if not pd.isna(D_overall) else "-", "Structure + Process + Outcome")

    render_overall_explainer("Integrated Index", ["S1", "S2", "S3", "T123"], [s1_overall, s2_overall, s3_overall, t123_core])
    render_overall_explainer("CMO Index", ["Context", "Mechanism", "Outcome"], [CMO_context, CMO_mechanism, CMO_outcome])
    render_overall_explainer("RE-AIM Index", ["Reach", "Effectiveness", "Adoption", "Implementation", "Maintenance"], [RE_reach, RE_effectiveness, RE_adoption, RE_implementation, RE_maintenance])
    render_overall_explainer("Donabedian/System Index", ["Structure", "Process", "Outcome"], [D_structure, D_process, D_outcome])

    comp = pd.DataFrame({
        "Component": ["S1 Quant", "S2 Quant", "S3 Quant", "T123 Core", "CMO", "RE-AIM", "Donabedian"],
        "Mean_1_5": [s1_overall, s2_overall, s3_overall, t123_core, CMO_overall, RE_overall, D_overall],
    })
    comp["Score_100"] = comp["Mean_1_5"].apply(scale100)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.bar(comp, x="Component", y="Score_100", text_auto='.1f', title="Overall Score 0-100"), use_container_width=True)
        render_graph_explainer("Overall Score 0-100", "All quantitative sheets and T123", "Framework / dataset component", "Score converted to 0–100", "Higher bars indicate stronger overall performance after filtering by negeri/zon.")
    with col2:
        fig = go.Figure(go.Scatterpolar(r=comp["Score_100"], theta=comp["Component"], fill="toself"))
        fig.update_layout(title="Radar Overall Framework", polar=dict(radialaxis=dict(visible=True, range=[0,100])), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#F8FAFC"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"""
    **Naratif automatik:** Untuk filter **{zone_pick} / {state_pick}**, sistem membaca **{len(fs1)} klien S1**, **{len(fs2)} pegawai S2**, **{len(fs3)} warga JKM S3**, **{len(fq1)+len(fq2)+len(fq3)} rekod kualitatif**, dan **{len(ft123)} rekod T1--T2--T3**.  
    Skor keseluruhan bersepadu ialah **{scale100(integrated):.1f}%**, CMO **{scale100(CMO_overall):.1f}%**, RE-AIM **{scale100(RE_overall):.1f}%**, dan Donabedian/System **{scale100(D_overall):.1f}%**. Bacaan ini boleh digunakan sebagai ringkasan awal untuk laporan pengurusan, tetapi perlu disokong dengan analisis item dan kualitatif.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Sheet Status")
    status = pd.DataFrame([{"Sheet": s, "Rows": len(sheets[s]), "Columns": len(sheets[s].columns)} for s in REQUIRED_SHEETS])
    st.dataframe(status, use_container_width=True)

with tabs[1]:
    st.subheader("Reliability Analysis: Cronbach Alpha")
    r1 = reliability_table(fs1, S1_MAP); r1["Source"] = "S1"
    r2 = reliability_table(fs2, S2_MAP); r2["Source"] = "S2"
    r3 = reliability_table(fs3, S3_MAP); r3["Source"] = "S3"
    rel = pd.concat([r1,r2,r3], ignore_index=True)
    st.dataframe(rel[["Source","Construct","Items","Mean_1_5","Score_100","Cronbach_Alpha","Status"]], use_container_width=True)
    st.plotly_chart(px.bar(rel, x="Construct", y="Cronbach_Alpha", color="Source", text_auto='.2f', title="Cronbach Alpha by Construct"), use_container_width=True)

with tabs[2]:
    st.subheader("S1 Quantitative - Klien")
    summ = score_summary(fs1)
    st.dataframe(summ, use_container_width=True)
    if not summ.empty:
        st.plotly_chart(px.bar(summ, x="Construct", y="Score_100", text_auto='.1f', title="S1 Construct Scores 0-100"), use_container_width=True)
        render_graph_explainer("S1 Construct Scores", "S1_Quant_Raw", "S1 constructs", "Mean construct score converted to 0–100", "This graph shows which client-experience construct is strongest or weakest.")
        for _p in ["K2A","K2B","K2C","K2D","K2E","K2F","K1O"]:
            render_construct_explainer("S1", _p, fs1)
    item_s = item_summary(fs1, ["K2A", "K2B", "K2C", "K2D", "K2E", "K2F", "K1O"])
    if not item_s.empty:
        st.subheader("Item Terendah / Perlu Intervensi")
        st.dataframe(item_s.head(20), use_container_width=True)
        st.plotly_chart(px.bar(item_s.head(20), x="Score_100", y="Item", orientation="h", title="20 Item S1 Terendah"), use_container_width=True)
        render_graph_explainer("20 Item S1 Terendah", "S1_Quant_Raw item columns", "Question item", "Item mean converted to 0–100", "Lowest items are priority gaps; these explain which exact questionnaire statements need intervention.")
    corr_cols = [c for c in score_cols(fs1) if c != "Score_Overall"]
    if len(corr_cols) > 1:
        corr = fs1[corr_cols].corr(numeric_only=True)
        st.plotly_chart(px.imshow(corr, text_auto='.2f', title="S1 Correlation Matrix"), use_container_width=True)

with tabs[3]:
    st.subheader("S2 Quantitative - PPsi / PPPsi")
    summ = score_summary(fs2); st.dataframe(summ, use_container_width=True)
    if not summ.empty:
        st.plotly_chart(px.bar(summ, x="Construct", y="Score_100", text_auto='.1f', title="S2 Construct Scores 0-100"), use_container_width=True)
        render_graph_explainer("S2 Construct Scores", "S2_Quant_Raw", "S2 constructs", "Mean construct score converted to 0–100", "This graph shows officer implementation strengths and gaps.")
        for _p in ["K3A","K3B","K3C","K4A","K4B","K4C","K5A"]:
            render_construct_explainer("S2", _p, fs2)
    item_s = item_summary(fs2, ["K3A", "K3B", "K3C", "K4A", "K4B", "K4C", "K5A"])
    if not item_s.empty:
        st.subheader("Item Terendah / Jurang Pelaksanaan")
        st.dataframe(item_s.head(20), use_container_width=True)
        st.plotly_chart(px.bar(item_s.head(20), x="Score_100", y="Item", orientation="h", title="20 Item S2 Terendah"), use_container_width=True)
        render_graph_explainer("20 Item S2 Terendah", "S2_Quant_Raw item columns", "Question item", "Item mean converted to 0–100", "Lowest items identify officer-side operational gaps such as workload, referral or capacity.")
    if "Monthly_Active_Cases" in fs2.columns and "Score_Overall" in fs2.columns:
        case = fs2.groupby("Monthly_Active_Cases", as_index=False)["Score_Overall"].mean()
        case["Score_100"] = case["Score_Overall"].apply(scale100)
        st.plotly_chart(px.bar(case, x="Monthly_Active_Cases", y="Score_100", text_auto='.1f', title="Workload Analysis by Active Cases"), use_container_width=True)

with tabs[4]:
    st.subheader("S3 Quantitative - Warga JKM")
    summ = score_summary(fs3); st.dataframe(summ, use_container_width=True)
    if not summ.empty:
        st.plotly_chart(px.bar(summ, x="Construct", y="Score_100", text_auto='.1f', title="S3 Construct Scores 0-100"), use_container_width=True)
        render_graph_explainer("S3 Construct Scores", "S3_Quant_Raw", "S3 constructs", "Mean construct score converted to 0–100", "This graph shows system support, role clarity, referral and coordination readiness.")
        for _p in ["K4D","K4E","K4F","K4G","K4H","K5B"]:
            render_construct_explainer("S3", _p, fs3)
    item_s = item_summary(fs3, ["K4D", "K4E", "K4F", "K4G", "K4H", "K5B"])
    if not item_s.empty:
        st.subheader("Item Terendah / Sistem Support Gap")
        st.dataframe(item_s.head(20), use_container_width=True)
        st.plotly_chart(px.bar(item_s.head(20), x="Score_100", y="Item", orientation="h", title="20 Item S3 Terendah"), use_container_width=True)
        render_graph_explainer("20 Item S3 Terendah", "S3_Quant_Raw item columns", "Question item", "Item mean converted to 0–100", "Lowest items indicate system-support gaps such as role clarity, coordination, stigma or data needs.")
    if "Contact_Frequency" in fs3.columns:
        cf = fs3.groupby("Contact_Frequency", as_index=False)["Score_Overall"].mean()
        cf["Score_100"] = cf["Score_Overall"].apply(scale100)
        st.plotly_chart(px.bar(cf, x="Contact_Frequency", y="Score_100", text_auto='.1f', title="System Readiness by Contact Frequency"), use_container_width=True)

def qual_tab(df, title, source):
    st.subheader(title)
    meta = QUAL_META.get(source, {})
    with st.expander(f"How qualitative result is derived • {source}"):
        st.markdown(f"**Source:** {meta.get('source','-')}  \n**Theory source:** {meta.get('theory','-')}  \n**How results are calculated:** text responses are grouped by section, counted for completeness/mentions, tagged to CMO and RE-AIM columns, then keyword frequency is extracted after basic stop-word removal.  \n**How to read:** high mention count means the theme is repeatedly discussed; it does not automatically mean positive or negative without reading the narrative.")
        if meta.get('sections'):
            st.dataframe(pd.DataFrame([{"Section": k, "Meaning / Mapping": v} for k,v in meta['sections'].items()]), use_container_width=True)
    if "RE_AIM_Tag" in df.columns:
        st.plotly_chart(px.pie(df, names="RE_AIM_Tag", title=f"{source} RE-AIM Tag"), use_container_width=True)
    if all(c in df.columns for c in ["CMO_Context", "CMO_Mechanism", "CMO_Outcome"]):
        cmo = df.groupby(["CMO_Context", "CMO_Mechanism", "CMO_Outcome"], as_index=False).size().sort_values("size", ascending=False)
        st.dataframe(cmo, use_container_width=True)
    th = qualitative_theme_counts(df, source)
    if not th.empty:
        st.plotly_chart(px.bar(th.head(15), x="Mentions", y="Section", orientation="h", title=f"{source} Section Mention Completeness"), use_container_width=True)
    kw = keyword_frequency(df)
    if not kw.empty:
        st.plotly_chart(px.bar(kw, x="Frequency", y="Keyword", orientation="h", title=f"{source} Keyword Frequency"), use_container_width=True)
    st.dataframe(df, use_container_width=True)

with tabs[5]: qual_tab(fq1, "Q1 Qualitative - Client Interview", "Q1")
with tabs[6]: qual_tab(fq2, "Q2 Qualitative - Officer Interview", "Q2")
with tabs[7]: qual_tab(fq3, "Q3 Qualitative - System / Warga JKM / Stakeholder", "Q3")

with tabs[8]:
    st.subheader("T1--T2--T3 Pilot Outcome Monitoring")
    if not ft123.empty:
        t_mean = ft123.groupby("Timepoint", as_index=False).agg(
            Core_Outcome=("Score_Core_Outcome", "mean"),
            N=("Respondent_ID", "nunique"),
            Rows=("Respondent_ID", "count"),
            T2_Process=("Score_T2_Process", "mean"),
            T3_Sustainability=("Score_T3_Sustainability", "mean"),
        )
        order = {"T1": 1, "T2": 2, "T3": 3}
        t_mean["Order"] = t_mean["Timepoint"].map(order)
        t_mean = t_mean.sort_values("Order")
        t_mean["Score_100"] = t_mean["Core_Outcome"].apply(scale100)
        st.plotly_chart(px.line(t_mean, x="Timepoint", y="Score_100", markers=True, text="Score_100", title="Mean Core Outcome T1 → T2 → T3"), use_container_width=True)
        render_graph_explainer("Mean Core Outcome T1 → T2 → T3", "T123_Pilot_Raw B1–B10", "Timepoint", "Average core outcome score converted to 0–100", "Rising line indicates improvement; falling line indicates deterioration or need for follow-up.")
        with st.expander("How T1–T2–T3 scores are calculated"):
            st.markdown("**Core outcome:** `(B1+B2+...+B10)/10`. The same B1–B10 items are used at T1, T2 and T3. **Delta T2-T1 = Outcome_T2 - Outcome_T1**; **Delta T3-T2 = Outcome_T3 - Outcome_T2**. T2_11–T2_13 are process items. T3_11–T3_13 are sustainability items and are not included in the core outcome score.")
            st.dataframe(pd.DataFrame([{"Set": v["set"], "Construct": v["construct"], "Theory": v["theory"], "Items": ", ".join(v["items"].keys())} for v in T123_META.values()]), use_container_width=True)
        st.dataframe(t_mean.drop(columns=["Order"]), use_container_width=True)
        pivot = ft123.pivot_table(index="Respondent_ID", columns="Timepoint", values="Score_Core_Outcome", aggfunc="mean").reset_index()
        for col in ["T1", "T2", "T3"]:
            if col not in pivot.columns: pivot[col] = np.nan
        pivot["Delta_T2_T1"] = pivot["T2"] - pivot["T1"]
        pivot["Delta_T3_T2"] = pivot["T3"] - pivot["T2"]
        pivot["Delta_T3_T1"] = pivot["T3"] - pivot["T1"]
        st.subheader("Individual Change Table")
        st.dataframe(pivot, use_container_width=True)
        ids_t1, ids_t2, ids_t3 = [set(ft123[ft123["Timepoint"].eq(t)]["Respondent_ID"].astype(str)) for t in ["T1","T2","T3"]]
        dropout_t2 = (len(ids_t1 - ids_t2) / len(ids_t1) * 100) if ids_t1 else np.nan
        dropout_t3 = (len(ids_t2 - ids_t3) / len(ids_t2) * 100) if ids_t2 else np.nan
        a,b,c = st.columns(3)
        with a: kpi("Dropout T1→T2", f"{dropout_t2:.1f}%" if not pd.isna(dropout_t2) else "-", "Pilot feasibility")
        with b: kpi("Dropout T2→T3", f"{dropout_t3:.1f}%" if not pd.isna(dropout_t3) else "-", "Maintenance feasibility")
        with c: kpi("T3 Sustainability", f"{scale100(mean_col(ft123,'Score_T3_Sustainability')):.1f}%" if not pd.isna(mean_col(ft123,'Score_T3_Sustainability')) else "-", "Additional T3 items")
    else:
        st.warning("Tiada data T1-T2-T3 untuk filter ini.")

with tabs[9]:
    st.subheader("CMO Framework Score")
    cmo_df = pd.DataFrame({"CMO": ["Context", "Mechanism", "Outcome", "Overall"], "Mean_1_5": [CMO_context, CMO_mechanism, CMO_outcome, CMO_overall]})
    cmo_df["Score_100"] = cmo_df["Mean_1_5"].apply(scale100)
    st.dataframe(cmo_df, use_container_width=True)
    st.plotly_chart(px.bar(cmo_df, x="CMO", y="Score_100", text_auto='.1f', title="CMO Score 0-100"), use_container_width=True)
    render_overall_explainer("CMO", ["Context", "Mechanism", "Outcome"], [CMO_context, CMO_mechanism, CMO_outcome])
    st.markdown("**CMO source:** Context is mainly from access, equity, setting and organisation. Mechanism is from communication, relationship, success factors, empowerment and coordination. Outcome is from client outcome, T123, improvement and sustainability.")

with tabs[10]:
    st.subheader("RE-AIM Framework Score")
    re_df = pd.DataFrame({"RE-AIM": ["Reach", "Effectiveness", "Adoption", "Implementation", "Maintenance", "Overall"], "Mean_1_5": [RE_reach, RE_effectiveness, RE_adoption, RE_implementation, RE_maintenance, RE_overall]})
    re_df["Score_100"] = re_df["Mean_1_5"].apply(scale100)
    st.dataframe(re_df, use_container_width=True)
    st.plotly_chart(px.bar(re_df, x="RE-AIM", y="Score_100", text_auto='.1f', title="RE-AIM Score 0-100"), use_container_width=True)
    render_overall_explainer("RE-AIM", ["Reach", "Effectiveness", "Adoption", "Implementation", "Maintenance"], [RE_reach, RE_effectiveness, RE_adoption, RE_implementation, RE_maintenance])
    st.markdown("**RE-AIM source:** Reach = access/referral; Effectiveness = outcome/success; Adoption = awareness/improvement acceptance; Implementation = process/capacity/coordination; Maintenance = continuity, T3 sustainability and system improvement.")

with tabs[11]:
    st.subheader("Donabedian / System Framework Score")
    d_df = pd.DataFrame({"Framework": ["Structure", "Process", "Outcome", "Overall"], "Mean_1_5": [D_structure, D_process, D_outcome, D_overall]})
    d_df["Score_100"] = d_df["Mean_1_5"].apply(scale100)
    st.dataframe(d_df, use_container_width=True)
    st.plotly_chart(px.bar(d_df, x="Framework", y="Score_100", text_auto='.1f', title="Structure → Process → Outcome Score 0-100"), use_container_width=True)
    render_overall_explainer("Donabedian/System", ["Structure", "Process", "Outcome"], [D_structure, D_process, D_outcome])
    st.markdown("**Donabedian source:** Structure = resources, access, workload and organisational support. Process = communication, relationship, SOP, coordination and ethics. Outcome = client outcome, T123 and improvement indices.")

with tabs[12]:
    st.subheader("Auto Intervention Recommendation Engine")
    recs = []
    recs += recommendations_from_scores(score_summary(fs1), "S1 Klien")
    recs += recommendations_from_scores(score_summary(fs2), "S2 Pegawai")
    recs += recommendations_from_scores(score_summary(fs3), "S3 Warga JKM")
    if scale100(RE_maintenance) < 65:
        recs.append("RE-AIM Maintenance rendah: Perkukuh sistem susulan, reminder, tracking T3 dan follow-up plan selepas sesi.")
    if scale100(CMO_context) < 65:
        recs.append("CMO Context rendah: Semak faktor zon/negeri, kategori klien, akses lokasi, kapasiti institusi dan keadaan lapangan.")
    if scale100(D_structure) < 65:
        recs.append("Donabedian Structure rendah: Semak semula perjawatan, ruang privasi, SOP, sistem data dan sumber operasi.")
    if not recs:
        recs = ["Tiada jurang kritikal dikesan berdasarkan filter semasa. Fokus kepada pengekalan amalan baik, pemantauan berkala dan dokumentasi amalan terbaik."]
    for i, r in enumerate(recs, 1):
        st.markdown(f'<div class="card2"><b>Recommendation {i}:</b> {r}</div>', unsafe_allow_html=True)

    report_df = pd.DataFrame({"Recommendation": recs})
    st.download_button("Download Recommendation CSV", report_df.to_csv(index=False).encode("utf-8-sig"), file_name="JKM_recommendations.csv", mime="text/csv", use_container_width=True)

with tabs[13]:
    st.subheader("Full audit trail: Theory → Set → Question → Formula → Framework → Result")
    st.markdown("This page explains exactly where each number in the dashboard comes from. It is designed for panel, auditor, perunding and JKM officers who need to defend every graph and result.")
    dataset_choice = st.selectbox("Choose questionnaire set", ["S1", "S2", "S3", "T123", "Q1", "Q2", "Q3"], key="audit_dataset_choice")
    if dataset_choice in ["S1", "S2", "S3"]:
        render_set_theory_overview(dataset_choice)
        current_df = {"S1": fs1, "S2": fs2, "S3": fs3}[dataset_choice]
        for prefix in QUESTION_TEXT[dataset_choice].keys():
            render_construct_explainer(dataset_choice, prefix, current_df, title_suffix="audit")
    elif dataset_choice == "T123":
        st.dataframe(pd.DataFrame([{"Set": v["set"], "Construct": v["construct"], "Theory": v["theory"], "Items": ", ".join(v["items"].keys())} for v in T123_META.values()]), use_container_width=True)
        st.markdown("**Formula:** Core Outcome at each timepoint = `(B1+B2+...+B10)/10`. Changes: `Delta_T2_T1 = T2 - T1`, `Delta_T3_T2 = T3 - T2`. T2 and T3 additional items are for process and sustainability only.")
    else:
        meta = QUAL_META.get(dataset_choice, {})
        st.markdown(f"**Qualitative source:** {meta.get('source','-')}  \n**Theory:** {meta.get('theory','-')}")
        st.dataframe(pd.DataFrame([{"Section": k, "Mapping": v} for k,v in meta.get('sections', {}).items()]), use_container_width=True)
        st.markdown("**How qualitative graphs are obtained:** section mention counts come from non-empty responses; RE-AIM and CMO charts come from tagged columns; keyword chart comes from text token frequency after stop-word removal.")

    st.subheader("Framework formula library")
    formula_library = pd.DataFrame([
        {"Result":"Construct score", "Formula":"Mean of all items in the construct", "Example":"K2A=(K2A1+...+K2A6)/6"},
        {"Result":"Score 0–100", "Formula":"(Mean_1_5 - 1) / 4 × 100", "Example":"Mean 4.25 = 81.25%"},
        {"Result":"Overall S1/S2/S3", "Formula":"Average of construct scores", "Example":"S1=(K2A+K2B+K2C+K2D+K2E+K2F+K1)/7"},
        {"Result":"CMO Overall", "Formula":"Average(Context, Mechanism, Outcome)", "Example":"CMO=(C+M+O)/3"},
        {"Result":"RE-AIM Overall", "Formula":"Average(Reach, Effectiveness, Adoption, Implementation, Maintenance)", "Example":"RE-AIM=(R+E+A+I+M)/5"},
        {"Result":"Donabedian Overall", "Formula":"Average(Structure, Process, Outcome)", "Example":"D=(S+P+O)/3"},
        {"Result":"Cronbach Alpha", "Formula":"k/(k-1) × (1 - sum item variances / total variance)", "Example":"Reliability of construct items"},
        {"Result":"T123 Delta", "Formula":"Outcome later timepoint - Outcome earlier timepoint", "Example":"Delta_T2_T1=T2-T1"}
    ])
    st.dataframe(formula_library, use_container_width=True)

with tabs[14]:
    st.subheader("Raw Data From Excel")
    choice = st.selectbox("Pilih sheet", REQUIRED_SHEETS)
    df = filter_df(sheets[choice], zone_pick, state_pick)
    st.dataframe(df, use_container_width=True)
    st.download_button("Download filtered CSV", df.to_csv(index=False).encode("utf-8-sig"), file_name=f"{choice}_filtered.csv", mime="text/csv", use_container_width=True)

st.markdown('<hr><div class="small">Nota: Sistem ini membaca data terus daripada Excel 7 sheet. Reliability, framework score, audit trail, formula explanation, set-theory mapping dan intervention engine dikira secara automatik daripada workbook aktif. Untuk production, simpan ADMIN_USERNAME dan ADMIN_PASSWORD dalam Streamlit secrets.</div>', unsafe_allow_html=True)
