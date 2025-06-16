# Установка и запуск Apache Airflow

Данное руководство описывает процесс установки и запуска Apache Airflow для выполнения ETL-процесса образовательных данных.

## Предварительные требования

1. Python 3.8+
2. Установленные зависимости из `requirements.txt`
3. Доступ к MySQL серверу для метаданных Airflow

## Инструкция по установке

### 1. Создание виртуального окружения
```bash
python -m venv airflow_env
source airflow_env/bin/activate  # Linux/MacOS
# airflow_env\Scripts\activate   # Windows
```
