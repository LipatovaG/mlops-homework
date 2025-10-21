import json
import os
import pickle

import pandas as pd
import yaml
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def load_params():
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)


def evaluate_model():
    params = load_params()

    with open("models/model.pkl", "rb") as f:
        model = pickle.load(f)

    df = pd.read_csv("data/processed/dataset.csv")

    X = df[["total_bill", "size"]]
    y = df["high_tip"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=params["test_size"], random_state=params["seed"]
    )

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # ПОДСЧЁТ КОЛИЧЕСТВА СТРОК
    num_rows = len(df)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Number of rows in data: {num_rows}")

    # ПАПКА METRICS
    os.makedirs("metrics", exist_ok=True)

    # МЕТРИКИ В JSON
    metrics = {"accuracy": accuracy, "num_rows": num_rows}

    with open("metrics/metrics.json", "w") as f:
        json.dump(metrics, f, indent=4)

    print("Metrics saved to metrics/metrics.json")


if __name__ == "__main__":
    evaluate_model()
