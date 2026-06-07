import io, re, math
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="JKM PsyCounsel Analytics", page_icon="🇲🇾", layout="wide", initial_sidebar_state="collapsed")

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"]{font-family:'Inter',sans-serif;}
#MainMenu, footer, header, [data-testid="stSidebar"], [data-testid="collapsedControl"]{display:none!important;}
.stApp{background:
 radial-gradient(circle at 8% 8%, rgba(255,214,102,.30) 0, transparent 26%),
 radial-gradient(circle at 92% 0%, rgba(34,211,238,.20) 0, transparent 30%),
 linear-gradient(135deg,#050816 0%,#081a35 42%,#111827 100%); color:#f8fafc;}
.block-container{padding-top:1.1rem;max-width:1580px;}
h1,h2,h3{color:#fff!important;letter-spacing:-.035em}.stMarkdown,p,li,label{color:#dbeafe!important;}
.hero{padding:34px;border-radius:34px;background:linear-gradient(135deg,rgba(255,214,102,.24),rgba(20,184,166,.11)),linear-gradient(135deg,#07152f,#102a55 55%,#073b4c);border:1px solid rgba(253,230,138,.44);box-shadow:0 28px 90px rgba(0,0,0,.45);margin-bottom:18px;position:relative;overflow:hidden}.hero:after{content:"";position:absolute;right:-80px;top:-80px;width:280px;height:280px;border-radius:999px;background:rgba(255,255,255,.08);filter:blur(2px)}
.badge{display:inline-block;padding:8px 14px;border-radius:999px;background:rgba(253,230,138,.18);border:1px solid rgba(253,230,138,.45);color:#fde68a!important;font-weight:900;font-size:12px;letter-spacing:.09em}.hero-title{font-size:43px;line-height:1.05;font-weight:900;margin-top:14px}.gold{background:linear-gradient(90deg,#fff7c2,#facc15,#c5a017);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.hero-subtitle{font-size:16px;max-width:1120px;color:#cbd5e1!important;margin-top:10px}
.navbtn button{height:68px;border-radius:22px!important;background:linear-gradient(135deg,rgba(15,23,42,.96),rgba(30,41,59,.70))!important;border:1px solid rgba(253,230,138,.26)!important;color:#fff!important;font-weight:900!important;box-shadow:0 15px 38px rgba(0,0,0,.26)}.navbtn button:hover{border-color:#fde68a!important;transform:translateY(-1px)}
.card{padding:22px;border-radius:27px;background:rgba(15,23,42,.76);border:1px solid rgba(148,163,184,.22);box-shadow:0 20px 58px rgba(0,0,0,.30);margin-bottom:18px}.glass{padding:16px;border-radius:22px;background:rgba(30,41,59,.52);border:1px solid rgba(148,163,184,.18);margin-bottom:14px}.kpi{padding:19px;border-radius:24px;background:linear-gradient(180deg,rgba(15,23,42,.98),rgba(15,23,42,.70));border:1px solid rgba(253,230,138,.20);min-height:126px;box-shadow:0 14px 34px rgba(0,0,0,.24)}.klabel{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:#93c5fd;font-weight:900}.kvalue{font-size:31px;color:white;font-weight:900;margin-top:8px}.knote{font-size:13px;color:#cbd5e1;margin-top:3px}.pill{display:inline-block;padding:7px 11px;border-radius:999px;background:rgba(14,165,233,.14);border:1px solid rgba(125,211,252,.28);margin:3px;color:#e0f2fe!important;font-weight:800;font-size:12px}.warn{color:#fde68a!important;font-weight:900}.ok{color:#86efac!important;font-weight:900}.bad{color:#fda4af!important;font-weight:900}.small{font-size:13px;color:#cbd5e1!important}.stDataFrame{border-radius:20px;overflow:hidden}.stButton>button{border-radius:18px!important;font-weight:900!important}.stSelectbox div[data-baseweb="select"], .stFileUploader{background:rgba(15,23,42,.55)!important;border-radius:18px}.js-plotly-plot{border-radius:24px;overflow:hidden}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

DEFAULT_EXCEL = Path("data/JKM_7Sheet_Full_Simulation_Raw_Data.xlsx")
REQUIRED = ["S1_Quant_Raw","S2_Quant_Raw","S3_Quant_Raw","Q1_Client_Raw","Q2_Officer_Raw","Q3_System_Raw","T123_Pilot_Raw"]
BM_COL = {"Zone":"Zon","State":"Negeri","Gender":"Jantina","Age_Group":"Kumpulan Umur","Client_Category":"Kategori Klien","Service_Type":"Jenis Perkhidmatan","Number_of_Sessions":"Bilangan Sesi","Service_Mode":"Mod Perkhidmatan","Referral_Pathway":"Laluan Rujukan","Position":"Jawatan","Grade":"Gred","Experience":"Pengalaman","Service_Setting":"Tetapan Perkhidmatan","Main_Intervention":"Intervensi Utama","Monthly_Active_Cases":"Kes Aktif Bulanan","Main_Client_Category":"Kategori Klien Utama","Job_Category":"Kategori Tugas","Years_in_JKM":"Tempoh Dalam JKM","Work_Setting":"Tetapan Kerja","Contact_Frequency":"Kekerapan Kontak","Role_Related_To_Service":"Peranan Berkaitan Perkhidmatan","Main_Client_Group":"Kumpulan Klien Utama","Participant_Group":"Kumpulan Peserta","Timepoint":"Titik Masa","Completion_Status":"Status Lengkap","Session_Count":"Bilangan Sesi"}
RESPONDENT_MAP = {"S1_Quant_Raw":"Klien", "S2_Quant_Raw":"Pegawai Psikologi/Kaunseling", "S3_Quant_Raw":"Warga JKM", "Q1_Client_Raw":"Klien - Kualitatif", "Q2_Officer_Raw":"Pegawai - Kualitatif", "Q3_System_Raw":"Pengurusan/Sistem - Kualitatif", "T123_Pilot_Raw":"Klien T1-T2-T3"}

if "page" not in st.session_state: st.session_state.page="Dashboard Utama"
if "workbook_bytes" not in st.session_state: st.session_state.workbook_bytes=None
if "workbook_name" not in st.session_state: st.session_state.workbook_name="Default workbook"

@st.cache_data(show_spinner=False)
def read_excel_bytes(b):
    xl = pd.ExcelFile(io.BytesIO(b), engine="openpyxl")
    return {s: pd.read_excel(xl, s) for s in xl.sheet_names}
@st.cache_data(show_spinner=False)
def read_excel_path(p):
    xl = pd.ExcelFile(p, engine="openpyxl")
    return {s: pd.read_excel(xl, s) for s in xl.sheet_names}

def find_col(df, candidates):
    norm = {re.sub(r"[^a-z0-9]","",str(c).lower()):c for c in df.columns}
    for x in candidates:
        k = re.sub(r"[^a-z0-9]","",x.lower())
        if k in norm: return norm[k]
    for c in df.columns:
        cl=str(c).lower()
        if any(x.lower() in cl for x in candidates): return c
    return None

def score_cols(df): return [c for c in df.columns if str(c).startswith("Score_") and pd.api.types.is_numeric_dtype(df[c])]
def item_cols(df): return [c for c in df.columns if re.match(r"^(K\d|B\d|T\d)", str(c)) and pd.api.types.is_numeric_dtype(df[c])]
def sq_cols(df): return [c for c in df.columns if str(c).startswith("SQ") or str(c).startswith("Open_") or str(c).startswith(("A_","B_","C_","D_","E_","F_","G_","H_","I_","J_","K_"))]
def safe_mean(s): return float(pd.to_numeric(s, errors="coerce").mean()) if len(s) else np.nan
def fmt(x,d=2): return "-" if pd.isna(x) else f"{x:.{d}f}"
def add_resp_type(df, sheet):
    out=df.copy(); out["Jenis Responden"] = RESPONDENT_MAP.get(sheet, sheet); return out

def kpi(label, value, note=""):
    st.markdown(f'<div class="kpi"><div class="klabel">{label}</div><div class="kvalue">{value}</div><div class="knote">{note}</div></div>', unsafe_allow_html=True)

def plot_bar(df, x, y, title, color=None):
    fig=px.bar(df, x=x, y=y, color=color, text_auto='.2f', title=title)
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,.25)", font_color="#E5E7EB", title_font_size=19, height=420, margin=dict(l=20,r=20,t=55,b=30))
    fig.update_traces(marker_line_width=0, textfont_size=12)
    st.plotly_chart(fig, use_container_width=True)

def plot_line(df, x, y, title, color=None):
    fig=px.line(df, x=x, y=y, color=color, markers=True, title=title)
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,.25)", font_color="#E5E7EB", title_font_size=19, height=420, margin=dict(l=20,r=20,t=55,b=30))
    st.plotly_chart(fig, use_container_width=True)

def cronbach_alpha(df_items):
    X=df_items.apply(pd.to_numeric, errors="coerce").dropna(axis=0, how="any")
    k=X.shape[1]
    if k<2 or X.shape[0]<3: return np.nan
    total=X.sum(axis=1); denom=total.var(ddof=1)
    return np.nan if denom==0 else (k/(k-1))*(1-X.var(ddof=1).sum()/denom)

def sem_table(df):
    groups={}
    for c in item_cols(df):
        m=re.match(r"^(K\d+[A-Z]?|B|T2|T3)", str(c))
        key=m.group(1) if m else str(c)[:3]
        groups.setdefault(key,[]).append(c)
    rows=[]
    latent=pd.DataFrame(index=df.index)
    for g, cols in groups.items():
        if len(cols)>=2:
            latent[g]=df[cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)
            alpha=cronbach_alpha(df[cols])
            corr=df[cols].apply(pd.to_numeric, errors="coerce").corr().values
            vals=corr[np.triu_indices_from(corr,1)] if corr.size else []
            mean_r=np.nanmean(vals) if len(vals) else np.nan
            cr=(len(cols)*mean_r)/(1+(len(cols)-1)*mean_r) if not pd.isna(mean_r) and (1+(len(cols)-1)*mean_r)!=0 else np.nan
            ave=np.nanmean([abs(v) for v in vals]) if len(vals) else np.nan
            rows.append({"Konstruk SEM":g,"Bil. Item":len(cols),"Mean Skor":safe_mean(latent[g]),"Cronbach Alpha":alpha,"Composite Reliability (anggaran)":cr,"AVE/Convergent (anggaran)":ave,"Status":("Kukuh" if alpha>=.70 else "Perlu semak") if not pd.isna(alpha) else "Tidak cukup data"})
    return pd.DataFrame(rows), latent

def path_analysis(latent):
    if latent.shape[1]<2: return pd.DataFrame()
    target=None
    for c in latent.columns[::-1]:
        if c.startswith("K1") or c.startswith("K5") or c.startswith("B") or c.startswith("T3"):
            target=c; break
    target=target or latent.columns[-1]
    rows=[]
    y=pd.to_numeric(latent[target], errors="coerce")
    for c in latent.columns:
        if c==target: continue
        x=pd.to_numeric(latent[c], errors="coerce")
        ok=x.notna() & y.notna()
        if ok.sum()>3 and x[ok].std()>0 and y[ok].std()>0:
            r=float(np.corrcoef(x[ok], y[ok])[0,1]); rows.append({"Predictor":c,"Outcome":target,"Path Coefficient r":r,"Kekuatan": "Kuat" if abs(r)>=.50 else "Sederhana" if abs(r)>=.30 else "Lemah"})
    return pd.DataFrame(rows).sort_values("Path Coefficient r", ascending=False)

def text_themes(frames):
    stop=set("dan yang untuk perlu kerana dengan dalam serta ialah adalah kepada bagi atau lebih masih utama berlaku boleh melalui secara antara ini itu apabila sangat sebagai pada klien jkm".split())
    text=[]
    for df in frames:
        for c in sq_cols(df): text += df[c].dropna().astype(str).tolist()
    words=[]
    for t in text:
        words += [w.lower() for w in re.findall(r"[A-Za-zÀ-ÿ]{4,}", t) if w.lower() not in stop]
    return pd.DataFrame(Counter(words).most_common(25), columns=["Tema/Kata Kunci","Kekerapan"])

def filter_any(df, zone, state, resp):
    out=df.copy()
    z=find_col(out,["Zone","Zon"]); s=find_col(out,["State","Negeri"])
    if zone!="Semua Zon" and z: out=out[out[z].astype(str)==zone]
    if state!="Semua Negeri" and s: out=out[out[s].astype(str)==state]
    if resp!="Semua Jenis Responden" and "Jenis Responden" in out.columns: out=out[out["Jenis Responden"].astype(str)==resp]
    return out

st.markdown('<div class="hero"><span class="badge">JKM PSYCOUNSEL • ADMIN EXCEL ANALYTICS • SEM READY</span><div class="hero-title">Dashboard Analitik <span class="gold">Psikologi & Kaunseling JKM</span></div><div class="hero-subtitle">Versi revised: nama kolum auto-detect, label <b>Jenis Responden</b> dibetulkan, tiada sidebar, reka bentuk premium, analisis kuantitatif, kualitatif, T1–T2–T3, audit formula dan SEM ringkas.</div></div>', unsafe_allow_html=True)

c1,c2,c3=st.columns([2,1,1])
with c1:
    up=st.file_uploader("Muat naik fail Excel 7 sheet (.xlsx)", type=["xlsx"], label_visibility="collapsed")
    if up: st.session_state.workbook_bytes=up.getvalue(); st.session_state.workbook_name=up.name; st.success(f"Fail dimuat naik: {up.name}")
with c2:
    if st.button("Reset Data", use_container_width=True): st.session_state.workbook_bytes=None; st.session_state.workbook_name="Default workbook"; st.rerun()
with c3:
    st.markdown(f'<span class="pill">Sumber Data: {st.session_state.workbook_name}</span>', unsafe_allow_html=True)

try:
    sheets = read_excel_bytes(st.session_state.workbook_bytes) if st.session_state.workbook_bytes else (read_excel_path(str(DEFAULT_EXCEL)) if DEFAULT_EXCEL.exists() else read_excel_path('/mnt/data/JKM_7Sheet_Full_Simulation_Raw_Data(2).xlsx'))
except Exception as e:
    st.error(f"Excel tidak dapat dibaca: {e}"); st.stop()

for s in list(sheets): sheets[s]=add_resp_type(sheets[s], s)
missing=[s for s in REQUIRED if s not in sheets]
if missing: st.warning("Sheet tidak dijumpai: "+", ".join(missing))

all_df=pd.concat([df for df in sheets.values()], ignore_index=True, sort=False)
zones=sorted(all_df[find_col(all_df,["Zone"])].dropna().astype(str).unique()) if find_col(all_df,["Zone"]) else []
states=sorted(all_df[find_col(all_df,["State"])].dropna().astype(str).unique()) if find_col(all_df,["State"]) else []
resps=sorted(all_df["Jenis Responden"].dropna().astype(str).unique())
f1,f2,f3=st.columns(3)
zone=f1.selectbox("Zon", ["Semua Zon"]+zones)
state=f2.selectbox("Negeri", ["Semua Negeri"]+states)
resp=f3.selectbox("Jenis Responden", ["Semua Jenis Responden"]+resps)

pages=["Dashboard Utama","S1 Klien","S2 Pegawai","S3 Warga JKM","Kualitatif","T1–T2–T3","Analisis SEM","Audit Trail & Formula"]
st.markdown('<div class="navbtn">', unsafe_allow_html=True)
cols=st.columns(len(pages))
for i,p in enumerate(pages):
    if cols[i].button(p, use_container_width=True): st.session_state.page=p
st.markdown('</div>', unsafe_allow_html=True)
page=st.session_state.page

def overview():
    st.markdown('<div class="card">', unsafe_allow_html=True); st.subheader("Ringkasan Keseluruhan")
    qdfs=[sheets[k] for k in ["S1_Quant_Raw","S2_Quant_Raw","S3_Quant_Raw","T123_Pilot_Raw"] if k in sheets]
    filt=[filter_any(d,zone,state,resp) for d in qdfs]
    n=sum(len(d) for d in filt); score_all=[]
    for d in filt:
        for c in score_cols(d): score_all += pd.to_numeric(d[c],errors="coerce").dropna().tolist()
    a,b,c,d=st.columns(4); a.markdown("<div class='kpi'><div class='klabel'>Jumlah Rekod Ditapis</div><div class='kvalue'>%s</div><div class='knote'>Mengikut zon, negeri dan jenis responden</div></div>"%n, unsafe_allow_html=True)
    b.markdown("<div class='kpi'><div class='klabel'>Purata Skor Keseluruhan</div><div class='kvalue'>%s</div><div class='knote'>Semua pemboleh ubah Score_</div></div>"%fmt(np.mean(score_all) if score_all else np.nan), unsafe_allow_html=True)
    c.markdown("<div class='kpi'><div class='klabel'>Jenis Responden</div><div class='kvalue'>%s</div><div class='knote'>Kategori responden tersedia</div></div>"%len(resps), unsafe_allow_html=True)
    d.markdown("<div class='kpi'><div class='klabel'>Sheet Dibaca</div><div class='kvalue'>%s/7</div><div class='knote'>Auto semak struktur workbook</div></div>"%len([x for x in REQUIRED if x in sheets]), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    mix=[]
    for name,df in sheets.items():
        fd=filter_any(df,zone,state,resp); mix.append({"Sheet":name,"Jenis Responden":RESPONDENT_MAP.get(name,name),"Rekod":len(fd),"Bil. Kolum":df.shape[1]})
    plot_bar(pd.DataFrame(mix), "Jenis Responden", "Rekod", "Taburan Rekod Mengikut Jenis Responden", "Jenis Responden")
    themes=text_themes([filter_any(d,zone,state,resp) for d in sheets.values()])
    if not themes.empty: plot_bar(themes.head(15), "Tema/Kata Kunci", "Kekerapan", "Tema Kualitatif Paling Kerap")

def quant_page(sheet, title):
    df=filter_any(sheets.get(sheet,pd.DataFrame()),zone,state,resp)
    st.markdown('<div class="card">', unsafe_allow_html=True); st.subheader(title)
    if df.empty: st.warning("Tiada data selepas tapisan."); st.markdown('</div>', unsafe_allow_html=True); return
    sc=score_cols(df); a,b,c,d=st.columns(4)
    with a: kpi("Rekod", len(df), "Bilangan responden")
    with b: kpi("Purata Overall", fmt(safe_mean(df["Score_Overall"]) if "Score_Overall" in df else np.nan), "Skor keseluruhan")
    with c: kpi("Bil. Konstruk", len(sc), "Kolum Score_ dikesan")
    with d: kpi("Item Likert", len(item_cols(df)), "Item numerik dikesan")
    st.markdown('</div>', unsafe_allow_html=True)
    summ=pd.DataFrame([{"Konstruk":c.replace("Score_","").replace("_"," "),"Mean":safe_mean(df[c]),"N":df[c].notna().sum()} for c in sc]).sort_values("Mean", ascending=False)
    if not summ.empty: plot_bar(summ, "Konstruk", "Mean", "Purata Skor Konstruk")
    z=find_col(df,["State"])
    if z and "Score_Overall" in df:
        by=df.groupby(z, dropna=False)["Score_Overall"].mean().reset_index().rename(columns={z:"Negeri","Score_Overall":"Mean Overall"}).sort_values("Mean Overall", ascending=False)
        plot_bar(by, "Negeri", "Mean Overall", "Perbandingan Skor Keseluruhan Mengikut Negeri")
    lows=[]
    for c in item_cols(df): lows.append({"Item":c,"Mean":safe_mean(df[c]),"Peratus Skor Rendah (1-2)":float((pd.to_numeric(df[c],errors='coerce')<=2).mean()*100)})
    lowdf=pd.DataFrame(lows).sort_values("Mean").head(12)
    if not lowdf.empty: plot_bar(lowdf, "Item", "Mean", "Item Kritikal / Skor Terendah")
    st.dataframe(summ, use_container_width=True)

def qualitative():
    st.subheader("Analisis Kualitatif: CMO, RE-AIM dan Donabedian")
    q=[filter_any(sheets.get(k,pd.DataFrame()),zone,state,resp) for k in ["Q1_Client_Raw","Q2_Officer_Raw","Q3_System_Raw"]]
    qq=pd.concat(q, ignore_index=True, sort=False) if q else pd.DataFrame()
    if qq.empty: st.warning("Tiada data kualitatif selepas tapisan."); return
    a,b,c=st.columns(3); a.metric("Rekod Kualitatif", len(qq)); b.metric("Kolum Teks", len(sq_cols(qq))); c.metric("RE-AIM Tag", qq["RE_AIM_Tag"].nunique() if "RE_AIM_Tag" in qq else 0)
    if "RE_AIM_Tag" in qq: plot_bar(qq["RE_AIM_Tag"].value_counts().reset_index().rename(columns={"RE_AIM_Tag":"RE-AIM","count":"Kekerapan"}), "RE-AIM", "Kekerapan", "Taburan RE-AIM")
    th=text_themes([qq]); plot_bar(th.head(20), "Tema/Kata Kunci", "Kekerapan", "Tema Utama Daripada Jawapan Terbuka")
    cmo=[c for c in ["CMO_Context","CMO_Mechanism","CMO_Outcome"] if c in qq.columns]
    if cmo: st.dataframe(qq[cmo+["RE_AIM_Tag"] if "RE_AIM_Tag" in qq else cmo].head(50), use_container_width=True)

def t123():
    df=filter_any(sheets.get("T123_Pilot_Raw",pd.DataFrame()),zone,state,resp)
    st.subheader("Analisis T1–T2–T3 / Pilot Outcome")
    if df.empty: st.warning("Tiada data T1–T2–T3 selepas tapisan."); return
    metrics=[c for c in ["Score_Core_Outcome","Score_T2_Process","Score_T3_Sustainability"] if c in df.columns]
    long=df.melt(id_vars=["Timepoint"], value_vars=metrics, var_name="Skor", value_name="Mean").dropna()
    if not long.empty:
        res=long.groupby(["Timepoint","Skor"], as_index=False)["Mean"].mean(); plot_line(res,"Timepoint","Mean","Perubahan Skor Mengikut Titik Masa", "Skor")
    st.dataframe(df.head(200), use_container_width=True)

def sem():
    st.subheader("Analisis SEM Ringkas: Reliability, Validity dan Path")
    selected=st.selectbox("Pilih set data SEM", [x for x in ["S1_Quant_Raw","S2_Quant_Raw","S3_Quant_Raw","T123_Pilot_Raw"] if x in sheets])
    df=filter_any(sheets[selected],zone,state,resp)
    tab, lat=sem_table(df)
    if tab.empty: st.warning("Item SEM tidak cukup untuk dikira."); return
    st.markdown("<div class='glass'>SEM di sini ialah analisis pantas berasaskan skor item: Cronbach Alpha, Composite Reliability anggaran, convergent validity anggaran dan korelasi laluan. Untuk laporan akademik penuh, eksport data ini ke SmartPLS/AMOS/semopy.</div>", unsafe_allow_html=True)
    st.dataframe(tab, use_container_width=True)
    plot_bar(tab, "Konstruk SEM", "Cronbach Alpha", "Reliability Konstruk SEM")
    path=path_analysis(lat)
    if not path.empty:
        plot_bar(path, "Predictor", "Path Coefficient r", "Anggaran Laluan SEM terhadap Konstruk Outcome")
        st.dataframe(path, use_container_width=True)
    if lat.shape[1]>1:
        corr=lat.corr()
        fig=px.imshow(corr, text_auto='.2f', title="Correlation Matrix Konstruk Laten")
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,.25)", height=560)
        st.plotly_chart(fig, use_container_width=True)

def audit():
    st.subheader("Audit Trail & Formula")
    rows=[]
    for name,df in sheets.items():
        rows.append({"Sheet":name,"Jenis Responden":RESPONDENT_MAP.get(name,name),"Rekod":len(df),"Kolum":df.shape[1],"Kolum Score_":", ".join(score_cols(df))})
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
    st.markdown("""
<div class='card'>
<b>Formula utama sistem</b><br><br>
1. <span class='warn'>Skor Konstruk</span> = purata item Likert dalam konstruk yang sama.<br>
2. <span class='warn'>Score_Overall</span> = purata konstruk utama responden jika kolum tersedia dalam Excel.<br>
3. <span class='warn'>Cronbach Alpha</span> = k/(k-1) × [1 − jumlah varians item / varians jumlah item].<br>
4. <span class='warn'>Analisis SEM ringkas</span> menggunakan skor laten purata item bagi setiap konstruk dan korelasi sebagai anggaran path coefficient.<br>
5. <span class='warn'>Jenis Responden</span> dijana daripada nama sheet, bukan lagi “Jenis Klien”.
</div>
""", unsafe_allow_html=True)
    st.write("Senarai kolum sebenar setiap sheet:")
    for name,df in sheets.items():
        with st.expander(name): st.write(list(df.columns))

if page=="Dashboard Utama": overview()
elif page=="S1 Klien": quant_page("S1_Quant_Raw", "S1 Klien: Pengalaman, Akses, Hubungan, Outcome")
elif page=="S2 Pegawai": quant_page("S2_Quant_Raw", "S2 Pegawai: Kejayaan, Halangan, Beban Kerja dan Penambahbaikan")
elif page=="S3 Warga JKM": quant_page("S3_Quant_Raw", "S3 Warga JKM: Kesedaran, Rujukan, Koordinasi dan Sokongan Organisasi")
elif page=="Kualitatif": qualitative()
elif page=="T1–T2–T3": t123()
elif page=="Analisis SEM": sem()
elif page=="Audit Trail & Formula": audit()
