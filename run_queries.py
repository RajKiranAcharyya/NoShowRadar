import os
import sqlite3
import pandas as pd
from config import DATABASE_PATH


def find_query_files():
    folder = "sql"
    names = sorted(os.listdir(folder))
    return [os.path.join(folder, name) for name in names if name.endswith(".sql")]


def read_query(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def execute_query(sql_text, database_path):
    connection = sqlite3.connect(database_path)
    result = pd.read_sql_query(sql_text, connection)
    connection.close()
    return result


def save_results(lines):
    with open("outputs/query_results.txt", "w", encoding="utf-8") as file:
        file.write("\n".join(lines) + "\n")


def main():
    paths = find_query_files()
    output_lines = []
    for path in paths:
        name = os.path.basename(path)
        sql_text = read_query(path)
        table = execute_query(sql_text, DATABASE_PATH)
        output_lines.append(f"Query: {name}")
        output_lines.append(table.to_string(index=False))
        output_lines.append("")
    full_output = "\n".join(output_lines)
    print(full_output)
    save_results(output_lines)


if __name__ == "__main__":
    main()
