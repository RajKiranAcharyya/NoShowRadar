# NoShowRadar

NoShowRadar predicts which patients are likely to miss scheduled medical appointments and visualizes key risk factors through SQL queries, charts, and machine learning models.

## Demo

Add a screenshot here.

## What it does

- Audits and cleans 110,527 raw appointment records, logging every removed row.
- Engineers features including appointment wait days, day of week, and demographic indicators.
- Stores cleaned records in a local SQLite database and executes standardized SQL queries.
- Generates four exploratory bar charts analyzing no-show rates across waiting times, ages, days, and SMS status.
- Trains and evaluates a Baseline, Logistic Regression, and Random Forest classifier with balanced class weights.
- Serves an interactive Streamlit web dashboard with visual analysis, model comparison, and patient risk scoring.

## Dataset

The data is the public Kaggle dataset titled "Medical Appointment No Shows" (one CSV file containing 110,527 appointment records collected from public clinics in Vitoria, Brazil). Because Kaggle requires authentication, the raw CSV is not committed to the repository and must be placed manually into `data/`.

## How to run

```powershell
git clone <repository-url>
cd noshowradar
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Download the Kaggle Medical Appointment No Shows CSV and place it in `data/`, then execute the scripts in order:

```powershell
python clean.py
python build_database.py
python run_queries.py
python charts.py
python train.py
streamlit run app.py
```

## Results

All figures below are generated directly from `outputs/cleaning_report.txt`, `outputs/query_results.txt`, and `outputs/model_results.csv`.

### Data Cleaning Summary
- Initial raw appointments: 110,527
- Rows removed with invalid age (< 0 or > 110): 6
- Rows removed with appointment date preceding scheduled date: 5
- Rows removed with duplicate appointment IDs: 0
- Rows removed with missing values: 0
- Final cleaned appointments: 110,516

### Key Findings from SQL Queries
- Overall appointment no-show rate: **20.2%** (110,516 total appointments).
- Lead time is the dominant factor: appointments scheduled for the **same day** had a no-show rate of only **4.6%**, whereas appointments booked **31+ days in advance** had a no-show rate of **33.0%**.
- Age disparity: adolescents aged **13-18** had the highest no-show rate (**26.1%**), while seniors aged **66+** had the lowest no-show rate (**15.5%**).
- SMS anomaly: appointments where an SMS reminder was logged had a **27.6%** no-show rate compared to **16.7%** for those without SMS, reflecting targeted reminders sent primarily to high-risk, longer-wait appointments.

### Model Performance Comparison

| Model | Accuracy | Precision (No-Show) | Recall (No-Show) | F1 Score (No-Show) |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline (Majority Class)** | 79.81% | 0.00% | 0.00% | 0.0000 |
| **Logistic Regression** | 66.27% | 31.33% | 56.28% | 0.4025 |
| **Random Forest (Best)** | 57.96% | 30.30% | 83.28% | **0.4444** |

In the Random Forest model, feature importance is dominated by `wait_days` (78.4%), followed by `age` (10.5%) and `sms_received` (5.9%).

## Limitations

- The predictive signal in demographic and scheduling features is weak, resulting in modest precision (~30%).
- Model evaluation reflects a single stratified train/test split (80/20).
- Model risk scores are uncalibrated rankings rather than true frequentist probabilities due to the use of balanced class weighting.
- Exploratory charts demonstrate statistical associations, not clinical or behavioral causality.
- Data originates from municipal healthcare clinics in a single geographic region (Vitoria, Brazil), limiting direct generalization to other healthcare networks.

## What I learned and next steps

This project highlights why classification accuracy is dangerously deceptive on imbalanced datasets: a dummy model achieves ~80% accuracy by predicting that everyone attends, but catches zero no-shows. Tuning for F1 and recall allows clinical staff to flag 83% of prospective no-shows. Next steps include testing probability calibration (Platt scaling / isotonic regression), collecting longitudinal attendance history per patient, and testing cost-sensitive decision thresholds.
