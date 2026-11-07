import sqlite3
import pandas as pd
from config import CLEANED_PATH, DATABASE_PATH


def load_cleaned_data():
    return pd.read_csv(CLEANED_PATH)


def build_table(data, database_path):
    connection = sqlite3.connect(database_path)
    data.to_sql("appointments", connection, if_exists="replace", index=False)
    connection.close()


def main():
    data = load_cleaned_data()
    build_table(data, DATABASE_PATH)
    print(f"Loaded {len(data)} rows into {DATABASE_PATH}")


if __name__ == "__main__":
    main()
