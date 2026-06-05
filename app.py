from pathlib import Path

code = r'''import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="Dashboard JKM | Psikologi & Kaunseling",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# REKA BENTUK PREMIUM
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* HIDE STREAMLIT WHITE HEADER */
header {visibility: hidden;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {display: none;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.stApp {
    background:
        radial-gradient(circle at 12% 5%, rgba(253, 230, 138, 0.26), transparent 27%),
        radial-gradient(circle at 88% 7%, rgba(16, 185, 129, 0.22), transparent 28%),
        radial-gradient(circle at 50% 95%, rgba(59, 130, 246, 0.20), transparent 38%),
        linear-gradient(135deg, #020617 0%, #071526 40%, #0B2545 78%, #123C69 100%);
    color: white;
}

.block-container {
    padding-top: 0rem !important;
    padding-bottom: 3rem;
    max-width: 1500px;
}

.hero {
    margin-top: -58px;
    padding: 34px 42px 30px 42px;
    border-radius: 0px 0px 34px 34px;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.18), rgba(255,255,255,0.055)),
        linear-gradient(90deg, rgba(253,230,138,0.16), rgba(14,165,233,0.08));
    border: 1px solid rgba(255,255,255,0.22);
    box-shadow: 0 32px 90px rgba(0,0,0,0.48);
    margin-bottom: 22px;
}

.hero-title {
    color: #FDE68A;
    font-size: 39px;
    font-weight: 950;
    line-height: 1.12;
    letter-spacing: -1.1px;
    text-shadow: 0 0 28px rgba(253,230,138,0.25);
}

.hero-subtitle {
    color: #DDEBFF;
    font-size: 16px;
    font-weight: 550;
    margin-top: 14px;
    max-width: 1050px;
}

.badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.58);
    border: 1px solid rgba(253,230,138,0.42);
    color: #FDE68A;
    font-weight: 800;
    font-size: 12px;
    margin-right: 8px;
    margin-top: 16px;
}

.kpi-card {
    min-height: 142px;
    padding: 22px;
    border-radius: 28px;
    background:
        linear-gradient(145deg, rgba(255,255,255,0.20), rgba(255,255,255,0.055)),
        radial-gradient(circle at top right, rgba(253,230,138,0.25), transparent 42%);
    border: 1px solid rgba(255,255,255,0.24);
    box-shadow:
        0 24px 55px rgba(0,0,0,0.38),
        inset 0 1px 0 rgba(255,255,255,0.22);
    margin-bottom: 12px;
}

.kpi-label {
    color: #E0F2FE;
    font-size: 12px;
    font-weight: 850;
    text-transform: uppercase;
    letter-spacing: .55px;
}

.kpi-value {
    color: #FDE68A;
    font-size: 36px;
    font-weight: 950;
    margin-top: 9px;
    line-height: 1;
}

.kpi-note {
    color: #BBF7D0;
    font-size: 12.5px;
    font-weight: 700;
    margin-top: 12px;
}

.panel {
    padding: 22px 24px;
    border-radius: 26px;
    background: rgba(255,255,255,0.095);
    border: 1px solid rgba(255,255,255,0.18);
    box-shadow: 0 20px 48px rgba(0,0,0,0.30);
    margin-bottom: 18px;
}

.intervention-panel {
    padding: 24px 26px;
    border-radius: 28px;
    background:
        linear-gradient(145deg, rgba(255,255,255,0.15), rgba(255,255,255,0.055)),
        radial-gradient(circle at top right, rgba(253,230,138,0.16), transparent 45%);
    border: 1px solid rgba(255,255,255,0.20);
    box-shadow: 0 22px 56px rgba(0,0,0,0.33);
    margin-bottom: 18px;
}

.info-box {
    padding: 18px 22px;
    border-radius: 24px;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.14), rgba(255,255,255,0.055));
    border: 1px solid rgba(255,255,255,0.20);
    border-left: 6px solid #FDE68A;
    color: #EAF6FF;
    box-shadow: 0 18px 38px rgba(0,0,0,0.26);
    margin-bottom: 18px;
}

.insight-card {
    padding: 18px 20px;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(253,230,138,0.16), rgba(255,255,255,0.07));
    border: 1px solid rgba(253,230,138,0.25);
    color: #F8FAFC;
    min-height: 110px;
}

.priority-critical {
    color: #991B1B;
    background: #FEE2E2;
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 900;
}

.priority-attention {
    color: #92400E;
    background: #FEF3C7;
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 900;
}

.priority-good {
    color: #14532D;
    background: #DCFCE7;
    padding: 6px 12px;
    border-radius: 999px;
    font-weight: 900;
}

h1, h2, h3 {
    color: #FDE68A !important;
    font-weight: 950 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 9px;
    flex-wrap: wrap;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    padding: 10px 18px;
    background: rgba(255,255,255,0.08);
    color: #E0F2FE;
    border: 1px solid rgba(255,255,255,0.14);
    font-weight: 750;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #FDE68A, #F59E0B) !important;
    color: #111827 !important;
    font-weight: 950;
}

div[data-baseweb="select"] > div {
    background-color: rgba(255,255,255,0.92);
    border-radius: 16px;
    min-height: 54px;
}

.stDataFrame {
    border-radius: 20px;
    overflow: hidden;
}

hr {
    border: none;
    height: 1px;
    background: rgba(255,255,255,0.15);
    margin: 18px 0;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA SIMULASI TOR
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

    rows = []
    negeri = list(negeri_zon.keys())

    for i in range(600):
        n = np.random.choice(negeri)
        z = negeri_zon[n]

        faktor_negeri = {
            "Selangor": 4, "Kuala Lumpur": 3, "Johor": 2, "Pulau Pinang": 2,
            "Melaka": 1, "Kedah": 0, "Pahang": -1, "Kelantan": -2,
            "Sarawak": -3, "Sabah": -4
        }[n]

        s1 = np.clip(np.random.normal(82 + faktor_negeri, 6.5), 50, 99)
        s2 = np.clip(np.random.normal(78 + faktor_negeri * 0.7, 7.5), 48, 98)
        s3 = np.clip(np.random.normal(76 + faktor_negeri * 0.6, 8.0), 45, 96)
        s4 = np.clip(np.random.normal(74 + faktor_negeri * 0.8, 8.5), 42, 96)

        whodas_t1 = np.clip(np.random.normal(59 - faktor_negeri * 0.4, 10), 25, 90)
        whodas_t2 = np.clip(whodas_t1 - np.random.normal(15 + faktor_negeri * 0.15, 5), 15, 85)
        whodas_t3 = np.clip(whodas_t2 + np.random.normal(3, 4), 15, 85)

        wellbeing_t1 = np.clip(np.random.normal(52 + faktor_negeri * 0.3, 10), 20, 88)
        wellbeing_t2 = np.clip(wellbeing_t1 + np.random.normal(18 + faktor_negeri * 0.2, 6), 25, 99)
        wellbeing_t3 = np.clip(wellbeing_t2 - np.random.normal(2, 4), 25, 99)

        kepuasan = np.clip(s1 + np.random.normal(2, 4.5), 45, 100)
        mekanisme = np.clip((s1 * 0.55) + (s2 * 0.45), 40, 100)
        kualiti = np.clip((s1 * 0.25) + (s2 * 0.40) + (s3 * 0.35), 40, 100)
        kapasiti = np.clip((s2 * 0.35) + (s3 * 0.30) + (s4 * 0.35), 40, 100)

        outcome = np.clip(
            ((100 - whodas_t2) * 0.35) +
            (wellbeing_t2 * 0.35) +
            (kepuasan * 0.20) +
            (mekanisme * 0.10),
            40, 100
        )

        bersepadu = np.clip(
            (outcome * 0.30) +
            (mekanisme * 0.20) +
            (kualiti * 0.20) +
            (kapasiti * 0.20) +
            (s4 * 0.10),
            40, 100
        )

        rows.append([
            i + 1, n, z,
            s1, s2, s3, s4,
            kepuasan, outcome, mekanisme, kualiti, kapasiti, bersepadu,
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
# FUNGSI ASAS
# =========================================================
def purata(x):
    return float(x.mean())

def kpi(label, value, note=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)

def graf_bar(data, x, y, title):
    fig = px.bar(data, x=x, y=y, text_auto=".1f", title=title)
    fig.update_traces(marker_line_width=0, textposition="outside")
    fig.update_layout(
        template="plotly_dark",
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        title_font=dict(size=22, color="#FDE68A"),
        margin=dict(l=20, r=20, t=70, b=30)
    )
    return fig

def graf_line(data, x, y, title):
    fig = px.line(data, x=x, y=y, markers=True, title=title)
    fig.update_traces(line=dict(width=5), marker=dict(size=13))
    fig.update_layout(
        template="plotly_dark",
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        title_font=dict(size=22, color="#FDE68A"),
        margin=dict(l=20, r=20, t=70, b=30)
    )
    return fig

def pilih_data(df):
    st.markdown("### Penapis Analisis")
    c1, c2 = st.columns(2)

    with c1:
        zon = st.selectbox("Pilih Zon", ["Semua Zon"] + sorted(df["Zon"].unique()))

    with c2:
        if zon == "Semua Zon":
            negeri_opsyen = sorted(df["Negeri"].unique())
        else:
            negeri_opsyen = sorted(df[df["Zon"] == zon]["Negeri"].unique())
        negeri = st.selectbox("Pilih Negeri", ["Semua Negeri"] + negeri_opsyen)

    dff = df.copy()
    if zon != "Semua Zon":
        dff = dff[dff["Zon"] == zon]
    if negeri != "Semua Negeri":
        dff = dff[dff["Negeri"] == negeri]

    return dff, zon, negeri

# =========================================================
# FUNGSI RUMUSAN INTERVENSI
# =========================================================
def kategori_tahap(skor):
    if skor < 70:
        return "Kritikal"
    if skor < 80:
        return "Perlu Perhatian"
    return "Memuaskan tetapi boleh ditambah baik"

def warna_tahap(tahap):
    if tahap == "Kritikal":
        return "#FCA5A5"
    if tahap == "Perlu Perhatian":
        return "#FDE68A"
    return "#86EFAC"

def css_tahap(tahap):
    if tahap == "Kritikal":
        return "priority-critical"
    if tahap == "Perlu Perhatian":
        return "priority-attention"
    return "priority-good"

def kamus_intervensi(isu):
    bank = {
        "Kepuasan Klien": {
            "sumber": "S1",
            "konstruk": "K1 + K2",
            "dapatan": "Tahap kepuasan klien lebih rendah berbanding komponen lain. Isu ini lazimnya berkait dengan pengalaman sesi, komunikasi, tempoh menunggu, layanan, kefahaman klien terhadap proses dan ruang maklum balas.",
            "intervensi": "Perkukuh komunikasi sesi, penerangan hak klien, pengurusan temu janji, pengalaman kaunter, dan sistem maklum balas selepas sesi.",
            "tindakan": "Audit pengalaman klien; borang maklum balas ringkas selepas sesi; latihan komunikasi empati; semakan tempoh menunggu; saluran aduan dan maklum balas digital.",
            "output": "Peningkatan skor kepuasan klien, pengurangan aduan, dan peningkatan kepercayaan klien terhadap perkhidmatan."
        },
        "Outcome Klien": {
            "sumber": "S1 + S4",
            "konstruk": "K1",
            "dapatan": "Perubahan outcome klien T1-T2-T3 masih rendah atau tidak stabil. Ini menunjukkan kesan intervensi belum cukup konsisten atau susulan T3 perlu diperkukuh.",
            "intervensi": "Perkukuh pelan intervensi individu, susulan T3, pemantauan kes berisiko dan outcome tracking berasaskan indikator.",
            "tindakan": "Outcome monitoring; sesi susulan wajib; review kes kompleks; senarai kes berisiko; semakan pencapaian WHODAS dan wellbeing mengikut masa.",
            "output": "Outcome klien lebih stabil, penurunan masalah kefungsian, dan peningkatan kesejahteraan selepas intervensi."
        },
        "Mekanisme Perkhidmatan": {
            "sumber": "S1 + S2",
            "konstruk": "K2",
            "dapatan": "Akses, responsif, hubungan terapeutik atau kesinambungan perkhidmatan perlu diperkukuh. Isu ini memberi kesan kepada kebolehcapaian dan pengekalan klien dalam perkhidmatan.",
            "intervensi": "Tingkatkan akses temu janji, tele-kaunseling, sistem peringatan susulan dan standard komunikasi klien.",
            "tindakan": "Sistem appointment digital; SMS/WhatsApp reminder; protokol susulan; slot fleksibel; pemantauan kes tidak hadir.",
            "output": "Akses lebih cepat, kadar susulan meningkat, dan kesinambungan sesi lebih baik."
        },
        "Kualiti Penyampaian": {
            "sumber": "S1 + S2 + S3",
            "konstruk": "K3",
            "dapatan": "Aspek SOP, koordinasi rujukan, komunikasi atau konsistensi penyampaian belum optimum. Ini boleh menyebabkan variasi kualiti antara lokasi dan pegawai.",
            "intervensi": "Seragamkan SOP, latihan case management, audit kualiti perkhidmatan dan penyelarasan rujukan antara agensi.",
            "tindakan": "Bengkel SOP; audit fail kes; meja rujukan antara agensi; checklist kualiti; penyeliaan berkala.",
            "output": "Penyampaian lebih seragam, rujukan lebih tersusun, dan standard perkhidmatan meningkat."
        },
        "Kapasiti Organisasi": {
            "sumber": "S2 + S3 + S4",
            "konstruk": "K4",
            "dapatan": "Kapasiti organisasi dari aspek beban kes, pegawai, latihan, kemudahan atau sistem rekod perlu dipertingkatkan. Isu ini lazimnya menjadi punca kepada kelemahan kualiti dan mekanisme perkhidmatan.",
            "intervensi": "Tambah kapasiti pegawai, agihkan semula beban kes, tambah latihan CPD dan sediakan ruang sesi yang lebih kondusif.",
            "tindakan": "Workload balancing; cadangan perjawatan; latihan CPD; semakan infrastruktur; dashboard beban kes; pelan sokongan pegawai.",
            "output": "Beban kerja lebih seimbang, kapasiti penyampaian meningkat, dan risiko burnout pegawai berkurang."
        },
        "Data Pentadbiran": {
            "sumber": "S4",
            "konstruk": "K1 + K4 + K5",
            "dapatan": "Data pentadbiran menunjukkan isu capaian, rekod, nisbah pegawai-klien, susulan atau pelaporan berkala. Ini menjejaskan kebolehan pengurusan memantau prestasi secara real-time.",
            "intervensi": "Perkukuh sistem rekod, dashboard pemantauan, integrasi data dan mekanisme pelaporan berkala.",
            "tindakan": "Dashboard bulanan; semakan data kes; KPI susulan negeri; standard definisi data; audit rekod; integrasi laporan.",
            "output": "Data lebih kemas, pelaporan lebih pantas, dan keputusan pengurusan lebih berasaskan bukti."
        }
    }
    return bank[isu]

def jana_rumusan_intervensi(data):
    negeri_list = sorted(data["Negeri"].unique())
    rows = []

    for negeri in negeri_list:
        d = data[data["Negeri"] == negeri]

        skor = {
            "Kepuasan Klien": purata(d["Indeks_Kepuasan_Klien"]),
            "Outcome Klien": purata(d["Indeks_Outcome_Klien"]),
            "Mekanisme Perkhidmatan": purata(d["Mekanisme_Perkhidmatan"]),
            "Kualiti Penyampaian": purata(d["Kualiti_Penyampaian"]),
            "Kapasiti Organisasi": purata(d["Kapasiti_Organisasi"]),
            "Data Pentadbiran": purata(d["S4_Data_Pentadbiran"]),
        }

        isu = min(skor, key=skor.get)
        nilai_isu = skor[isu]
        meta = kamus_intervensi(isu)
        tahap = kategori_tahap(nilai_isu)

        rows.append([
            negeri,
            d["Zon"].iloc[0],
            round(purata(d["Indeks_Keberkesanan_Bersepadu"]), 1),
            isu,
            round(nilai_isu, 1),
            tahap,
            meta["sumber"],
            meta["konstruk"],
            meta["dapatan"],
            meta["intervensi"],
            meta["tindakan"],
            meta["output"]
        ])

    return pd.DataFrame(rows, columns=[
        "Negeri",
        "Zon",
        "Indeks Keberkesanan Bersepadu",
        "Isu Dominan",
        "Skor Isu",
        "Tahap Keutamaan",
        "Sumber Data",
        "Konstruk",
        "Rumusan Dapatan",
        "Cadangan Intervensi",
        "Tindakan Operasi",
        "Output Dijangka"
    ])

def jana_rumusan_keseluruhan(data):
    total_summary = pd.DataFrame({
        "Indikator Keseluruhan": [
            "Indeks Keberkesanan Bersepadu",
            "Indeks Kepuasan Klien",
            "Indeks Outcome Klien",
            "Mekanisme Perkhidmatan",
            "Kualiti Penyampaian",
            "Kapasiti Organisasi",
            "Data Pentadbiran"
        ],
        "Skor": [
            purata(data["Indeks_Keberkesanan_Bersepadu"]),
            purata(data["Indeks_Kepuasan_Klien"]),
            purata(data["Indeks_Outcome_Klien"]),
            purata(data["Mekanisme_Perkhidmatan"]),
            purata(data["Kualiti_Penyampaian"]),
            purata(data["Kapasiti_Organisasi"]),
            purata(data["S4_Data_Pentadbiran"])
        ]
    })
    return total_summary.sort_values("Skor").iloc[0], total_summary

# =========================================================
# HERO
# =========================================================
st.markdown("""
<div class="hero">
    <div class="hero-title">
        Dashboard Kajian Penilaian Keberkesanan<br>
        Perkhidmatan Psikologi dan Kaunseling JKM
    </div>
    <div class="hero-subtitle">
        Sistem Analitik Simulasi Premium berasaskan TOR JKM: Konstruk K1-K5,
        Sumber Data S1-S4, SEM, RE-AIM, CMO, analisis negeri, zon, outcome T1-T2-T3
        dan cadangan intervensi automatik mengikut isu dominan negeri.
    </div>
    <span class="badge">Data Simulasi Tender</span>
    <span class="badge">S1-S4 Triangulasi</span>
    <span class="badge">K1-K5 Konstruk</span>
    <span class="badge">SEM Analisis Utama</span>
    <span class="badge">RE-AIM & CMO</span>
    <span class="badge">Intervensi Negeri</span>
</div>
""", unsafe_allow_html=True)

# =========================================================
# PENAPIS
# =========================================================
dff, zon_pilih, negeri_pilih = pilih_data(df)

st.markdown(f"""
<div class="info-box">
<b>Skop Paparan Semasa:</b> {zon_pilih} | {negeri_pilih}<br>
Semua KPI, graf, SEM, RE-AIM, CMO, rumusan negeri dan cadangan intervensi berubah mengikut penapis ini.
Data ini ialah <b>simulasi</b> untuk demonstrasi cadangan teknikal dan perlu diganti dengan data lapangan sebenar selepas kajian dilaksanakan.
</div>
""", unsafe_allow_html=True)

# =========================================================
# KPI WAJIB
# =========================================================
c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi("Indeks Keberkesanan Bersepadu", f"{purata(dff['Indeks_Keberkesanan_Bersepadu']):.1f}%", "S1 + S2 + S3 + S4")
with c2:
    kpi("Indeks Kepuasan Klien", f"{purata(dff['Indeks_Kepuasan_Klien']):.1f}%", "S1 Klien")
with c3:
    kpi("Indeks Outcome Klien", f"{purata(dff['Indeks_Outcome_Klien']):.1f}%", "K1 Outcome")
with c4:
    kpi("Kualiti Penyampaian", f"{purata(dff['Kualiti_Penyampaian']):.1f}%", "K3 Kualiti")

c5, c6, c7, c8 = st.columns(4)
with c5:
    kpi("Kapasiti Organisasi", f"{purata(dff['Kapasiti_Organisasi']):.1f}%", "K4 Kapasiti")
with c6:
    kpi("Mekanisme Perkhidmatan", f"{purata(dff['Mekanisme_Perkhidmatan']):.1f}%", "K2 Mekanisme")
with c7:
    kpi("Responden Kuantitatif", f"{len(dff):,}", "Subset selepas penapis")
with c8:
    kpi("Temu Bual Kualitatif", "85", "Selaras TOR")

# =========================================================
# QUICK INSIGHT
# =========================================================
state_summary = df.groupby("Negeri", as_index=False)["Indeks_Keberkesanan_Bersepadu"].mean()
best_state = state_summary.sort_values("Indeks_Keberkesanan_Bersepadu", ascending=False).iloc[0]
low_state = state_summary.sort_values("Indeks_Keberkesanan_Bersepadu", ascending=True).iloc[0]

i1, i2, i3 = st.columns(3)
with i1:
    st.markdown(f"""
    <div class="insight-card">
    <b>Negeri Prestasi Tertinggi</b><br><br>
    {best_state['Negeri']} merekodkan skor simulasi tertinggi iaitu 
    <b>{best_state['Indeks_Keberkesanan_Bersepadu']:.1f}%</b>.
    </div>
    """, unsafe_allow_html=True)
with i2:
    st.markdown(f"""
    <div class="insight-card">
    <b>Negeri Memerlukan Perhatian</b><br><br>
    {low_state['Negeri']} merekodkan skor simulasi terendah iaitu 
    <b>{low_state['Indeks_Keberkesanan_Bersepadu']:.1f}%</b>.
    </div>
    """, unsafe_allow_html=True)
with i3:
    improvement = purata(dff["Wellbeing_T2"]) - purata(dff["Wellbeing_T1"])
    st.markdown(f"""
    <div class="insight-card">
    <b>Peningkatan Outcome T1 ke T2</b><br><br>
    Skor kesejahteraan meningkat sebanyak 
    <b>{improvement:.1f} mata</b> selepas intervensi.
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TAB LENGKAP
# =========================================================
tabs = st.tabs([
    "Ringkasan Eksekutif",
    "Negeri & Zon",
    "Outcome T1-T2-T3",
    "SEM",
    "RE-AIM",
    "CMO",
    "Rumusan Negeri & Intervensi",
    "Pemetaan K-S-Teori",
    "Simulasi Dasar"
])

with tabs[0]:
    st.subheader("Ringkasan Eksekutif")

    st.markdown(f"""
    <div class="info-box">
    Indeks Keberkesanan Bersepadu bagi paparan semasa ialah 
    <b>{purata(dff['Indeks_Keberkesanan_Bersepadu']):.1f}%</b>. 
    Indeks ini menggabungkan S1 Klien, S2 PPsi/PPPsi, S3 Warga JKM dan S4 Data Pentadbiran.
    Kepuasan klien pula dikira khusus daripada S1 kerana kepuasan hanya boleh dijawab secara langsung oleh klien.
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
            purata(dff["S1_Klien"]),
            purata(dff["S2_PPsi_PPPsi"]),
            purata(dff["S3_Warga_JKM"]),
            purata(dff["S4_Data_Pentadbiran"]),
            purata(dff["Indeks_Kepuasan_Klien"]),
            purata(dff["Indeks_Keberkesanan_Bersepadu"])
        ]
    })

    st.plotly_chart(graf_bar(summary, "Komponen", "Skor Purata", "Ringkasan Skor Utama"), use_container_width=True)

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

    st.plotly_chart(graf_bar(by_state, "Negeri", "Indeks_Keberkesanan_Bersepadu", "Indeks Keberkesanan Mengikut Negeri"), use_container_width=True)
    st.plotly_chart(graf_bar(by_zone, "Zon", "Indeks_Keberkesanan_Bersepadu", "Indeks Keberkesanan Mengikut Zon"), use_container_width=True)

    with st.expander("Lihat jadual terperinci negeri dan zon"):
        st.dataframe(by_state.round(2), use_container_width=True)
        st.dataframe(by_zone.round(2), use_container_width=True)

with tabs[2]:
    st.subheader("Analisis Outcome Longitudinal T1-T2-T3")

    t_data = pd.DataFrame({
        "Masa": ["T1", "T2", "T3"],
        "WHODAS": [purata(dff["WHODAS_T1"]), purata(dff["WHODAS_T2"]), purata(dff["WHODAS_T3"])],
        "Wellbeing": [purata(dff["Wellbeing_T1"]), purata(dff["Wellbeing_T2"]), purata(dff["Wellbeing_T3"])]
    })

    st.markdown("""
    <div class="info-box">
    WHODAS yang menurun menunjukkan kefungsian klien bertambah baik. 
    Wellbeing yang meningkat menunjukkan kesejahteraan klien bertambah baik.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(graf_line(t_data, "Masa", "WHODAS", "Trend WHODAS T1-T2-T3"), use_container_width=True)
    with c2:
        st.plotly_chart(graf_line(t_data, "Masa", "Wellbeing", "Trend Wellbeing T1-T2-T3"), use_container_width=True)

    with st.expander("Lihat data T1-T2-T3"):
        st.dataframe(t_data.round(2), use_container_width=True)

with tabs[3]:
    st.subheader("Analisis SEM: Kapasiti → Kualiti → Mekanisme → Outcome")

    cap = purata(dff["Kapasiti_Organisasi"]) / 100
    qua = purata(dff["Kualiti_Penyampaian"]) / 100
    mec = purata(dff["Mekanisme_Perkhidmatan"]) / 100

    beta1 = np.clip(0.45 + cap * 0.35, 0.50, 0.88)
    beta2 = np.clip(0.42 + qua * 0.35, 0.50, 0.88)
    beta3 = np.clip(0.40 + mec * 0.35, 0.50, 0.88)

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi("β Kapasiti → Kualiti", f"{beta1:.2f}", "K4 → K3")
    with c2:
        kpi("β Kualiti → Mekanisme", f"{beta2:.2f}", "K3 → K2")
    with c3:
        kpi("β Mekanisme → Outcome", f"{beta3:.2f}", "K2 → K1")

    fig = go.Figure()
    nodes = ["Kapasiti Organisasi", "Kualiti Penyampaian", "Mekanisme Perkhidmatan", "Outcome Klien"]
    xs = [0.08, 0.36, 0.64, 0.92]
    ys = [0.5, 0.5, 0.5, 0.5]

    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="markers+text",
        marker=dict(size=72, color=["#FDE68A", "#93C5FD", "#86EFAC", "#FCA5A5"]),
        text=nodes,
        textposition="bottom center",
        textfont=dict(size=14, color="white"),
        hoverinfo="text"
    ))

    for i, b in enumerate([beta1, beta2, beta3]):
        fig.add_trace(go.Scatter(
            x=[xs[i], xs[i+1]], y=[ys[i], ys[i+1]],
            mode="lines+text",
            line=dict(width=6, color="#FDE68A"),
            text=["", f"β={b:.2f}"],
            textposition="top center",
            textfont=dict(size=16, color="#FDE68A"),
            hoverinfo="skip"
        ))

    fig.update_xaxes(visible=False, range=[0, 1])
    fig.update_yaxes(visible=False, range=[0.2, 0.8])
    fig.update_layout(
        height=420,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(text="Model SEM Simulasi", font=dict(size=24, color="#FDE68A")),
        margin=dict(l=20, r=20, t=70, b=30)
    )
    st.plotly_chart(fig, use_container_width=True)

with tabs[4]:
    st.subheader("Analisis RE-AIM")

    reaim = pd.DataFrame({
        "Domain": ["Reach", "Effectiveness", "Adoption", "Implementation", "Maintenance"],
        "Skor": [
            purata(dff["S4_Data_Pentadbiran"]),
            purata(dff["Indeks_Outcome_Klien"]),
            purata(dff["S2_PPsi_PPPsi"]),
            purata(dff["Kapasiti_Organisasi"]),
            purata(dff["Indeks_Keberkesanan_Bersepadu"])
        ]
    })

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=reaim["Skor"],
        theta=reaim["Domain"],
        fill="toself",
        name="RE-AIM"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        template="plotly_dark",
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        title=dict(text="Radar RE-AIM Mengikut Pilihan Semasa", font=dict(color="#FDE68A", size=24))
    )
    st.plotly_chart(fig, use_container_width=True)

with tabs[5]:
    st.subheader("Analisis CMO: Context–Mechanism–Outcome")

    cmo = [
        ("Beban Kes Tinggi", "Kapasiti pegawai terhad dan masa menunggu meningkat", "Outcome klien lebih perlahan", "S2 + S4"),
        ("Akses Lokasi Mencabar", "Keperluan tele-kaunseling dan susulan digital", "Reach perkhidmatan boleh meningkat", "S1 + S4"),
        ("SOP Rujukan Jelas", "Koordinasi antara agensi lebih lancar", "Kualiti penyampaian meningkat", "S2 + S3"),
        ("Hubungan Terapeutik Baik", "Klien lebih percaya dan kekal dalam sesi", "Kepuasan dan outcome meningkat", "S1"),
    ]

    for context, mechanism, outcome, source in cmo:
        st.markdown(f"""
        <div class="panel">
        <h3>{context}</h3>
        <b>Mekanisme:</b> {mechanism}<br>
        <b>Outcome:</b> {outcome}<br>
        <b>Sumber Data:</b> {source}
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# TAB BARU: RUMUSAN NEGERI & INTERVENSI
# =========================================================
with tabs[6]:
    st.subheader("Rumusan Dapatan dan Cadangan Intervensi Mengikut Negeri")

    rumusan = jana_rumusan_intervensi(dff)
    isu_keseluruhan, total_summary = jana_rumusan_keseluruhan(dff)
    meta_keseluruhan = kamus_intervensi(
        "Data Pentadbiran" if isu_keseluruhan["Indikator Keseluruhan"] == "Data Pentadbiran"
        else isu_keseluruhan["Indikator Keseluruhan"].replace("Indeks ", "").replace("Skor ", "")
    ) if isu_keseluruhan["Indikator Keseluruhan"] in [
        "Indeks Kepuasan Klien", "Indeks Outcome Klien", "Mekanisme Perkhidmatan",
        "Kualiti Penyampaian", "Kapasiti Organisasi", "Data Pentadbiran"
    ] else kamus_intervensi("Outcome Klien")

    st.markdown(f"""
    <div class="info-box">
    Bahagian ini menjana rumusan automatik berdasarkan <b>skor terendah</b> bagi setiap negeri.
    Sistem mengenal pasti isu dominan, sumber data yang menyokong dapatan, konstruk kajian yang terlibat,
    cadangan intervensi, tindakan operasi dan output dijangka. Paparan semasa: 
    <b>{zon_pilih}</b> | <b>{negeri_pilih}</b>.
    </div>
    """, unsafe_allow_html=True)

    a, b, c, d = st.columns(4)
    with a:
        kpi("Jumlah Negeri Dianalisis", f"{rumusan['Negeri'].nunique()}", "Mengikut penapis semasa")
    with b:
        kpi("Purata Skor Isu Dominan", f"{rumusan['Skor Isu'].mean():.1f}%", "Lebih rendah = lebih perlu perhatian")
    with c:
        kpi("Isu Keseluruhan Terendah", isu_keseluruhan["Indikator Keseluruhan"], f"{isu_keseluruhan['Skor']:.1f}%")
    with d:
        kpi("Negeri Kritikal", f"{(rumusan['Tahap Keutamaan'] == 'Kritikal').sum()}", "Skor isu < 70%")

    st.markdown(f"""
    <div class="intervention-panel">
    <h3>Rumusan Keseluruhan Sistem</h3>
    Secara keseluruhan, komponen yang paling memerlukan perhatian ialah 
    <b>{isu_keseluruhan['Indikator Keseluruhan']}</b> dengan skor 
    <b>{isu_keseluruhan['Skor']:.1f}%</b>. 
    Cadangan intervensi perlu dimulakan pada komponen ini sebelum diperluas kepada komponen lain.
    <br><br>
    <b>Cadangan Fokus:</b> {meta_keseluruhan['intervensi']}<br>
    <b>Tindakan Operasi:</b> {meta_keseluruhan['tindakan']}
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1.15, 1])
    with c1:
        st.plotly_chart(
            graf_bar(
                rumusan.sort_values("Skor Isu"),
                "Negeri",
                "Skor Isu",
                "Skor Isu Dominan Mengikut Negeri"
            ),
            use_container_width=True
        )

    with c2:
        tahap_count = rumusan["Tahap Keutamaan"].value_counts().reset_index()
        tahap_count.columns = ["Tahap Keutamaan", "Bilangan Negeri"]
        st.plotly_chart(
            graf_bar(
                tahap_count,
                "Tahap Keutamaan",
                "Bilangan Negeri",
                "Bilangan Negeri Mengikut Tahap Keutamaan"
            ),
            use_container_width=True
        )

    c3, c4 = st.columns([1, 1])
    with c3:
        isu_count = rumusan["Isu Dominan"].value_counts().reset_index()
        isu_count.columns = ["Isu Dominan", "Bilangan Negeri"]
        st.plotly_chart(
            graf_bar(
                isu_count,
                "Isu Dominan",
                "Bilangan Negeri",
                "Taburan Isu Dominan Mengikut Negeri"
            ),
            use_container_width=True
        )

    with c4:
        st.plotly_chart(
            graf_bar(
                total_summary.sort_values("Skor"),
                "Indikator Keseluruhan",
                "Skor",
                "Skor Komponen Keseluruhan"
            ),
            use_container_width=True
        )

    st.markdown("### Jadual Ringkasan Intervensi Mengikut Negeri")
    st.dataframe(rumusan, use_container_width=True)

    csv = rumusan.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇️ Download Rumusan Intervensi CSV",
        data=csv,
        file_name="rumusan_intervensi_negeri.csv",
        mime="text/csv"
    )

    st.markdown("### Kad Rumusan Negeri")

    for _, row in rumusan.sort_values(["Tahap Keutamaan", "Skor Isu"]).iterrows():
        warna = warna_tahap(row["Tahap Keutamaan"])
        css = css_tahap(row["Tahap Keutamaan"])

        st.markdown(f"""
        <div class="intervention-panel" style="border-left: 8px solid {warna};">
            <h3>{row['Negeri']} ({row['Zon']})</h3>
            <span class="{css}">{row['Tahap Keutamaan']}</span>
            <br><br>
            <b>Indeks Keberkesanan Bersepadu:</b> {row['Indeks Keberkesanan Bersepadu']}%<br>
            <b>Isu Dominan:</b> {row['Isu Dominan']} ({row['Skor Isu']}%)<br>
            <b>Sumber Data:</b> {row['Sumber Data']}<br>
            <b>Konstruk:</b> {row['Konstruk']}<br><br>
            <b>Rumusan Dapatan:</b><br>
            {row['Rumusan Dapatan']}<br><br>
            <b>Cadangan Intervensi:</b><br>
            {row['Cadangan Intervensi']}<br><br>
            <b>Tindakan Operasi:</b><br>
            {row['Tindakan Operasi']}<br><br>
            <b>Output Dijangka:</b><br>
            {row['Output Dijangka']}
        </div>
        """, unsafe_allow_html=True)

with tabs[7]:
    st.subheader("Pemetaan Konstruk, Sumber Data, Instrumen dan Teori")

    st.markdown("### Pemetaan Konstruk K1-K5")
    st.dataframe(K_SOURCE_MAP, use_container_width=True)

    st.markdown("### Pemetaan Result Sistem")
    st.dataframe(RESULT_SOURCE_MAP, use_container_width=True)

with tabs[8]:
    st.subheader("Simulasi Dasar dan Penambahbaikan")

    a, b, c = st.columns(3)
    with a:
        tambah_pegawai = st.slider("Penambahan kapasiti pegawai (%)", 0, 30, 10)
    with b:
        tambah_latihan = st.slider("Peningkatan latihan (%)", 0, 30, 10)
    with c:
        tambah_digital = st.slider("Pendigitalan susulan (%)", 0, 30, 10)

    base = purata(dff["Indeks_Keberkesanan_Bersepadu"])
    simulated = np.clip(base + tambah_pegawai * 0.20 + tambah_latihan * 0.25 + tambah_digital * 0.18, 0, 100)

    c1, c2 = st.columns(2)
    with c1:
        kpi("Indeks Semasa", f"{base:.1f}%", "Sebelum simulasi dasar")
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
        "Sumber Data": ["S2 + S4", "S2 + S3", "S1 + S4", "S2 + S3"],
        "Konstruk": ["K4", "K3 + K4", "K2 + K5", "K3"],
    })

    with st.expander("Lihat matriks cadangan dasar"):
        st.dataframe(policy, use_container_width=True)
'''

path = Path("/mnt/data/app.py")
path.write_text(code, encoding="utf-8")
print(f"Created {path} ({path.stat().st_size:,} bytes)")
