import requests
import time
import json
from datetime import datetime
import yaml
import os
import statistics


class AdvancedServiceMonitor:
    def __init__(self, config_path="config/monitoring_config.yaml"):
        self.load_config(config_path)
        self.consecutive_failures = 0
        self.response_times = []
        self.error_count = 0
        self.total_checks = 0

    def load_config(self, config_path):
        """Загрузка конфигурации из YAML файла"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.base_url = self.config['service']['base_url']
        self.timeout = self.config['monitoring']['request_timeout_seconds']
        self.check_interval = self.config['monitoring']['check_interval_seconds']

    def calculate_p95(self, data):
        """Расчёт 95-го перцентиля"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(0.95 * len(sorted_data))
        return sorted_data[index]

    def save_json_log(self, log_data):
        """Сохранение лога в JSON файл"""
        log_file = self.config['logging']['log_file']
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False)
            f.write('\n')

    def save_metrics_jsonl(self, metrics_data):
        """Сохранение метрик в JSONL файл"""
        metrics_file = self.config['logging']['metrics_file']
        os.makedirs(os.path.dirname(metrics_file), exist_ok=True)

        with open(metrics_file, 'a', encoding='utf-8') as f:
            # JSONL: одна JSON строка на запись
            json_line = json.dumps(metrics_data, ensure_ascii=False)
            f.write(json_line + '\n')

    def get_alert_level(self):
        """Определение уровня алерта на основе метрик"""
        if not self.response_times:
            return "🟢 ЗЕЛЕНЫЙ"

        current_response_time = self.response_times[-1]
        error_rate = (self.error_count / max(1, self.total_checks)) * 100

        response_warning = self.config['thresholds']['response_time_ms']['warning']
        response_critical = self.config['thresholds']['response_time_ms']['critical']
        error_warning = self.config['thresholds']['error_rate_percent']['warning']
        error_critical = self.config['thresholds']['error_rate_percent']['critical']
        failures_warning = self.config['thresholds']['consecutive_failures']['warning']
        failures_critical = self.config['thresholds']['consecutive_failures']['critical']

        if (current_response_time > response_critical or
                error_rate > error_critical or
                self.consecutive_failures >= failures_critical):
            return "🔴 КРИТИЧЕСКИЙ"
        elif (current_response_time > response_warning or
              error_rate > error_warning or
              self.consecutive_failures >= failures_warning):
            return "🟡 ПРЕДУПРЕЖДЕНИЕ"
        else:
            return "🟢 НОРМА"

    def check_health(self):
        """Проверка здоровья сервиса с расширенной статистикой"""
        self.total_checks += 1

        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            response_time = (time.time() - start_time) * 1000

            # Сохраняем время ответа для статистики
            self.response_times.append(response_time)
            if len(self.response_times) > 100:  # Ограничиваем историю
                self.response_times.pop(0)

            result = {
                "timestamp": datetime.now().isoformat(),
                "endpoint": "/health",
                "status_code": response.status_code,
                "response_time_ms": round(response_time, 2),
                "success": response.status_code == 200,
                "consecutive_failures": self.consecutive_failures,
                "p95_latency": round(self.calculate_p95(self.response_times), 2),
                "error_rate": round((self.error_count / self.total_checks) * 100, 2)
            }

            # Обновляем счётчики ошибок
            if response.status_code == 200:
                self.consecutive_failures = 0
            else:
                self.consecutive_failures += 1
                self.error_count += 1

            # Определяем уровень алерта
            alert_level = self.get_alert_level()

            print(f"{alert_level} HEALTH: {response.status_code} | "
                  f"{response_time:.2f}ms | P95: {result['p95_latency']}ms | "
                  f"Errors: {result['error_rate']}% | Failures: {self.consecutive_failures}")

            # Сохраняем логи и метрики
            self.save_json_log(result)
            self.save_metrics_jsonl(result)

            return result

        except Exception as e:
            self.consecutive_failures += 1
            self.error_count += 1

            error_result = {
                "timestamp": datetime.now().isoformat(),
                "endpoint": "/health",
                "error": str(e),
                "success": False,
                "consecutive_failures": self.consecutive_failures,
                "p95_latency": round(self.calculate_p95(self.response_times), 2),
                "error_rate": round((self.error_count / self.total_checks) * 100, 2)
            }

            alert_level = self.get_alert_level()
            print(f"{alert_level} HEALTH ERROR: {e} | Failures: {self.consecutive_failures}")

            # Сохраняем логи ошибок
            self.save_json_log(error_result)
            self.save_metrics_jsonl(error_result)

            return error_result

    def run_advanced_monitoring(self):
        """Запуск расширенного мониторинга"""
        print("🚀 ЗАПУСК РАСШИРЕННОГО МОНИТОРИНГА...")
        print(f"📊 Интервал проверок: {self.check_interval} секунд")
        print(f"🎯 Целевой сервис: {self.base_url}")
        print(f"📁 Логи: {self.config['logging']['log_file']}")
        print(f"📈 Метрики: {self.config['logging']['metrics_file']}")
        print("Для остановки нажмите Ctrl+C\n")

        try:
            while True:
                print(f"\n--- Проверка в {datetime.now().strftime('%H:%M:%S')} ---")
                health_result = self.check_health()

                # Выводим сводную статистику каждые 5 проверок
                if self.total_checks % 5 == 0:
                    self.print_summary()

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n🛑 Мониторинг остановлен")
            self.print_final_summary()

    def print_summary(self):
        """Вывод сводной статистики"""
        if not self.response_times:
            return

        avg_response = statistics.mean(self.response_times)
        p95 = self.calculate_p95(self.response_times)
        error_rate = (self.error_count / self.total_checks) * 100

        print(f"📊 СВОДКА: Avg: {avg_response:.2f}ms | P95: {p95:.2f}ms | "
              f"Errors: {error_rate:.2f}% | Total: {self.total_checks}")

    def print_final_summary(self):
        """Финальная сводка при остановке"""
        if not self.response_times:
            return

        avg_response = statistics.mean(self.response_times)
        p95 = self.calculate_p95(self.response_times)
        error_rate = (self.error_count / self.total_checks) * 100

        print(f"\n📈 ФИНАЛЬНАЯ СТАТИСТИКА:")
        print(f"   Среднее время: {avg_response:.2f}ms")
        print(f"   P95 Latency: {p95:.2f}ms")
        print(f"   Процент ошибок: {error_rate:.2f}%")
        print(f"   Всего проверок: {self.total_checks}")
        print(f"   Файл логов: {self.config['logging']['log_file']}")
        print(f"   Файл метрик: {self.config['logging']['metrics_file']}")


if __name__ == "__main__":
    monitor = AdvancedServiceMonitor()
    monitor.run_advanced_monitoring()
