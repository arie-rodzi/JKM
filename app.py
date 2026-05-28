import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter

st.set_page_config(
    page_title="JKM PsyCounsel Impact Dashboard",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "JKM_PsyCounsel_Questionnaire_and_Simulation.xlsx"

PREMIUM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: radial-gradient(circle at top left, #12355B 0, #071A2F 26%, #06111F 55%, #040812 100%); color:#F8FAFC; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #06111F 0%, #0B2545 100%); border-right: 1px solid rgba(247,215,116,.25); }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
.hero {
    padding: 28px 32px; border-radius: 28px;
    background: linear-gradient(135deg, rgba(247,215,116,.18), rgba(255,255,255,.06) 35%, rgba(11,37,69,.80));
    border: 1px solid rgba(247,215,116,.35);
    box-shadow: 0 24px 80px rgba(0,0,0,.35);
}
.hero h1 { font-size: 2.6rem; line-height:1.05; margin:0; color:#F7D774; letter-spacing:-1.5px; }
.hero p { color:#DDE7F3; font-size: 1.05rem; margin-top:.7rem; }
.kpi {
    padding: 18px 18px; border-radius: 22px;
    background: linear-gradient(180deg, rgba(255,255,255,.10), rgba(255,255,255,.045));
    border: 1px solid rgba(255,255,255,.14);
    box-shadow: 0 14px 50px rgba(0,0,0,.26);
}
.kpi .label { color:#AFC2D6; font-size:.82rem; font-weight:700; text-transform:uppercase; letter-spacing:.09em; }
.kpi .value { color:#FFFFFF; font-size:1.75rem; font-weight:900; margin-top:.2rem; }
.kpi .note { color:#F7D774; font-size:.82rem; margin-top:.25rem; }
.section-title { color:#F7D774; font-size:1.35rem; font-weight:900; margin: 18px 0 10px; }
.card {
    padding: 20px; border-radius: 24px;
    background: rgba(255,255,255,.075);
    border: 1px solid rgba(255,255,255,.13);
    box-shadow: 0 18px 55px rgba(0,0,0,.25);
}
.badge { display:inline-block; padding: 6px 12px; border-radius: 999px; background: rgba(247,215,116,.15); color:#F7D774; border:1px solid rgba(247,215,116,.35); font-weight:800; }
.small-muted { color:#B8C7D8; font-size:.88rem; }
hr { border: 0; border-top: 1px solid rgba(255,255,255,.13); margin: 1.2rem 0; }
[data-testid="stMetricValue"] { color:#F7D774; }
</style>
"""
st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data(path):
    quant = pd.read_excel(path, sheet_name="03_Sim_Quant_600")
    qual = pd.read_excel(path, sheet_name="04_Sim_Interview_90")
    questions = pd.read_excel(path, sheet_name="01_Questionnaire")
    interviews = pd.read_excel(path, sheet_name="02_Interview_Guide")
    return quant, qual, questions, interviews

quant, qual, questions, interview_guide = load_data(DATA_PATH)

st.sidebar.markdown("### ✨ JKM PsyCounsel")
st.sidebar.caption("Premium impact dashboard prototype")
selected_zones = st.sidebar.multiselect("Pilih zon", sorted(quant["Zon"].unique()), default=sorted(quant["Zon"].unique()))
selected_intervention = st.sidebar.multiselect("Jenis intervensi", sorted(quant["Jenis_Intervensi"].unique()), default=sorted(quant["Jenis_Intervensi"].unique()))
selected_status = st.sidebar.multiselect("Status keberkesanan", sorted(quant["Status"].unique()), default=sorted(quant["Status"].unique()))
view = st.sidebar.radio("Paparan", ["Executive", "RE-AIM", "CMO", "Kualitatif", "Instrumen & Data"], index=0)

df = quant[quant["Zon"].isin(selected_zones) & quant["Jenis_Intervensi"].isin(selected_intervention) & quant["Status"].isin(selected_status)].copy()
qf = qual[qual["Zon"].isin(selected_zones)].copy()

st.markdown("""
<div class="hero">
  <span class="badge">Expected Result Prototype • Simulasi 600 + 90</span>
  <h1>Sistem Pemantauan Keberkesanan Psikologi & Kaunseling JKM</h1>
  <p>Dashboard premium untuk memaparkan impak kajian melalui RE-AIM, Realist Evaluation CMO, perubahan T1–T2–T3, analisis zon dan dapatan temu bual.</p>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("Tiada data selepas tapisan. Sila ubah filter.")
    st.stop()

avg_overall = df["Overall_Effectiveness"].mean()
improve_dass = df["DASS_T1"].mean() - df["DASS_T3"].mean()
improve_who = df["WHODAS_T1"].mean() - df["WHODAS_T3"].mean()
well_gain = df["Wellbeing_T3"].mean() - df["Wellbeing_T1"].mean()

k1, k2, k3, k4 = st.columns(4)
for col, label, value, note in [
    (k1, "Overall Effectiveness", f"{avg_overall:,.1f}%", "Indeks komposit expected result"),
    (k2, "DASS Reduction", f"{improve_dass:,.1f}", "Penurunan tekanan T1→T3"),
    (k3, "WHODAS Improvement", f"{improve_who:,.1f}", "Peningkatan fungsi harian"),
    (k4, "Wellbeing Gain", f"+{well_gain:,.1f}", "Kesejahteraan T1→T3"),
]:
    col.markdown(f"<div class='kpi'><div class='label'>{label}</div><div class='value'>{value}</div><div class='note'>{note}</div></div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

premium_template = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.03)",
    font=dict(color="#EAF2FF"),
    colorway=["#F7D774", "#60A5FA", "#34D399", "#F472B6", "#A78BFA", "#FB923C"],
)

def style_fig(fig, height=420):
    fig.update_layout(**premium_template, height=height, margin=dict(l=20, r=20, t=60, b=35), legend=dict(orientation="h", y=-0.18))
    return fig

if view == "Executive":
    st.markdown("<div class='section-title'>Executive Impact Overview</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1.15, .85])
    zone_avg = df.groupby("Zon", as_index=False)["Overall_Effectiveness"].mean().sort_values("Overall_Effectiveness", ascending=False)
    fig1 = px.bar(zone_avg, x="Zon", y="Overall_Effectiveness", text_auto=".1f", title="Skor Keberkesanan Keseluruhan Mengikut Zon")
    c1.plotly_chart(style_fig(fig1), use_container_width=True)

    status_count = df["Status"].value_counts().reset_index()
    status_count.columns = ["Status", "Jumlah"]
    fig2 = px.pie(status_count, names="Status", values="Jumlah", hole=.62, title="Komposisi Status Keberkesanan")
    c2.plotly_chart(style_fig(fig2), use_container_width=True)

    st.markdown("<div class='section-title'>Perubahan T1–T2–T3</div>", unsafe_allow_html=True)
    trend = pd.DataFrame({
        "Masa": ["T1 Intake", "T2 Akhir", "T3 Susulan"],
        "DASS": [df["DASS_T1"].mean(), df["DASS_T2"].mean(), df["DASS_T3"].mean()],
        "WHODAS": [df["WHODAS_T1"].mean(), df["WHODAS_T2"].mean(), df["WHODAS_T3"].mean()],
        "Wellbeing": [df["Wellbeing_T1"].mean(), df["Wellbeing_T2"].mean(), df["Wellbeing_T3"].mean()],
    })
    long = trend.melt("Masa", var_name="Indikator", value_name="Skor")
    fig3 = px.line(long, x="Masa", y="Skor", color="Indikator", markers=True, title="Trajectory Expected Result: Tekanan, Fungsi dan Kesejahteraan")
    st.plotly_chart(style_fig(fig3, 430), use_container_width=True)

elif view == "RE-AIM":
    st.markdown("<div class='section-title'>RE-AIM Performance Matrix</div>", unsafe_allow_html=True)
    reaim_cols = ["REACH", "EFFECTIVENESS", "ADOPTION", "IMPLEMENTATION", "MAINTENANCE"]
    reaim = df.groupby("Zon")[reaim_cols].mean().reset_index()
    fig = go.Figure()
    for _, row in reaim.iterrows():
        fig.add_trace(go.Scatterpolar(r=[row[c] for c in reaim_cols], theta=reaim_cols, fill="toself", name=row["Zon"]))
    fig.update_polars(radialaxis=dict(visible=True, range=[0,100]))
    fig.update_layout(title="Radar RE-AIM Mengikut Zon")
    st.plotly_chart(style_fig(fig, 560), use_container_width=True)
    st.dataframe(reaim.style.format({c:"{:.1f}" for c in reaim_cols}), use_container_width=True)

elif view == "CMO":
    st.markdown("<div class='section-title'>Realist Evaluation: Context–Mechanism–Outcome</div>", unsafe_allow_html=True)
    cmo_cols = ["CMO_CONTEXT", "CMO_MECHANISM", "CMO_OUTCOME"]
    cmo = df.groupby("Zon")[cmo_cols].mean().reset_index()
    fig = px.imshow(cmo.set_index("Zon"), text_auto=".1f", aspect="auto", title="Heatmap CMO Mengikut Zon")
    st.plotly_chart(style_fig(fig, 500), use_container_width=True)
    st.markdown("<div class='card'><b>Interpretasi automatik:</b> Zon dengan mekanisme tinggi tetapi outcome sederhana menandakan hubungan kaunselor-klien baik, namun faktor konteks seperti akses, masa menunggu atau susulan masih perlu diperkukuh.</div>", unsafe_allow_html=True)

elif view == "Kualitatif":
    st.markdown("<div class='section-title'>Analisis Temu Bual 90 Peserta</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    tema = qf["Tema_Utama"].value_counts().reset_index()
    tema.columns = ["Tema", "Bilangan"]
    fig1 = px.bar(tema.head(10), x="Bilangan", y="Tema", orientation="h", title="Tema Utama Temu Bual")
    c1.plotly_chart(style_fig(fig1, 470), use_container_width=True)
    sent = qf.groupby(["Zon", "Sentimen"]).size().reset_index(name="Bilangan")
    fig2 = px.bar(sent, x="Zon", y="Bilangan", color="Sentimen", barmode="group", title="Sentimen Dapatan Kualitatif Mengikut Zon")
    c2.plotly_chart(style_fig(fig2, 470), use_container_width=True)
    st.dataframe(qf[["Interview_ID","Zon","Kategori_Peserta","Tema_Utama","CMO_Dimensi","RE-AIM_Dimensi","Sentimen","Petikan_Ringkas_Simulasi"]], use_container_width=True, height=360)

elif view == "Instrumen & Data":
    st.markdown("<div class='section-title'>Instrumen, Soalan dan Data Simulasi</div>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Questionnaire", "Interview Guide", "Simulated Data"])
    with tab1:
        st.dataframe(questions, use_container_width=True, height=420)
    with tab2:
        st.dataframe(interview_guide, use_container_width=True, height=420)
    with tab3:
        st.dataframe(df, use_container_width=True, height=420)

st.markdown("<hr>", unsafe_allow_html=True)
st.caption("Nota: Semua data dalam prototype ini ialah simulasi untuk expected result dan demonstrasi dashboard sahaja.")
