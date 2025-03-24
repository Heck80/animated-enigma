
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

# Farbauswahl mit Vorschau
def color_preview_option(rgb_string, name):
    return f"{name} ▉ ({rgb_string})"

farben = {
    "Schneeweiß": "rgb(250,250,250)",
    "Lichtgrau": "rgb(220,220,220)",
    "Grau": "rgb(180,180,180)",
    "Mittelgrau": "rgb(140,140,140)",
    "Dunkelgrau": "rgb(100,100,100)",
    "Aschgrau": "rgb(80,80,80)",
    "Ebenholz": "rgb(50,40,40)",
    "Elfenbein": "rgb(245,240,230)",
    "Zementweiß": "rgb(235,235,235)",
    "Blaugrau": "rgb(190,195,200)"
}

farboptionen = [color_preview_option(rgb, name) for name, rgb in farben.items()]
farbauswahl = st.selectbox("Aschefarbe auswählen:", options=farboptionen)

# Extrahiere RGB-Wert
selected_rgb = farbauswahl.split("(")[-1].replace(")", "")

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
            "Aschefarbe_RGB": selected_rgb
        }])

        neue_zeile.to_csv(CSV_FILE, mode='a', header=False, index=False)
        st.success(f"Eintrag für {lot} gespeichert!")

st.subheader("📁 Aktuelle Referenzdaten")
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Noch keine Daten vorhanden.")
