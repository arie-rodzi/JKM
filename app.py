import streamlit as st
import pandas as pd

st.set_page_config(page_title="JKM PsyCounsel Dashboard", layout="wide")

st.title("Sistem Pemantauan Keberkesanan Psikologi & Kaunseling JKM")
st.markdown("Upload fail Excel anda bila data sebenar telah tersedia. Tidak wajib upload semasa buka dashboard.")

uploaded_file = st.file_uploader(
    "Upload fail Excel (.xlsx) — optional",
    type=["xlsx"]
)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("Data berjaya dimuat naik.")
    st.dataframe(df, use_container_width=True)

    st.subheader("Ringkasan Data")
    st.write(f"Jumlah rekod: {len(df)}")
else:
    st.info("Tiada fail dimuat naik lagi. Dashboard sedia digunakan. Upload bila-bila masa apabila data telah tersedia.")
