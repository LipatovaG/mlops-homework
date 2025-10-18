import os
import tempfile
import shutil
import pandas as pd
import yaml


def load_params():
    with open("params.yaml", "r") as f:
        return yaml.safe_load(f)


def download_data():
    params = load_params()
    url = params["urls"]["tips"]

    # ПУТИ ДЛЯ WINDOWS
    raw_dir = os.path.join("data", "raw")
    os.makedirs(raw_dir, exist_ok=True)

    df = pd.read_csv(url)

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp_file:
        df.to_csv(tmp_file.name, index=False)
        tmp_path = tmp_file.name

    output_path = os.path.join(raw_dir, "tips.csv")
    shutil.move(tmp_path, output_path)
    print(f"Данные сохранены в: {output_path}")


if __name__ == "__main__":
    download_data()
