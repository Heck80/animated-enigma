
import streamlit as st
import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

st.set_page_config(page_title="050-000056 Weighted Regression", layout="centered")
st.title("📈 Dosage Prediction via Group-wise Weighted Regression")

CSV_FILE = "referenzdaten.csv"

if not os.path.exists(CSV_FILE):
    st.error("Reference data not found. Please enter data in App 1 first.")
else:
    df = pd.read_csv(CSV_FILE)

    if df.empty or len(df) < 4:
        st.warning("Not enough reference data for regression. Enter more in App 1.")
    else:
        st.subheader("🔢 Describe Your Sample")

        col1, col2 = st.columns(2)
        with col1:
            emission_count = st.number_input("Emission count", min_value=0, step=1)
            natural = st.number_input("Natural fiber (%)", 0.0, 100.0, step=0.1)
            black = st.number_input("Black fiber (%)", 0.0, 100.0, step=0.1)
        with col2:
            white = st.number_input("White fiber (%)", 0.0, 100.0, step=0.1)
            indigo = st.number_input("Indigo fiber (%)", 0.0, 100.0, step=0.1)

        total_fiber = natural + black + white + indigo
        if abs(total_fiber - 100.0) > 0.1:
            st.error("Fiber percentages must sum to 100%.")
        else:
            st.subheader("📊 Result")
            X_input = np.array([[emission_count]])

            prediction = 0
            weights = {
                "Natural_Fiber_%": natural / 100,
                "White_Fiber_%": white / 100,
                "Black_Fiber_%": black / 100,
                "Indigo_Fiber_%": indigo / 100,
            }

            used_models = []
            for fiber_type, weight in weights.items():
                df_fiber = df[np.isclose(df[fiber_type], 100.0, atol=0.1)]
                if len(df_fiber) >= 3:
                    X_train = df_fiber[["Emission_Count"]].values
                    y_train = df_fiber["Effective_Dosage_ppm"].values
                    model = LinearRegression()
                    model.fit(X_train, y_train)
                    pred = model.predict(X_input)[0]
                    prediction += weight * pred
                    used_models.append((fiber_type.replace("_Fiber_%", ""), model))

            if used_models:
                st.success(f"📌 Estimated Dosage: **{round(prediction, 2)} ppm** (weighted)")
            else:
                st.error("Not enough 100% data in any fiber group to calculate a prediction.")

            # Plot
            st.subheader("📉 Regression Lines by Fiber Type")
            fig, ax = plt.subplots()
            for fiber_type, model in used_models:
                df_fiber = df[np.isclose(df[f"{fiber_type}_Fiber_%"], 100.0, atol=0.1)]
                X_plot = df_fiber["Emission_Count"].values.reshape(-1, 1)
                y_plot = df_fiber["Effective_Dosage_ppm"].values
                ax.scatter(X_plot, y_plot, label=f"{fiber_type} (data)")
                ax.plot(X_plot, model.predict(X_plot), label=f"{fiber_type} (fit)")
            ax.axvline(emission_count, color="red", linestyle="--", label="Your emission count")
            ax.set_xlabel("Emission Count")
            ax.set_ylabel("Effective Dosage (ppm)")
            ax.legend()
            st.pyplot(fig)


st.subheader("📋 Model Status by Fiber Group")
status_data = []
for fiber_type in weights.keys():
    count = len(df[np.isclose(df[fiber_type], 100.0, atol=0.1)])
    status_data.append({
        "Fiber Type": fiber_type.replace("_Fiber_%", ""),
        "Entries (100%)": count,
        "Model Used": "✅" if count >= 3 else "❌"
    })

st.table(pd.DataFrame(status_data))


# 🔎 Konfidenzbewertung basierend auf der Anzahl verwendeter Teilmodelle
st.subheader("📈 Confidence Indicator")
model_count = sum([1 for row in status_data if row["Model Used"] == "✅"])
if model_count == 4:
    st.success("✅ High confidence: all fiber types represented.")
elif model_count == 3:
    st.info("ℹ️ Moderate confidence: 3 of 4 fiber types represented.")
elif model_count == 2:
    st.warning("⚠️ Low confidence: only 2 fiber types represented.")
elif model_count == 1:
    st.error("❗ Very low confidence: only 1 fiber type represented.")
else:
    st.error("❌ No valid reference models available.")
