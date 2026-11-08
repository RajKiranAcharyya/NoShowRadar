import os
import sys
import pandas as pd
from config import (
    CLEANED_PATH,
    CLEANING_REPORT_PATH,
    MAX_AGE,
    MIN_AGE,
    RAW_DATA_FOLDER,
)
from features import add_features


def find_raw_file():
    files = [f for f in os.listdir(RAW_DATA_FOLDER) if f.endswith(".csv")]
    if len(files) == 0:
        sys.exit("No CSV file found in data/. Please download the Kaggle dataset.")
    if len(files) > 1:
        sys.exit("Multiple CSV files found in data/. Keep only one CSV file.")
    return os.path.join(RAW_DATA_FOLDER, files[0])


def load_raw_data(path):
    return pd.read_csv(path)


def rename_columns(data):
    mapping = {
        "PatientId": "patient_id",
        "AppointmentID": "appointment_id",
        "Gender": "gender",
        "ScheduledDay": "scheduled_day",
        "AppointmentDay": "appointment_day",
        "Age": "age",
        "Neighbourhood": "neighbourhood",
        "Scholarship": "scholarship",
        "Hipertension": "hypertension",
        "Diabetes": "diabetes",
        "Alcoholism": "alcoholism",
        "Handcap": "handicap",
        "SMS_received": "sms_received",
        "No-show": "no_show_text",
    }
    return data.rename(columns=mapping)


def convert_dates(data):
    data = data.copy()
    data["scheduled_day"] = pd.to_datetime(data["scheduled_day"]).dt.normalize()
    data["appointment_day"] = pd.to_datetime(data["appointment_day"]).dt.normalize()
    return data


def create_target(data):
    data = data.copy()
    data["no_show"] = (data["no_show_text"] == "Yes").astype(int)
    return data


def remove_invalid_ages(data):
    valid_mask = (data["age"] >= MIN_AGE) & (data["age"] <= MAX_AGE)
    removed_count = int((~valid_mask).sum())
    return data[valid_mask].copy(), removed_count


def remove_invalid_date_order(data):
    valid_mask = data["appointment_day"] >= data["scheduled_day"]
    removed_count = int((~valid_mask).sum())
    return data[valid_mask].copy(), removed_count


def remove_duplicate_appointments(data):
    duplicate_count = int(data.duplicated(subset=["appointment_id"]).sum())
    cleaned_data = data.drop_duplicates(subset=["appointment_id"]).copy()
    return cleaned_data, duplicate_count


def report_missing_values(data):
    missing_counts = data.isna().sum()
    rows_with_missing = int(data.isna().any(axis=1).sum())
    cleaned_data = data.dropna().copy()
    return cleaned_data, rows_with_missing, missing_counts


def save_outputs(data, report_lines):
    os.makedirs("outputs", exist_ok=True)
    data.to_csv(CLEANED_PATH, index=False)
    with open(CLEANING_REPORT_PATH, "w", encoding="utf-8") as file:
        file.write("\n".join(report_lines) + "\n")


def main():
    raw_path = find_raw_file()
    raw_data = load_raw_data(raw_path)
    initial_rows = len(raw_data)
    data = rename_columns(raw_data)
    data = convert_dates(data)
    data = create_target(data)
    data, removed_ages = remove_invalid_ages(data)
    data, removed_dates = remove_invalid_date_order(data)
    data, removed_dupes = remove_duplicate_appointments(data)
    data, removed_missing, missing_counts = report_missing_values(data)
    data = add_features(data)
    final_rows = len(data)
    report_lines = [
        f"Initial rows: {initial_rows}",
        f"Rows removed (invalid age < {MIN_AGE} or > {MAX_AGE}): {removed_ages}",
        f"Rows removed (appointment day earlier than scheduled day): {removed_dates}",
        f"Rows removed (duplicate appointment id): {removed_dupes}",
        f"Rows removed (missing values): {removed_missing}",
        f"Final rows: {final_rows}",
    ]
    save_outputs(data, report_lines)
    for line in report_lines:
        print(line)


if __name__ == "__main__":
    main()

