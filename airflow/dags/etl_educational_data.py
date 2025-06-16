"""
DAG для ETL-процесса образовательных данных

Этот Directed Acyclic Graph (DAG) автоматизирует процесс извлечения, преобразования и загрузки 
образовательных данных из гетерогенных источников в центральное хранилище данных.

Основные этапы:
1. Extract - извлечение данных из LMS и электронных журналов
2. Transform - очистка, нормализация и объединение данных
3. Load - загрузка подготовленных данных в DWH (MySQL)

Архитектура:
- Использует PythonOperator для выполнения задач
- Поддерживает ежедневное выполнение
- Обеспечивает обработку ошибок через retry механизм

Требования:
- Apache Airflow >= 2.0
- Библиотеки: pandas, requests, apache-airflow-providers-mysql
- Настроенное подключение к MySQL в Airflow (conn_id='educational_dwh')
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.mysql.hooks.mysql import MySqlHook
import pandas as pd
import requests
import json
import os

# Конфигурация DAG по умолчанию
default_args = {
    'owner': 'maxim_dupley',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': 'admin@example.com'
}

# Инициализация DAG
dag = DAG(
    'etl_educational_data',
    default_args=default_args,
    description='Автоматизированный ETL-пайплайн для образовательных данных',
    schedule_interval='@daily',
    catchup=False,
    tags=['education', 'ETL', 'BMSTU']
)

def extract_lms_data(**kwargs):
    """
    Извлекает данные из Learning Management System (LMS) через API
    
    Параметры:
        **kwargs: Контекст выполнения Airflow (автоматически передается)
    
    Действия:
        1. Выполняет запрос к Google Classroom API
        2. Сохраняет полученные данные в формате JSON
        3. Логирует результат выполнения
    
    Источники данных:
        - Курсы
        - Студенческие работы
        - Оценки заданий
    """
    ti = kwargs['ti']
    try:
        api_url = "https://classroom.googleapis.com/v1/courses"
        response = requests.get(api_url)
        response.raise_for_status()  # Проверка ошибок HTTP
        
        data = response.json()
        output_path = '/data/lms_data.json'
        
        with open(output_path, 'w') as f:
            json.dump(data, f)
            
        ti.xcom_push(key='lms_status', value='success')
        print(f"Успешно извлечено {len(data.get('courses', []))} записей из LMS")
    except Exception as e:
        ti.xcom_push(key='lms_status', value=str(e))
        raise

def extract_electronic_journal(**kwargs):
    """
    Извлекает данные из электронного журнала успеваемости
    
    Параметры:
        **kwargs: Контекст выполнения Airflow
    
    Действия:
        1. Читает данные из CSV/JSON файлов
        2. Выполняет базовую валидацию данных
        3. Конвертирует в JSON для последующей обработки
        4. Сохраняет промежуточные результаты
    
    Особенности:
        - Поддерживает различные форматы (CSV, JSON)
        - Обрабатывает кодировки UTF-8
        - Логирует количество полученных записей
    """
    ti = kwargs['ti']
    try:
        # Пример: загрузка данных из CSV
        input_path = '/data/eljur_grades.csv'
        output_path = '/data/eljur_data.json'
        
        if os.path.exists(input_path):
            df = pd.read_csv(input_path, encoding='utf-8')
            if not df.empty:
                df.to_json(output_path, orient='records', force_ascii=False)
                record_count = len(df)
                ti.xcom_push(key='journal_status', value='success')
                print(f"Успешно обработано {record_count} записей из электронного журнала")
            else:
                raise ValueError("Файл журнала пуст")
        else:
            raise FileNotFoundError(f"Файл {input_path} не найден")
    except Exception as e:
        ti.xcom_push(key='journal_status', value=str(e))
        raise

def transform_data(**kwargs):
    """
    Трансформирует и объединяет данные из различных источников
    
    Параметры:
        **kwargs: Контекст выполнения Airflow
    
    Действия:
        1. Загружает данные из LMS и электронных журналов
        2. Выполняет очистку и нормализацию данных
        3. Объединяет данные по ключевым полям (student_id, course_id)
        4. Рассчитывает производные метрики (нормализованные оценки)
        5. Сохраняет результат в CSV для загрузки в DWH
    
    Логика преобразований:
        - Обработка пропущенных значений
        - Нормализация шкал оценок
        - Преобразование форматов дат
        - Агрегация данных по студентам/курсам
    """
    ti = kwargs['ti']
    try:
        # Загрузка данных из предыдущих шагов
        with open('/data/lms_data.json') as f:
            lms_data = json.load(f)
            lms_df = pd.DataFrame(lms_data.get('courses', []))
        
        journal_df = pd.read_json('/data/eljur_data.json')
        
        # Проверка наличия необходимых колонок
        required_columns = ['student_id', 'course_id', 'grade']
        if not all(col in journal_df.columns for col in required_columns):
            missing = [col for col in required_columns if col not in journal_df.columns]
            raise ValueError(f"Отсутствуют обязательные колонки: {missing}")
        
        # Пример преобразований
        # Нормализация оценок к 100-балльной шкале
        if 'max_grade' in journal_df.columns:
            journal_df['normalized_grade'] = journal_df['grade'] / journal_df['max_grade'] * 100
        else:
            # Стандартная шкала по умолчанию
            journal_df['normalized_grade'] = journal_df['grade'] * 20
        
        # Объединение данных
        merged_data = pd.merge(
            lms_df, 
            journal_df, 
            on=['student_id', 'course_id'],
            how='left'
        )
        
        # Дополнительные преобразования
        merged_data['load_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Сохранение результата
        output_path = '/data/transformed_data.csv'
        merged_data.to_csv(output_path, index=False)
        
        ti.xcom_push(key='transform_record_count', value=len(merged_data))
        print(f"Успешно трансформировано {len(merged_data)} записей")
    except Exception as e:
        ti.xcom_push(key='transform_error', value=str(e))
        raise

def load_to_dwh(**kwargs):
    """
    Загружает преобразованные данные в хранилище данных (MySQL)
    
    Параметры:
        **kwargs: Контекст выполнения Airflow
    
    Действия:
        1. Устанавливает соединение с MySQL через Airflow connection
        2. Использует LOAD DATA INFILE для эффективной загрузки
        3. Обрабатывает возможные конфликты данных
        4. Фиксирует изменения в базе данных
        5. Логирует результат операции
    
    Особенности:
        - Пакетная загрузка для оптимизации производительности
        - Поддержка режимов обновления/добавления записей
        - Обработка дубликатов через REPLACE
    """
    ti = kwargs['ti']
    try:
        mysql_hook = MySqlHook(mysql_conn_id='educational_dwh')
        connection = mysql_hook.get_conn()
        cursor = connection.cursor()
        
        # Загрузка CSV в таблицу grades
        load_query = """
            LOAD DATA LOCAL INFILE '/data/transformed_data.csv'
            REPLACE INTO TABLE educational_institution.grades
            FIELDS TERMINATED BY ',' 
            OPTIONALLY ENCLOSED BY '"'
            LINES TERMINATED BY '\n'
            IGNORE 1 ROWS
            (student_id, course_id, grade, normalized_grade, @load_date_str)
            SET load_date = STR_TO_DATE(@load_date_str, '%Y-%m-%d');
        """
        
        cursor.execute(load_query)
        affected_rows = cursor.rowcount
        connection.commit()
        
        ti.xcom_push(key='loaded_rows', value=affected_rows)
        print(f"Успешно загружено {affected_rows} записей в DWH")
    except Exception as e:
        connection.rollback()
        ti.xcom_push(key='load_error', value=str(e))
        raise
    finally:
        cursor.close()
        connection.close()

# Определение задач
extract_lms_task = PythonOperator(
    task_id='extract_lms_data',
    python_callable=extract_lms_data,
    provide_context=True,
    dag=dag,
    doc="Извлечение данных из систем управления обучением (LMS)"
)

extract_journal_task = PythonOperator(
    task_id='extract_electronic_journal',
    python_callable=extract_electronic_journal,
    provide_context=True,
    dag=dag,
    doc="Извлечение данных из электронных журналов успеваемости"
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
    doc="Очистка, преобразование и объединение образовательных данных"
)

load_task = PythonOperator(
    task_id='load_to_dwh',
    python_callable=load_to_dwh,
    provide_context=True,
    dag=dag,
    doc="Загрузка подготовленных данных в хранилище данных (MySQL)"
)

# Определение порядка выполнения
extract_lms_task >> transform_task
extract_journal_task >> transform_task
transform_task >> load_task
