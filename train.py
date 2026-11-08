import os
import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from config import (
    CLEANED_PATH,
    FEATURE_COLUMNS,
    MODEL_PATH,
    MODEL_RESULTS_PATH,
    RANDOM_STATE,
    TARGET_COLUMN,
    TEST_SIZE,
)


def load_cleaned_data():
    return pd.read_csv(CLEANED_PATH)


def split_data(data):
    features = data[FEATURE_COLUMNS]
    target = data[TARGET_COLUMN]
    return train_test_split(
        features,
        target,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=target,
    )


def build_models():
    return {
        "baseline": DummyClassifier(strategy="most_frequent"),
        "logistic_regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE),
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_leaf=20,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }


def evaluate_model(model, x_test, y_test):
    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    precision = precision_score(y_test, predictions, pos_label=1, zero_division=0)
    recall = recall_score(y_test, predictions, pos_label=1, zero_division=0)
    f1 = f1_score(y_test, predictions, pos_label=1, zero_division=0)
    matrix = confusion_matrix(y_test, predictions)
    true_negative, false_positive, false_negative, true_positive = matrix.ravel()
    report = classification_report(y_test, predictions, zero_division=0)
    return {
        "accuracy": round(float(accuracy), 4),
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1": round(float(f1), 4),
        "true_negative": int(true_negative),
        "false_positive": int(false_positive),
        "false_negative": int(false_negative),
        "true_positive": int(true_positive),
        "classification_report": report,
    }


def save_results(results):
    os.makedirs("outputs", exist_ok=True)
    table = pd.DataFrame(results)
    table_to_save = table.drop(columns=["classification_report"])
    table_to_save.to_csv(MODEL_RESULTS_PATH, index=False)


def save_best_model(models, results):
    os.makedirs("model", exist_ok=True)
    best_name = None
    best_f1 = -1.0
    for record in results:
        if record["f1"] > best_f1:
            best_f1 = record["f1"]
            best_name = record["model"]
    payload = {
        "model_name": best_name,
        "model": models[best_name],
        "feature_columns": FEATURE_COLUMNS,
    }
    joblib.dump(payload, MODEL_PATH)


def save_feature_importance(model, feature_names):
    os.makedirs("outputs", exist_ok=True)
    importances = model.feature_importances_
    frame = pd.DataFrame({"feature": feature_names, "importance": importances})
    sorted_frame = frame.sort_values(by="importance", ascending=False)
    sorted_frame.to_csv("outputs/feature_importance.csv", index=False)


def main():
    data = load_cleaned_data()
    x_train, x_test, y_train, y_test = split_data(data)
    models = build_models()
    results = []
    for name, model in models.items():
        model.fit(x_train, y_train)
        metrics = evaluate_model(model, x_test, y_test)
        print(f"=== {name} ===")
        print(metrics["classification_report"])
        metrics["model"] = name
        results.append(metrics)
    save_results(results)
    save_best_model(models, results)
    save_feature_importance(models["random_forest"], FEATURE_COLUMNS)


if __name__ == "__main__":
    main()

