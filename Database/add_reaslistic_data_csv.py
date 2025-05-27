import random
import time
from datetime import datetime, timedelta
from faker import Faker
import mysql.connector
from mysql.connector import pooling, Error
from collections import defaultdict
import textwrap
import logging
import sys

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_generation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация генератора
CONFIG = {
    "num_teachers": 200,
    "num_students": 10000,
    "num_departments": 5,
    "num_courses": 50,
    "num_schedule": 200,
    "num_enrollments": 20000,
    "num_grades": 30000,
    "num_attendance": 50000,
    "num_assignments": 200,
    "num_assignment_grades": 30000,
    "batch_size": 1000,
    "academic_year": {
        "start": datetime(datetime.now().year - 1, 9, 1),
        "end": datetime(datetime.now().year, 6, 30)
    }
}

# Инициализация Faker
fake = Faker('ru_RU')
random.seed(42)

# Кэши данных
cache = {
    "emails": set(),
    "phones": set(),
    "teacher_ids": [],
    "student_ids": [],
    "course_ids": [],
    "department_ids": [],
    "schedule_ids": [],
    "assignment_ids": []
}

# Пул соединений с БД
connection_pool = pooling.MySQLConnectionPool(
    pool_name="edu_pool",
    pool_size=5,
    host="localhost",
    user="root",
    password="root", #root
    database="educational_institution",
    autocommit=False
)

def get_db_connection():
    return connection_pool.get_connection()

def execute_batch_insert(query, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany(query, data)
        conn.commit()
    except Error as e:
        logger.error(f"Ошибка вставки: {str(e)}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def generate_unique_email(first, last, domain):
    base = f"{first[0].lower()}.{last.lower()}"
    email = f"{base}@{domain}"
    counter = 1
    while email in cache["emails"]:
        email = f"{base}{counter}@{domain}"
        counter += 1
    cache["emails"].add(email)
    return email

def generate_phone():
    codes = ['901', '902', '904', '908', '910', '915', '916', '919', 
            '920', '921', '922', '923', '924', '925', '926', '927', 
            '928', '929', '930', '931', '933', '934', '936', '937', 
            '938', '939', '941', '950', '951', '952', '953', '954', 
            '955', '956', '958', '960', '961', '962', '963', '964', 
            '965', '966', '967', '968', '969', '970', '971', '977', 
            '978', '980', '981', '982', '983', '984', '985', '986', 
            '987', '988', '989', '991', '992', '993', '994', '995', 
            '996', '997', '999']
    while True:
        phone = f"+7{random.choice(codes)}{random.randint(1000000, 9999999)}"
        if phone not in cache["phones"]:
            cache["phones"].add(phone)
            return phone

def generate_teacher_bio(first, last, qualification, experience):
    research_areas = [
        "нейронные сети", "квантовая физика", "история философии",
        "мировая экономика", "биоинформатика", "теоретическая математика"
    ]
    return textwrap.dedent(f"""
    {first} {last}
    {qualification} с {experience}-летним стажем
    Специализация: {random.choice(research_areas)}
    Публикации: {random.randint(5, 45)} научных работ
    Образование: {fake.sentence(nb_words=10)}
    Контакт: {generate_phone()}
    """).strip()

def generate_student_bio(student_id):
    interests = [
        "программирование", "робототехника", "история искусства",
        "экономика", "биология", "иностранные языки"
    ]
    return textwrap.dedent(f"""
    Студент ID: {student_id}
    Увлечения: {', '.join(random.sample(interests, 2))}
    Достижения: {fake.sentence(nb_words=8)}
    Цели: {fake.sentence(nb_words=6)}
    Контактные данные: {generate_phone()}
    """).strip()

def generate_teachers():
    logger.info("Начало генерации преподавателей...")
    qualifications = ['Доктор наук']*30 + ['Кандидат наук']*100 + ['Профессор']*40 + ['Доцент']*30
    
    batch = []
    for _ in range(CONFIG["num_teachers"]):
        gender = random.choice(['male', 'female'])
        first = fake.first_name_male() if gender == 'male' else fake.first_name_female()
        last = fake.last_name_male() if gender == 'male' else fake.last_name_female()
        exp = random.randint(3, 35)
        
        teacher_data = (
            first,
            last,
            generate_unique_email(first, last, "faculty.uni.ru"),
            generate_phone(),
            random.choice(qualifications),
            fake.date_between(start_date='-30y', end_date='-1y'),
            generate_teacher_bio(first, last, random.choice(qualifications), exp),
            exp
        )
        batch.append(teacher_data)
        
        if len(batch) >= CONFIG["batch_size"]:
            execute_batch_insert(
                """INSERT INTO Teachers (first_name, last_name, email, phone, 
                qualification, hire_date, biography, experience_years) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                batch
            )
            batch = []
    
    if batch:
        execute_batch_insert(
            """INSERT INTO Teachers (first_name, last_name, email, phone, 
            qualification, hire_date, biography, experience_years) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            batch
        )
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT teacher_id FROM Teachers")
        cache["teacher_ids"] = [row[0] for row in cursor.fetchall()]
    logger.info(f"Добавлено {CONFIG['num_teachers']} преподавателей")

def generate_departments():
    logger.info("Генерация факультетов...")
    departments = [
        ('Факультет информационных технологий', 'ИТ и компьютерные науки', 1),
        ('Экономический факультет', 'Финансы и менеджмент', 2),
        ('Гуманитарный факультет', 'История и философия', 3),
        ('Инженерный факультет', 'Технические науки', 4),
        ('Медицинский факультет', 'Биомедицина', 5)
    ]
    
    execute_batch_insert(
        """INSERT INTO Departments (department_name, description, building_number) 
        VALUES (%s,%s,%s)""",
        departments
    )
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT department_id FROM Departments")
        cache["department_ids"] = [row[0] for row in cursor.fetchall()]
    logger.info("Добавлено 5 факультетов")

def generate_students():
    logger.info("Начало генерации студентов...")
    batch = []
    
    for i in range(CONFIG["num_students"]):
        gender = random.choice(['male', 'female'])
        first = fake.first_name_male() if gender == 'male' else fake.first_name_female()
        last = fake.last_name_male() if gender == 'male' else fake.last_name_female()
        
        student_data = (
            first,
            last,
            fake.date_of_birth(minimum_age=17, maximum_age=25),
            generate_unique_email(first, last, "student.uni.ru"),
            generate_phone(),
            fake.date_between(
                start_date=CONFIG["academic_year"]["start"] - timedelta(days=30),
                end_date=CONFIG["academic_year"]["start"] + timedelta(days=30)
            ),
            generate_student_bio(i + 1),
            random.choice(cache["department_ids"])
        )
        batch.append(student_data)
        
        if len(batch) >= CONFIG["batch_size"]:
            execute_batch_insert(
                """INSERT INTO Students (first_name, last_name, date_of_birth, email, 
                phone, enrollment_date, biography, department_id) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                batch
            )
            batch = []
    
    if batch:
        execute_batch_insert(
            """INSERT INTO Students (first_name, last_name, date_of_birth, email, 
            phone, enrollment_date, biography, department_id) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            batch
        )
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id FROM Students")
        cache["student_ids"] = [row[0] for row in cursor.fetchall()]
    logger.info(f"Добавлено {CONFIG['num_students']} студентов")

def generate_courses():
    logger.info("Генерация курсов...")
    courses_by_department = {
        1: [
            ('Основы Python', 'Программирование на Python для начинающих', 4),
            ('Машинное обучение', 'Основы ML и анализа данных', 5),
            ('Базы данных', 'Проектирование и работа с СУБД', 4)
        ],
        2: [
            ('Микроэкономика', 'Основы микроэкономического анализа', 4),
            ('Финансовый менеджмент', 'Управление корпоративными финансами', 5)
        ],
        3: [
            ('Философия Возрождения', 'Изучение философских течений XV-XVI веков', 3),
            ('История искусства', 'От античности до современности', 4)
        ],
        4: [
            ('Теоретическая механика', 'Основы механики сплошных сред', 5),
            ('Сопротивление материалов', 'Расчеты конструкций на прочность', 4)
        ],
        5: [
            ('Анатомия человека', 'Строение человеческого тела', 6),
            ('Биохимия', 'Основы биохимических процессов', 5)
        ]
    }
    
    batch = []
    for dept_id in cache["department_ids"]:
        courses = courses_by_department.get(dept_id, [])
        for course in courses:
            batch.append((
                course[0],
                course[1],
                course[2],
                random.choice(cache["teacher_ids"]),
                dept_id,
                fake.date_between(
                    start_date=CONFIG["academic_year"]["start"],
                    end_date=CONFIG["academic_year"]["end"])
            ))
    
    execute_batch_insert(
        """INSERT INTO Courses (course_name, description, credits, teacher_id, 
        department_id, start_date) 
        VALUES (%s,%s,%s,%s,%s,%s)""",
        batch
    )
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT course_id FROM Courses")
        cache["course_ids"] = [row[0] for row in cursor.fetchall()]
    logger.info(f"Добавлено {len(batch)} курсов")

def generate_schedule():
    logger.info("Генерация расписания...")
    timeslots = [
        ('09:00', '10:30'),
        ('11:00', '12:30'),
        ('13:30', '15:00'),
        ('15:30', '17:00'),
        ('17:30', '19:00')
    ]
    
    # Получаем курсы с преподавателями
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT course_id, teacher_id FROM Courses")
        courses = cursor.fetchall()
    
    batch = []
    for _ in range(CONFIG["num_schedule"]):
        course_id, teacher_id = random.choice(courses)
        classroom = f"Корпус {random.randint(1,3)} ауд. {random.randint(100, 500)}"
        start_date = fake.date_between_dates(
            CONFIG["academic_year"]["start"],
            CONFIG["academic_year"]["end"]
        )
        while start_date.weekday() >= 5:
            start_date += timedelta(days=1)
        start_time = random.choice(timeslots)[0]
        class_time = datetime.combine(
            start_date,
            datetime.strptime(start_time, "%H:%M").time()
        )
        
        batch.append((course_id, teacher_id, classroom, class_time))
        
        if len(batch) >= CONFIG["batch_size"]:
            execute_batch_insert(
                """INSERT INTO Schedule (course_id, teacher_id, classroom, class_time) 
                VALUES (%s,%s,%s,%s)""",
                batch
            )
            batch = []
    
    if batch:
        execute_batch_insert(
            """INSERT INTO Schedule (course_id, teacher_id, classroom, class_time) 
            VALUES (%s,%s,%s,%s)""",
            batch
        )
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT schedule_id FROM Schedule")
        cache["schedule_ids"] = [row[0] for row in cursor.fetchall()]
    logger.info(f"Добавлено {CONFIG['num_schedule']} записей расписания")

def generate_enrollments():
    logger.info("Генерация записей на курсы...")
    dept_students = defaultdict(list)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, department_id FROM Students")
        for row in cursor.fetchall():
            dept_students[row[1]].append(row[0])
    
    batch = []
    for course_id in cache["course_ids"]:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT department_id FROM Courses WHERE course_id = %s", (course_id,))
            dept_id = cursor.fetchone()[0]
        
        students = random.sample(
            dept_students.get(dept_id, []),
            k=min(200, len(dept_students.get(dept_id, [])))
        )
        enrollment_date = fake.date_between(
            CONFIG["academic_year"]["start"] - timedelta(days=30),
            CONFIG["academic_year"]["start"] + timedelta(days=30)
        )
        
        for student_id in students:
            batch.append((student_id, course_id, enrollment_date))
            if len(batch) >= CONFIG["batch_size"]:
                execute_batch_insert(
                    """INSERT INTO Enrollments (student_id, course_id, enrollment_date) 
                    VALUES (%s,%s,%s)""",
                    batch
                )
                batch = []
    
    if batch:
        execute_batch_insert(
            """INSERT INTO Enrollments (student_id, course_id, enrollment_date) 
            VALUES (%s,%s,%s)""",
            batch
        )
    logger.info(f"Добавлено {CONFIG['num_enrollments']} записей о зачислениях")

def generate_grades():
    logger.info("Генерация оценок...")
    grade_weights = [2.0]*5 + [3.0]*15 + [3.5]*20 + [4.0]*30 + [4.5]*20 + [5.0]*10
    exam_types = ['экзамен', 'зачет', 'курсовая работа']
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, course_id FROM Enrollments")
        enrollments = cursor.fetchall()
    
    batch = []
    for _ in range(CONFIG["num_grades"]):
        student_id, course_id = random.choice(enrollments)
        grade = random.choice(grade_weights)
        grade_date = fake.date_between(
            CONFIG["academic_year"]["start"],
            CONFIG["academic_year"]["end"]
        )
        exam_type = random.choice(exam_types)
        
        batch.append((student_id, course_id, grade, grade_date, exam_type))
        if len(batch) >= CONFIG["batch_size"]:
            execute_batch_insert(
                """INSERT INTO Grades (student_id, course_id, grade, 
                grade_date, exam_type) 
                VALUES (%s,%s,%s,%s,%s)""",
                batch
            )
            batch = []
    
    if batch:
        execute_batch_insert(
            """INSERT INTO Grades (student_id, course_id, grade, 
            grade_date, exam_type) 
            VALUES (%s,%s,%s,%s,%s)""",
            batch
        )
    logger.info(f"Добавлено {CONFIG['num_grades']} оценок")

def generate_attendance():
    logger.info("Генерация посещаемости...")
    statuses = ['present', 'absent']
    probabilities = [0.85, 0.10, 0.05]
    
    batch = []
    for _ in range(CONFIG["num_attendance"]):
        student_id = random.choice(cache["student_ids"])
        schedule_id = random.choice(cache["schedule_ids"])
        status = random.choices(statuses, weights=probabilities)[0]
        attendance_date = fake.date_between(
            start_date=CONFIG["academic_year"]["start"],
            end_date=CONFIG["academic_year"]["end"]
        ).strftime('%Y-%m-%d')  # Форматирование даты
        check_time = fake.time(pattern='%H:%M:%S')  # Генерация времени без микросекунд
        notes = fake.sentence(nb_words=5) if status == 'absent' else None
        
        batch.append((
            student_id, 
            schedule_id, 
            status, 
            attendance_date,
            check_time,
            notes
        ))
        
        if len(batch) >= CONFIG["batch_size"]:
            execute_batch_insert(
                """INSERT INTO Attendance (student_id, schedule_id, 
                status, attendance_date, check_time, notes) 
                VALUES (%s,%s,%s,%s,%s,%s)""",
                batch
            )
            batch = []
    
    if batch:
        execute_batch_insert(
            """INSERT INTO Attendance (student_id, schedule_id, 
            status, attendance_date, check_time, notes) 
            VALUES (%s,%s,%s,%s,%s,%s)""",
            batch
        )
    logger.info(f"Добавлено {CONFIG['num_attendance']} записей посещаемости")

def generate_assignments():
    logger.info("Генерация заданий...")
    assignment_types = ['лабораторная', 'курсовая', 'реферат', 'тест', 'проект']
    batch = []
    
    for course_id in cache["course_ids"]:
        for _ in range(random.randint(3, 8)):
            assignment_data = (
                f"Задание {random.randint(1, 100)}",
                fake.paragraph(nb_sentences=3),
                random.choice(assignment_types),
                fake.date_between(
                    start_date=CONFIG["academic_year"]["start"],
                    end_date=CONFIG["academic_year"]["end"]
                ),
                random.randint(10, 100),
                course_id
            )
            batch.append(assignment_data)
            
            if len(batch) >= CONFIG["batch_size"]:
                execute_batch_insert(
                    """INSERT INTO Assignments (title, description, 
                    assignment_type, due_date, max_score, course_id) 
                    VALUES (%s,%s,%s,%s,%s,%s)""",
                    batch
                )
                batch = []
    
    if batch:
        execute_batch_insert(
            """INSERT INTO Assignments (title, description, 
            assignment_type, due_date, max_score, course_id) 
            VALUES (%s,%s,%s,%s,%s,%s)""",
            batch
        )
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT assignment_id FROM Assignments")
        cache["assignment_ids"] = [row[0] for row in cursor.fetchall()]
    logger.info(f"Добавлено {CONFIG['num_assignments']} заданий")

def generate_assignment_grades():
    logger.info("Генерация оценок за задания...")
    batch = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT assignment_id, course_id FROM Assignments")
        assignments = cursor.fetchall()
    
    for assignment_id, course_id in assignments:
        cursor.execute(
            """SELECT student_id FROM Enrollments 
            WHERE course_id = %s""", (course_id,))
        students = [row[0] for row in cursor.fetchall()]
        
        for student_id in random.sample(students, k=min(50, len(students))):
            submission_date = fake.date_between(
                start_date=CONFIG["academic_year"]["start"],
                end_date=CONFIG["academic_year"]["end"]
            )
            score = round(random.uniform(0, 100), 1)
            feedback = fake.paragraph(nb_sentences=2)
            
            batch.append((
                assignment_id,
                student_id,
                score,
                submission_date,
                feedback
            ))
            
            if len(batch) >= CONFIG["batch_size"]:
                execute_batch_insert(
                    """INSERT INTO AssignmentGrades (assignment_id, student_id, 
                    score, submission_date, feedback) 
                    VALUES (%s,%s,%s,%s,%s)""",
                    batch
                )
                batch = []
    
    if batch:
        execute_batch_insert(
            """INSERT INTO AssignmentGrades (assignment_id, student_id, 
            score, submission_date, feedback) 
            VALUES (%s,%s,%s,%s,%s)""",
            batch
        )
    logger.info(f"Добавлено {CONFIG['num_assignment_grades']} оценок за задания")

def main():
    start_time = time.time()
    try:
        generate_teachers()
        generate_departments()
        generate_students()
        generate_courses()
        generate_schedule()
        generate_enrollments()
        generate_grades()
        generate_attendance()
        generate_assignments()
        generate_assignment_grades()
        
        logger.info(f"Общее время выполнения: {time.time() - start_time:.2f} секунд")
        logger.info("Генерация данных успешно завершена!")
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")
        raise

if __name__ == "__main__":
    main()
