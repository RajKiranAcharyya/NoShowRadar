# NoShowRadar: build instructions for Codex

Save this file as AGENTS.md in the root of the noshowradar project folder. Read all of it before writing any code.

## What you are building

NoShowRadar studies a public dataset of medical appointments and asks one question: which patients are likely to miss their appointment?

It cleans the raw data and records everything it removes.
It creates a few useful features, mainly how many days the patient waited.
It loads the data into a small SQL database and answers questions with SQL queries.
It draws four charts of the no-show rate.
It trains three models, compares them honestly, and saves the best one.
It shows everything on a simple Streamlit page, including a box where the user enters appointment details and sees a risk score.

It is a standalone Python project that runs on the user's own computer. Use plain .py scripts only. No Jupyter notebooks, no Colab.

The owner is a final-year B.Tech student who must be able to explain every line of this project in an interview. Simple and readable always beats clever and short.

## The dataset

The data is the public Kaggle dataset called "Medical Appointment No Shows", one CSV file with about 110,000 appointments. Kaggle needs a login, so do not try to download it. The user places the CSV in the data/ folder. If data/ has no CSV, stop and ask the user to download it and put it there.

From memory, the columns are PatientId, AppointmentID, Gender, ScheduledDay, AppointmentDay, Age, Neighbourhood, Scholarship, Hipertension, Diabetes, Alcoholism, Handcap, SMS_received, No-show. This list may be slightly wrong. Read the real header first, adapt to it, and tell the user about any difference.

Known quirks: some column names are misspelled, in No-show the value No means the patient attended, a few ages are negative or very high, and some appointment dates fall before the scheduled date.

## Hard rules for every file
1. No comments of any kind in code files, including SQL files. No # comments, no -- comments, no docstrings, no commented-out code. Make the code readable with clear names and short functions. All explanations go in WALKTHROUGH.md, never in the code.
2. Plain Python 3.11 or newer. No classes, no lambdas, no type hints, no decorators except where Streamlit needs one, no clever one-liners, no nested list comprehensions.
3. Each function does one job and is ideally under 20 lines. Use full-word names such as remove_invalid_ages, never abbreviations.
4. Use only the packages listed below.
5. Never invent results, numbers or findings. Every number in README.md must come from a file produced by a real run.
6. After writing each stage, run it and confirm it works before starting the next. Never say something works unless you ran it.
7. Keep the scope exactly as written. No extra features, no deep learning, no hyperparameter search, no Docker, no CI.
8. Write SQL without date functions so the same queries would also run on MySQL.
9. If a choice is not covered here, pick the simplest option and mention it in your final message.

## Packages

pandas, scikit-learn, matplotlib, streamlit, joblib, and the standard library sqlite3. Do not use seaborn.

Create a virtual environment named .venv, install the packages, then write requirements.txt with the versions actually installed.

## Folder layout

```text
noshowradar/
  AGENTS.md
  README.md
  WALKTHROUGH.md
  requirements.txt
  .gitignore
  config.py
  clean.py
  features.py
  build_database.py
  run_queries.py
  charts.py
  train.py
  app.py
  sql/
  data/
  outputs/
  charts/
  model/
```

.gitignore must exclude .venv, __pycache__, data/*.csv, outputs/noshow.db and model/*.joblib. The model file is rebuilt by running train.py.

Run the scripts from the project root in this order: clean.py, build_database.py, run_queries.py, charts.py, train.py, then streamlit run app.py.

## Stage 1: setup and config

Create the folders, .gitignore, the virtual environment and requirements.txt. Run git init.

config.py holds these constants and nothing else:

RAW_DATA_FOLDER = "data"
CLEANED_PATH = "outputs/cleaned.csv"
CLEANING_REPORT_PATH = "outputs/cleaning_report.txt"
DATABASE_PATH = "outputs/noshow.db"
MODEL_RESULTS_PATH = "outputs/model_results.csv"
MODEL_PATH = "model/best_model.joblib"
TARGET_COLUMN = "no_show"
FEATURE_COLUMNS = ["age", "wait_days", "weekday", "sms_received", "scholarship", "hypertension", "diabetes", "alcoholism", "handicap", "gender_male"]
MIN_AGE = 0
MAX_AGE = 110
TEST_SIZE = 0.2
RANDOM_STATE = 42

## Stage 2: clean.py and features.py

clean.py functions, run in this order:

- find_raw_file(): returns the single CSV in data/. If there are none or several, stop with a clear message.
- load_raw_data(path): reads the CSV.
- rename_columns(data): renames to lowercase snake_case: patient_id, appointment_id, gender, scheduled_day, appointment_day, age, neighbourhood, scholarship, hypertension, diabetes, alcoholism, handicap, sms_received, no_show_text. This also fixes the misspellings.
- convert_dates(data): converts the two date columns to dates and keeps only the day, not the time, so comparisons happen at day level.
- create_target(data): adds no_show as 1 when no_show_text is Yes and 0 when it is No.
- remove_invalid_ages(data): removes ages below MIN_AGE or above MAX_AGE.
- remove_invalid_date_order(data): removes rows where the appointment day is earlier than the scheduled day. Same-day appointments stay.
- remove_duplicate_appointments(data): removes duplicate appointment_id rows.
- report_missing_values(data): records missing values per used column. Drop rows with missing values in a used column.
- save_outputs(data, report_lines): saves outputs/cleaned.csv and outputs/cleaning_report.txt.

Every removal step must count the rows it removed. cleaning_report.txt lists the starting row count, the rows removed by each rule, and the final row count. These numbers are what the owner will quote in interviews, so they must be exact.

features.py has one function, add_features(data), which adds:

- wait_days: appointment day minus scheduled day, in days
- weekday: weekday of the appointment, Monday as 0 to Sunday as 6
- gender_male: 1 if the gender is M, otherwise 0
- age_group: bins 0-12, 13-18, 19-35, 36-50, 51-65, 66+
- wait_band: same day, 1-7 days, 8-30 days, 31+ days

clean.py calls add_features before saving, so cleaned.csv already contains every engineered column. Do not use patient_id, appointment_id or neighbourhood as model features.

## Stage 3: database and SQL

build_database.py loads outputs/cleaned.csv into a SQLite database at outputs/noshow.db, in a table named appointments, replacing it if it exists. SQLite needs no setup because it ships with Python.

Put each query in its own file in sql/, named for what it answers, since comments are not allowed:

- overall_no_show_rate.sql
- no_show_by_wait_band.sql
- no_show_by_age_group.sql
- no_show_by_weekday.sql
- no_show_by_sms_received.sql
- no_show_by_gender.sql

Every query returns the group, the number of appointments, and ROUND(100 * AVG(no_show), 1) AS no_show_rate_pct. Order the results sensibly, for example wait bands from shortest to longest.

run_queries.py runs every file in sql/, prints the file name and the result as a readable table, and saves everything to outputs/query_results.txt.

## Stage 4: charts.py

Make four bar charts with matplotlib, saved as PNG files in charts/: no-show rate by wait band, by age group, by weekday (Monday to Sunday in order), and by SMS received. Each chart has a clear title, labelled axes with the unit No-show rate (%), the value printed above each bar, and a horizontal line for the overall rate. Print the numbers behind each chart to the terminal.

## Stage 5: train.py

Functions:

- load_cleaned_data(): reads outputs/cleaned.csv.
- split_data(data): splits into train and test sets with TEST_SIZE, RANDOM_STATE and stratification on the target.
- build_models(): returns three models in a dictionary:
  - baseline: DummyClassifier(strategy="most_frequent")
  - logistic_regression: a pipeline of StandardScaler and LogisticRegression(max_iter=1000, class_weight="balanced")
  - random_forest: RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_leaf=20, class_weight="balanced", random_state=42, n_jobs=-1), with settings chosen to keep the saved file small
- evaluate_model(model, x_test, y_test): returns accuracy, plus precision, recall and F1 for the no-show class, plus the four confusion-matrix counts.
- save_results(results): writes outputs/model_results.csv with one row per model.
- save_best_model(models, results): picks the model with the highest F1 on the no-show class, and saves a dictionary with the model name, the fitted model and the feature column list to model/best_model.joblib.
- save_feature_importance(model, feature_names): for the random forest, writes outputs/feature_importance.csv.

Print the full classification_report for each model. Never report accuracy alone anywhere.

## Stage 6: app.py (Streamlit page)

One simple page with three sections:

- What the data shows: the four chart images and one sentence under each that only describes what the chart plots, not conclusions.
- Model comparison: the table from outputs/model_results.csv, with a short line explaining why precision and recall are shown instead of accuracy alone.
- Try it: a form with age, waiting days, weekday, SMS received, scholarship, hypertension, diabetes, alcoholism, handicap and gender. On submit, load the saved model and show the result as Risk score with a caption saying it is a model score, not a true probability, because the models use balanced class weights. Also show the name of the model being used.

If any required output file is missing, show a message naming the script to run instead of crashing.

## Stage 7: documentation

README.md structure: one-line summary, Demo (placeholder for a screenshot), What it does, Dataset (link by name, not uploaded), How to run (virtual environment, install, put the CSV in data/, then the six commands in order), Results, Limitations, What I learned and next steps.

The Results section is filled only from outputs/cleaning_report.txt, outputs/query_results.txt and outputs/model_results.csv. State a finding only if it appears in those numbers, and quote the numbers.
Limitations must be honest: the signal in this data is weak so recall is modest, results come from one train/test split, scores are not calibrated probabilities, the charts show association and not cause, and the data comes from one region.

WALKTHROUGH.md is for the owner to learn from, written in plain simple English:

- One paragraph on what the project does and why it matters for a clinic
- The data flow from raw CSV to risk score in numbered steps
- Each file: its one-sentence purpose, then each function with what goes in, what comes out, and why it exists
- The decisions and the reason for each: why no_show is 1 for a missed appointment, each cleaning rule, why wait days is a feature, why IDs and neighbourhood are left out, why SQLite, why a stratified split, why a baseline, why balanced class weights, why F1 picks the best model, why accuracy alone misleads
- What data leakage is and how this project avoids it
- Ten likely interview questions about this project, each with a two-sentence answer based only on what is in the code and in the results files

## Git

Make a commit after each stage with a clear message such as add data cleaning with report. Never push, never force anything.

## Definition of done

- All six scripts run in order without errors
- outputs/cleaning_report.txt, outputs/query_results.txt, outputs/model_results.csv and the four charts exist
- streamlit run app.py shows the charts, the model table and a working prediction form
- No code file, including SQL, contains a comment or docstring
- README.md and WALKTHROUGH.md exist and contain no invented numbers

