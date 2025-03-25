import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import gspread
from gspread.auth import authorize

# OAuth-Flow starten
gc = authorize()

SHEET_ID = "1KXuZrDUBTJtNIh9o-9mlepPyukpVyUUC9oeNW5RJYy0"
SHEET_NAME = "Sheet1"
sheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

df = pd.DataFrame(sheet.get_all_records())

st.set_page_config(page_title="050-000056 Weighted Regression", layout="centered")
st.title("📈 Dosage Prediction via Smart Weighted Regression")

if df.empty or len(df) < 4:
    st.warning("Nicht genug Referenzdaten für Regression. Bitte über App 1 Daten hinzufügen.")
else:
    st.subheader("🔢 Neue Probe erfassen")

    col1, col2 = st.columns(2)
    with col1:
        emission_count = st.number_input("Emission count", min_value=0, step=1)
        natural = st.number_input("Natural fiber (%)", 0.0, 100.0)
        black = st.number_input("Black fiber (%)", 0.0, 100.0)
    with col2:
        white = st.number_input("White fiber (%)", 0.0, 100.0)
        indigo = st.number_input("Indigo fiber (%)", 0.0, 100.0)

    total_fiber = natural + black + white + indigo
    if abs(total_fiber - 100.0) > 0.1:
        st.error("Faseranteile müssen insgesamt 100% ergeben.")
    else:
        X_input = np.array([[emission_count]])
        prediction = 0
        weights = {
            "Natural_Fiber_%": natural / 100,
            "White_Fiber_%": white / 100,
            "Black_Fiber_%": black / 100,
            "Indigo_Fiber_%": indigo / 100,
        }

        used_models = []
        fallback_models = []

        for fiber_type, weight in weights.items():
            if weight == 0:
                continue

            df_exact = df[np.isclose(df[fiber_type], 100.0, atol=0.1)]
            if len(df_exact) >= 3:
                data_used = df_exact
            else:
                data_used = df.sort_values(by=fiber_type, ascending=False).head(3)
                fallback_models.append(fiber_type)

            if len(data_used) >= 2:
                X_train = data_used[["Emission_Count"]].values
                y_train = data_used["Effective_Dosage_ppm"].values
                model = LinearRegression()
                model.fit(X_train, y_train)
                pred = model.predict(X_input)[0]
                prediction += weight * pred
                used_models.append((fiber_type.replace("_Fiber_%", ""), model))

        if used_models:
            st.success(f"📌 Prognostizierte Dosierung: **{round(prediction, 2)} ppm** (gewichtet)")
        else:
            st.error("Nicht genug Daten zur Prognose. Bitte mehr Referenzen erfassen.")

        st.subheader("📉 Regressionslinien nach Faserart")
        fig, ax = plt.subplots()
        for fiber_type, model in used_models:
            df_plot = df.sort_values(by=f"{fiber_type}_Fiber_%", ascending=False).head(3)
            X_plot = df_plot["Emission_Count"].values.reshape(-1, 1)
            y_plot = df_plot["Effective_Dosage_ppm"].values
            ax.scatter(X_plot, y_plot, label=f"{fiber_type} (Daten)")
            ax.plot(X_plot, model.predict(X_plot), label=f"{fiber_type} (Fit)")
        ax.axvline(emission_count, color="red", linestyle="--", label="Emission Count")
        ax.set_xlabel("Emission Count")
        ax.set_ylabel("Effective Dosage (ppm)")
        ax.legend()
        st.pyplot(fig)