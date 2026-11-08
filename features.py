import pandas as pd


def add_features(data):
    data = data.copy()
    data["wait_days"] = (data["appointment_day"] - data["scheduled_day"]).dt.days
    data["weekday"] = data["appointment_day"].dt.weekday
    data["gender_male"] = (data["gender"] == "M").astype(int)
    age_bins = [-1, 12, 18, 35, 50, 65, 150]
    age_labels = ["0-12", "13-18", "19-35", "36-50", "51-65", "66+"]
    data["age_group"] = pd.cut(data["age"], bins=age_bins, labels=age_labels)
    wait_bins = [-1, 0, 7, 30, 10000]
    wait_labels = ["Same day", "1-7 days", "8-30 days", "31+ days"]
    data["wait_band"] = pd.cut(data["wait_days"], bins=wait_bins, labels=wait_labels)
    return data

