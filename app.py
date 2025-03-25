import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

SHEET_ID = "1KXuZrDUBTJtNIh9o-9mlepPyukpVyUUC9oeNW5RJYy0"
SHEET_NAME = "Sheet1"
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

st.title("📊 Referenzdaten eingeben (Google Sheets)")

columns = [
    "LOT_Number", "Natural_Fiber_%", "Black_Fiber_%", "White_Fiber_%", "Indigo_Fiber_%",
    "Mastermix_Dosage_%", "Luminescent_Content_in_Fiber_%", "Marked_R_Cotton_in_Sample_%",
    "Marker_in_Marked_Sample_ppm", "Effective_Dosage_ppm", "Emission_Count", "Ash_Bodycolor_RGB"
]

# Farbwahl
color_hex = st.color_picker("Ash/sample bodycolor", value="#D3D3D3")

with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        lot = st.text_input("LOT number")
        natural = st.number_input("Natural fiber content (%)", 0.0, 100.0)
        black = st.number_input("Black fiber content (%)", 0.0, 100.0)
        white = st.number_input("White fiber content (%)", 0.0, 100.0)
        indigo = st.number_input("Indigo fiber content (%)", 0.0, 100.0)
    with col2:
        dosage = st.number_input("Mastermix Dosage (%)", 0.0, 1.0)
        lum_content = st.number_input("Luminescent content in fiber (%)", 0.0, 100.0)
        cotton_share = st.number_input("Marked R-Cotton in Sample (%)", 0.0, 100.0)
        emission = st.number_input("Emission count", 0, 100000)

    submitted = st.form_submit_button("✅ Save entry")

    if submitted:
        total_fiber = natural + black + white + indigo
        if abs(total_fiber - 100.0) > 0.1:
            st.error("Fiber percentages must sum to 100%.")
        else:
            r, g, b = [int(color_hex[i:i+2], 16) for i in (1, 3, 5)]
            rgb_string = f"rgb({r},{g},{b})"

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

            data = pd.DataFrame(sheet.get_all_records())
            updated_df = pd.concat([data, new_entry], ignore_index=True)
            sheet.clear()
            set_with_dataframe(sheet, updated_df)
            st.success("✅ Entry saved to Google Sheet.")