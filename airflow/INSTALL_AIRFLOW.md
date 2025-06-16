# Установка и запуск Apache Airflow

Данное руководство описывает процесс установки и запуска `Apache Airflow` для выполнения `ETL-процесса образовательных данных`

## Предварительные требования

1. `Python 3.8+`
2. Установленные зависимости из `requirements.txt`
3. Доступ к `MySQL` серверу для метаданных `Airflow`

## Инструкция по установке

### 1. Создание виртуального окружения
```bash
python -m venv airflow_env
source airflow_env/bin/activate  # Linux/MacOS
# airflow_env\Scripts\activate   # Windows
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Инициализация базы данных метаданных
```bash
airflow db init
```

### 4. Создание административного пользователя
```bash
airflow users create \
  --username admin \
  --firstname Maxim \
  --lastname Dupley \
  --role Admin \
  --email admin@example.com \
  --password admin123  # Замените на надежный пароль
```

### 5. Конфигурация подключения к DWH
Добавьте подключение к хранилищу данных через CLI:
```bash
airflow connections add 'educational_dwh' \
  --conn-type 'mysql' \
  --conn-host 'dwh.bmstu.ru' \
  --conn-login 'etl_user' \
  --conn-password 'SecurePass123!' \
  --conn-port 3306 \
  --conn-schema 'educational_institution'
```

Или через веб-интерфейс:
1. Откройте http://localhost:8080
2. Перейдите в Admin -> Connections
3. Добавьте новое соединение с параметрами:
   - Conn Id: `educational_dwh`
   - Conn Type: `MySQL`
   - Host: ваш DWH сервер
   - Schema: `educational_institution`
   - Login: etl_user
   - Password: ваш пароль
   - Port: 3306

## Запуск системы

### 1. Запуск веб-сервера (в отдельном терминале)
```bash
airflow webserver --port 8080
```

### 2. Запуск планировщика (в отдельном терминале)
```bash
airflow scheduler
```

### 3. Доступ к веб-интерфейсу
Откройте в браузере: http://localhost:8080

Логин: admin  
Пароль: admin123 (или тот, что вы установили при создании пользователя)

## Размещение DAG

Поместите файл `etl_educational_data.py` в папку `~/airflow/dags`:

```bash
cp dags/etl_educational_data.py ~/airflow/dags/
```

После этого DAG появится в интерфейсе Airflow через 1-2 минуты.

## Проверка работы

1. В веб-интерфейсе найдите DAG `etl_educational_data`
2. Включите его (переключатель слева от имени DAG)
3. Запустите вручную (кнопка "Trigger DAG")
4. Мониторьте выполнение в разделе "Grid View"

## Управление

### Полезные команды
- Проверка списка DAG: `airflow dags list`
- Тестовый запуск задачи: `airflow tasks test etl_educational_data extract_lms_data 2025-01-01`
- Очистка логов: `airflow db clean --clean-before-timestamp 2023-01-01`

### Конфигурационные файлы
Основной конфиг: `~/airflow/airflow.cfg`
Рекомендуемые настройки:
```ini
[core]
dags_folder = /path/to/your/dags
load_examples = False

[scheduler]
min_file_process_interval = 30
```

### Системные службы
Для production использования создайте systemd службы:
```ini
# /etc/systemd/system/airflow-webserver.service
[Unit]
Description=Airflow webserver

[Service]
User=airflow
Group=airflow
Environment="PATH=/path/to/airflow_env/bin"
ExecStart=/path/to/airflow_env/bin/airflow webserver

[Install]
WantedBy=multi-user.target
```

## Устранение неполадок

1. **DAG не отображается в интерфейсе**:
   - Проверьте путь к `DAG` в `airflow.cfg`
   - Убедитесь что файл имеет расширение `.py`
   - Проверьте логи планировщика на наличие ошибок синтаксиса

2. **Ошибки подключения к MySQL**:
   - Проверьте параметры соединения
   - Убедитесь что пользователь имеет права на создание таблиц
   - Проверьте доступность сервера `БД`

3. **Задачи не запускаются**:
   - Проверьте статус планировщика
   - Убедитесь что нет активных ограничений параллелизма
   - Проверьте наличие свободных слотов для выполнения задач
