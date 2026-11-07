# NoShowRadar walkthrough

NoShowRadar analyzes 110,000+ medical appointment records from public clinics to identify patients at high risk of skipping their appointments. When patients fail to attend appointments without notice, clinic equipment and clinical staff sit idle, operational costs increase, and patient care is delayed. By identifying high-risk appointments in advance, healthcare providers can send targeted reminders, prioritize proactive phone follow-ups, or arrange double-booking workflows to optimize resource utilization.

## Data flow

1. The raw dataset (`noshowappointments-kagglev2-may-2016.csv`) is placed into `data/`.
2. `clean.py` audits row counts, renames misspelled columns, normalizes timestamps to calendar dates, applies cleaning rules, calls feature engineering, and writes `outputs/cleaned.csv` and `outputs/cleaning_report.txt`.
3. `features.py` calculates elapsed wait days, calendar weekday, gender indicators, age groups, and wait bands.
4. `build_database.py` creates a local SQLite database at `outputs/noshow.db` and writes an `appointments` table.
5. `run_queries.py` executes six SQL scripts in `sql/` without database-specific date functions and logs results to `outputs/query_results.txt`.
6. `charts.py` renders four bar charts in `charts/` displaying no-show percentages with overall reference baselines.
7. `train.py` splits cleaned data using stratified sampling, trains three models with balanced class weights, evaluates metrics, logs results to `outputs/model_results.csv`, and saves the highest-F1 model to `model/best_model.joblib`.
8. `app.py` loads the saved artifacts and serves a Streamlit dashboard showing exploratory trends, model benchmarking, and an interactive risk scoring calculator.

## Files and functions

### `config.py`
One central file defining constants for paths, column definitions, bounds, and split parameters. It contains no functions.

### `features.py`
Calculates derived features for data analysis and machine learning.
- `add_features(data)`: takes a DataFrame and returns an enriched DataFrame with `wait_days`, `weekday`, `gender_male`, `age_group`, and `wait_band`.

### `clean.py`
Audits and purges invalid appointment records.
- `find_raw_file()`: takes no arguments and returns the single CSV path in `data/`, stopping if missing or multiple files exist.
- `load_raw_data(path)`: takes a file path and returns a raw DataFrame.
- `rename_columns(data)`: takes a DataFrame and returns a DataFrame with lowercase snake_case headers, correcting original typos like `Hipertension` and `Handcap`.
- `convert_dates(data)`: takes a DataFrame and returns normalized calendar date values stripped of timestamp noise.
- `create_target(data)`: takes a DataFrame and returns a DataFrame with binary target `no_show` (1 for Yes, 0 for No).
- `remove_invalid_ages(data)`: takes a DataFrame and returns valid age records within 0–110 years and the count of dropped records.
- `remove_invalid_date_order(data)`: takes a DataFrame and returns records where appointment date is on or after scheduled date, plus dropped count.
- `remove_duplicate_appointments(data)`: takes a DataFrame and returns deduplicated records by appointment ID and dropped count.
- `report_missing_values(data)`: takes a DataFrame and returns rows without missing fields, total rows dropped, and missing value counts.
- `save_outputs(data, report_lines)`: takes a DataFrame and audit lines and writes `outputs/cleaned.csv` and `outputs/cleaning_report.txt`.
- `main()`: orchestrates the pipeline steps and prints report lines.

### `build_database.py`
Loads cleaned records into SQLite.
- `load_cleaned_data()`: takes no arguments and reads `outputs/cleaned.csv`.
- `build_table(data, database_path)`: takes a DataFrame and database path and creates or replaces the `appointments` SQL table.
- `main()`: executes the database generation process.

### `run_queries.py`
Executes SQL queries against the local database.
- `find_query_files()`: takes no arguments and returns sorted SQL file paths in `sql/`.
- `read_query(path)`: takes an SQL file path and returns raw query text.
- `execute_query(sql_text, database_path)`: takes SQL text and database path and returns query results as a DataFrame.
- `save_results(lines)`: takes text lines and writes `outputs/query_results.txt`.
- `main()`: executes all queries, displays them in the terminal, and saves the text output.

### `charts.py`
Generates exploratory bar charts.
- `load_cleaned_data()`: takes no arguments and reads `outputs/cleaned.csv`.
- `calculate_overall_rate(data)`: takes a DataFrame and returns the overall percentage of no-shows.
- `draw_bar_chart(categories, rates, overall_rate, title, x_label, file_name)`: takes plot data and renders a formatted PNG chart with labeled values and a reference line.
- `plot_wait_band(data, overall_rate)`: aggregates no-show rates across lead times and calls `draw_bar_chart`.
- `plot_age_group(data, overall_rate)`: aggregates no-show rates across age brackets and calls `draw_bar_chart`.
- `plot_weekday(data, overall_rate)`: aggregates no-show rates across appointment weekdays and calls `draw_bar_chart`.
- `plot_sms_received(data, overall_rate)`: aggregates no-show rates across SMS notification status and calls `draw_bar_chart`.
- `main()`: coordinates chart creation and prints exact numeric tables to the terminal.

### `train.py`
Trains, benchmarks, and persists classification models.
- `load_cleaned_data()`: takes no arguments and reads `outputs/cleaned.csv`.
- `split_data(data)`: takes a DataFrame and returns train/test splits stratified by the target column.
- `build_models()`: takes no arguments and returns a dictionary with DummyClassifier, LogisticRegression pipeline, and RandomForestClassifier.
- `evaluate_model(model, x_test, y_test)`: takes a model and test set and returns accuracy, precision, recall, F1, confusion matrix values, and classification report.
- `save_results(results)`: takes model metrics and writes `outputs/model_results.csv`.
- `save_best_model(models, results)`: takes models and result dictionaries, finds the model with highest F1 score on the positive class, and saves the payload to `model/best_model.joblib`.
- `save_feature_importance(model, feature_names)`: takes the fitted random forest and feature names and writes `outputs/feature_importance.csv`.
- `main()`: coordinates model fitting, evaluation logging, and file persistence.

### `app.py`
Interactive web application.
- `check_missing_files()`: takes no arguments and returns a list of missing required artifact paths.
- `show_charts_section()`: takes no arguments and displays the four saved chart images with objective descriptions.
- `show_model_comparison_section()`: takes no arguments and renders the model comparison table with explanatory text.
- `get_weekday_number(day_name)`: takes a day string and returns integer index 0–6.
- `show_prediction_section(payload)`: takes a model payload and renders an appointment form, calculating and displaying the patient risk score.
- `main()`: sets up the page layout and controls rendering flow.

## Decisions

- **Why no_show is 1 for a missed appointment:** Standard machine learning convention assigns the positive class (1) to the event of interest being predicted (a missed appointment), rather than the common status quo.
- **Each cleaning rule:** Negative ages and ages above 110 are physical recording errors. Appointments scheduled after the appointment day violate temporal causality. Duplicate appointment IDs distort statistical distribution.
- **Why wait days is a feature:** Lead time between booking and appointment is historically the strongest behavioral predictor of appointment adherence.
- **Why IDs and neighbourhood are left out:** Patient ID and Appointment ID are arbitrary database keys with no generalization value. Neighbourhood has dozens of categories with high cardinality that risk memorization and geographical overfitting.
- **Why SQLite:** SQLite requires no external server setup, runs out of the box with Python's standard library, and allows cross-platform SQL analysis.
- **Why a stratified split:** Only ~20% of appointments are no-shows; stratification ensures the 80/20 train/test split maintains identical class ratios in both splits.
- **Why a baseline:** A DummyClassifier provides a minimum performance benchmark; without it, an engineer cannot evaluate whether complex algorithms add real value.
- **Why balanced class weights:** Standard loss functions heavily favor the 80% majority class. Balanced weighting penalizes mistakes on no-shows 4x more severely, forcing models to actively identify positive cases.
- **Why F1 picks the best model:** F1 is the harmonic mean of precision and recall on the minority class, ensuring the chosen model balances finding no-shows without generating excessive false alarms.
- **Why accuracy alone misleads:** Predicting that every single patient attends yields ~80% accuracy while failing to identify a single missed appointment (0% recall).

## Data leakage and prevention

Data leakage occurs when information from outside the training dataset is used to create or tune a machine learning model, artificially inflating test scores. NoShowRadar prevents data leakage through three mechanisms:
1. All feature engineering operations (such as wait day subtraction and weekday derivation) are row-independent deterministic transformations that do not rely on global sample statistics (such as dataset-wide means or medians).
2. For Logistic Regression, normalization scaling (`StandardScaler`) is packaged within an `sklearn.pipeline.make_pipeline`, fitting strictly on training folds during cross-validation or split execution.
3. The train/test split is performed strictly before model training, and all evaluations are reported on unseen test records using a frozen `RANDOM_STATE`.

## Interview questions

1. **What problem does NoShowRadar solve?** NoShowRadar identifies patients likely to miss clinic appointments using clinical scheduling records. This allows clinics to proactively reduce idle chair time through targeted reminders or overbooking buffers.
2. **Why did you encode the target as 1 for No-show instead of attendance?** Machine learning frameworks designate the rare event being detected as the positive class (1). In this dataset, attendance is the 80% majority, so missed appointments represent the operational event of interest.
3. **What was the single most predictive feature in your models?** The number of waiting days between booking and appointment was the dominant feature, accounting for 78.4% of feature importance in the Random Forest. Same-day appointments exhibited a 4.6% no-show rate compared to 33.0% for appointments booked over a month ahead.
4. **Why does the SMS reminder group exhibit a higher no-show rate than the non-SMS group?** In `query_results.txt`, patients receiving an SMS had a 27.6% no-show rate versus 16.7% for those without. This reflects confounding by indication: clinics systematically send SMS reminders to longer-wait, higher-risk appointments rather than allocating them randomly.
5. **Why did your DummyClassifier achieve ~80% accuracy?** The dataset has an 80/20 class imbalance, so a trivial model that always predicts attendance achieves 79.8% accuracy. However, its recall and precision are 0.0%, demonstrating that accuracy is a misleading metric for imbalanced classification.
6. **Why did you use balanced class weights?** Without balanced class weights, machine learning algorithms optimize overall accuracy by predicting attendance for nearly every sample. Balanced class weighting inversely scales loss by class frequency, pushing the Random Forest recall to 83.3%.
7. **Why is the risk score displayed in the Streamlit app not a calibrated probability?** Training with balanced class weights artificially shifts the model's decision threshold toward the minority class. As a result, the output reflects relative ranking risk rather than true frequentist likelihood.
8. **Why did you choose SQLite over MySQL or PostgreSQL for this project?** SQLite is self-contained, serverless, and included directly in the Python standard library, ensuring zero-configuration portability for local evaluation. The SQL queries were deliberately written without dialect-specific date functions so they remain portable to MySQL or PostgreSQL.
9. **Why did you exclude patient ID and neighbourhood from the feature set?** IDs are arbitrary primary keys that carry no predictive signal and lead to data memorization. Neighbourhood introduces high categorical cardinality and risks overfitting to regional volume rather than patient behavior.
10. **How would you deploy this model into a real hospital management system?** I would expose the saved model as a lightweight REST API (FastAPI) integrated into the Electronic Health Record (EHR) scheduling workflow. When an appointment is booked, the API returns a risk score that automatically triggers SMS sequences or alerts front-desk coordinators.
