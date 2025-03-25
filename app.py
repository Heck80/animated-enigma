
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="050-000056 Reference Data Collection", layout="centered")
st.title("📊 050-000056 Reference Data Collection")

CSV_FILE = r"C:\Users\tobias.herzog\Tailorlux integrity solutions\Qualität - Artikelmanagement\050 - Träger\050-000056\04_Messdaten Kundenmuster\referenzdaten.csv"


columns = [
    "LOT_Number",
    "Natural_Fiber_%",
    "Black_Fiber_%",
    "White_Fiber_%",
    "Indigo_Fiber_%",
    "Mastermix_Dosage_%",
    "Luminescent_Content_in_Fiber_%",
    "Marked_R_Cotton_in_Sample_%",
    "Marker_in_Marked_Sample_ppm",
    "Effective_Dosage_ppm",
    "Emission_Count",
    "Ash_Bodycolor_RGB"
]

# Create CSV with correct headers if not exists
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=columns).to_csv(CSV_FILE, index=False)

st.subheader("➕ Enter New Reference Sample")

# Color picker
color_hex = st.color_picker("Ash/sample bodycolor", value="#D3D3D3")
r, g, b = [int(color_hex[i:i+2], 16) for i in (1, 3, 5)]
rgb_string = f"rgb({r},{g},{b})"

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
        lum_content = st.number_input("Luminescent content in fiber (%)", 0.0, 100.0, step=0.1)
        cotton_share = st.number_input("Marked R-Cotton in Sample (%)", 0.0, 100.0, step=0.1)
        emission = st.number_input("Emission count (luminescence signal)", 0, 100000, step=1)

    submitted = st.form_submit_button("✅ Save entry")

    if submitted:
        total_fiber = natural + black + white + indigo
        if abs(total_fiber - 100.0) > 0.1:
            st.error("Fiber percentages must sum to 100%.")
        else:
            marker_ppm = dosage * lum_content * 100
            effective_ppm = marker_ppm * (cotton_share / 100)

            new_entry = pd.DataFrame([{
                "LOT_Number": lot,
                "Natural_Fiber_%": natural,
                "Black_Fiber_%": black,
                "White_Fiber_%": white,
                "Indigo_Fiber_%": indigo,
                "Mastermix_Dosage_%": dosage,
                "Luminescent_Content_in_Fiber_%": lum_content,
                "Marked_R_Cotton_in_Sample_%": cotton_share,
                "Marker_in_Marked_Sample_ppm": round(marker_ppm, 2),
                "Effective_Dosage_ppm": round(effective_ppm, 2),
                "Emission_Count": emission,
                "Ash_Bodycolor_RGB": rgb_string
            }])

            new_entry.to_csv(CSV_FILE, mode="a", index=False, header=False)
            st.success(f"Entry for LOT {lot} saved.")

st.subheader("📁 Current Reference Data")
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    st.dataframe(df, use_container_width=True)

    # 🗑️ Löschfunktion basierend auf LOT_Number
    st.subheader("🗑️ Delete an Entry")
    unique_lots = df["LOT_Number"].dropna().unique().tolist()
    if unique_lots:
        lot_to_delete = st.selectbox("Select LOT to delete:", unique_lots)
        if st.button("❌ Delete selected entry"):
            df = df[df["LOT_Number"] != lot_to_delete]
            df.to_csv(CSV_FILE, index=False)
            st.success(f"Entry with LOT {lot_to_delete} has been deleted.")
            st.rerun()
    else:
        st.info("No LOTs available to delete.")

else:
    st.info("No data available.")
