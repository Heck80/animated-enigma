
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Reference Data Entry", layout="centered")
st.title("📊 Luminescent Marker Reference Data")

# Define CSV file
CSV_FILE = "referenzdaten.csv"

# If file doesn't exist, create it with headers
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=[
        "LOT_Number", "Natural_Fiber_%", "Black_Fiber_%", "White_Fiber_%", "Indigo_Fiber_%",
        "Marker_Fiber_Dosage_%", "Luminescent_Content_in_Fiber_%", "Cotton_Content_in_Yarn_%",
        "Pure_Marker_in_Cotton_ppm", "Effective_Dosage_ppm",
        "Emission_Count", "Ash_Bodycolor_RGB"
    ])
    df_init.to_csv(CSV_FILE, index=False)

st.subheader("➕ Enter a new reference sample")

# Color picker input
selected_color = st.color_picker("Bodycolor of ash/sample", value="#D3D3D3")

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        lot = st.text_input("LOT number")
        natural = st.number_input("Natural fiber (%)", 0.0, 100.0, step=0.1)
        black = st.number_input("Black fiber (%)", 0.0, 100.0, step=0.1)
        white = st.number_input("White fiber (%)", 0.0, 100.0, step=0.1)
        indigo = st.number_input("Indigo fiber (%)", 0.0, 100.0, step=0.1)
    with col2:
        dosage = st.number_input("Marker fiber dosage in cotton (%)", 0.0, 1.0, step=0.001)
        lum_percent = st.number_input("Luminescent content in fiber (%)", 0.0, 100.0, value=4.0, step=0.1)
        cotton_content = st.number_input("Cotton content in yarn (%)", 0.0, 100.0, value=20.0, step=0.1)
        count = st.number_input("Emission count (luminescence)", 0, 100000, step=1)

    submitted = st.form_submit_button("✅ Save entry")

    if submitted:
        marker_in_cotton_ppm = dosage * (lum_percent / 100) * 10000
        effective_dosage_ppm = marker_in_cotton_ppm * (cotton_content / 100)

        new_entry = pd.DataFrame([{
            "LOT_Number": lot,
            "Natural_Fiber_%": natural,
            "Black_Fiber_%": black,
            "White_Fiber_%": white,
            "Indigo_Fiber_%": indigo,
            "Marker_Fiber_Dosage_%": dosage,
            "Luminescent_Content_in_Fiber_%": lum_percent,
            "Cotton_Content_in_Yarn_%": cotton_content,
            "Pure_Marker_in_Cotton_ppm": round(marker_in_cotton_ppm, 2),
            "Effective_Dosage_ppm": round(effective_dosage_ppm, 2),
            "Emission_Count": count,
            "Ash_Bodycolor_RGB": selected_color
        }])

        new_entry.to_csv(CSV_FILE, mode='a', header=False, index=False)
        st.success(f"Entry for {lot} saved!")

st.subheader("📁 Current reference data")
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data available yet.")
