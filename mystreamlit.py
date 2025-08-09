# frontend/mystreamlit.py
import streamlit as st
import requests
import pandas as pd
import os
from datetime import date

BACKEND = os.getenv("BACKEND_HOST", "http://127.0.0.1:8000")

st.set_page_config(page_title="Intelligent Health Platform", layout="centered")
st.title("Intelligent Digital Health Platform")

menu = ["Create patient", "Enter vitals & Predict", "Patient history"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Create patient":
    st.header("Create a new patient")
    name = st.text_input("Full name")
    dob = st.date_input("Date of birth", value=date(1990,1,1))
    gender = st.selectbox("Gender", ["M","F","O"])
    if st.button("Create patient"):
        payload = {"name": name, "dob": dob.isoformat(), "gender": gender}
        try:
            r = requests.post(f"{BACKEND}/patients", json=payload, timeout=10)
            if r.status_code in (200,201) or r.ok:
                st.success(f"Patient created: {r.json()}")
            else:
                st.error(f"Failed: {r.status_code} {r.text}")
        except Exception as e:
            st.error(f"Error: {e}")

elif choice == "Enter vitals & Predict":
    st.header("Enter patient vitals")
    pid = st.number_input("Patient ID", min_value=1, value=1)
    age = st.number_input("Age", min_value=0, value=40)
    height = st.number_input("Height (cm)", value=170.0)
    weight = st.number_input("Weight (kg)", value=70.0)
    bmi = round(weight / ((height/100)**2), 2) if height > 0 else 0.0
    st.write(f"Calculated BMI: {bmi}")
    glucose = st.number_input("Glucose", value=95.0)
    bp_systolic = st.number_input("Systolic BP", value=120)
    cholesterol = st.number_input("Cholesterol", value=180.0)
    symptoms = st.text_area("Symptoms (optional)")
    if st.button("Run Diabetes Prediction"):
        payload = {"patient_id": int(pid), "age": float(age), "bmi": float(bmi), "glucose": float(glucose), "bp_systolic": int(bp_systolic), "cholesterol": float(cholesterol), "symptoms": symptoms}
        try:
            r = requests.post(f"{BACKEND}/predict/diabetes", json=payload, timeout=30)
            if r.ok:
                data = r.json()
                pred = data.get("prediction", {})
                rec = data.get("recommendation", "")
                st.subheader("Prediction")
                st.metric("Diabetes risk probability", f"{pred.get('probability', 0):.2f}")
                st.write("Risk label:", pred.get("label"))
                st.subheader("Recommendation")
                st.write(rec)
                st.success(f"Prediction saved id: {data.get('prediction_id')}")
            else:
                st.error(f"API error: {r.status_code} {r.text}")
        except Exception as e:
            st.error(f"Request error: {e}")

elif choice == "Patient history":
    st.header("Patient prediction history")
    pid = st.number_input("Patient ID to view", min_value=1, value=1, key="hist_pid")
    if st.button("Load history"):
        try:
            r = requests.get(f"{BACKEND}/patient/{int(pid)}/history", timeout=10)
            if r.ok:
                data = r.json()
                if not data:
                    st.info("No history found.")
                else:
                    df = pd.DataFrame(data)
                    st.dataframe(df)
                    if "created_at" in df.columns and "risk_score" in df.columns:
                        df["created_at"] = pd.to_datetime(df["created_at"])
                        df_sorted = df.sort_values("created_at")
                        st.line_chart(df_sorted.set_index("created_at")["risk_score"])
            else:
                st.error(f"Failed to load: {r.status_code} {r.text}")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.caption("Prototype only — not for clinical use.")
