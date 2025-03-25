import streamlit as st
import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# === Konfiguration ===
st.set_page_config(page_title="050-000056 Weighted Regression", layout="centered")
st.title("📈 Dosage Prediction via Smart Weighted Regression")

CSV_FILE = r"T:\0300_Entwicklung\referenzdaten.csv"


LOGO_PATH = "IntegriTEX-Logo.png"
PDF_PATH = "prediction_report.pdf"

# === PDF Export Funktion ===
def export_prediction_to_pdf(logo_path, prediction_value, emission_count, fiber_weights):
    c = canvas.Canvas(PDF_PATH, pagesize=A4)
    width, height = A4

    if os.path.exists(logo_path):
        c.drawImage(logo_path, (width - 200) / 2, height - 80, width=200, height=60, mask='auto')

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 120, "📄 Prediction Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 150, f"Estimated Dosage: {round(prediction_value, 2)} ppm")
    c.drawString(50, height - 170, f"Emission Count: {emission_count}")

    y_pos = height - 200
    for fiber, weight in fiber_weights.items():
        c.drawString(50, y_pos, f"{fiber.replace('_Fiber_%', '')}: {round(weight * 100)}%")
        y_pos -= 20

    c.save()
    return PDF_PATH

# === Daten laden ===
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
            fallback_models = []

            for fiber_type, weight in weights.items():
                if weight == 0:
                    continue

                df_exact = df[np.isclose(df[fiber_type], 100.0, atol=0.1)]
                if len(df_exact) >= 3:
                    data_used = df_exact
                else:
                    # Fallback: Top 3 mit höchstem Anteil dieser Faser
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
                st.success(f"📌 Estimated Dosage: **{round(prediction, 2)} ppm** (weighted)")
                if st.button("📤 Export as PDF"):
                    export_prediction_to_pdf(LOGO_PATH, prediction, emission_count, weights)
                    with open(PDF_PATH, "rb") as file:
                        st.download_button("⬇️ Download PDF", data=file, file_name="prediction_report.pdf")
            else:
                st.error("Not enough data to perform regression. Please check your reference entries.")

            # 📉 Plot
            st.subheader("📉 Regression Lines by Fiber Type")
            fig, ax = plt.subplots()
            for fiber_type, model in used_models:
                df_plot = df.sort_values(by=f"{fiber_type}_Fiber_%", ascending=False).head(3)
                X_plot = df_plot["Emission_Count"].values.reshape(-1, 1)
                y_plot = df_plot["Effective_Dosage_ppm"].values
                ax.scatter(X_plot, y_plot, label=f"{fiber_type} (data)")
                ax.plot(X_plot, model.predict(X_plot), label=f"{fiber_type} (fit)")
            ax.axvline(emission_count, color="red", linestyle="--", label="Your emission count")
            ax.set_xlabel("Emission Count")
            ax.set_ylabel("Effective Dosage (ppm)")
            ax.legend()
            st.pyplot(fig)

            # 📋 Model-Status
            st.subheader("📋 Model Status by Fiber Group")
            status_data = []
            for fiber_type in weights.keys():
                exact = len(df[np.isclose(df[fiber_type], 100.0, atol=0.1)])
                fallback = fiber_type in fallback_models
                used = fiber_type.replace("_Fiber_%", "") in [x[0] for x in used_models]
                status_data.append({
                    "Fiber Type": fiber_type.replace("_Fiber_%", ""),
                    "Exact Matches (100%)": exact,
                    "Used Fallback?": "✅" if fallback else "❌",
                    "Model Used": "✅" if used else "❌"
                })
            st.table(pd.DataFrame(status_data))

            # 🧭 Confidence
            st.subheader("🧭 Confidence Indicator")
            used_count = len(used_models)
            total_possible = sum([1 for wt in weights.values() if wt > 0])
            if used_count == total_possible and total_possible > 0:
                st.success(f"✅ All relevant fiber models used ({used_count}/{total_possible}) — high confidence.")
            elif used_count > 0:
                st.warning(f"⚠️ Only {used_count}/{total_possible} fiber models used — result may be incomplete.")
            else:
                st.error("❌ No models available for the selected fiber composition.")
