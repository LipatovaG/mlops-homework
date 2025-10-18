import json
import yaml
import sys


def validate_model():
    # Метрики из файла
    with open('metrics/metrics.json', 'r') as f:
        metrics = json.load(f)

    # Параметры из params.yaml
    with open('params.yaml', 'r') as f:
        params = yaml.safe_load(f)

    accuracy = metrics['accuracy']
    accuracy_min = params['accuracy_min']

    print(f"Текущая accuracy: {accuracy:.4f}")
    print(f"Минимальная accuracy: {accuracy_min:.4f}")

    # Сравнение accuracy с минимальной
    if accuracy < accuracy_min:
        print("❌ Модель не прошла валидацию!")
        sys.exit(1)  # С ошибкой (код не 0)
    else:
        print("✅ Модель прошла валидацию!")
        sys.exit(0)  # Успешно

if __name__ == "__main__":
    validate_model()
