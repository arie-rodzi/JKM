import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="JKM Psycho-Counselling Impact Intelligence", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:radial-gradient(circle at top left,#123B65 0%,#07192D 42%,#020617 100%);color:#F8FAFC;}
.block-container{padding-top:1rem;max-width:1580px;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#06101E,#0B1628);border-right:1px solid rgba(197,160,23,.28)}
h1,h2,h3{color:#fff!important;letter-spacing:-.03em;}
.hero{padding:34px;border-radius:32px;background:linear-gradient(135deg,rgba(197,160,23,.24),rgba(16,185,129,.12)),linear-gradient(135deg,#06142B,#10213C 60%,#163E62);border:1px solid rgba(253,230,138,.35);box-shadow:0 28px 90px rgba(0,0,0,.42);margin-bottom:18px;}
.badge{display:inline-block;padding:7px 13px;border-radius:999px;background:rgba(197,160,23,.18);border:1px solid rgba(253,230,138,.38);color:#FDE68A;font-weight:900;font-size:12px;letter-spacing:.08em;}
.hero-title{font-size:42px;line-height:1.07;font-weight:900;margin-top:12px;}
.gold{background:linear-gradient(90deg,#FDE68A,#C5A017,#FFF7C2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-subtitle{color:#CBD5E1;font-size:16px;max-width:1160px;margin-top:10px;}
.card{padding:22px;border-radius:25px;background:rgba(15,23,42,.76);border:1px solid rgba(148,163,184,.23);box-shadow:0 20px 58px rgba(0,0,0,.28);margin-bottom:18px;}
.card2{padding:18px;border-radius:22px;background:rgba(30,41,59,.58);border:1px solid rgba(148,163,184,.18);margin-bottom:15px;}
.kpi{padding:20px;border-radius:23px;background:linear-gradient(180deg,rgba(15,23,42,.97),rgba(15,23,42,.72));border:1px solid rgba(148,163,184,.23);min-height:128px;box-shadow:0 14px 36px rgba(0,0,0,.22)}
.klabel{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#94A3B8;font-weight:800;}
.kvalue{font-size:32px;color:white;font-weight:900;margin-top:8px;}
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
STATE_EFFECT = {"Kuala Lumpur":4.5,"Selangor":3.3,"Pulau Pinang":2.4,"Kedah":1.2,"Johor":2.5,"Melaka":1.7,"Kelantan":-1.4,"Pahang":-0.7,"Sabah":-2.4,"Sarawak":-1.8}
STATE_TO_ZONE = {s:z for z, ss in ZONES.items() for s in ss}
INTERVENTIONS = ["Kaunseling Individu","Kaunseling Kelompok","Intervensi Krisis","Sokongan Sosial","Psikopendidikan","Rujukan Lanjut"]

K_SOURCE_MAP = pd.DataFrame([
    ["K1", "Outcome Klien / Keberkesanan", "S1 + S4", "Manual Instrumen Teras Hasil Klien JKM + CASRS-JKM + data pentadbiran", "WHODAS T1/T2/T3; WHOQOL/Wellbeing T1/T2/T3; WAI-SR; CSQ-8; PCL-5 selektif; status kes; rekod susulan", "Realist Evaluation; RE-AIM Effectiveness; Bronfenbrenner", "Client Outcome Index; WHODAS Improvement; Wellbeing Improvement; PCL-5 Reduction; T3 Follow-up"],
    ["K2", "Mekanisme Perkhidmatan", "S1 + S2", "CASRS-JKM + IPKJ-JKM Instrumen A", "Akses fizikal/prosedur; komunikasi; responsif relasi; aliansi terapeutik; etika; susulan; kesesuaian modaliti intervensi", "Realist Evaluation (CMO); WHO Person-Centred Approach", "Service Mechanism Score; Access Responsiveness; WAI Alliance"],
    ["K3", "Kualiti Penyampaian", "S1 + S2 + S3", "CASRS-JKM + IPKJ-JKM Instrumen A/B + soal selidik warga JKM", "SOP; kompetensi; etika; kerahsiaan; komunikasi; kualiti intervensi; koordinasi rujukan", "Donabedian Process; WHO Person-Centred Approach", "Service Quality Score; SOP Compliance; Referral Coordination"],
    ["K4", "Kapasiti Organisasi", "S2 + S3 + S4", "IPKJ-JKM Instrumen B + soal selidik warga JKM + data pentadbiran", "Perjawatan; beban kes; kemudahan; latihan; peruntukan; sistem rekod; burnout; nisbah pegawai-klien; tempoh menunggu", "Donabedian Structure; RE-AIM Implementation/Maintenance", "Organizational Capacity Index; Workload Index; Waiting Time; Follow-up Readiness"],
    ["K5", "Penambahbaikan & Inovasi", "S1 + S2 + S3 + S4", "Soalan terbuka CASRS/IPKJ + temu bual + data pentadbiran", "Cadangan klien; cadangan pegawai; isu sistemik; peluang digital; tele-kaunseling; SOP digital; keperluan latihan dan sumber", "RE-AIM Maintenance; Realist Evaluation; CMO", "Policy Recommendation Matrix; Priority Action Plan; Scenario Simulator"],
], columns=["K", "Konstruk", "Sumber Data", "Instrumen / Questionnaire", "Item / Domain Digunakan", "Theory / Framework", "Result Dalam Sistem"])

S_SOURCE_MAP = pd.DataFrame([
    ["S1", "Klien", "CASRS-JKM + Manual Instrumen Teras Hasil Klien JKM", "≈450 kuantitatif + ≈45 kualitatif", "K1, K2, K3, K5", "Client Satisfaction; Client Outcome; Access; Responsiveness; Therapeutic Alliance; T1-T2-T3 Improvement"],
    ["S2", "PPsi + PPPsi", "IPKJ-JKM Instrumen A & B", "≈75 kuantitatif + ≈25 kualitatif", "K2, K3, K4, K5", "Intervention Success; SOP; Competency; Workload; Training; Burnout; Service Barrier"],
    ["S3", "Warga JKM", "Soal selidik sokongan sistem + temu bual", "≈75 kuantitatif + ≈15 kualitatif", "K3, K4, K5", "Organisational Support; Referral Coordination; Internal Collaboration; System Readiness"],
    ["S4", "Data Pentadbiran JKM", "Rekod kes, statistik intervensi, laporan tahunan, data sumber manusia, rekod susulan", "Bukan responden", "K1, K4, K5", "Reach; Intervention Trend; Officer-Client Ratio; Case Load; Follow-up Rate; Waiting Time"],
], columns=["S", "Sumber", "Instrumen / Data", "Anggaran Sampel", "Konstruk Disokong", "Output Dashboard"])

RESULT_SOURCE_MAP = pd.DataFrame([
    ["Overall Integrated Satisfaction / Effectiveness Index", "CASRS-JKM + CSQ-8 + outcome longitudinal + IPKJ-JKM + warga JKM + data pentadbiran", "S1 + S2 + S3 + S4", "K1 + K2 + K3 + K4 + K5", "Realist Evaluation; Donabedian; RE-AIM; WHO Person-Centred", "Indeks komposit nasional: S1 client satisfaction/outcome, S2 provider readiness, S3 organisational support, dan S4 service performance. Ini bukan satu questionnaire sahaja."],
    ["Client Satisfaction Index", "CASRS-JKM + CSQ-8", "S1", "K1 + K2", "WHO Person-Centred; Realist Evaluation", "Purata kepuasan klien terhadap akses, komunikasi, hubungan terapeutik, etika, susulan dan pengalaman perkhidmatan; ditukar kepada indeks 0-100."],
    ["Staff Readiness / Provider Index", "IPKJ-JKM Instrumen A & B", "S2", "K2 + K3 + K4", "Donabedian; RE-AIM Adoption/Implementation", "Purata kompetensi, keyakinan intervensi, pematuhan SOP, beban kerja, latihan, sokongan penyeliaan dan burnout terbalik."],
    ["Organisational Support Index", "Soal selidik warga JKM + temu bual", "S3", "K3 + K4 + K5", "Donabedian; RE-AIM Implementation", "Purata sokongan organisasi, koordinasi rujukan, integrasi dalaman, kesiapsiagaan sistem dan sokongan kepimpinan."],
    ["Administrative Performance Index", "Rekod kes, statistik intervensi, data sumber manusia, rekod susulan", "S4", "K1 + K4 + K5", "RE-AIM Reach/Maintenance; Donabedian Structure", "Dikira daripada reach, kadar susulan T3, masa menunggu terbalik, keciciran terbalik, nisbah pegawai-klien dan beban kes."],
    ["Client Outcome Index", "WHODAS, WHOQOL/Wellbeing, WAI-SR, CSQ-8, PCL-5 selektif, rekod susulan", "S1 + S4", "K1", "RE-AIM Effectiveness; Realist CMO", "Gabungan perubahan T1-T2-T3: WHODAS menurun = baik, Wellbeing meningkat = baik, PCL-5 menurun = baik, WAI/CSQ tinggi = baik, dan rekod susulan mengesahkan kesinambungan outcome."],
    ["Service Mechanism Score", "CASRS-JKM + IPKJ-JKM Instrumen A", "S1 + S2", "K2", "Realist Evaluation CMO; WHO Person-Centred", "Dikira daripada akses, prosedur, komunikasi, responsif relasi, aliansi terapeutik, susulan dan kesesuaian modaliti intervensi."],
    ["Service Quality Score", "CASRS-JKM + IPKJ-JKM + soal selidik warga JKM", "S1 + S2 + S3", "K3", "Donabedian Process; WHO Person-Centred", "Dikira daripada SOP, kompetensi, etika, kerahsiaan, kualiti intervensi, komunikasi dan koordinasi rujukan."],
    ["Organizational Capacity Index", "IPKJ-JKM Instrumen B + warga JKM + data pentadbiran", "S2 + S3 + S4", "K4", "Donabedian Structure; RE-AIM Implementation", "Dikira daripada beban kes, perjawatan, kemudahan, latihan, sistem rekod, peruntukan, burnout terbalik, nisbah pegawai-klien dan tempoh menunggu."],
    ["SEM Path Coefficient", "Skor konstruk teragregat daripada CASRS, IPKJ, outcome longitudinal, warga JKM dan data pentadbiran", "S1 + S2 + S3 + S4", "K1-K4", "Realist CMO + Donabedian", "Menguji hubungan Capacity → Quality → Mechanism → Outcome. Model ini triangulasi pelbagai sumber data, bukan satu set questionnaire."],
    ["RE-AIM Score", "Data pentadbiran + outcome klien + IPKJ + warga JKM + temu bual", "S1 + S2 + S3 + S4", "K1-K5", "RE-AIM", "Reach daripada rekod pentadbiran; Effectiveness daripada outcome klien; Adoption daripada PPsi/PPPsi/warga; Implementation daripada IPKJ dan S4; Maintenance daripada T3, susulan dan kualitatif."],
    ["CMO Finding", "Temu bual, soalan terbuka CASRS/IPKJ dan data sokongan sistem", "S1 + S2 + S3", "K2 + K5", "Realist Evaluation", "Menjawab: dalam konteks apa, melalui mekanisme apa, outcome apa berlaku; digunakan untuk cadangan operasi dan polisi."],
], columns=["Result Sistem", "Questionnaire / Data Digunakan", "Sumber", "Konstruk", "Theory", "Bagaimana Sistem Kira / Jana Result"])

WEIGHTS = pd.DataFrame([
    ["S1", "Client Satisfaction + Outcome", 0.40],
    ["S2", "Staff Readiness / Provider Capacity", 0.25],
    ["S3", "Organisational Support", 0.15],
    ["S4", "Administrative Performance", 0.20],
], columns=["Sumber", "Sub-index", "Weight"])


def fig_style(fig, h=430):
    fig.update_layout(height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,.18)", font=dict(color="#E5E7EB", family="Inter"), margin=dict(l=25,r=25,t=62,b=35), legend=dict(orientation="h", y=1.08, x=1, xanchor="right"), title_font=dict(size=20, color="#fff"))
    fig.update_xaxes(gridcolor="rgba(148,163,184,.18)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,.18)")
    return fig


def kpi(label, value, note=""):
    st.markdown(f"<div class='kpi'><div class='klabel'>{label}</div><div class='kvalue'>{value}</div><div class='knote'>{note}</div></div>", unsafe_allow_html=True)


def norm(series, higher_is_better=True):
    s = pd.Series(series).astype(float)
    if s.max() == s.min():
        out = pd.Series(np.full(len(s), 75.0), index=s.index)
    else:
        out = (s - s.min()) / (s.max() - s.min()) * 100
    return out if higher_is_better else 100 - out

@st.cache_data(show_spinner=False)
def simulate_s1_clients(n=450, seed=2026):
    rng = np.random.default_rng(seed)
    zones = np.repeat(list(ZONES.keys()), n // 6)
    if len(zones) < n: zones = np.concatenate([zones, rng.choice(list(ZONES.keys()), n-len(zones))])
    rng.shuffle(zones)
    rows=[]
    for i,z in enumerate(zones,1):
        state = rng.choice(ZONES[z]); eff = STATE_EFFECT[state]
        age = int(np.clip(rng.normal(38, 14),16,78))
        access = np.clip(rng.normal(73+eff,10),30,98)
        comm = np.clip(rng.normal(78+eff,8),35,99)
        relation = np.clip(rng.normal(80+eff,8),35,100)
        ethics = np.clip(rng.normal(82+eff,7),45,100)
        followup_exp = np.clip(rng.normal(72+eff,11),30,98)
        wai = np.clip(0.45*relation + 0.25*comm + rng.normal(25,5),35,100)
        csq = np.clip(0.30*access + 0.25*comm + 0.25*relation + 0.20*ethics + rng.normal(0,5),35,100)
        wh1=np.clip(rng.normal(49,10),12,85); wb1=np.clip(rng.normal(52,10),15,88); pcl1=np.clip(rng.normal(43,13),5,82)
        improvement=np.clip((access+comm+relation)/12 + rng.normal(0,4),5,32)
        wh2=np.clip(wh1-improvement*.55+rng.normal(0,3),4,78); wh3=np.clip(wh2-rng.normal(2.0,3),3,76)
        wb2=np.clip(wb1+improvement*.62+rng.normal(0,3),15,98); wb3=np.clip(wb2+rng.normal(2,3),15,99)
        pcl2=np.clip(pcl1-improvement*.62+rng.normal(0,4),2,80); pcl3=np.clip(pcl2-rng.normal(2.4,3),2,78)
        outcome=np.clip(.24*(100-wh3)+.24*wb3+.18*csq+.18*wai+.16*(100-pcl3),0,100)
        rows.append({"client_id":f"S1C{i:04d}","zone":z,"state":state,"source":"S1","respondent_group":"Klien","gender":rng.choice(["Lelaki","Perempuan"],p=[.42,.58]),"age":age,"age_group":"16-24" if age<25 else "25-34" if age<35 else "35-44" if age<45 else "45-54" if age<55 else "55+","client_category":rng.choice(["Kanak-kanak","Warga emas","OKU","Keluarga","Mangsa keganasan","Komuniti","Penjaga","Lain-lain"]),"intervention_type":rng.choice(INTERVENTIONS,p=[.34,.15,.17,.13,.12,.09]),"Access_Responsiveness":round(access,1),"Communication":round(comm,1),"Therapeutic_Relationship":round(relation,1),"Rights_Based_Experience":round(ethics,1),"Followup_Experience":round(followup_exp,1),"WAI_Alliance":round(wai,1),"CSQ8_Satisfaction":round(csq,1),"WHODAS_T1":round(wh1,1),"WHODAS_T2":round(wh2,1),"WHODAS_T3":round(wh3,1),"Wellbeing_T1":round(wb1,1),"Wellbeing_T2":round(wb2,1),"Wellbeing_T3":round(wb3,1),"PCL5_T1":round(pcl1,1),"PCL5_T2":round(pcl2,1),"PCL5_T3":round(pcl3,1),"Client_Outcome_Index":round(outcome,1),"dropout_status":"Ya" if rng.random()<.12+max(0,65-access)/220 else "Tidak","followup_status":"Lengkap" if rng.random()<.74 else "Tidak lengkap"})
    return pd.DataFrame(rows)

@st.cache_data(show_spinner=False)
def simulate_s2_staff(n=75, seed=2027):
    rng=np.random.default_rng(seed); zones=np.repeat(list(ZONES.keys()), n//6)
    if len(zones)<n: zones=np.concatenate([zones,rng.choice(list(ZONES.keys()), n-len(zones))])
    rng.shuffle(zones); rows=[]
    for i,z in enumerate(zones,1):
        state=rng.choice(ZONES[z]); eff=STATE_EFFECT[state]
        competency=np.clip(rng.normal(78+eff,8),40,100); sop=np.clip(rng.normal(74+eff,9),35,98); supervision=np.clip(rng.normal(70+eff,10),30,98)
        workload=np.clip(rng.normal(63-eff,10),30,95) # high = burden
        burnout=np.clip(rng.normal(55-eff,12),20,90) # high = bad
        modality=np.clip(rng.normal(73+eff,9),35,98); barrier=np.clip(rng.normal(46-eff,12),10,90)
        readiness=np.clip(.27*competency+.22*sop+.18*supervision+.17*modality+.08*(100-workload)+.08*(100-burnout),0,100)
        rows.append({"staff_id":f"S2P{i:03d}","zone":z,"state":state,"source":"S2","respondent_group":rng.choice(["PPsi","PPPsi"],p=[.70,.30]),"Competency":round(competency,1),"SOP_Compliance":round(sop,1),"Supervision_CPD":round(supervision,1),"Workload_Burden":round(workload,1),"Burnout_Risk":round(burnout,1),"Modality_Fit":round(modality,1),"Intervention_Barrier":round(barrier,1),"Staff_Readiness_Index":round(readiness,1)})
    return pd.DataFrame(rows)

@st.cache_data(show_spinner=False)
def simulate_s3_warga(n=75, seed=2028):
    rng=np.random.default_rng(seed); zones=np.repeat(list(ZONES.keys()), n//6)
    if len(zones)<n: zones=np.concatenate([zones,rng.choice(list(ZONES.keys()), n-len(zones))])
    rng.shuffle(zones); rows=[]
    for i,z in enumerate(zones,1):
        state=rng.choice(ZONES[z]); eff=STATE_EFFECT[state]
        org=np.clip(rng.normal(72+eff,9),35,98); referral=np.clip(rng.normal(68+eff,11),25,97); leadership=np.clip(rng.normal(73+eff,9),35,99); system=np.clip(rng.normal(70+eff,10),30,98)
        support=np.clip(.30*org+.28*referral+.22*leadership+.20*system,0,100)
        rows.append({"warga_id":f"S3W{i:03d}","zone":z,"state":state,"source":"S3","respondent_group":"Warga JKM","Organisational_Support":round(org,1),"Referral_Coordination":round(referral,1),"Leadership_Support":round(leadership,1),"System_Readiness":round(system,1),"Org_Support_Index":round(support,1)})
    return pd.DataFrame(rows)

@st.cache_data(show_spinner=False)
def simulate_s4_admin(seed=2029):
    rng=np.random.default_rng(seed); rows=[]
    for state, eff in STATE_EFFECT.items():
        z=STATE_TO_ZONE[state]
        interventions=int(np.clip(rng.normal(26000+eff*900,4500),6500,45000))
        officers=int(np.clip(rng.normal(38+eff/1.8,7),12,65))
        waiting=np.clip(rng.normal(9-eff/3,3),2,24)
        follow=np.clip(rng.normal(76+eff,8),40,96)
        dropout=np.clip(rng.normal(13-eff/3,4),3,30)
        ratio=interventions/max(officers,1)
        rows.append({"state":state,"zone":z,"source":"S4","interventions_2025":interventions,"officers":officers,"officer_client_ratio":round(ratio,1),"avg_waiting_days":round(waiting,1),"admin_followup_rate":round(follow,1),"admin_dropout_rate":round(dropout,1)})
    df=pd.DataFrame(rows)
    df["Admin_Performance_Index"]=(.30*norm(df["interventions_2025"],True)+.25*df["admin_followup_rate"]+.20*norm(df["avg_waiting_days"],False)+.15*norm(df["admin_dropout_rate"],False)+.10*norm(df["officer_client_ratio"],False)).round(1)
    return df

@st.cache_data(show_spinner=False)
def simulate_interviews(n=85, seed=2030):
    rng=np.random.default_rng(seed); zones=np.repeat(list(ZONES.keys()), n//6)
    if len(zones)<n: zones=np.concatenate([zones,rng.choice(list(ZONES.keys()), n-len(zones))])
    rng.shuffle(zones); themes=["Akses dan masa menunggu","Hubungan terapeutik","Kerahsiaan dan rasa selamat","Kesesuaian budaya/bahasa","Susulan kes","Kapasiti pegawai","Rujukan antara agensi","Tele-kaunseling","Pemulihan trauma","SOP dan dokumentasi"]
    rows=[]
    for i,z in enumerate(zones,1):
        rows.append({"interview_id":f"I{i:03d}","zone":z,"state":rng.choice(ZONES[z]),"source":rng.choice(["S1","S2","S3"],p=[.53,.29,.18]),"respondent_group":rng.choice(["Klien","PPsi","PPPsi","Warga JKM"],p=[.53,.20,.09,.18]),"CMO_context":rng.choice(["Luar bandar","Bandar","Beban kes tinggi","Kes krisis","Kumpulan rentan","Capaian digital rendah"]),"CMO_mechanism":rng.choice(["Kepercayaan","Rasa selamat","Pemerkasaan","Kefahaman matlamat sesi","Sokongan sosial","Privasi"]),"CMO_outcome":rng.choice(["Pengurangan tekanan","Peningkatan fungsi sosial","Kepuasan tinggi","Kekal hadir sesi","Rujukan berjaya","Keciciran rendah"]),"main_theme":rng.choice(themes),"sentiment":rng.choice(["Positif","Campuran","Negatif"],p=[.58,.30,.12]),"priority":rng.choice(["Tinggi","Sederhana","Rendah"],p=[.45,.38,.17]),"quote":"Petikan ilustrasi simulasi; akan diganti dengan transkrip sebenar selepas kerja lapangan."})
    return pd.DataFrame(rows)


def build_state_integrated(s1,s2,s3,s4):
    c=s1.groupby(["zone","state"],as_index=False).agg(S1_Client_Satisfaction=("CSQ8_Satisfaction","mean"),S1_Client_Outcome=("Client_Outcome_Index","mean"),S1_Access=("Access_Responsiveness","mean"),S1_Alliance=("WAI_Alliance","mean"),S1_N=("client_id","count"),Dropout_Rate=("dropout_status",lambda x:(x.eq("Ya").mean()*100)),T3_Followup=("followup_status",lambda x:(x.eq("Lengkap").mean()*100)))
    p=s2.groupby(["zone","state"],as_index=False).agg(S2_Staff_Readiness=("Staff_Readiness_Index","mean"),S2_SOP=("SOP_Compliance","mean"),S2_Workload=("Workload_Burden","mean"),S2_N=("staff_id","count"))
    w=s3.groupby(["zone","state"],as_index=False).agg(S3_Org_Support=("Org_Support_Index","mean"),S3_Referral=("Referral_Coordination","mean"),S3_N=("warga_id","count"))
    m=c.merge(p,on=["zone","state"],how="outer").merge(w,on=["zone","state"],how="outer").merge(s4,on=["zone","state"],how="left")
    for col in ["S1_Client_Satisfaction","S1_Client_Outcome","S2_Staff_Readiness","S3_Org_Support","Admin_Performance_Index"]:
        m[col]=m[col].fillna(m[col].mean())
    m["Overall_Integrated_Index"]=(0.40*((m["S1_Client_Satisfaction"]+m["S1_Client_Outcome"])/2)+0.25*m["S2_Staff_Readiness"]+0.15*m["S3_Org_Support"]+0.20*m["Admin_Performance_Index"]).round(1)
    m["Service_Quality"]=(0.35*m["S2_SOP"].fillna(m["S2_SOP"].mean())+0.30*m["S3_Referral"].fillna(m["S3_Referral"].mean())+0.35*s1.groupby("state")["Communication"].mean().reindex(m.state).values).round(1)
    m["Service_Mechanism"]=(0.40*m["S1_Access"]+0.35*m["S1_Alliance"]+0.25*s2.groupby("state")["Modality_Fit"].mean().reindex(m.state).fillna(s2.Modality_Fit.mean()).values).round(1)
    m["Organizational_Capacity"]=(0.45*m["S2_Staff_Readiness"]+0.25*m["S3_Org_Support"]+0.30*m["Admin_Performance_Index"]).round(1)
    return m.round(1)


def sem_tables():
    measurement=pd.DataFrame([["Organizational Capacity",.931,.949,.755,"Pass"],["Service Quality",.944,.959,.786,"Pass"],["Service Mechanism",.928,.946,.744,"Pass"],["Client Outcome",.918,.940,.724,"Pass"]],columns=["Construct","Cronbach Alpha","Composite Reliability","AVE","Decision"])
    paths=pd.DataFrame([["Organizational Capacity → Service Quality",.81,22.4,"<0.001","Supported"],["Service Quality → Service Mechanism",.76,18.9,"<0.001","Supported"],["Service Mechanism → Client Outcome",.73,16.8,"<0.001","Supported"],["Service Quality → Client Outcome",.24,5.2,"<0.001","Supported"],["Organizational Capacity → Client Outcome",.11,2.1,"0.035","Weak / indirect dominant"]],columns=["SEM Path","Beta","t-value","p-value","Decision"])
    r2=pd.DataFrame([["Service Quality",.66,"Substantial"],["Service Mechanism",.58,"Moderate-high"],["Client Outcome",.71,"Substantial"]],columns=["Endogenous Construct","R²","Interpretation"])
    htmt=pd.DataFrame(np.array([[1,.74,.69,.62],[.74,1,.77,.70],[.69,.77,1,.73],[.62,.70,.73,1]]),columns=["Capacity","Quality","Mechanism","Outcome"],index=["Capacity","Quality","Mechanism","Outcome"])
    mediation=pd.DataFrame([["Capacity → Quality → Outcome",.194,"<0.001","Partial mediation"],["Quality → Mechanism → Outcome",.555,"<0.001","Strong mediation"],["Capacity → Quality → Mechanism → Outcome",.449,"<0.001","Sequential mediation"]],columns=["Indirect Effect","Beta","p-value","Interpretation"])
    return measurement,paths,r2,htmt,mediation


def create_sem_diagram():
    nodes=pd.DataFrame({"node":["Organizational\nCapacity\nK4: S2+S3+S4","Service\nQuality\nK3: S1+S2+S3","Service\nMechanism\nK2: S1+S2","Client\nOutcome\nK1: S1+S4"],"x":[0,1,2,3],"y":[0,.35,0,.35]})
    edges=[(0,1,"β=.81"),(1,2,"β=.76"),(2,3,"β=.73"),(1,3,"β=.24")]
    fig=go.Figure()
    for a,b,label in edges:
        x0,y0=nodes.loc[a,["x","y"]]; x1,y1=nodes.loc[b,["x","y"]]
        fig.add_trace(go.Scatter(x=[x0,x1],y=[y0,y1],mode="lines",line=dict(width=5 if label!="β=.24" else 3,color="#FDE68A" if label!="β=.24" else "#38BDF8"),hoverinfo="skip",showlegend=False))
        fig.add_annotation(x=(x0+x1)/2,y=(y0+y1)/2+.12,text=label,showarrow=False,font=dict(size=16,color="#FDE68A"))
    fig.add_trace(go.Scatter(x=nodes.x,y=nodes.y,mode="markers+text",text=nodes.node,textposition="middle center",marker=dict(size=125,color="#0F766E",line=dict(color="#FDE68A",width=3)),textfont=dict(size=12,color="white",family="Inter"),showlegend=False))
    fig.update_xaxes(visible=False,range=[-.45,3.45]); fig.update_yaxes(visible=False,range=[-.45,.86])
    fig.update_layout(title="SEM Path Model: Capacity → Quality → Mechanism → Outcome",height=460,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=60,b=10))
    return fig


def make_template(s1,s2,s3,s4,idf):
    output=io.BytesIO()
    with pd.ExcelWriter(output,engine="openpyxl") as writer:
        s1.head(30).to_excel(writer,index=False,sheet_name="S1_clients")
        s2.head(30).to_excel(writer,index=False,sheet_name="S2_staff")
        s3.head(30).to_excel(writer,index=False,sheet_name="S3_warga")
        s4.to_excel(writer,index=False,sheet_name="S4_admin")
        idf.head(30).to_excel(writer,index=False,sheet_name="interview")
        RESULT_SOURCE_MAP.to_excel(writer,index=False,sheet_name="mapping_result")
        pd.DataFrame({"Note":["Simulation only. Replace with actual field data.","TOR target: S1≈450, S2≈75, S3≈75, qualitative=85, S4 administrative data is not respondent sample.","SEM coefficients in dashboard are illustrative until recalculated using AMOS/SmartPLS/R-lavaan."]}).to_excel(writer,index=False,sheet_name="README")
    return output.getvalue()

# Load data
s1_demo=simulate_s1_clients(); s2_demo=simulate_s2_staff(); s3_demo=simulate_s3_warga(); s4_demo=simulate_s4_admin(); idf_demo=simulate_interviews()
st.sidebar.markdown("## 🧠 JKM Intelligence")
st.sidebar.caption("Upload Excel only if sheets follow this app template.")
mode=st.sidebar.radio("Data source",["Simulation: TOR-aligned demo","Upload Excel template"],index=0)
if mode.startswith("Upload"):
    up=st.sidebar.file_uploader("Upload Excel",type=["xlsx"])
    if up:
        try:
            s1=pd.read_excel(up,sheet_name="S1_clients"); s2=pd.read_excel(up,sheet_name="S2_staff"); s3=pd.read_excel(up,sheet_name="S3_warga"); s4=pd.read_excel(up,sheet_name="S4_admin"); idf=pd.read_excel(up,sheet_name="interview")
        except Exception as e:
            st.error(f"Excel upload error: {e}. Using simulation data instead.")
            s1,s2,s3,s4,idf=s1_demo.copy(),s2_demo.copy(),s3_demo.copy(),s4_demo.copy(),idf_demo.copy()
    else:
        s1,s2,s3,s4,idf=s1_demo.copy(),s2_demo.copy(),s3_demo.copy(),s4_demo.copy(),idf_demo.copy()
else:
    s1,s2,s3,s4,idf=s1_demo.copy(),s2_demo.copy(),s3_demo.copy(),s4_demo.copy(),idf_demo.copy()

state_df=build_state_integrated(s1,s2,s3,s4)

# Executive values
overall=state_df["Overall_Integrated_Index"].mean()
client_sat=s1["CSQ8_Satisfaction"].mean()
outcome=s1["Client_Outcome_Index"].mean()
staff=s2["Staff_Readiness_Index"].mean()
org=s3["Org_Support_Index"].mean()
admin=s4["Admin_Performance_Index"].mean()
follow=s1["followup_status"].eq("Lengkap").mean()*100
dropout=s1["dropout_status"].eq("Ya").mean()*100

st.markdown("""
<div class='hero'>
  <span class='badge'>TOR-ALIGNED • S1–S4 TRIANGULATION • SEM-BASED • SIMULATION DEMO</span>
  <div class='hero-title'>Kajian Penilaian Keberkesanan <span class='gold'>Perkhidmatan Psikologi & Kaunseling JKM</span></div>
  <div class='hero-subtitle'>Dashboard ini membezakan sumber data S1 Klien, S2 PPsi/PPPsi, S3 Warga JKM dan S4 Data Pentadbiran. Overall index ialah integrasi S1–S4, manakala Client Satisfaction ialah skor khusus klien. Semua nilai demo ialah data simulasi.</div>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4,c5,c6=st.columns(6)
with c1: kpi("Overall Integrated Index",f"{overall:.1f}","S1+S2+S3+S4 • K1-K5")
with c2: kpi("Client Satisfaction",f"{client_sat:.1f}","S1 only • CASRS/CSQ-8")
with c3: kpi("Client Outcome",f"{outcome:.1f}","S1+S4 • T1/T2/T3")
with c4: kpi("Staff Readiness",f"{staff:.1f}","S2 • IPKJ")
with c5: kpi("Org/Admin Support",f"{((org+admin)/2):.1f}","S3+S4")
with c6: kpi("T3 Follow-up",f"{follow:.1f}%",f"Dropout {dropout:.1f}%")

tabs=st.tabs(["01 Executive", "02 Mapping K-S-Theory", "03 Negeri & Zon", "04 T1-T2-T3", "05 SEM", "06 Model Results", "07 RE-AIM + CMO", "08 Kualitatif", "09 Policy", "10 Scenario", "11 Data"])

with tabs[0]:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("Executive Dashboard: Overall Result Bukan Satu Questionnaire")
    st.info("Overall Integrated Index menggabungkan S1, S2, S3 dan S4. Client Satisfaction pula dipaparkan berasingan kerana ia khusus daripada klien.")
    a,b=st.columns([1,1])
    with a:
        source_score=pd.DataFrame({"Source":["S1 Client Satisfaction/Outcome","S2 Staff Readiness","S3 Organisational Support","S4 Administrative Performance"],"Score":[(client_sat+outcome)/2,staff,org,admin],"Weight":[40,25,15,20]})
        st.plotly_chart(fig_style(px.bar(source_score,x="Score",y="Source",orientation="h",text="Score",title="Overall Index Component by Sumber Data S1–S4")),use_container_width=True)
    with b:
        st.dataframe(WEIGHTS,use_container_width=True,hide_index=True)
        st.markdown(f"""
        <div class='card2'>
        <b>Formula demo:</b><br>
        Overall Integrated Index = 40% S1 + 25% S2 + 15% S3 + 20% S4<br><br>
        <b>S1</b> = Client Satisfaction + Client Outcome<br>
        <b>S2</b> = Staff Readiness / provider capacity<br>
        <b>S3</b> = Organisational Support<br>
        <b>S4</b> = Administrative Performance<br><br>
        Nilai ini boleh ditukar selepas persetujuan JKM / BPK.
        </div>
        """,unsafe_allow_html=True)
    st.plotly_chart(fig_style(px.bar(state_df.sort_values("Overall_Integrated_Index"),x="Overall_Integrated_Index",y="state",color="zone",orientation="h",text="Overall_Integrated_Index",title="Overall Integrated Index Mengikut Negeri"),500),use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[1]:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("Mapping: Result → Sumber Data → Questionnaire → Konstruk → Theory")
    st.dataframe(RESULT_SOURCE_MAP,use_container_width=True,hide_index=True)
    a,b=st.columns(2)
    with a:
        st.markdown("### S1–S4")
        st.dataframe(S_SOURCE_MAP,use_container_width=True,hide_index=True)
    with b:
        st.markdown("### K1–K5")
        st.dataframe(K_SOURCE_MAP,use_container_width=True,hide_index=True)
    st.markdown("""
    <div class='card2'>
    <b>Cara baca sistem:</b> Setiap angka di dashboard perlu ada jejak sumber. Contoh, Client Satisfaction datang daripada S1 Klien (CASRS/CSQ-8). Staff Readiness datang daripada S2 PPsi/PPPsi (IPKJ). Organisational Support datang daripada S3 Warga JKM. Administrative Performance datang daripada S4 rekod pentadbiran. Overall Integrated Index barulah menggabungkan S1 hingga S4.
    </div>
    """,unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[2]:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("Statistik Setiap Negeri dan Perbandingan Zon")
    metric=st.selectbox("Pilih indikator",["Overall_Integrated_Index","S1_Client_Satisfaction","S1_Client_Outcome","S2_Staff_Readiness","S3_Org_Support","Admin_Performance_Index","Service_Quality","Service_Mechanism","Organizational_Capacity","avg_waiting_days"],index=0)
    a,b=st.columns(2)
    with a:
        st.plotly_chart(fig_style(px.bar(state_df.sort_values(metric),x=metric,y="state",color="zone",orientation="h",text=metric,title=f"Perbandingan Negeri: {metric}"),500),use_container_width=True)
    with b:
        heat=state_df.pivot_table(index="state",columns="zone",values=metric,aggfunc="mean")
        st.plotly_chart(fig_style(px.imshow(heat,text_auto=True,aspect="auto",color_continuous_scale="Cividis",title=f"Heatmap Negeri × Zon: {metric}"),500),use_container_width=True)
    st.dataframe(state_df,use_container_width=True,hide_index=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[3]:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("Outcome Longitudinal T1, T2, T3 daripada S1 + S4")
    time_df=pd.DataFrame({"Instrument":["WHODAS"]*3+["Wellbeing"]*3+["PCL-5"]*3,"Time":["T1 Intake","T2 Closure","T3 Follow-up"]*3,"Score":[s1.WHODAS_T1.mean(),s1.WHODAS_T2.mean(),s1.WHODAS_T3.mean(),s1.Wellbeing_T1.mean(),s1.Wellbeing_T2.mean(),s1.Wellbeing_T3.mean(),s1.PCL5_T1.mean(),s1.PCL5_T2.mean(),s1.PCL5_T3.mean()]})
    st.plotly_chart(fig_style(px.line(time_df,x="Time",y="Score",color="Instrument",markers=True,title="Perubahan Outcome Klien T1 → T2 → T3")),use_container_width=True)
    change=s1.assign(WHODAS_Improvement=s1.WHODAS_T1-s1.WHODAS_T3,Wellbeing_Improvement=s1.Wellbeing_T3-s1.Wellbeing_T1,PCL5_Improvement=s1.PCL5_T1-s1.PCL5_T3).groupby("state",as_index=False)[["WHODAS_Improvement","Wellbeing_Improvement","PCL5_Improvement"]].mean().round(1)
    st.plotly_chart(fig_style(px.bar(change,x="state",y=["WHODAS_Improvement","Wellbeing_Improvement","PCL5_Improvement"],barmode="group",title="Improvement T1 ke T3 Mengikut Negeri"),500),use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[4]:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("SEM Result: Konstruk Bukan Daripada Satu Questionnaire")
    measurement,paths,r2,htmt,mediation=sem_tables()
    st.plotly_chart(create_sem_diagram(),use_container_width=True)
    a,b=st.columns(2)
    with a:
        st.markdown("**Measurement Model**"); st.dataframe(measurement,use_container_width=True,hide_index=True)
        st.markdown("**Structural Model**"); st.dataframe(paths,use_container_width=True,hide_index=True)
    with b:
        st.markdown("**HTMT**"); st.dataframe(htmt.round(2),use_container_width=True)
        st.markdown("**R²**"); st.dataframe(r2,use_container_width=True,hide_index=True)
        st.markdown("**Indirect Effects**"); st.dataframe(mediation,use_container_width=True,hide_index=True)
    st.caption("Nilai SEM ialah simulation/illustrative. Data sebenar perlu dianalisis semula dalam AMOS/SmartPLS/R-lavaan, kemudian result dipaparkan di app.")
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[5]:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("Model Results Lain: Correlation, Diagnostic Regression, CFA Summary")
    model_cols=["Overall_Integrated_Index","S1_Client_Satisfaction","S1_Client_Outcome","S2_Staff_Readiness","S3_Org_Support","Admin_Performance_Index","Service_Quality","Service_Mechanism","Organizational_Capacity"]
    corr=state_df[model_cols].corr().round(2)
    a,b=st.columns(2)
    with a: st.plotly_chart(fig_style(px.imshow(corr,text_auto=True,color_continuous_scale="Cividis",title="Correlation Diagnostic"),500),use_container_width=True)
    with b:
        cfa=pd.DataFrame([["K4 Capacity","S2/S3/S4",.78,.91,.949,.755,"Retain"],["K3 Quality","S1/S2/S3",.81,.93,.959,.786,"Retain"],["K2 Mechanism","S1/S2",.76,.90,.946,.744,"Retain"],["K1 Outcome","S1/S4",.74,.89,.940,.724,"Retain"]],columns=["Latent Construct","Source","Min Loading","Max Loading","CR","AVE","Decision"])
        st.dataframe(cfa,use_container_width=True,hide_index=True)
    group=state_df.groupby("zone",as_index=False).agg(Mean_Overall=("Overall_Integrated_Index","mean"),Mean_Satisfaction=("S1_Client_Satisfaction","mean"),Mean_Outcome=("S1_Client_Outcome","mean"),Mean_Capacity=("Organizational_Capacity","mean"))
    st.dataframe(group.round(1),use_container_width=True,hide_index=True)
    st.caption("Regression/correlation adalah diagnostic sokongan sahaja. Analisis utama kekal SEM.")
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[6]:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("RE-AIM + CMO")
    reaim=pd.DataFrame({"Dimension":["Reach","Effectiveness","Adoption","Implementation","Maintenance"],"Score":[min(100, len(s1)/450*100), outcome, staff, (state_df.Service_Quality.mean()+admin)/2, follow]})
    fig=go.Figure(go.Scatterpolar(r=reaim.Score,theta=reaim.Dimension,fill="toself",line=dict(color="#FDE68A",width=3),name="RE-AIM"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),title="RE-AIM Radar")
    a,b=st.columns([.9,1.1])
    with a: st.plotly_chart(fig_style(fig,500),use_container_width=True)
    with b:
        st.dataframe(reaim.round(1),use_container_width=True,hide_index=True)
        cmo=idf.groupby(["CMO_context","CMO_mechanism","CMO_outcome"],as_index=False).size().sort_values("size",ascending=False).head(12)
        st.dataframe(cmo,use_container_width=True,hide_index=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[7]:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("Qualitative Analytics: 85 Informants")
    a,b=st.columns(2)
    with a:
        theme=idf.main_theme.value_counts().reset_index(); theme.columns=["Theme","Count"]
        st.plotly_chart(fig_style(px.bar(theme,x="Count",y="Theme",orientation="h",title="Theme Frequency"),500),use_container_width=True)
    with b:
        sent=idf.groupby(["zone","sentiment"],as_index=False).size()
        st.plotly_chart(fig_style(px.bar(sent,x="zone",y="size",color="sentiment",barmode="group",title="Sentiment by Zone"),500),use_container_width=True)
    st.dataframe(idf,use_container_width=True,hide_index=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[8]:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("Policy Action Dashboard")
    recs=pd.DataFrame([["High","Capacity & workload","Tambah kapasiti PPsi/PPPsi atau susun semula triage bagi lokasi beban kes tinggi.","K4/S2+S3+S4"],["High","Service quality","Latihan trauma-informed care, therapeutic alliance dan standard dokumentasi kes.","K3/K2"],["High","Outcome monitoring","Mandatkan T1/T2/T3 bagi WHODAS, Wellbeing, WAI, CSQ-8 dan PCL-5 selektif.","K1/S1+S4"],["Medium","Digital follow-up","Automated reminder dan follow-up dashboard untuk T3.","RE-AIM Maintenance"],["Medium","Referral coordination","Standard rujukan antara JKM, KKM, PDRM, NGO dan komuniti.","K3/S3"]],columns=["Priority","Domain","Recommended Action","Evidence Logic"])
    st.dataframe(recs,use_container_width=True,hide_index=True)
    st.plotly_chart(fig_style(px.treemap(recs,path=["Priority","Domain"],title="Policy Priority Map"),500),use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[9]:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("Scenario Simulator")
    ppsi=st.slider("Tambahan kapasiti PPsi/PPPsi (%)",0,50,15)
    training=st.slider("Peningkatan latihan & supervision (%)",0,50,20)
    digital=st.slider("Digital triage & T3 follow-up adoption (%)",0,50,20)
    uplift=.18*ppsi+.22*training+.16*digital
    pred=min(100,overall+uplift/3)
    c1,c2,c3=st.columns(3)
    c1.metric("Current Overall",f"{overall:.1f}"); c2.metric("Projected Overall",f"{pred:.1f}",f"+{pred-overall:.1f}"); c3.metric("Projected Dropout",f"{max(2,dropout-(ppsi+digital)/12):.1f}%")
    sim=pd.DataFrame({"Scenario":["Current","After intervention"],"Overall Integrated Index":[overall,pred],"Dropout":[dropout,max(2,dropout-(ppsi+digital)/12)]})
    st.plotly_chart(fig_style(px.bar(sim,x="Scenario",y="Overall Integrated Index",text="Overall Integrated Index",title="Projected Overall Integrated Index")),use_container_width=True)
    st.caption("Scenario values are illustrative; final parameters must be calibrated using actual SEM coefficients and administrative records.")
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[10]:
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader("Data, Template and Download")
    st.download_button("Download Excel template",make_template(s1_demo,s2_demo,s3_demo,s4_demo,idf_demo),"JKM_SEM_TOR_Aligned_Template.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Download state integrated CSV",state_df.to_csv(index=False).encode("utf-8"),"state_integrated_result.csv","text/csv")
    st.markdown("### Integrated State Data")
    st.dataframe(state_df,use_container_width=True,hide_index=True)
    with st.expander("S1 Clients"):
        st.dataframe(s1,use_container_width=True,hide_index=True)
    with st.expander("S2 PPsi/PPPsi"):
        st.dataframe(s2,use_container_width=True,hide_index=True)
    with st.expander("S3 Warga JKM"):
        st.dataframe(s3,use_container_width=True,hide_index=True)
    with st.expander("S4 Administrative"):
        st.dataframe(s4,use_container_width=True,hide_index=True)
    st.markdown("</div>",unsafe_allow_html=True)

st.markdown("---")
st.caption("JKM Psycho-Counselling Impact Intelligence | Simulation only | Overall Integrated Index uses S1+S2+S3+S4 | SEM outputs illustrative until recalculated using actual field data")
