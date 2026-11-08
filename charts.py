import os
import matplotlib.pyplot as plt
import pandas as pd
from config import CLEANED_PATH


def load_cleaned_data():
    return pd.read_csv(CLEANED_PATH)


def calculate_overall_rate(data):
    return float(data["no_show"].mean() * 100)


def draw_bar_chart(categories, rates, overall_rate, title, x_label, file_name):
    plt.figure(figsize=(8, 5))
    bars = plt.bar(categories, rates, color="#2b5c8f")
    plt.axhline(overall_rate, color="red", linestyle="--", label=f"Overall rate ({overall_rate:.1f}%)")
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel("No-show rate (%)")
    plt.ylim(0, max(rates) + 8)
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 0.8, f"{height:.1f}%", ha="center")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join("charts", file_name))
    plt.close()


def plot_wait_band(data, overall_rate):
    order = ["Same day", "1-7 days", "8-30 days", "31+ days"]
    grouped = data.groupby("wait_band", observed=False)["no_show"].mean() * 100
    rates = [grouped.get(band, 0.0) for band in order]
    print("Wait Band rates:")
    for band, rate in zip(order, rates):
        print(f"  {band}: {rate:.1f}%")
    draw_bar_chart(order, rates, overall_rate, "No-Show Rate by Wait Band", "Wait Band", "wait_band.png")


def plot_age_group(data, overall_rate):
    order = ["0-12", "13-18", "19-35", "36-50", "51-65", "66+"]
    grouped = data.groupby("age_group", observed=False)["no_show"].mean() * 100
    rates = [grouped.get(age, 0.0) for age in order]
    print("Age Group rates:")
    for age, rate in zip(order, rates):
        print(f"  {age}: {rate:.1f}%")
    draw_bar_chart(order, rates, overall_rate, "No-Show Rate by Age Group", "Age Group", "age_group.png")


def plot_weekday(data, overall_rate):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    grouped = data.groupby("weekday", observed=False)["no_show"].mean() * 100
    rates = [grouped.get(i, 0.0) for i in range(7)]
    print("Weekday rates:")
    for day, rate in zip(days, rates):
        print(f"  {day}: {rate:.1f}%")
    draw_bar_chart(days, rates, overall_rate, "No-Show Rate by Weekday", "Weekday", "weekday.png")


def plot_sms_received(data, overall_rate):
    labels = ["No SMS", "SMS Received"]
    grouped = data.groupby("sms_received", observed=False)["no_show"].mean() * 100
    rates = [grouped.get(0, 0.0), grouped.get(1, 0.0)]
    print("SMS Received rates:")
    for label, rate in zip(labels, rates):
        print(f"  {label}: {rate:.1f}%")
    draw_bar_chart(labels, rates, overall_rate, "No-Show Rate by SMS Received", "SMS Status", "sms_received.png")


def main():
    os.makedirs("charts", exist_ok=True)
    data = load_cleaned_data()
    overall_rate = calculate_overall_rate(data)
    print(f"Overall No-Show Rate: {overall_rate:.1f}%\n")
    plot_wait_band(data, overall_rate)
    plot_age_group(data, overall_rate)
    plot_weekday(data, overall_rate)
    plot_sms_received(data, overall_rate)


if __name__ == "__main__":
    main()

