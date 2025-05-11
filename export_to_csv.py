"""
Установка необходимых библиотек:
~ pip install mysql-connector-python mysql
"""

import csv
import mysql.connector
from mysql.connector import Error

# Конфигурация подключения к базе данных
DB_CONFIG = {
    'host': 'localhost',
    'user': 'ваш_логин',
    'password': 'ваш_пароль',
    'database': 'educational_institution',
    'charset': 'utf8mb4'
}

# Список таблиц для экспорта
TABLES = [
    'Teachers', 'Departments', 'Students', 'Courses',
    'Schedule', 'Enrollments', 'Grades', 'Attendance',
    'Assignments', 'AssignmentGrades'
]

def export_tables_to_csv():
    try:
        # Подключение к базе данных
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        for table in TABLES:
            # Выполнение SQL-запроса
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            # Получение названий столбцов
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = [col[0] for col in cursor.fetchall()]

            # Создание CSV-файла
            with open(f'{table}.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                writer.writerow(columns)  # Запись заголовков
                writer.writerows(rows)    # Запись данных

            print(f'Таблица {table} экспортирована в {table}.csv')

    except Error as e:
        print(f'Ошибка подключения к MySQL: {e}')
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print('Соединение с базой данных закрыто')

if __name__ == '__main__':
    export_tables_to_csv()
