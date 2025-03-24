
import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
import base64

st.set_page_config(page_title="050-000056 Advanced Dosage Prediction", layout="centered")
st.title("🧪 Predict Dosage from Emission and Sample Description")

CSV_FILE = "referenzdaten.csv"

if not os.path.exists(CSV_FILE):
    st.error("Reference data file not found. Please use App 1 to create it first.")
else:
    df = pd.read_csv(CSV_FILE)

    if df.empty:
        st.warning("Reference data is empty.")
    else:
        st.subheader("🔍 Describe Your Sample")

        col1, col2 = st.columns(2)
        with col1:
            emission_count = st.number_input("Emission count", min_value=0, max_value=100000, step=1)
            ash_color = st.color_picker("Ash/sample bodycolor", value="#D3D3D3")
        with col2:
            natural = st.number_input("Natural fiber content (%)", 0.0, 100.0, step=0.1)
            black = st.number_input("Black fiber content (%)", 0.0, 100.0, step=0.1)
            white = st.number_input("White fiber content (%)", 0.0, 100.0, step=0.1)
            indigo = st.number_input("Indigo fiber content (%)", 0.0, 100.0, step=0.1)

        submitted = st.button("🔎 Predict Dosage")

        if submitted:
            total_fiber = natural + black + white + indigo
            if abs(total_fiber - 100.0) > 0.1:
                st.error("Fiber contents must sum to 100%.")
            else:
                # RGB aus Hex extrahieren
                ash_rgb = tuple(int(ash_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                r, g, b = ash_rgb

                # RGB-Werte aus gespeicherter Spalte extrahieren
                df["R"] = df["Ash_Bodycolor_RGB"].str.extract(r'rgb\((\d+),')[0].astype(float)
                df["G"] = df["Ash_Bodycolor_RGB"].str.extract(r'rgb\(\d+,(\d+),')[0].astype(float)
                df["B"] = df["Ash_Bodycolor_RGB"].str.extract(r'rgb\(\d+,\d+,(\d+)\)')[0].astype(float)

                feature_cols = ["Emission_Count", "Natural_Fiber_%", "Black_Fiber_%", "White_Fiber_%", "Indigo_Fiber_%", "R", "G", "B"]
                if not all(col in df.columns for col in feature_cols):
                    st.error("Some required columns are missing in the reference data.")
                else:
                    X = df[feature_cols].values
                    y = df["Effective_Dosage_ppm"].values

                    model = LinearRegression()
                    model.fit(X, y)

                    input_features = [[emission_count, natural, black, white, indigo, r, g, b]]
                    prediction = model.predict(input_features)[0]

                    st.success(f"📌 Estimated Dosage: **{round(prediction, 2)} ppm**")

                    # Optionale Visualisierung (nur Count vs Dosierung)
                    st.subheader("📊 Reference Plot (Count vs Dosage)")
                    fig, ax = plt.subplots()
                    ax.scatter(df["Emission_Count"], y, color="gray", label="Reference data")
                    ax.set_xlabel("Emission Count")
                    ax.set_ylabel("Effective Dosage (ppm)")
                    ax.axvline(emission_count, color="red", linestyle="--", label="Your input")
                    ax.legend()
                    st.pyplot(fig)

        # CSV Download Button
        st.subheader("📥 Download Reference Data")
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="referenzdaten.csv">📄 Download referenzdaten.csv</a>'
        st.markdown(href, unsafe_allow_html=True)
