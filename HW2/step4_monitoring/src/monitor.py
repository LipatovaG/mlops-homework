import requests
import time
import json
from datetime import datetime
import yaml
import os


class ServiceMonitor:
    def __init__(self, config_path="config/monitoring_config.yaml"):
        self.load_config(config_path)
        self.consecutive_failures = 0
        self.metrics_history = []

    def load_config(self, config_path):
        """Загрузка конфигурации из YAML файла"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.base_url = self.config['service']['base_url']
        self.timeout = self.config['monitoring']['request_timeout_seconds']
        self.check_interval = self.config['monitoring']['check_interval_seconds']

    def get_color_status(self, response_time, status_code, endpoint="/health"):
        """Определение цветового статуса на основе порогов"""
        if endpoint == "/health":
            warning_threshold = self.config['thresholds']['response_time_ms']['warning']
            critical_threshold = self.config['thresholds']['response_time_ms']['critical']
        else:
            warning_threshold = self.config['thresholds']['p95_latency_ms']['warning']
            critical_threshold = self.config['thresholds']['p95_latency_ms']['critical']

        if status_code != 200:
            return "🔴 КРАСНЫЙ"
        elif response_time < warning_threshold:
            return "🟢 ЗЕЛЕНЫЙ"
        elif response_time < critical_threshold:
            return "🟡 ЖЕЛТЫЙ"
        else:
            return "🔴 КРАСНЫЙ"

    def check_health(self):
        """Проверка здоровья сервиса"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000

            result = {
                "timestamp": datetime.now().isoformat(),
                "endpoint": "/health",
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "success": response.status_code == 200
            }

            # Счётчик последовательных ошибок
            if response.status_code == 200:
                self.consecutive_failures = 0
            else:
                self.consecutive_failures += 1

            status_color = self.get_color_status(response_time, response.status_code, "/health")
            print(
                f"{status_color} HEALTH: {response.status_code} | {response_time:.2f}ms | Failures: {self.consecutive_failures}")

            return result

        except Exception as e:
            self.consecutive_failures += 1
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "endpoint": "/health",
                "error": str(e),
                "success": False
            }
            status_color = "🔴 КРАСНЫЙ"
            print(f"{status_color} HEALTH ERROR: {e} | Failures: {self.consecutive_failures}")
            return error_result

    def check_predict(self):
        """Проверка эндпоинта /predict"""
        try:
            # POST запрос на /predict
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/predict",
                timeout=self.timeout,
                files={"file": ("test.jpg", b"fake_image_data", "image/jpeg")}
            )
            response_time = (time.time() - start_time) * 1000

            result = {
                "timestamp": datetime.now().isoformat(),
                "endpoint": "/predict",
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "success": response.status_code == 200
            }

            status_color = self.get_color_status(response_time, response.status_code, "/predict")
            print(f"{status_color} PREDICT: {response.status_code} | {response_time:.2f}ms")

            return result

        except Exception as e:
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "endpoint": "/predict",
                "error": str(e),
                "success": False
            }
            status_color = "🔴 КРАСНЫЙ"
            print(f"{status_color} PREDICT ERROR: {e}")
            return error_result

    def run_continuous_monitoring(self):
        """Запуск непрерывного мониторинга"""
        print("🚀 Запуск мониторинга сервиса...")
        print(f"📊 Интервал проверок: {self.check_interval} секунд")
        print(f"🎯 Целевой сервис: {self.base_url}")
        print("Для остановки нажмите Ctrl+C\n")

        try:
            while True:
                print(f"\n--- Проверка в {datetime.now().strftime('%H:%M:%S')} ---")
                health_result = self.check_health()
                predict_result = self.check_predict()

                # Метрики для будущего P95 расчёта
                self.metrics_history.append({
                    "health": health_result,
                    "predict": predict_result
                })

                # Последние 100 измерений
                if len(self.metrics_history) > 100:
                    self.metrics_history.pop(0)

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n🛑 Мониторинг остановлен")


if __name__ == "__main__":
    monitor = ServiceMonitor()
    monitor.run_continuous_monitoring()
