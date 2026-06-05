import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Sistem Analitik Keberkesanan Psikologi & Kaunseling JKM",
    page_icon="🇲🇾",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

ZON = {
    "Tengah": ["Kuala Lumpur", "Selangor"],
    "Utara": ["Pulau Pinang", "Kedah"],
    "Selatan": ["Johor", "Melaka"],
    "Timur": ["Kelantan", "Pahang"],
    "Sabah": ["Sabah"],
    "Sarawak": ["Sarawak"],
}
KESAN_NEGERI = {"Kuala Lumpur":4.5,"Selangor":3.3,"Pulau Pinang":2.4,"Kedah":1.2,"Johor":2.5,"Melaka":1.7,"Kelantan":-1.4,"Pahang":-0.7,"Sabah":-2.4,"Sarawak":-1.8}
NEGERI_KE_ZON = {s:z for z, senarai in ZON.items() for s in senarai}
INTERVENSI = ["Kaunseling Individu","Kaunseling Kelompok","Intervensi Krisis","Sokongan Sosial","Psikopendidikan","Rujukan Lanjut"]

PETA_K_SUMBER = pd.DataFrame([
    ["K1", "Outcome Klien / Keberkesanan", "S1 + S4", "Manual Instrumen Teras Hasil Klien JKM + CASRS-JKM + data pentadbiran", "WHODAS T1/T2/T3; WHOQOL/Kesejahteraan T1/T2/T3; WAI-SR; CSQ-8; PCL-5 selektif; status kes; rekod susulan", "Realist Evaluation; RE-AIM Keberkesanan; Bronfenbrenner", "Indeks Outcome Klien; peningkatan WHODAS; peningkatan kesejahteraan; penurunan PCL-5; susulan T3"],
    ["K2", "Mekanisme Perkhidmatan", "S1 + S2", "CASRS-JKM + IPKJ-JKM Instrumen A", "Akses fizikal/prosedur; komunikasi; responsif relasi; aliansi terapeutik; etika; susulan; kesesuaian modaliti intervensi", "Realist Evaluation (CMO); Pendekatan Berpusatkan Individu WHO", "Skor Mekanisme Perkhidmatan; responsif akses; aliansi terapeutik"],
    ["K3", "Kualiti Penyampaian", "S1 + S2 + S3", "CASRS-JKM + IPKJ-JKM Instrumen A/B + soal selidik warga JKM", "SOP; kompetensi; etika; kerahsiaan; komunikasi; kualiti intervensi; koordinasi rujukan", "Model Donabedian - Proses; Pendekatan Berpusatkan Individu WHO", "Skor Kualiti Penyampaian; pematuhan SOP; koordinasi rujukan"],
    ["K4", "Kapasiti Organisasi", "S2 + S3 + S4", "IPKJ-JKM Instrumen B + soal selidik warga JKM + data pentadbiran", "Perjawatan; beban kes; kemudahan; latihan; peruntukan; sistem rekod; burnout; nisbah pegawai-klien; tempoh menunggu", "Model Donabedian - Struktur; RE-AIM Pelaksanaan/Pengekalan", "Indeks Kapasiti Organisasi; beban kerja; tempoh menunggu; kesiapsiagaan susulan"],
    ["K5", "Penambahbaikan & Inovasi", "S1 + S2 + S3 + S4", "Soalan terbuka CASRS/IPKJ + temu bual + data pentadbiran", "Cadangan klien; cadangan pegawai; isu sistemik; peluang digital; tele-kaunseling; SOP digital; keperluan latihan dan sumber", "RE-AIM Pengekalan; Realist Evaluation; CMO", "Matriks cadangan dasar; pelan tindakan keutamaan; simulator senario"],
], columns=["K", "Konstruk", "Sumber Data", "Instrumen / Soal Selidik", "Item / Domain Digunakan", "Teori / Kerangka", "Result Dalam Sistem"])

PETA_S_SUMBER = pd.DataFrame([
    ["S1", "Klien", "CASRS-JKM + Manual Instrumen Teras Hasil Klien JKM", "≈450 kuantitatif + ≈45 kualitatif", "K1, K2, K3, K5", "Kepuasan klien; outcome klien; akses; responsif; aliansi terapeutik; peningkatan T1-T2-T3"],
    ["S2", "PPsi + PPPsi", "IPKJ-JKM Instrumen A & B", "≈75 kuantitatif + ≈25 kualitatif", "K2, K3, K4, K5", "Kejayaan intervensi; SOP; kompetensi; beban kerja; latihan; burnout; halangan perkhidmatan"],
    ["S3", "Warga JKM", "Soal selidik sokongan sistem + temu bual", "≈75 kuantitatif + ≈15 kualitatif", "K3, K4, K5", "Sokongan organisasi; koordinasi rujukan; kolaborasi dalaman; kesiapsiagaan sistem"],
    ["S4", "Data Pentadbiran JKM", "Rekod kes, statistik intervensi, laporan tahunan, data sumber manusia, rekod susulan", "Bukan responden", "K1, K4, K5", "Capaian perkhidmatan; trend intervensi; nisbah pegawai-klien; beban kes; kadar susulan; masa menunggu"],
], columns=["S", "Sumber", "Instrumen / Data", "Anggaran Sampel", "Konstruk Disokong", "Output Dashboard"])

PETA_RESULT_SUMBER = pd.DataFrame([
    ["Indeks Bersepadu Kepuasan & Keberkesanan", "CASRS-JKM + CSQ-8 + outcome longitudinal + IPKJ-JKM + warga JKM + data pentadbiran", "S1 + S2 + S3 + S4", "K1 + K2 + K3 + K4 + K5", "Realist Evaluation; Donabedian; RE-AIM; WHO Person-Centred", "Indeks komposit: S1 kepuasan/outcome klien, S2 kesiapsiagaan pelaksana, S3 sokongan organisasi, S4 prestasi pentadbiran. Ini bukan satu soal selidik sahaja."],
    ["Indeks Kepuasan Klien", "CASRS-JKM + CSQ-8", "S1", "K1 + K2", "WHO Person-Centred; Realist Evaluation", "Purata kepuasan klien terhadap akses, komunikasi, hubungan terapeutik, etika, susulan dan pengalaman perkhidmatan; ditukar kepada indeks 0-100."],
    ["Indeks Kesiapsiagaan Pegawai", "IPKJ-JKM Instrumen A & B", "S2", "K2 + K3 + K4", "Donabedian; RE-AIM Adoption/Implementation", "Purata kompetensi, keyakinan intervensi, pematuhan SOP, beban kerja, latihan, sokongan penyeliaan dan skor burnout terbalik."],
    ["Indeks Sokongan Organisasi", "Soal selidik warga JKM + temu bual", "S3", "K3 + K4 + K5", "Donabedian; RE-AIM Implementation", "Purata sokongan organisasi, koordinasi rujukan, integrasi dalaman, kesiapsiagaan sistem dan sokongan kepimpinan."],
    ["Indeks Prestasi Pentadbiran", "Rekod kes, statistik intervensi, data sumber manusia, rekod susulan", "S4", "K1 + K4 + K5", "RE-AIM Reach/Maintenance; Donabedian Structure", "Dikira daripada capaian, kadar susulan T3, masa menunggu terbalik, keciciran terbalik, nisbah pegawai-klien dan beban kes."],
    ["Indeks Outcome Klien", "WHODAS, WHOQOL/Kesejahteraan, WAI-SR, CSQ-8, PCL-5 selektif, rekod susulan", "S1 + S4", "K1", "RE-AIM Effectiveness; Realist CMO", "Gabungan perubahan T1-T2-T3: WHODAS menurun = baik, kesejahteraan meningkat = baik, PCL-5 menurun = baik, WAI/CSQ tinggi = baik, dan rekod susulan mengesahkan kesinambungan outcome."],
    ["Skor Mekanisme Perkhidmatan", "CASRS-JKM + IPKJ-JKM Instrumen A", "S1 + S2", "K2", "Realist Evaluation CMO; WHO Person-Centred", "Dikira daripada akses, prosedur, komunikasi, responsif relasi, aliansi terapeutik, susulan dan kesesuaian modaliti intervensi."],
    ["Skor Kualiti Penyampaian", "CASRS-JKM + IPKJ-JKM + soal selidik warga JKM", "S1 + S2 + S3", "K3", "Donabedian Process; WHO Person-Centred", "Dikira daripada SOP, kompetensi, etika, kerahsiaan, kualiti intervensi, komunikasi dan koordinasi rujukan."],
    ["Indeks Kapasiti Organisasi", "IPKJ-JKM Instrumen B + warga JKM + data pentadbiran", "S2 + S3 + S4", "K4", "Donabedian Structure; RE-AIM Implementation", "Dikira daripada beban kes, perjawatan, kemudahan, latihan, sistem rekod, peruntukan, burnout terbalik, nisbah pegawai-klien dan tempoh menunggu."],
    ["Pekali Laluan SEM", "Skor konstruk teragregat daripada CASRS, IPKJ, outcome longitudinal, warga JKM dan data pentadbiran", "S1 + S2 + S3 + S4", "K1-K4", "Realist CMO + Donabedian", "Menguji hubungan Kapasiti → Kualiti → Mekanisme → Outcome. Model ini triangulasi pelbagai sumber data, bukan satu set soal selidik."],
    ["Skor RE-AIM", "Data pentadbiran + outcome klien + IPKJ + warga JKM + temu bual", "S1 + S2 + S3 + S4", "K1-K5", "RE-AIM", "Capaian daripada rekod pentadbiran; keberkesanan daripada outcome klien; adopsi daripada PPsi/PPPsi/warga; pelaksanaan daripada IPKJ dan S4; pengekalan daripada T3, susulan dan kualitatif."],
    ["Dapatan CMO", "Temu bual, soalan terbuka CASRS/IPKJ dan data sokongan sistem", "S1 + S2 + S3", "K2 + K5", "Realist Evaluation", "Menjawab: dalam konteks apa, melalui mekanisme apa, outcome apa berlaku; digunakan untuk cadangan penambahbaikan."],
], columns=["Result Sistem", "Soal Selidik / Data Digunakan", "Sumber", "Konstruk", "Teori", "Bagaimana Sistem Kira / Jana Result"])

def norm(s, tinggi_baik=True):
    s = pd.Series(s).astype(float)
    if s.max() == s.min():
        return pd.Series(np.repeat(50, len(s)), index=s.index)
    v = (s - s.min())/(s.max()-s.min())*100
    return v if tinggi_baik else 100-v

@st.cache_data(show_spinner=False)
def simulasi_s1_klien(n=450, seed=2026):
    rng=np.random.default_rng(seed)
    zon=np.repeat(list(ZON.keys()), n//6)
    if len(zon)<n: zon=np.concatenate([zon,rng.choice(list(ZON.keys()), n-len(zon))])
    rng.shuffle(zon); rows=[]
    for i,z in enumerate(zon,1):
        negeri=rng.choice(ZON[z]); eff=KESAN_NEGERI[negeri]
        akses=np.clip(rng.normal(76+eff,9),35,98); komunikasi=np.clip(rng.normal(82+eff,7),45,99); relasi=np.clip(rng.normal(84+eff,7),45,99)
        etika=np.clip(rng.normal(86+eff,6),50,100); susulan=np.clip(rng.normal(72+eff,10),30,98); budaya=np.clip(rng.normal(79+eff,8),40,99)
        wai=np.clip(rng.normal(80+eff,7),40,100); csq=np.clip(.22*akses+.20*komunikasi+.22*relasi+.18*etika+.10*susulan+.08*budaya+rng.normal(0,3),0,100)
        wh1=np.clip(rng.normal(58-eff/2,10),25,90); wh2=np.clip(wh1-rng.normal(15+eff/4,6),8,80); wh3=np.clip(wh2+rng.normal(2.5,4),5,85)
        wb1=np.clip(rng.normal(50+eff/3,10),20,80); wb2=np.clip(wb1+rng.normal(18+eff/3,6),25,95); wb3=np.clip(wb2-rng.normal(2.5,4),20,95)
        pcl1=np.clip(rng.normal(45-eff/3,12),5,80); pcl2=np.clip(pcl1-rng.normal(12+eff/5,7),0,70); pcl3=np.clip(pcl2+rng.normal(1.8,5),0,75)
        outcome=np.clip(.30*norm([wh1-wh2, wh1-wh3]).iloc[0]+.30*norm([wb2-wb1, wb3-wb1]).iloc[0]+.20*csq+.12*wai+.08*norm([pcl1-pcl2, pcl1-pcl3]).iloc[0],0,100)
        rows.append({"id_klien":f"S1K{i:03d}","zon":z,"negeri":negeri,"sumber":"S1","kumpulan_responden":"Klien","kategori_klien":rng.choice(["Kanak-kanak","Warga emas","OKU","Mangsa keganasan rumah tangga","Keluarga/komuniti","Klien krisis","Remaja","Penerima bantuan"]),"jenis_intervensi":rng.choice(INTERVENSI),"Responsif_Akses":round(akses,1),"Komunikasi":round(komunikasi,1),"Hubungan_Terapeutik":round(relasi,1),"Etika_Kerahsiaan":round(etika,1),"Susulan_Koordinasi":round(susulan,1),"Responsif_Budaya":round(budaya,1),"Aliansi_WAI":round(wai,1),"Kepuasan_CSQ8":round(csq,1),"WHODAS_T1":round(wh1,1),"WHODAS_T2":round(wh2,1),"WHODAS_T3":round(wh3,1),"Kesejahteraan_T1":round(wb1,1),"Kesejahteraan_T2":round(wb2,1),"Kesejahteraan_T3":round(wb3,1),"PCL5_T1":round(pcl1,1),"PCL5_T2":round(pcl2,1),"PCL5_T3":round(pcl3,1),"Indeks_Outcome_Klien":round(outcome,1),"status_keciciran":"Ya" if rng.random()<.12+max(0,65-akses)/220 else "Tidak","status_susulan":"Lengkap" if rng.random()<.74 else "Tidak lengkap"})
    return pd.DataFrame(rows)

@st.cache_data(show_spinner=False)
def simulasi_s2_pegawai(n=75, seed=2027):
    rng=np.random.default_rng(seed); zon=np.repeat(list(ZON.keys()), n//6)
    if len(zon)<n: zon=np.concatenate([zon,rng.choice(list(ZON.keys()), n-len(zon))])
    rng.shuffle(zon); rows=[]
    for i,z in enumerate(zon,1):
        negeri=rng.choice(ZON[z]); eff=KESAN_NEGERI[negeri]
        kompetensi=np.clip(rng.normal(78+eff,8),40,100); sop=np.clip(rng.normal(74+eff,9),35,98); penyeliaan=np.clip(rng.normal(70+eff,10),30,98)
        beban=np.clip(rng.normal(63-eff,10),30,95); burnout=np.clip(rng.normal(55-eff,12),20,90); modaliti=np.clip(rng.normal(73+eff,9),35,98); halangan=np.clip(rng.normal(46-eff,12),10,90)
        siap=np.clip(.27*kompetensi+.22*sop+.18*penyeliaan+.17*modaliti+.08*(100-beban)+.08*(100-burnout),0,100)
        rows.append({"id_pegawai":f"S2P{i:03d}","zon":z,"negeri":negeri,"sumber":"S2","kumpulan_responden":rng.choice(["PPsi","PPPsi"],p=[.70,.30]),"Kompetensi":round(kompetensi,1),"Pematuhan_SOP":round(sop,1),"Penyeliaan_CPD":round(penyeliaan,1),"Beban_Kerja":round(beban,1),"Risiko_Burnout":round(burnout,1),"Kesesuaian_Modaliti":round(modaliti,1),"Halangan_Intervensi":round(halangan,1),"Indeks_Kesiapsiagaan_Pegawai":round(siap,1)})
    return pd.DataFrame(rows)

@st.cache_data(show_spinner=False)
def simulasi_s3_warga(n=75, seed=2028):
    rng=np.random.default_rng(seed); zon=np.repeat(list(ZON.keys()), n//6)
    if len(zon)<n: zon=np.concatenate([zon,rng.choice(list(ZON.keys()), n-len(zon))])
    rng.shuffle(zon); rows=[]
    for i,z in enumerate(zon,1):
        negeri=rng.choice(ZON[z]); eff=KESAN_NEGERI[negeri]
        org=np.clip(rng.normal(72+eff,9),35,98); rujukan=np.clip(rng.normal(68+eff,11),25,97); kepimpinan=np.clip(rng.normal(73+eff,9),35,99); sistem=np.clip(rng.normal(70+eff,10),30,98)
        sokongan=np.clip(.30*org+.28*rujukan+.22*kepimpinan+.20*sistem,0,100)
        rows.append({"id_warga":f"S3W{i:03d}","zon":z,"negeri":negeri,"sumber":"S3","kumpulan_responden":"Warga JKM","Sokongan_Organisasi":round(org,1),"Koordinasi_Rujukan":round(rujukan,1),"Sokongan_Kepimpinan":round(kepimpinan,1),"Kesiapsiagaan_Sistem":round(sistem,1),"Indeks_Sokongan_Organisasi":round(sokongan,1)})
    return pd.DataFrame(rows)

@st.cache_data(show_spinner=False)
def simulasi_s4_pentadbiran(seed=2029):
    rng=np.random.default_rng(seed); rows=[]
    for negeri, eff in KESAN_NEGERI.items():
        z=NEGERI_KE_ZON[negeri]
        intervensi=int(np.clip(rng.normal(26000+eff*900,4500),6500,45000)); pegawai=int(np.clip(rng.normal(38+eff/1.8,7),12,65))
        tunggu=np.clip(rng.normal(9-eff/3,3),2,24); susulan=np.clip(rng.normal(76+eff,8),40,96); cicir=np.clip(rng.normal(13-eff/3,4),3,30); nisbah=intervensi/max(pegawai,1)
        rows.append({"negeri":negeri,"zon":z,"sumber":"S4","intervensi_2025":intervensi,"bilangan_pegawai":pegawai,"nisbah_pegawai_klien":round(nisbah,1),"purata_hari_menunggu":round(tunggu,1),"kadar_susulan_pentadbiran":round(susulan,1),"kadar_keciciran_pentadbiran":round(cicir,1)})
    df=pd.DataFrame(rows)
    df["Indeks_Prestasi_Pentadbiran"]=(.30*norm(df["intervensi_2025"],True)+.25*df["kadar_susulan_pentadbiran"]+.20*norm(df["purata_hari_menunggu"],False)+.15*norm(df["kadar_keciciran_pentadbiran"],False)+.10*norm(df["nisbah_pegawai_klien"],False)).round(1)
    return df

@st.cache_data(show_spinner=False)
def simulasi_temubual(n=85, seed=2030):
    rng=np.random.default_rng(seed); zon=np.repeat(list(ZON.keys()), n//6)
    if len(zon)<n: zon=np.concatenate([zon,rng.choice(list(ZON.keys()), n-len(zon))])
    rng.shuffle(zon); tema=["Akses dan masa menunggu","Hubungan terapeutik","Kerahsiaan dan rasa selamat","Kesesuaian budaya/bahasa","Susulan kes","Kapasiti pegawai","Rujukan antara agensi","Tele-kaunseling","Pemulihan trauma","SOP dan dokumentasi"]
    rows=[]
    for i,z in enumerate(zon,1):
        rows.append({"id_temubual":f"I{i:03d}","zon":z,"negeri":rng.choice(ZON[z]),"sumber":rng.choice(["S1","S2","S3"],p=[.53,.29,.18]),"kumpulan_responden":rng.choice(["Klien","PPsi","PPPsi","Warga JKM"],p=[.53,.20,.09,.18]),"Konteks_CMO":rng.choice(["Luar bandar","Bandar","Beban kes tinggi","Kes krisis","Kumpulan rentan","Capaian digital rendah"]),"Mekanisme_CMO":rng.choice(["Kepercayaan","Rasa selamat","Pemerkasaan","Kefahaman matlamat sesi","Sokongan sosial","Privasi"]),"Outcome_CMO":rng.choice(["Pengurangan tekanan","Peningkatan fungsi sosial","Kepuasan tinggi","Kekal hadir sesi","Rujukan berjaya","Keciciran rendah"]),"tema_utama":rng.choice(tema),"sentimen":rng.choice(["Positif","Campuran","Negatif"],p=[.58,.30,.12]),"keutamaan":rng.choice(["Tinggi","Sederhana","Rendah"],p=[.45,.38,.17]),"petikan":"Petikan ilustrasi simulasi; akan diganti dengan transkrip sebenar selepas kerja lapangan."})
    return pd.DataFrame(rows)

def bina_integrasi_negeri(s1,s2,s3,s4):
    c=s1.groupby(["zon","negeri"],as_index=False).agg(S1_Kepuasan_Klien=("Kepuasan_CSQ8","mean"),S1_Outcome_Klien=("Indeks_Outcome_Klien","mean"),S1_Akses=("Responsif_Akses","mean"),S1_Aliansi=("Aliansi_WAI","mean"),N_S1=("id_klien","count"),Kadar_Keciciran=("status_keciciran",lambda x:(x.eq("Ya").mean()*100)),Susulan_T3=("status_susulan",lambda x:(x.eq("Lengkap").mean()*100)))
    p=s2.groupby(["zon","negeri"],as_index=False).agg(S2_Kesiapsiagaan_Pegawai=("Indeks_Kesiapsiagaan_Pegawai","mean"),S2_SOP=("Pematuhan_SOP","mean"),S2_Beban_Kerja=("Beban_Kerja","mean"),N_S2=("id_pegawai","count"))
    w=s3.groupby(["zon","negeri"],as_index=False).agg(S3_Sokongan_Organisasi=("Indeks_Sokongan_Organisasi","mean"),S3_Rujukan=("Koordinasi_Rujukan","mean"),N_S3=("id_warga","count"))
    m=c.merge(p,on=["zon","negeri"],how="outer").merge(w,on=["zon","negeri"],how="outer").merge(s4,on=["zon","negeri"],how="left")
    for col in ["S1_Kepuasan_Klien","S1_Outcome_Klien","S2_Kesiapsiagaan_Pegawai","S3_Sokongan_Organisasi","Indeks_Prestasi_Pentadbiran"]:
        m[col]=m[col].fillna(m[col].mean())
    komunikasi=s1.groupby("negeri")["Komunikasi"].mean()
    modaliti=s2.groupby("negeri")["Kesesuaian_Modaliti"].mean()
    m["Indeks_Bersepadu"]=(0.40*((m["S1_Kepuasan_Klien"]+m["S1_Outcome_Klien"])/2)+0.25*m["S2_Kesiapsiagaan_Pegawai"]+0.15*m["S3_Sokongan_Organisasi"]+0.20*m["Indeks_Prestasi_Pentadbiran"]).round(1)
    m["Kualiti_Penyampaian"]=(0.35*m["S2_SOP"].fillna(m["S2_SOP"].mean())+0.30*m["S3_Rujukan"].fillna(m["S3_Rujukan"].mean())+0.35*komunikasi.reindex(m.negeri).values).round(1)
    m["Mekanisme_Perkhidmatan"]=(0.40*m["S1_Akses"]+0.35*m["S1_Aliansi"]+0.25*modaliti.reindex(m.negeri).fillna(s2.Kesesuaian_Modaliti.mean()).values).round(1)
    m["Kapasiti_Organisasi"]=(0.45*m["S2_Kesiapsiagaan_Pegawai"]+0.25*m["S3_Sokongan_Organisasi"]+0.30*m["Indeks_Prestasi_Pentadbiran"]).round(1)
    return m.round(1)

def jadual_sem():
    ukuran=pd.DataFrame([["Kapasiti Organisasi",.931,.949,.755,"Lulus"],["Kualiti Penyampaian",.944,.959,.786,"Lulus"],["Mekanisme Perkhidmatan",.928,.946,.744,"Lulus"],["Outcome Klien",.918,.940,.724,"Lulus"]],columns=["Konstruk","Alpha Cronbach","Kebolehpercayaan Komposit","AVE","Keputusan"])
    laluan=pd.DataFrame([["Kapasiti Organisasi → Kualiti Penyampaian",.81,22.4,"<0.001","Disokong"],["Kualiti Penyampaian → Mekanisme Perkhidmatan",.76,18.9,"<0.001","Disokong"],["Mekanisme Perkhidmatan → Outcome Klien",.73,16.8,"<0.001","Disokong"],["Kualiti Penyampaian → Outcome Klien",.24,5.2,"<0.001","Disokong"],["Kapasiti Organisasi → Outcome Klien",.11,2.1,"0.035","Lemah / kesan tidak langsung dominan"]],columns=["Laluan SEM","Beta","Nilai-t","Nilai-p","Keputusan"])
    r2=pd.DataFrame([["Kualiti Penyampaian",.66,"Substantial"],["Mekanisme Perkhidmatan",.58,"Sederhana tinggi"],["Outcome Klien",.71,"Substantial"]],columns=["Konstruk Endogen","R²","Interpretasi"])
    htmt=pd.DataFrame(np.array([[1,.74,.69,.62],[.74,1,.77,.70],[.69,.77,1,.73],[.62,.70,.73,1]]),columns=["Kapasiti","Kualiti","Mekanisme","Outcome"],index=["Kapasiti","Kualiti","Mekanisme","Outcome"])
    mediasi=pd.DataFrame([["Kapasiti → Kualiti → Outcome",.194,"<0.001","Mediasi separa"],["Kualiti → Mekanisme → Outcome",.555,"<0.001","Mediasi kuat"],["Kapasiti → Kualiti → Mekanisme → Outcome",.449,"<0.001","Mediasi berjujukan"]],columns=["Kesan Tidak Langsung","Beta","Nilai-p","Interpretasi"])
    return ukuran,laluan,r2,htmt,mediasi

def rajah_sem():
    nodes=pd.DataFrame({"node":["Kapasiti\nOrganisasi\nK4: S2+S3+S4","Kualiti\nPenyampaian\nK3: S1+S2+S3","Mekanisme\nPerkhidmatan\nK2: S1+S2","Outcome\nKlien\nK1: S1+S4"],"x":[0,1,2,3],"y":[0,.35,0,.35]})
    edges=[(0,1,"β=.81"),(1,2,"β=.76"),(2,3,"β=.73"),(1,3,"β=.24")]
    fig=go.Figure()
    for a,b,label in edges:
        x0,y0=nodes.loc[a,["x","y"]]; x1,y1=nodes.loc[b,["x","y"]]
        fig.add_trace(go.Scatter(x=[x0,x1],y=[y0,y1],mode="lines",line=dict(width=5 if label!="β=.24" else 3,color="#FDE68A" if label!="β=.24" else "#38BDF8"),hoverinfo="skip",showlegend=False))
        fig.add_annotation(x=(x0+x1)/2,y=(y0+y1)/2+.12,text=label,showarrow=False,font=dict(size=16,color="#FDE68A"))
    fig.add_trace(go.Scatter(x=nodes.x,y=nodes.y,mode="markers+text",text=nodes.node,textposition="middle center",marker=dict(size=125,color="#0F766E",line=dict(color="#FDE68A",width=3)),textfont=dict(size=12,color="white",family="Inter"),showlegend=False))
    fig.update_xaxes(visible=False,range=[-.45,3.45]); fig.update_yaxes(visible=False,range=[-.45,.86])
    fig.update_layout(title="Model Laluan SEM: Kapasiti → Kualiti → Mekanisme → Outcome",height=460,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",margin=dict(l=10,r=10,t=60,b=10),font=dict(color="#F8FAFC"))
    return fig

def kad(label,value,note=""):
    st.markdown(f'<div class="kpi"><div class="klabel">{label}</div><div class="kvalue">{value}</div><div class="knote">{note}</div></div>',unsafe_allow_html=True)

def seksyen(title, body=""):
    st.markdown(f'<div class="card"><h3>{title}</h3><div class="small">{body}</div></div>', unsafe_allow_html=True)

def filter_df(df, zon_pilih, negeri_pilih):
    out=df.copy()
    if zon_pilih != "Semua Zon" and "zon" in out.columns: out=out[out["zon"].eq(zon_pilih)]
    if negeri_pilih != "Semua Negeri" and "negeri" in out.columns: out=out[out["negeri"].eq(negeri_pilih)]
    return out

def safe_mean(df,col):
    return float(df[col].mean()) if len(df) and col in df.columns else 0.0

def safe_count(df,col=None):
    return int(len(df)) if col is None or col not in df.columns else int(df[col].count())

s1=simulasi_s1_klien(); s2=simulasi_s2_pegawai(); s3=simulasi_s3_warga(); s4=simulasi_s4_pentadbiran(); ql=simulasi_temubual(); integrasi=bina_integrasi_negeri(s1,s2,s3,s4)

st.markdown("""
<div class="hero">
<span class="badge">SISTEM DEMONSTRASI DATA SIMULASI • SELARAS TOR JKM</span>
<div class="hero-title">Sistem Analitik Keberkesanan <span class="gold">Perkhidmatan Psikologi dan Kaunseling JKM</span></div>
<div class="hero-subtitle">Dashboard ini menunjukkan bagaimana hasil kajian akan dijana daripada S1 Klien, S2 PPsi/PPPsi, S3 Warga JKM dan S4 Data Pentadbiran. Semua analisis boleh ditapis mengikut semua negeri, semua zon, zon tertentu atau negeri tertentu.</div>
</div>
""", unsafe_allow_html=True)

c1,c2,c3=st.columns([1,1,1])
with c1:
    zon_pilih=st.selectbox("Pilih Zon Analisis", ["Semua Zon"]+list(ZON.keys()))
with c2:
    negeri_ops=["Semua Negeri"] + (ZON[zon_pilih] if zon_pilih!="Semua Zon" else list(NEGERI_KE_ZON.keys()))
    negeri_pilih=st.selectbox("Pilih Negeri Analisis", negeri_ops)
with c3:
    st.info("Semua tab di bawah menggunakan pilihan zon/negeri ini.")

fs1,fs2,fs3,fs4,fql,fi = [filter_df(x,zon_pilih,negeri_pilih) for x in [s1,s2,s3,s4,ql,integrasi]]
if fi.empty:
    st.error("Tiada data untuk pilihan ini."); st.stop()

tab = st.tabs(["Ringkasan Eksekutif", "Negeri & Zon", "T1-T2-T3", "SEM", "RE-AIM", "CMO & Kualitatif", "Pemetaan K-S-Teori", "Simulasi Dasar", "Data & Muat Turun"])

with tab[0]:
    st.subheader("Ringkasan Eksekutif Mengikut Pilihan Analisis")
    a,b,c,d,e=st.columns(5)
    with a: kad("Indeks Bersepadu", f"{safe_mean(fi,'Indeks_Bersepadu'):.1f}%", "S1+S2+S3+S4")
    with b: kad("Kepuasan Klien", f"{safe_mean(fs1,'Kepuasan_CSQ8'):.1f}%", "S1: CASRS + CSQ-8")
    with c: kad("Outcome Klien", f"{safe_mean(fs1,'Indeks_Outcome_Klien'):.1f}%", "S1+S4: T1-T2-T3")
    with d: kad("Kualiti Penyampaian", f"{safe_mean(fi,'Kualiti_Penyampaian'):.1f}%", "K3: S1+S2+S3")
    with e: kad("Kapasiti Organisasi", f"{safe_mean(fi,'Kapasiti_Organisasi'):.1f}%", "K4: S2+S3+S4")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"""
    **Naratif sistem:** Untuk pilihan **{zon_pilih} / {negeri_pilih}**, Indeks Bersepadu dijana melalui integrasi empat sumber: **S1 Klien**, **S2 PPsi/PPPsi**, **S3 Warga JKM** dan **S4 Data Pentadbiran**. Kepuasan klien sahaja datang daripada S1, tetapi keputusan keseluruhan keberkesanan tidak bergantung kepada satu soal selidik sahaja.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        ring=fi[["S1_Kepuasan_Klien","S1_Outcome_Klien","S2_Kesiapsiagaan_Pegawai","S3_Sokongan_Organisasi","Indeks_Prestasi_Pentadbiran"]].mean().reset_index()
        ring.columns=["Komponen","Skor"]
        ring["Komponen"]=ring["Komponen"].replace({"S1_Kepuasan_Klien":"S1 Kepuasan Klien","S1_Outcome_Klien":"S1 Outcome Klien","S2_Kesiapsiagaan_Pegawai":"S2 Kesiapsiagaan Pegawai","S3_Sokongan_Organisasi":"S3 Sokongan Organisasi","Indeks_Prestasi_Pentadbiran":"S4 Prestasi Pentadbiran"})
        st.plotly_chart(px.bar(ring,x="Komponen",y="Skor",title="Komponen Indeks Bersepadu",text_auto='.1f'),use_container_width=True)
    with col2:
        radar=pd.DataFrame({"Dimensi":["Outcome Klien","Mekanisme","Kualiti","Kapasiti","Prestasi Pentadbiran"],"Skor":[safe_mean(fs1,'Indeks_Outcome_Klien'),safe_mean(fi,'Mekanisme_Perkhidmatan'),safe_mean(fi,'Kualiti_Penyampaian'),safe_mean(fi,'Kapasiti_Organisasi'),safe_mean(fi,'Indeks_Prestasi_Pentadbiran')]})
        fig=go.Figure(go.Scatterpolar(r=radar["Skor"],theta=radar["Dimensi"],fill="toself"))
        fig.update_layout(title="Profil Dimensi Utama",polar=dict(radialaxis=dict(visible=True,range=[0,100])),paper_bgcolor="rgba(0,0,0,0)",font=dict(color="#F8FAFC"))
        st.plotly_chart(fig,use_container_width=True)

with tab[1]:
    st.subheader("Perbandingan Negeri dan Zon")
    st.caption("Analisis ini juga ikut pilihan filter di atas. Jika pilih semua, sistem paparkan semua negeri/zon. Jika pilih satu negeri, paparan menjadi ringkasan negeri tersebut.")
    st.dataframe(fi.sort_values("Indeks_Bersepadu",ascending=False),use_container_width=True)
    col1,col2=st.columns(2)
    with col1:
        st.plotly_chart(px.bar(fi.sort_values("Indeks_Bersepadu",ascending=False),x="negeri",y="Indeks_Bersepadu",color="zon",title="Indeks Bersepadu Mengikut Negeri",text_auto='.1f'),use_container_width=True)
    with col2:
        zon_sum=fi.groupby("zon",as_index=False).agg(Indeks_Bersepadu=("Indeks_Bersepadu","mean"),Kepuasan_Klien=("S1_Kepuasan_Klien","mean"),Kapasiti=("Kapasiti_Organisasi","mean"))
        st.plotly_chart(px.bar(zon_sum,x="zon",y=["Indeks_Bersepadu","Kepuasan_Klien","Kapasiti"],barmode="group",title="Perbandingan Zon"),use_container_width=True)
    st.plotly_chart(px.scatter(fi,x="Kapasiti_Organisasi",y="S1_Outcome_Klien",size="intervensi_2025",color="zon",hover_name="negeri",title="Hubungan Kapasiti Organisasi dan Outcome Klien Mengikut Negeri"),use_container_width=True)

with tab[2]:
    st.subheader("Analisis Longitudinal T1-T2-T3")
    st.caption("Sumber utama: S1 Klien melalui Manual Instrumen Teras Hasil Klien JKM, disokong S4 rekod susulan.")
    t=pd.DataFrame({"Titik Masa":["T1 Asas","T2 Penutupan","T3 Susulan"],"WHODAS (lebih rendah lebih baik)":[safe_mean(fs1,'WHODAS_T1'),safe_mean(fs1,'WHODAS_T2'),safe_mean(fs1,'WHODAS_T3')],"Kesejahteraan (lebih tinggi lebih baik)":[safe_mean(fs1,'Kesejahteraan_T1'),safe_mean(fs1,'Kesejahteraan_T2'),safe_mean(fs1,'Kesejahteraan_T3')],"PCL-5 selektif (lebih rendah lebih baik)":[safe_mean(fs1,'PCL5_T1'),safe_mean(fs1,'PCL5_T2'),safe_mean(fs1,'PCL5_T3')]})
    col1,col2=st.columns(2)
    with col1: st.plotly_chart(px.line(t,x="Titik Masa",y=["WHODAS (lebih rendah lebih baik)","PCL-5 selektif (lebih rendah lebih baik)"],markers=True,title="Perubahan Risiko / Kesukaran Klien"),use_container_width=True)
    with col2: st.plotly_chart(px.line(t,x="Titik Masa",y="Kesejahteraan (lebih tinggi lebih baik)",markers=True,title="Perubahan Kesejahteraan Klien"),use_container_width=True)
    st.dataframe(t,use_container_width=True)

with tab[3]:
    st.subheader("Analisis SEM Mengikut Pilihan Analisis")
    st.caption("SEM menggunakan skor konstruk teragregat K1-K4 daripada S1, S2, S3 dan S4. Untuk demonstrasi, nilai pekali adalah simulasi; selepas data sebenar diterima, sistem perlu mengira semula model.")
    st.plotly_chart(rajah_sem(),use_container_width=True)
    ukuran,laluan,r2,htmt,mediasi=jadual_sem()
    st.write("Model Pengukuran") ; st.dataframe(ukuran,use_container_width=True)
    st.write("Model Struktur") ; st.dataframe(laluan,use_container_width=True)
    c1,c2=st.columns(2)
    with c1: st.dataframe(r2,use_container_width=True)
    with c2: st.dataframe(mediasi,use_container_width=True)
    st.write("HTMT") ; st.dataframe(htmt,use_container_width=True)
    sem_local=fi[["negeri","zon","Kapasiti_Organisasi","Kualiti_Penyampaian","Mekanisme_Perkhidmatan","S1_Outcome_Klien"]].copy()
    st.write("Skor Konstruk Negeri/Zon Untuk SEM") ; st.dataframe(sem_local,use_container_width=True)

with tab[4]:
    st.subheader("RE-AIM Mengikut Pilihan Analisis")
    reach=safe_mean(fi,'Indeks_Prestasi_Pentadbiran')
    effectiveness=safe_mean(fs1,'Indeks_Outcome_Klien')
    adoption=safe_mean(fs2,'Indeks_Kesiapsiagaan_Pegawai')
    implementation=(safe_mean(fi,'Kualiti_Penyampaian')+safe_mean(fi,'Kapasiti_Organisasi'))/2
    maintenance=(safe_mean(fs1,'status_susulan') if False else safe_mean(fi,'Susulan_T3'))
    reaim=pd.DataFrame({"Domain RE-AIM":["Capaian (Reach)","Keberkesanan (Effectiveness)","Adopsi (Adoption)","Pelaksanaan (Implementation)","Pengekalan (Maintenance)"],"Skor":[reach,effectiveness,adoption,implementation,maintenance],"Sumber":["S4","S1+S4","S2+S3","S2+S3+S4","S1+S4+Kualitatif"]})
    st.plotly_chart(px.bar(reaim,x="Domain RE-AIM",y="Skor",color="Sumber",title="Skor RE-AIM",text_auto='.1f'),use_container_width=True)
    st.dataframe(reaim,use_container_width=True)

with tab[5]:
    st.subheader("CMO dan Analisis Kualitatif")
    col1,col2=st.columns(2)
    with col1:
        tema=fql.groupby("tema_utama",as_index=False).size().sort_values("size",ascending=False)
        st.plotly_chart(px.bar(tema,x="size",y="tema_utama",orientation="h",title="Tema Utama Temu Bual / Soalan Terbuka"),use_container_width=True)
    with col2:
        sent=fql.groupby("sentimen",as_index=False).size()
        st.plotly_chart(px.pie(sent,names="sentimen",values="size",title="Sentimen Kualitatif"),use_container_width=True)
    cmo=fql.groupby(["Konteks_CMO","Mekanisme_CMO","Outcome_CMO"],as_index=False).size().sort_values("size",ascending=False)
    st.write("Dapatan CMO: Konteks → Mekanisme → Outcome")
    st.dataframe(cmo,use_container_width=True)
    st.write("Data Temu Bual Simulasi")
    st.dataframe(fql,use_container_width=True)

with tab[6]:
    st.subheader("Pemetaan Result → Soal Selidik → Sumber → Konstruk → Teori")
    st.markdown("Bahagian ini menerangkan bagaimana setiap result dalam sistem dijana. Ini penting supaya panel faham bahawa dashboard tidak bergantung kepada satu set soal selidik sahaja.")
    st.write("Pemetaan Konstruk K1-K5") ; st.dataframe(PETA_K_SUMBER,use_container_width=True)
    st.write("Pemetaan Sumber Data S1-S4") ; st.dataframe(PETA_S_SUMBER,use_container_width=True)
    st.write("Pemetaan Result Sistem") ; st.dataframe(PETA_RESULT_SUMBER,use_container_width=True)

with tab[7]:
    st.subheader("Simulator Senario Dasar")
    st.caption("Simulator ini boleh dijalankan untuk semua negeri atau negeri tertentu mengikut pilihan filter di atas.")
    tambah_pegawai=st.slider("Pertambahan Pegawai Psikologi / PPPsi (%)",0,50,15)
    tambah_latihan=st.slider("Pertambahan Latihan / CPD (%)",0,50,20)
    tambah_digital=st.slider("Pengukuhan Sistem Digital / Tele-kaunseling (%)",0,50,15)
    asas=safe_mean(fi,'Indeks_Bersepadu')
    impak=min(18,0.12*tambah_pegawai+0.10*tambah_latihan+0.08*tambah_digital)
    baru=min(100,asas+impak)
    a,b,c=st.columns(3)
    with a: kad("Indeks Semasa", f"{asas:.1f}%", "Berdasarkan pilihan filter")
    with b: kad("Impak Simulasi", f"+{impak:.1f}%", "Anggaran dasar")
    with c: kad("Indeks Selepas Intervensi", f"{baru:.1f}%", "Simulasi sahaja")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"Cadangan sistem: sekiranya pegawai meningkat **{tambah_pegawai}%**, latihan meningkat **{tambah_latihan}%** dan sistem digital meningkat **{tambah_digital}%**, indeks bersepadu dijangka meningkat daripada **{asas:.1f}%** kepada **{baru:.1f}%**.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab[8]:
    st.subheader("Data Simulasi dan Muat Turun")
    st.caption("Semua data di bawah ialah data simulasi untuk demonstrasi tender. Data sebenar perlu dimuat naik selepas kerja lapangan.")
    pilih=st.selectbox("Pilih set data",["S1 Klien","S2 Pegawai","S3 Warga JKM","S4 Pentadbiran","Integrasi Negeri","Kualitatif"])
    data_map={"S1 Klien":fs1,"S2 Pegawai":fs2,"S3 Warga JKM":fs3,"S4 Pentadbiran":fs4,"Integrasi Negeri":fi,"Kualitatif":fql}
    dd=data_map[pilih]
    st.dataframe(dd,use_container_width=True)
    st.download_button("Muat turun CSV", dd.to_csv(index=False).encode('utf-8-sig'), file_name=f"{pilih.replace(' ','_')}.csv", mime="text/csv")

st.markdown('<hr><div class="small">Nota: Sistem ini menggunakan data simulasi untuk demonstrasi. Semua keputusan, pekali SEM, RE-AIM, CMO dan simulasi dasar perlu dikira semula menggunakan data sebenar JKM selepas pengumpulan data lapangan.</div>', unsafe_allow_html=True)
