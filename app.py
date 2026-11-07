import os
import joblib
import pandas as pd
import streamlit as st
from config import MODEL_PATH, MODEL_RESULTS_PATH


def check_missing_files():
    required = [
        ("charts/wait_band.png", "charts.py"),
        ("charts/age_group.png", "charts.py"),
        ("charts/weekday.png", "charts.py"),
        ("charts/sms_received.png", "charts.py"),
        (MODEL_RESULTS_PATH, "train.py"),
        (MODEL_PATH, "train.py"),
    ]
    missing = []
    for file_path, script_name in required:
        if not os.path.exists(file_path):
            missing.append(f"Missing {file_path}. Please run {script_name} first.")
    return missing


def show_charts_section():
    st.header("What the data shows")
    col1, col2 = st.columns(2)
    with col1:
        st.image("charts/wait_band.png")
        st.caption("This chart plots the appointment no-show rate across four waiting time intervals.")
        st.image("charts/weekday.png")
        st.caption("This chart plots the appointment no-show rate for each day of the week from Monday to Sunday.")
    with col2:
        st.image("charts/age_group.png")
        st.caption("This chart plots the appointment no-show rate across six patient age brackets.")
        st.image("charts/sms_received.png")
        st.caption("This chart plots the appointment no-show rate for appointments with and without an SMS reminder.")


def show_model_comparison_section():
    st.header("Model comparison")
    results = pd.read_csv(MODEL_RESULTS_PATH)
    st.dataframe(results, use_container_width=True)
    st.write("Precision and recall are shown alongside accuracy because 80% of patients attend, making a naive majority-class model look accurate while failing to catch any no-shows.")


def get_weekday_number(day_name):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days.index(day_name)


def show_prediction_section(payload):
    st.header("Try it")
    model = payload["model"]
    model_name = payload["model_name"]
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=0, max_value=110, value=35)
            wait_days = st.number_input("Waiting days", min_value=0, max_value=365, value=7)
            weekday_name = st.selectbox("Weekday", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            sms = st.selectbox("SMS received", ["No", "Yes"])
            gender = st.selectbox("Gender", ["Female", "Male"])
        with col2:
            scholarship = st.selectbox("Scholarship (Bolsa Familia)", ["No", "Yes"])
            hypertension = st.selectbox("Hypertension", ["No", "Yes"])
            diabetes = st.selectbox("Diabetes", ["No", "Yes"])
            alcoholism = st.selectbox("Alcoholism", ["No", "Yes"])
            handicap = st.selectbox("Handicap level", [0, 1, 2, 3, 4])
        submitted = st.form_submit_button("Calculate Risk")
    if submitted:
        input_data = pd.DataFrame([{
            "age": age,
            "wait_days": wait_days,
            "weekday": get_weekday_number(weekday_name),
            "sms_received": 1 if sms == "Yes" else 0,
            "scholarship": 1 if scholarship == "Yes" else 0,
            "hypertension": 1 if hypertension == "Yes" else 0,
            "diabetes": 1 if diabetes == "Yes" else 0,
            "alcoholism": 1 if alcoholism == "Yes" else 0,
            "handicap": handicap,
            "gender_male": 1 if gender == "Male" else 0,
        }])
        probability = model.predict_proba(input_data)[0][1]
        st.subheader(f"Risk score: {probability * 100:.1f}%")
        st.caption("This is a model risk score, not a true probability, because the models use balanced class weights.")
        st.write(f"Model used: {model_name}")


def main():
    st.set_page_config(page_title="NoShowRadar", layout="wide")
    st.title("NoShowRadar")
    missing = check_missing_files()
    if missing:
        for message in missing:
            st.error(message)
        return
    show_charts_section()
    show_model_comparison_section()
    payload = joblib.load(MODEL_PATH)
    show_prediction_section(payload)


if __name__ == "__main__":
    main()
