import io
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="JKM SEM Impact Intelligence", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"]{font-family:'Inter',sans-serif}.stApp{background:radial-gradient(circle at top left,#0F2D52 0%,#081525 45%,#020617 100%);color:#F8FAFC}.block-container{padding-top:1rem;max-width:1550px}[data-testid="stSidebar"]{background:linear-gradient(180deg,#06101E,#0B1628);border-right:1px solid rgba(197,160,23,.28)}h1,h2,h3{color:#fff!important;letter-spacing:-.03em}.hero{padding:34px;border-radius:30px;background:linear-gradient(135deg,rgba(197,160,23,.22),rgba(16,185,129,.10)),linear-gradient(135deg,#06142B,#10213C 60%,#163E62);border:1px solid rgba(253,230,138,.32);box-shadow:0 28px 90px rgba(0,0,0,.42);margin-bottom:18px}.badge{display:inline-block;padding:7px 13px;border-radius:999px;background:rgba(197,160,23,.16);border:1px solid rgba(253,230,138,.34);color:#FDE68A;font-weight:900;font-size:12px;letter-spacing:.08em}.hero-title{font-size:44px;line-height:1.06;font-weight:900;margin-top:10px}.gold{background:linear-gradient(90deg,#FDE68A,#C5A017,#FFF7C2);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.hero-subtitle{color:#CBD5E1;font-size:16px;max-width:1120px;margin-top:8px}.card{padding:22px;border-radius:24px;background:rgba(15,23,42,.74);border:1px solid rgba(148,163,184,.22);box-shadow:0 20px 55px rgba(0,0,0,.28);margin-bottom:18px}.kpi{padding:20px;border-radius:22px;background:linear-gradient(180deg,rgba(15,23,42,.96),rgba(15,23,42,.70));border:1px solid rgba(148,163,184,.22);min-height:132px}.klabel{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:#94A3B8;font-weight:800}.kvalue{font-size:33px;color:white;font-weight:900;margin-top:8px}.knote{font-size:13px;color:#CBD5E1;margin-top:4px}.stTabs [data-baseweb="tab"]{background:rgba(15,23,42,.86);border:1px solid rgba(148,163,184,.22);border-radius:999px;color:#CBD5E1;padding:10px 17px}.stTabs [aria-selected="true"]{background:linear-gradient(90deg,#C5A017,#FDE68A)!important;color:#0F172A!important;font-weight:900}.small{font-size:13px;color:#CBD5E1}.ok{color:#86EFAC;font-weight:900}.warn{color:#FDE68A;font-weight:900}.bad{color:#FDA4AF;font-weight:900}</style>
""", unsafe_allow_html=True)

ZONES={"Tengah":["Kuala Lumpur","Selangor"],"Utara":["Pulau Pinang","Kedah"],"Selatan":["Johor","Melaka"],"Timur":["Kelantan","Pahang"],"Sabah":["Kota Kinabalu"],"Sarawak":["Kuching"]}
RESP_GROUPS=["Klien","PPsi","PPPsi","Warga Jabatan"]
INTERVENTIONS=["Kaunseling Individu","Kaunseling Kelompok","Intervensi Krisis","Sokongan Sosial","Psikopendidikan","Rujukan Lanjut"]

@st.cache_data
def simulate_questionnaire(n=600, seed=2026):
    rng=np.random.default_rng(seed)
    zones=np.repeat(list(ZONES), n//6); zones=np.concatenate([zones,rng.choice(list(ZONES),n-len(zones))]) if len(zones)<n else zones; rng.shuffle(zones)
    rows=[]
    for i,z in enumerate(zones,1):
        ze={"Tengah":4,"Selatan":3,"Utara":2,"Timur":-1,"Sabah":-2,"Sarawak":-1}[z]
        group=rng.choice(RESP_GROUPS,p=[.75,.105,.045,.10])
        age=int(np.clip(rng.normal(38,13),16,75))
        org_capacity=np.clip(rng.normal(70+ze,9),35,96)
        service_quality=np.clip(0.64*org_capacity+np.random.default_rng(seed+i).normal(28+ze,7),35,99)
        mechanism=np.clip(0.62*service_quality+rng.normal(30,7),35,99)
        wai=np.clip(mechanism+rng.normal(2,7),35,99)
        csq8=np.clip(0.58*mechanism+0.30*service_quality+rng.normal(13,6),35,100)
        access=np.clip(rng.normal(72+ze,10),30,98)
        rights=np.clip(rng.normal(80+ze,8),45,100)
        whodas_t1=np.clip(rng.normal(48,11),12,86)
        wellbeing_t1=np.clip(rng.normal(52,10),15,88)
        pcl5_t1=np.clip(rng.normal(44,13),5,82)
        improvement=np.clip((mechanism+service_quality+access)/10+rng.normal(0,4),5,32)
        whodas_t2=np.clip(whodas_t1-improvement*.55+rng.normal(0,3),4,78)
        whodas_t3=np.clip(whodas_t2-rng.normal(2.2,3),3,75)
        wellbeing_t2=np.clip(wellbeing_t1+improvement*.60+rng.normal(0,3),15,98)
        wellbeing_t3=np.clip(wellbeing_t2+rng.normal(2,3),15,99)
        pcl5_t2=np.clip(pcl5_t1-improvement*.65+rng.normal(0,4),2,80)
        pcl5_t3=np.clip(pcl5_t2-rng.normal(2.5,3),2,78)
        outcome=np.clip(.24*(100-whodas_t3)+.24*wellbeing_t3+.20*csq8+.18*wai+.14*(100-pcl5_t3),0,100)
        rows.append({"respondent_id":f"Q{i:04d}","zone":z,"state_location":rng.choice(ZONES[z]),"respondent_group":group,"gender":rng.choice(["Lelaki","Perempuan"],p=[.42,.58]),"age":age,"age_group":"16-24" if age<25 else "25-34" if age<35 else "35-44" if age<45 else "45-54" if age<55 else "55+","intervention_type":rng.choice(INTERVENTIONS,p=[.34,.15,.17,.13,.12,.09]),"waiting_days":int(np.clip(rng.normal(9-ze/2,4),1,28)),"sessions_completed":int(np.clip(rng.poisson(4)+1,1,12)),"dropout_status":"Ya" if rng.random() < .12+max(0,65-access)/220 else "Tidak","followup_status":"Lengkap" if rng.random()<.75 else "Tidak lengkap","Organizational_Capacity":round(org_capacity,1),"Service_Quality":round(service_quality,1),"Service_Mechanism":round(mechanism,1),"WHODAS_T1":round(whodas_t1,1),"WHODAS_T2":round(whodas_t2,1),"WHODAS_T3":round(whodas_t3,1),"Wellbeing_T1":round(wellbeing_t1,1),"Wellbeing_T2":round(wellbeing_t2,1),"Wellbeing_T3":round(wellbeing_t3,1),"PCL5_T1":round(pcl5_t1,1),"PCL5_T2":round(pcl5_t2,1),"PCL5_T3":round(pcl5_t3,1),"WAI_Alliance":round(wai,1),"CSQ8_Satisfaction":round(csq8,1),"Access_Responsiveness":round(access,1),"Rights_Based_Experience":round(rights,1),"Client_Outcome_Index":round(outcome,1)})
    return pd.DataFrame(rows)

@st.cache_data
def simulate_interviews(n=85, seed=2027):
    rng=np.random.default_rng(seed); zones=np.repeat(list(ZONES), n//6); zones=np.concatenate([zones,rng.choice(list(ZONES),n-len(zones))]); rng.shuffle(zones)
    themes=["Akses dan masa menunggu","Hubungan terapeutik","Kerahsiaan dan rasa selamat","Kesesuaian budaya/bahasa","Susulan kes","Kapasiti pegawai","Rujukan antara agensi","Tele-kaunseling","Pemulihan trauma","SOP dan dokumentasi"]
    rows=[]
    for i,z in enumerate(zones,1):
        theme=rng.choice(themes)
        rows.append({"interview_id":f"I{i:03d}","zone":z,"respondent_group":rng.choice(["Klien","PPsi","PPPsi","Warga Jabatan","Pemegang Taruh"],p=[.53,.20,.09,.10,.08]),"CMO_context":rng.choice(["Luar bandar","Bandar","Beban kes tinggi","Kes krisis","Kumpulan rentan","Capaian digital rendah"]),"CMO_mechanism":rng.choice(["Kepercayaan","Rasa selamat","Pemerkasaan","Kefahaman matlamat sesi","Sokongan sosial","Privasi"]),"CMO_outcome":rng.choice(["Pengurangan tekanan","Peningkatan fungsi sosial","Kepuasan tinggi","Kekal hadir sesi","Rujukan berjaya","Keciciran rendah"]),"main_theme":theme,"sentiment":rng.choice(["Positif","Campuran","Negatif"],p=[.58,.30,.12]),"priority":rng.choice(["Tinggi","Sederhana","Rendah"],p=[.45,.38,.17]),"quote":"Petikan ilustrasi simulasi: aspek ini perlu disahkan melalui transkrip sebenar selepas kerja lapangan."})
    return pd.DataFrame(rows)

@st.cache_data
def sem_tables(seed=11):
    measurement=pd.DataFrame([
        ["Organizational Capacity",0.931,0.949,0.755,"Pass"],["Service Quality",0.944,0.959,0.786,"Pass"],["Service Mechanism",0.928,0.946,0.744,"Pass"],["Client Outcome",0.918,0.940,0.724,"Pass"]],columns=["Construct","Cronbach Alpha","Composite Reliability","AVE","Decision"])
    paths=pd.DataFrame([
        ["Organizational Capacity → Service Quality",0.81,22.4,"<0.001","Supported"],["Service Quality → Service Mechanism",0.76,18.9,"<0.001","Supported"],["Service Mechanism → Client Outcome",0.73,16.8,"<0.001","Supported"],["Service Quality → Client Outcome",0.24,5.2,"<0.001","Supported"],["Organizational Capacity → Client Outcome",0.11,2.1,"0.035","Weak / indirect dominant"]],columns=["SEM Path","Beta","t-value","p-value","Decision"])
    r2=pd.DataFrame([["Service Quality",0.66,"Substantial"],["Service Mechanism",0.58,"Moderate-high"],["Client Outcome",0.71,"Substantial"]],columns=["Endogenous Construct","R²","Interpretation"])
    htmt=pd.DataFrame(np.array([[1,.74,.69,.62],[.74,1,.77,.70],[.69,.77,1,.73],[.62,.70,.73,1]]),columns=["Capacity","Quality","Mechanism","Outcome"],index=["Capacity","Quality","Mechanism","Outcome"])
    return measurement,paths,r2,htmt

def kpi(label,value,note=""):
    st.markdown(f"<div class='kpi'><div class='klabel'>{label}</div><div class='kvalue'>{value}</div><div class='knote'>{note}</div></div>",unsafe_allow_html=True)

def fig_style(fig,h=430):
    fig.update_layout(height=h,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(15,23,42,.20)",font=dict(color="#E5E7EB",family="Inter"),margin=dict(l=25,r=25,t=62,b=35),legend=dict(orientation="h",y=1.05,x=1,xanchor="right"),title_font=dict(size=20,color="#fff"))
    fig.update_xaxes(gridcolor="rgba(148,163,184,.18)"); fig.update_yaxes(gridcolor="rgba(148,163,184,.18)")
    return fig

def make_template(qdf,idf):
    output=io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        qdf.head(20).to_excel(writer,index=False,sheet_name="questionnaire")
        idf.head(20).to_excel(writer,index=False,sheet_name="interview")
        pd.DataFrame({"Note":["Template aligned to TOR: 600 quantitative and 85 qualitative.","Use real data to replace simulation rows.","SEM results in Streamlit are illustrative until recalculated using AMOS/SmartPLS/R/lavaan."]}).to_excel(writer,index=False,sheet_name="README")
    return output.getvalue()

qdf_demo=simulate_questionnaire(); idf_demo=simulate_interviews()
st.sidebar.markdown("## 🧠 JKM SEM Intelligence")
st.sidebar.caption("Simulation data aligned to TOR. Upload real Excel to replace demo data.")
data_mode=st.sidebar.radio("Data source",["Simulation: TOR aligned 600 + 85","Upload real Excel"],label_visibility="collapsed")
qdf,idf=qdf_demo,idf_demo
if data_mode=="Upload real Excel":
    up=st.sidebar.file_uploader("Upload .xlsx with sheets questionnaire and interview",type=["xlsx"])
    if up:
        try:
            xls=pd.ExcelFile(up); qdf=pd.read_excel(up,sheet_name="questionnaire" if "questionnaire" in xls.sheet_names else xls.sheet_names[0]); idf=pd.read_excel(up,sheet_name="interview" if "interview" in xls.sheet_names else xls.sheet_names[1]); st.sidebar.success("Real Excel loaded.")
        except Exception as e: st.sidebar.error(f"Cannot read Excel: {e}")
zone_filter=st.sidebar.multiselect("Zone filter",sorted(qdf.zone.unique()),default=sorted(qdf.zone.unique()))
group_filter=st.sidebar.multiselect("Respondent group",sorted(qdf.respondent_group.unique()),default=sorted(qdf.respondent_group.unique()))
qdf=qdf[qdf.zone.isin(zone_filter)&qdf.respondent_group.isin(group_filter)].copy(); idf=idf[idf.zone.isin(zone_filter)].copy()

st.markdown("""<div class='hero'><div class='badge'>TOR-ALIGNED SEM + MIXED-METHOD DASHBOARD</div><div class='hero-title'>JKM <span class='gold'>PsyCounsel SEM Impact Intelligence</span></div><div class='hero-subtitle'>Dashboard demo untuk Kajian Penilaian Keberkesanan Perkhidmatan Psikologi dan Kaunseling JKM. Sistem ini menggunakan data simulasi yang diselaraskan dengan TOR: 600 responden kuantitatif, 85 informan kualitatif, instrumen WHODAS/WHOQOL-Wellbeing/WAI-SR/CSQ-8/PCL-5, analisis utama SEM, CMO Realist Evaluation dan RE-AIM.</div></div>""",unsafe_allow_html=True)

avg_out=qdf.Client_Outcome_Index.mean(); whodas_imp=qdf.WHODAS_T1.mean()-qdf.WHODAS_T3.mean(); wb_imp=qdf.Wellbeing_T3.mean()-qdf.Wellbeing_T1.mean(); dropout=qdf.dropout_status.eq("Ya").mean()*100
c1,c2,c3,c4,c5=st.columns(5)
with c1:kpi("Kuantitatif",f"{len(qdf):,}","TOR target: 600")
with c2:kpi("Kualitatif",f"{len(idf):,}","TOR target: 85")
with c3:kpi("Client Outcome",f"{avg_out:.1f}","SEM outcome index")
with c4:kpi("WHODAS Improvement",f"{whodas_imp:.1f}","T1 → T3 lower is better")
with c5:kpi("Dropout",f"{dropout:.1f}%","retention monitoring")

st.info("Nota penting: semua keputusan SEM, skor dan insight dalam demo ini adalah data simulasi untuk pembentangan cadangan. Selepas kerja lapangan, model SEM mesti dijalankan semula menggunakan data sebenar melalui AMOS/SmartPLS/R-lavaan dan dipaparkan semula dalam dashboard.")

tabs=st.tabs(["Executive", "TOR Alignment", "SEM Model", "Outcome T1-T2-T3", "RE-AIM & CMO", "Zonal Drilldown", "Scenario Simulator", "Policy Actions", "Data & Template"])

with tabs[0]:
    st.markdown("<div class='card'>",unsafe_allow_html=True); st.subheader("Executive Result Snapshot")
    zs=qdf.groupby("zone",as_index=False).agg(Respondents=("respondent_id","count"),Outcome=("Client_Outcome_Index","mean"),Capacity=("Organizational_Capacity","mean"),Quality=("Service_Quality","mean"),Mechanism=("Service_Mechanism","mean"),Satisfaction=("CSQ8_Satisfaction","mean"),WHODAS_T1=("WHODAS_T1","mean"),WHODAS_T3=("WHODAS_T3","mean"))
    zs["WHODAS Improvement"]=zs.WHODAS_T1-zs.WHODAS_T3
    st.dataframe(zs.drop(columns=["WHODAS_T1","WHODAS_T3"]).round(1),use_container_width=True)
    a,b=st.columns(2)
    with a: st.plotly_chart(fig_style(px.bar(zs.sort_values("Outcome",ascending=False),x="zone",y="Outcome",text="Outcome",color="Outcome",title="Client Outcome Index by Zone",color_continuous_scale="Cividis")),use_container_width=True)
    with b: st.plotly_chart(fig_style(px.scatter(qdf,x="Service_Mechanism",y="Client_Outcome_Index",size="sessions_completed",color="zone",hover_data=["respondent_group","intervention_type"],title="Mechanism vs Client Outcome")),use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[1]:
    st.markdown("<div class='card'>",unsafe_allow_html=True); st.subheader("TOR Compliance Matrix")
    tor=pd.DataFrame([
        ["Mixed-method design","Quantitative survey + qualitative interview/FGD","Included"],["Quantitative sample","600 respondents across six zones","Included"],["Qualitative sample","85 informants using purposeful sampling","Included"],["Locations","Tengah, Utara, Selatan, Timur, Sabah, Sarawak","Included"],["Main quantitative analysis","SEM as primary analysis; correlation only diagnostic","Revised"],["Client outcome instruments","WHODAS, Wellbeing/WHOQOL proxy, WAI-SR, CSQ-8, PCL-5","Revised"],["Theoretical lens","Realist Evaluation CMO, Donabedian, RE-AIM reporting","Included"],["Operational output","Streamlit dashboard, knowledge transfer, monitoring framework","Included"]],columns=["TOR Requirement","Implementation in App","Status"])
    st.dataframe(tor,use_container_width=True)
    st.markdown("<p class='small'>DASS-21 has been removed as the main outcome in this revised system to avoid mismatch with the proposed core outcome instruments.</p>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[2]:
    st.markdown("<div class='card'>",unsafe_allow_html=True); st.subheader("SEM Analysis Dashboard: Measurement + Structural Model")
    measurement,paths,r2,htmt=sem_tables()
    a,b=st.columns([1.15,1])
    with a:
        st.markdown("**Measurement Model**"); st.dataframe(measurement,use_container_width=True)
        st.markdown("**Structural Model**"); st.dataframe(paths,use_container_width=True)
    with b:
        st.markdown("**HTMT Discriminant Validity**"); st.dataframe(htmt.round(2),use_container_width=True)
        st.markdown("**R² Endogenous Constructs**"); st.dataframe(r2,use_container_width=True)
    nodes=["Capacity","Quality","Mechanism","Outcome"]; x=[.05,.35,.65,.95]; y=[.55,.70,.55,.70]
    fig=go.Figure()
    for i in range(3): fig.add_annotation(x=x[i+1],y=y[i+1],ax=x[i],ay=y[i],xref="paper",yref="paper",axref="paper",ayref="paper",showarrow=True,arrowhead=3,arrowsize=1.5,arrowwidth=4,arrowcolor="#FDE68A",text="")
    fig.add_annotation(x=.95,y=.70,ax=.35,ay=.70,xref="paper",yref="paper",axref="paper",ayref="paper",showarrow=True,arrowhead=3,arrowwidth=2,arrowcolor="#38BDF8",text="")
    for xi,yi,n in zip(x,y,nodes): fig.add_trace(go.Scatter(x=[xi],y=[yi],mode="markers+text",text=[n],textposition="middle center",marker=dict(size=92,color="#0F766E",line=dict(color="#FDE68A",width=3)),textfont=dict(color="white",size=15),hoverinfo="text",hovertext=[n]))
    for label,xi,yi in [("β=.81",.20,.68),("β=.76",.50,.68),("β=.73",.80,.68),("β=.24",.65,.82)]: fig.add_annotation(x=xi,y=yi,text=label,showarrow=False,font=dict(color="#FDE68A",size=16))
    fig.update_xaxes(visible=False,range=[0,1]); fig.update_yaxes(visible=False,range=[0,1]); fig.update_layout(title="SEM Path Diagram: Capacity → Quality → Mechanism → Outcome",height=430,paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",showlegend=False,margin=dict(l=10,r=10,t=60,b=10))
    st.plotly_chart(fig,use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[3]:
    st.markdown("<div class='card'>",unsafe_allow_html=True); st.subheader("Client Outcome Monitoring: T1, T2, T3")
    tm=pd.DataFrame({"Instrument":["WHODAS"]*3+["Wellbeing"]*3+["PCL-5"]*3,"Time":["T1 Intake","T2 Closure","T3 Follow-up"]*3,"Score":[qdf.WHODAS_T1.mean(),qdf.WHODAS_T2.mean(),qdf.WHODAS_T3.mean(),qdf.Wellbeing_T1.mean(),qdf.Wellbeing_T2.mean(),qdf.Wellbeing_T3.mean(),qdf.PCL5_T1.mean(),qdf.PCL5_T2.mean(),qdf.PCL5_T3.mean()]})
    st.plotly_chart(fig_style(px.line(tm,x="Time",y="Score",color="Instrument",markers=True,title="Longitudinal Client Outcome Trend")),use_container_width=True)
    a,b=st.columns(2)
    with a: st.plotly_chart(fig_style(px.box(qdf,x="zone",y="Client_Outcome_Index",color="zone",title="Outcome Distribution by Zone")),use_container_width=True)
    with b: st.plotly_chart(fig_style(px.bar(qdf.groupby("intervention_type",as_index=False).Client_Outcome_Index.mean().sort_values("Client_Outcome_Index"),x="Client_Outcome_Index",y="intervention_type",orientation="h",title="Average Outcome by Intervention Type")),use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[4]:
    st.markdown("<div class='card'>",unsafe_allow_html=True); st.subheader("RE-AIM and Realist CMO Integration")
    reaim=pd.DataFrame({"Dimension":["Reach","Effectiveness","Adoption","Implementation","Maintenance"],"Score":[min(100,len(qdf)/600*100),qdf.Client_Outcome_Index.mean(),qdf.Access_Responsiveness.mean(),(qdf.Rights_Based_Experience.mean()+qdf.Service_Quality.mean())/2,100-dropout]})
    fig=go.Figure(go.Scatterpolar(r=reaim.Score,theta=reaim.Dimension,fill="toself",line=dict(color="#FDE68A",width=3),name="RE-AIM")); fig.update_layout(polar=dict(radialaxis=dict(visible=True,range=[0,100])),title="RE-AIM Radar")
    c1,c2=st.columns([.9,1.1]); c1.plotly_chart(fig_style(fig,500),use_container_width=True)
    c2.dataframe(reaim.round(1),use_container_width=True)
    cm=idf.main_theme.value_counts().reset_index(); cm.columns=["Theme","Count"]
    st.plotly_chart(fig_style(px.bar(cm,x="Count",y="Theme",orientation="h",title="Qualitative Theme Frequency from 85 Informants")),use_container_width=True)
    st.dataframe(idf[["interview_id","zone","respondent_group","CMO_context","CMO_mechanism","CMO_outcome","main_theme","sentiment","priority"]],use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[5]:
    st.markdown("<div class='card'>",unsafe_allow_html=True); st.subheader("Zonal Drilldown")
    z=st.selectbox("Select zone",sorted(qdf.zone.unique())); zd=qdf[qdf.zone==z]
    c1,c2,c3,c4=st.columns(4); c1.metric("Respondents",len(zd)); c2.metric("Outcome",f"{zd.Client_Outcome_Index.mean():.1f}"); c3.metric("Quality",f"{zd.Service_Quality.mean():.1f}"); c4.metric("Dropout",f"{zd.dropout_status.eq('Ya').mean()*100:.1f}%")
    st.plotly_chart(fig_style(px.histogram(zd,x="respondent_group",color="intervention_type",barmode="group",title=f"Case Profile for {z}")),use_container_width=True)
    st.dataframe(zd,use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[6]:
    st.markdown("<div class='card'>",unsafe_allow_html=True); st.subheader("Scenario Simulator for Policy Planning")
    ppsi=st.slider("Additional PPsi / PPPsi capacity (%)",0,50,15); training=st.slider("Training and supervision improvement (%)",0,50,20); digital=st.slider("Digital triage and follow-up adoption (%)",0,50,20)
    uplift=0.18*ppsi+0.22*training+0.16*digital
    pred=min(100,avg_out+uplift/3)
    c1,c2,c3=st.columns(3); c1.metric("Current Outcome",f"{avg_out:.1f}"); c2.metric("Projected Outcome",f"{pred:.1f}",f"+{pred-avg_out:.1f}"); c3.metric("Estimated Dropout",f"{max(2,dropout-(ppsi+digital)/12):.1f}%")
    sim=pd.DataFrame({"Scenario":["Current","After capacity + training + digital follow-up"],"Outcome":[avg_out,pred],"Dropout":[dropout,max(2,dropout-(ppsi+digital)/12)]})
    st.plotly_chart(fig_style(px.bar(sim,x="Scenario",y="Outcome",text="Outcome",title="Projected Client Outcome under Scenario")),use_container_width=True)
    st.caption("Scenario values are illustrative for proposal demonstration only; final parameters must be calibrated using actual SEM coefficients and administrative records.")
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[7]:
    st.markdown("<div class='card'>",unsafe_allow_html=True); st.subheader("Evidence-Based Policy Actions")
    recs=pd.DataFrame([
        ["High","Capacity & workload","Tambah kapasiti PPsi/PPPsi atau susun semula triage bagi lokasi beban kes tinggi.","Expected impact through Capacity → Quality path."],
        ["High","Service quality","Latihan trauma-informed care, aliansi terapeutik dan standard dokumentasi kes.","Strong pathway Quality → Mechanism."],
        ["High","Outcome monitoring","Mandatkan T1/T2/T3 untuk WHODAS, Wellbeing, WAI, CSQ-8 dan PCL-5 selektif.","Needed for effectiveness evidence."],
        ["Medium","Digital follow-up","Automated reminder and follow-up dashboard for T3.","Improves Maintenance and reduces dropout."],
        ["Medium","Referral coordination","Standard rujukan antara JKM, KKM, PDRM, NGO and local support.","Improves mechanism and continuity."],
    ],columns=["Priority","Domain","Recommended Action","Evidence Logic"])
    st.dataframe(recs,use_container_width=True)
    st.plotly_chart(fig_style(px.treemap(recs,path=["Priority","Domain"],title="Policy Priority Map"),500),use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

with tabs[8]:
    st.markdown("<div class='card'>",unsafe_allow_html=True); st.subheader("Data Preview, Upload Template and Downloads")
    st.download_button("Download TOR-aligned Excel template",make_template(qdf_demo,idf_demo),"JKM_SEM_TOR_Aligned_Template.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.download_button("Download current questionnaire CSV",qdf.to_csv(index=False).encode("utf-8"),"questionnaire_current.csv","text/csv")
    st.download_button("Download current interview CSV",idf.to_csv(index=False).encode("utf-8"),"interview_current.csv","text/csv")
    st.dataframe(qdf,use_container_width=True); st.dataframe(idf,use_container_width=True)
    st.markdown("</div>",unsafe_allow_html=True)

st.markdown("---")
st.caption("JKM SEM Impact Intelligence | Simulation dashboard aligned to TOR | SEM outputs illustrative until replaced with actual field-data model estimates")
