# Step 4: Data Validation with Great Expectations

ML пайплайн с валидацией данных используя Great Expectations и Data Docs.

## Установка
```make install
dvc init
dvc remote add -d local ../../.dvcstore
```

## Запуск
```bash
dvc repro
```

Пайплайн включает шаг валидации данных, который:

- Проверяет отсутствие пустых значений в total_bill, tip, size
- Проверяет что total_bill в диапазоне [0, 100]
- Проверяет что size в диапазоне [1, 10]
- Генерирует красивый HTML отчет по валидации в reports/validation/index.html
- Останавливает пайплайн если валидация не пройдена

Детальный отчёт можно посмотреть в браузере reports/validation/index.html.
