"""
1. Установите зависимости:
   ```bash
   pip install faker mysql-connector-python
   ```

2. Настройте параметры подключения в коде:
   ```bash
    conn = mysql.connector.connect(
    host="localhost",
    user="your_username",
    password="your_password",
    database="educational_institution"
    )
   ```

3. Запустите скрипт:
   ```bash
   python data_generator.py
   ```

4. Для генерации больших объемов:
- Увеличьте значения в CONFIG
- Используйте параметр batch_size=5000
- Запускайте на сервере с достаточными ресурсами
"""

from faker import Faker
import mysql.connector
import random
from datetime import datetime, timedelta
import itertools

# Конфигурация генерации
CONFIG = {
    "num_teachers": 300,
    "num_students": 10000,
    "num_courses": 500,
    "num_departments": 15,
    "max_courses_per_teacher": 5,
    "max_enrollments_per_student": 8,
    "min_grades_per_course": 10,
    "batch_size": 1000
}

fake = Faker('ru_RU')

# Подключение к MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Stalkerqwe1007",
    database="educational_institution"
)
cursor = conn.cursor()

def generate_teachers():
    print("Генерация преподавателей...")
    data = []
    for _ in range(CONFIG['num_teachers']):
        data.append((
            fake.first_name(),
            fake.last_name(),
            fake.unique.email(),
            f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}",
            random.choice([
                'Доктор наук', 
                'Кандидат наук',
                'Профессор',
                'Доцент'
            ]),
            fake.date_between(start_date='-30y', end_date='-1y')
        ))
    
    for i in range(0, len(data), CONFIG['batch_size']):
        batch = data[i:i+CONFIG['batch_size']]
        cursor.executemany(
            """INSERT INTO Teachers 
            (first_name, last_name, email, phone, qualification, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            batch
        )
    conn.commit()

def generate_departments():
    print("Генерация факультетов...")
    cursor.execute("SELECT teacher_id FROM Teachers ORDER BY RAND() LIMIT %s", 
                  (CONFIG['num_departments'],))
    heads = [row[0] for row in cursor.fetchall()]
    
    departments = [
        ('Физико-математический', 'Исследования в области точных наук'),
        ('Гуманитарных наук', 'Изучение человеческой культуры'),
        ('Информационных технологий', 'Программирование и IT-технологии'),
        ('Естественных наук', 'Биология, химия, физика'),
        ('Экономический', 'Экономика и управление'),
        ('Юридический', 'Правовые дисциплины'),
        ('Медицинский', 'Подготовка медицинских специалистов'),
        ('Лингвистический', 'Изучение иностранных языков'),
        ('Психологический', 'Психология и поведение человека'),
        ('Исторический', 'Изучение исторических процессов')
    ]
    
    data = []
    for i, (name, desc) in enumerate(departments):
        data.append((
            f"{name} факультет",
            heads[i] if i < len(heads) else None
        ))
    
    cursor.executemany(
        """INSERT INTO Departments 
        (department_name, head_of_department)
        VALUES (%s, %s)""",
        data
    )
    conn.commit()

def generate_students():
    print("Генерация студентов...")
    data = []
    for _ in range(CONFIG['num_students']):
        enrollment_date = fake.date_between(start_date='-5y', end_date='-6m')
        data.append((
            fake.first_name(),
            fake.last_name(),
            fake.date_of_birth(minimum_age=16, maximum_age=25),
            fake.unique.email(),
            f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}",
            enrollment_date
        ))
    
    for i in range(0, len(data), CONFIG['batch_size']):
        batch = data[i:i+CONFIG['batch_size']]
        cursor.executemany(
            """INSERT INTO Students 
            (first_name, last_name, date_of_birth, email, phone, enrollment_date)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            batch
        )
    conn.commit()

def generate_courses():
    print("Генерация курсов...")
    cursor.execute("SELECT teacher_id FROM Teachers")
    teachers = [row[0] for row in cursor.fetchall()]
    
    courses = []
    course_templates = [
        ('Основы программирования', 'Базовые концепции программирования', 4),
        ('Высшая математика', 'Математический анализ и линейная алгебра', 6),
        ('Мировая литература', 'Анализ литературных произведений', 3),
        ('Общая химия', 'Основные химические процессы', 5),
        ('Экономическая теория', 'Принципы микро- и макроэкономики', 4),
        ('История искусств', 'Развитие искусства через века', 3),
        ('Анатомия человека', 'Строение человеческого тела', 6),
        ('Психология личности', 'Теории личности и их развитие', 4),
        ('Международное право', 'Основы международного законодательства', 5),
        ('Статистика', 'Статистические методы анализа данных', 4)
    ]
    
    # Генерация вариантов курсов
    for _ in range(CONFIG['num_courses']):
        base_course = random.choice(course_templates)
        courses.append((
            f"{base_course[0]} {fake.random_int(100, 999)}",
            base_course[1],
            base_course[2],
            random.choice(teachers)
        ))
    
    for i in range(0, len(courses), CONFIG['batch_size']):
        batch = courses[i:i+CONFIG['batch_size']]
        cursor.executemany(
            """INSERT INTO Courses 
            (course_name, description, credits, teacher_id)
            VALUES (%s, %s, %s, %s)""",
            batch
        )
    conn.commit()

def generate_enrollments():
    print("Генерация записей о зачислениях...")
    cursor.execute("SELECT student_id FROM Students")
    students = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT course_id FROM Courses")
    courses = [row[0] for row in cursor.fetchall()]
    
    data = []
    for student_id in students:
        num_enrollments = random.randint(3, CONFIG['max_enrollments_per_student'])
        for course_id in random.sample(courses, num_enrollments):
            enrollment_date = fake.date_between(
                start_date='-2y', 
                end_date='today'
            )
            data.append((
                student_id,
                course_id,
                enrollment_date
            ))
    
    for i in range(0, len(data), CONFIG['batch_size']):
        batch = data[i:i+CONFIG['batch_size']]
        cursor.executemany(
            """INSERT INTO Enrollments 
            (student_id, course_id, enrollment_date)
            VALUES (%s, %s, %s)""",
            batch
        )
    conn.commit()

def generate_grades():
    print("Генерация оценок...")
    cursor.execute("""
        SELECT e.student_id, e.course_id 
        FROM Enrollments e
        JOIN Courses c ON e.course_id = c.course_id
    """)
    enrollments = cursor.fetchall()
    
    data = []
    for enrollment in enrollments:
        num_grades = random.randint(CONFIG['min_grades_per_course'], 
                                  CONFIG['min_grades_per_course'] + 5)
        for _ in range(num_grades):
            grade_date = fake.date_between(
                start_date='-1y', 
                end_date='today'
            )
            data.append((
                enrollment[0],
                enrollment[1],
                round(random.uniform(2.0, 5.0), 1),
                grade_date
            ))
    
    for i in range(0, len(data), CONFIG['batch_size']):
        batch = data[i:i+CONFIG['batch_size']]
        cursor.executemany(
            """INSERT INTO Grades 
            (student_id, course_id, grade, grade_date)
            VALUES (%s, %s, %s, %s)""",
            batch
        )
    conn.commit()

def generate_assignments():
    print("Генерация учебных заданий...")
    cursor.execute("SELECT course_id FROM Courses")
    courses = [row[0] for row in cursor.fetchall()]
    
    data = []
    for course_id in courses:
        for _ in range(random.randint(3, 8)):
            data.append((
                course_id,
                random.choice(['лабораторная', 'практическая', 'реферат', 'доклад']),
                f"Задание {fake.random_int(1, 100)} по курсу {course_id}",
                fake.paragraph(nb_sentences=3),
                random.choice([50, 100, 150]),
                fake.date_between(start_date='+1m', end_date='+3m')
            ))
    
    for i in range(0, len(data), CONFIG['batch_size']):
        batch = data[i:i+CONFIG['batch_size']]
        cursor.executemany(
            """INSERT INTO Assignments 
            (course_id, assignment_type, title, description, max_score, due_date)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            batch
        )
    conn.commit()

def generate_assignment_grades():
    print("Генерация оценок за задания...")
    cursor.execute("SELECT assignment_id, course_id FROM Assignments")
    assignments = cursor.fetchall()
    
    cursor.execute("SELECT student_id FROM Students")
    students = [row[0] for row in cursor.fetchall()]
    
    data = []
    for assignment_id, course_id in assignments:
        cursor.execute(
            "SELECT student_id FROM Enrollments WHERE course_id = %s",
            (course_id,)
        )
        enrolled_students = [row[0] for row in cursor.fetchall()]
        
        for student_id in random.sample(
            enrolled_students, 
            k=int(len(enrolled_students)*0.8)
        ):
            data.append((
                assignment_id,
                student_id,
                random.randint(0, 100),
                fake.date_between(start_date='-1m', end_date='today'),
                fake.paragraph(nb_sentences=2)
            ))
    
    for i in range(0, len(data), CONFIG['batch_size']):
        batch = data[i:i+CONFIG['batch_size']]
        cursor.executemany(
            """INSERT INTO AssignmentGrades 
            (assignment_id, student_id, score, submission_date, feedback)
            VALUES (%s, %s, %s, %s, %s)""",
            batch
        )
    conn.commit()

def main():
    try:
        tables = [
            ('Teachers', generate_teachers),
            ('Departments', generate_departments),
            ('Students', generate_students),
            ('Courses', generate_courses),
            ('Enrollments', generate_enrollments),
            ('Grades', generate_grades),
            ('Assignments', generate_assignments),
            ('AssignmentGrades', generate_assignment_grades)
        ]
        
        for table_name, generator in tables:
            print(f"\nНачало генерации для таблицы {table_name}")
            generator()
            print(f"Генерация для {table_name} завершена")
            
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
