
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Referenzdaten-Erfassung", layout="centered")
st.title("📊 Referenzdaten zur Lumineszenzmarkierung")

# CSV-Datei definieren
CSV_FILE = "referenzdaten.csv"

# Wenn die Datei nicht existiert, erstellen wir sie mit Headern
if not os.path.exists(CSV_FILE):
    df_init = pd.DataFrame(columns=[
        "LOT_Nummer", "Naturfaser_%", "Schwarz_%", "Weiß_%", "Indigo_%",
        "Dosierung_Markierfaser_%", "Lumineszenzanteil_in_Faser_%", "Baumwollanteil_im_Garn_%",
        "Reiner_Marker_in_Baumwolle_ppm", "Effektive_Dosierung_ppm",
        "Countwert", "Aschefarbe_RGB"
    ])
    df_init.to_csv(CSV_FILE, index=False)

st.subheader("➕ Neue Referenzprobe eingeben")

# Variante 2: Vordefinierte Grautöne mit visueller Vorschau
farben = {
    "Light Gray": "#D3D3D3",
    "Silver": "#C0C0C0",
    "Charcoal": "#36454F",
    "White Gray": "#F5F5F5",
    "Neutral Gray": "#B8B8BC"
}

option = st.radio("Aschefarbe auswählen:", options=list(farben.keys()))

selected_hex = farben[option]
st.markdown(
    f"<div style='width:100px;height:30px;background-color:{selected_hex};border:1px solid #000;margin-bottom:10px'></div>",
    unsafe_allow_html=True
)

with st.form("eingabe_formular"):
    col1, col2 = st.columns(2)
    with col1:
        lot = st.text_input("LOT-Nummer")
        natur = st.number_input("Anteil Naturfaser (%)", 0.0, 100.0, step=0.1)
        schwarz = st.number_input("Anteil schwarze Faser (%)", 0.0, 100.0, step=0.1)
        weiss = st.number_input("Anteil weiße Faser (%)", 0.0, 100.0, step=0.1)
        indigo = st.number_input("Anteil Indigo-Faser (%)", 0.0, 100.0, step=0.1)
    with col2:
        dosierung = st.number_input("Dosierung Markierfaser in Baumwolle (%)", 0.0, 1.0, step=0.001)
        lumianzteil = st.number_input("Lumineszenzanteil in der Faser (%)", 0.0, 100.0, value=4.0, step=0.1)
        baumwollanteil = st.number_input("Baumwollanteil im Garn (%)", 0.0, 100.0, value=20.0, step=0.1)
        countwert = st.number_input("Countwert (Lumineszenzsignal)", 0, 100000, step=1)

    submitted = st.form_submit_button("✅ Eintrag speichern")

    if submitted:
        marker_baumwolle_ppm = dosierung * (lumianzteil / 100) * 10000
        effektive_dosierung_ppm = marker_baumwolle_ppm * (baumwollanteil / 100)

        neue_zeile = pd.DataFrame([{
            "LOT_Nummer": lot,
            "Naturfaser_%": natur,
            "Schwarz_%": schwarz,
            "Weiß_%": weiss,
            "Indigo_%": indigo,
            "Dosierung_Markierfaser_%": dosierung,
            "Lumineszenzanteil_in_Faser_%": lumianzteil,
            "Baumwollanteil_im_Garn_%": baumwollanteil,
            "Reiner_Marker_in_Baumwolle_ppm": round(marker_baumwolle_ppm, 2),
            "Effektive_Dosierung_ppm": round(effektive_dosierung_ppm, 2),
            "Countwert": countwert,
            "Aschefarbe_RGB": selected_hex
        }])

        neue_zeile.to_csv(CSV_FILE, mode='a', header=False, index=False)
        st.success(f"Eintrag für {lot} gespeichert!")

st.subheader("📁 Aktuelle Referenzdaten")
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Noch keine Daten vorhanden.")
