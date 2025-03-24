
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="050-000056 Reference Data Collection", layout="centered")
st.title("📊 050-000056 Reference Data Collection")

# CSV-Datei definieren
CSV_FILE = "referenzdaten.csv"

# Wenn die Datei nicht existiert, erstellen wir sie mit Headern
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=[
        "LOT_Number", "Natural_Fiber_%", "Black_Fiber_%", "White_Fiber_%", "Indigo_Fiber_%",
        "Mastermix_Dosage_%", "Luminescent_Content_in_Fiber_%", "Marked_R_Cotton_in_Sample_%",
        "Marker_in_Cotton_ppm", "Effective_Dosage_ppm",
        "Emission_Count", "Ash_Bodycolor_RGB"
    ])
    df_init.to_csv(CSV_FILE, index=False)

st.subheader("➕ Enter New Reference Sample")

# Farbauswahl mit Hinweis
st.markdown("**Ash/sample bodycolor**")
selected_color = st.color_picker("Pick or confirm ash color", value="#D3D3D3")
if not selected_color or selected_color == "#000000":
    st.warning("Please confirm or adjust the ash color value.")
st.markdown(f"Selected: `{selected_color}`")

with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        lot = st.text_input("LOT number")
        natural = st.number_input("Natural fiber content (%)", 0.0, 100.0, step=0.1)
        black = st.number_input("Black fiber content (%)", 0.0, 100.0, step=0.1)
        white = st.number_input("White fiber content (%)", 0.0, 100.0, step=0.1)
        indigo = st.number_input("Indigo fiber content (%)", 0.0, 100.0, step=0.1)
    with col2:
        dosage = st.number_input("Mastermix Dosage (%)", 0.0, 1.0, step=0.001)
        lumianzteil = st.number_input("Luminescent content in fiber (%)", 0.0, 100.0, value=4.0, step=0.1)
        cotton_share = st.number_input("Marked R-Cotton in Sample (%)", 0.0, 100.0, value=20.0, step=0.1)
        countwert = st.number_input("Emission count (luminescence signal)", 0, 100000, step=1)

    submitted = st.form_submit_button("✅ Save entry")

    if submitted:
        total_fiber = natural + black + white + indigo
        if abs(total_fiber - 100.0) > 0.1:
            st.error("Fiber percentages must add up to 100%.")
        else:
            marker_baumwolle_ppm = dosage * (lumianzteil / 100) * 10000
            effektive_dosierung_ppm = marker_baumwolle_ppm * (cotton_share / 100)

            rgb_str = f"rgb({int(selected_color[1:3],16)},{int(selected_color[3:5],16)},{int(selected_color[5:7],16)})"

            neue_zeile = pd.DataFrame([{
                "LOT_Number": lot,
                "Natural_Fiber_%": natural,
                "Black_Fiber_%": black,
                "White_Fiber_%": white,
                "Indigo_Fiber_%": indigo,
                "Mastermix_Dosage_%": dosage,
                "Luminescent_Content_in_Fiber_%": lumianzteil,
                "Marked_R_Cotton_in_Sample_%": cotton_share,
                "Marker_in_Cotton_ppm": round(marker_baumwolle_ppm, 2),
                "Effective_Dosage_ppm": round(effektive_dosierung_ppm, 2),
                "Emission_Count": countwert,
                "Ash_Bodycolor_RGB": rgb_str
            }])

            neue_zeile.to_csv(CSV_FILE, mode='a', header=False, index=False)
            st.success(f"Entry for {lot} saved.")

st.subheader("📁 Current Reference Data")
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data available.")

# 🗑️ Delete Section
st.subheader("🗑️ Delete Existing Entry")
if os.path.exists(CSV_FILE):
    df_existing = pd.read_csv(CSV_FILE)
    if not df_existing.empty:
        lots = df_existing["LOT_Number"].astype(str).unique().tolist()
        lot_to_delete = st.selectbox("Select LOT number to delete:", options=lots)
        if st.button("❌ Delete selected entry"):
            df_new = df_existing[df_existing["LOT_Number"].astype(str) != lot_to_delete]
            df_new.to_csv(CSV_FILE, index=False)
            st.success(f"Entry with LOT number '{lot_to_delete}' has been deleted.")
            st.rerun()
    else:
        st.info("No entries to delete.")
