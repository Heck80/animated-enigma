
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="050-000056 Reference Data Collection", layout="centered")
st.title("📊 050-000056 Reference Data Collection")

# Define CSV file
CSV_FILE = "referenzdaten.csv"

# Create file if it doesn't exist
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=[
        "LOT_Number", "Natural_Fiber_%", "Black_Fiber_%", "White_Fiber_%", "Indigo_Fiber_%",
        "Mastermix_Dosage_%", "Luminescent_Content_in_Fiber_%", "Marked_R_Cotton_in_Sample_%",
        "Marker_in_Cotton_ppm", "Effective_Dosage_ppm",
        "Emission_Count", "Ash_Bodycolor_RGB"
    ])
    df_init.to_csv(CSV_FILE, index=False)

st.subheader("➕ Enter New Reference Sample")

# Variant 1: Free color selection using color_picker
selected_color = st.color_picker("Bodycolor of ash/sample:", value="#D3D3D3")

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
        lum_content = st.number_input("Luminescent content in fiber (%)", 0.0, 100.0, value=4.0, step=0.1)
        cotton_share = st.number_input("Marked R-Cotton in Sample (%)", 0.0, 100.0, value=20.0, step=0.1)
        count = st.number_input("Emission count (luminescence signal)", 0, 100000, step=1)

    submitted = st.form_submit_button("✅ Save entry")

    if submitted:
        total_fiber = natural + black + white + indigo
        if abs(total_fiber - 100.0) > 0.1:
            st.error("The total of Natural, Black, White and Indigo fiber percentages must equal 100%.")
        else:
            marker_ppm = dosage * (lum_content / 100) * 10000
            effective_ppm = marker_ppm * (cotton_share / 100)

            new_row = pd.DataFrame([{
                "LOT_Number": lot,
                "Natural_Fiber_%": natural,
                "Black_Fiber_%": black,
                "White_Fiber_%": white,
                "Indigo_Fiber_%": indigo,
                "Mastermix_Dosage_%": dosage,
                "Luminescent_Content_in_Fiber_%": lum_content,
                "Marked_R_Cotton_in_Sample_%": cotton_share,
                "Marker_in_Cotton_ppm": round(marker_ppm, 2),
                "Effective_Dosage_ppm": round(effective_ppm, 2),
                "Emission_Count": count,
                "Ash_Bodycolor_RGB": selected_color
            }])

            new_row.to_csv(CSV_FILE, mode='a', header=False, index=False)
            st.success(f"Entry for {lot} saved!")

st.subheader("📁 Current Reference Data")
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data available yet.")
