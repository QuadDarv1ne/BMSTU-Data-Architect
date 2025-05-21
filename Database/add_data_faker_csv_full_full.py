import random
from datetime import datetime, timedelta
from faker import Faker
import mysql.connector

# Инициализация Faker для генерации данных на русском языке
fake = Faker('ru_RU')

# Подключение к базе данных
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="educational_institution"
)

cursor = db.cursor()

def generate_phone():
    """Генерирует российский номер телефона"""
    return f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999):07d}"

def generate_teachers(num_teachers=50):
    """Генерирует данные преподавателей"""
    qualifications = ['Доктор наук', 'Кандидат наук', 'Профессор', 'Доцент']
    for _ in range(num_teachers):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name[0].lower()}.{last_name.lower()}@uni.ru"
        phone = generate_phone()
        qualification = random.choice(qualifications)
        hire_date = fake.date_between(start_date='-30y', end_date='-1y')

        sql = "INSERT INTO Teachers (first_name, last_name, email, phone, qualification, hire_date) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (first_name, last_name, email, phone, qualification, hire_date)
        cursor.execute(sql, val)
    db.commit()

def generate_departments():
    """Генерирует данные факультетов"""
    departments = [
        'Физико-математический факультет',
        'Филологический факультет',
        'Факультет информационных технологий',
        'Химический факультет',
        'Биологический факультет',
        'Экономический факультет',
        'Исторический факультет',
        'Психологический факультет',
        'Юридический факультет',
        'Медицинский факультет'
    ]

    # Получаем случайных преподавателей для назначения заведующими
    cursor.execute("SELECT teacher_id FROM Teachers ORDER BY RAND() LIMIT 10")
    heads = [row[0] for row in cursor.fetchall()]

    for name, head in zip(departments, heads):
        sql = "INSERT INTO Departments (department_name, head_of_department) VALUES (%s, %s)"
        val = (name, head)
        cursor.execute(sql, val)
    db.commit()

def generate_students(num_students=1000):
    """Генерирует данные студентов"""
    for _ in range(num_students):
        first_name = fake.first_name()
        last_name = fake.last_name()
        date_of_birth = fake.date_of_birth(minimum_age=16, maximum_age=25)
        email = f"{first_name[0].lower()}.{last_name.lower()}@stud.uni.ru"
        phone = generate_phone()
        enrollment_date = fake.date_between(start_date='-5y', end_date='-6m')

        sql = "INSERT INTO Students (first_name, last_name, date_of_birth, email, phone, enrollment_date) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (first_name, last_name, date_of_birth, email, phone, enrollment_date)
        cursor.execute(sql, val)
    db.commit()

def generate_courses(num_courses=50):
    """Генерирует данные курсов"""
    cursor.execute("SELECT teacher_id FROM Teachers")
    teacher_ids = [row[0] for row in cursor.fetchall()]

    for _ in range(num_courses):
        course_name = fake.catch_phrase()
        description = fake.text()
        credits = random.randint(1, 5)
        teacher_id = random.choice(teacher_ids)

        sql = "INSERT INTO Courses (course_name, description, credits, teacher_id) VALUES (%s, %s, %s, %s)"
        val = (course_name, description, credits, teacher_id)
        cursor.execute(sql, val)
    db.commit()

def generate_schedule(num_entries=200):
    """Генерирует данные расписания"""
    cursor.execute("SELECT course_id, teacher_id FROM Courses")
    courses = cursor.fetchall()

    for _ in range(num_entries):
        course_id, teacher_id = random.choice(courses)
        classroom = f"Аудитория {random.randint(100, 500)}"
        class_time = fake.date_time_between(start_date='+1d', end_date='+30d')

        sql = "INSERT INTO Schedule (course_id, teacher_id, classroom, class_time) VALUES (%s, %s, %s, %s)"
        val = (course_id, teacher_id, classroom, class_time)
        cursor.execute(sql, val)
    db.commit()

def generate_enrollments(num_enrollments=2000):
    """Генерирует данные регистрации на курсы"""
    cursor.execute("SELECT student_id FROM Students")
    student_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT course_id FROM Courses")
    course_ids = [row[0] for row in cursor.fetchall()]

    for _ in range(num_enrollments):
        student_id = random.choice(student_ids)
        course_id = random.choice(course_ids)
        enrollment_date = fake.date_between(start_date='-1y', end_date='today')

        sql = "INSERT INTO Enrollments (student_id, course_id, enrollment_date) VALUES (%s, %s, %s)"
        val = (student_id, course_id, enrollment_date)
        cursor.execute(sql, val)
    db.commit()

def generate_grades(num_grades=3000):
    """Генерирует данные оценок"""
    cursor.execute("SELECT student_id, course_id FROM Enrollments")
    enrollments = cursor.fetchall()

    for _ in range(num_grades):
        student_id, course_id = random.choice(enrollments)
        grade = round(random.uniform(2.0, 5.0), 1)
        grade_date = fake.date_between(start_date='-1y', end_date='today')

        sql = "INSERT INTO Grades (student_id, course_id, grade, grade_date) VALUES (%s, %s, %s, %s)"
        val = (student_id, course_id, grade, grade_date)
        cursor.execute(sql, val)
    db.commit()

def generate_attendance(num_attendance=5000):
    """Генерирует данные посещаемости"""
    cursor.execute("SELECT student_id FROM Students")
    student_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT schedule_id FROM Schedule")
    schedule_ids = [row[0] for row in cursor.fetchall()]

    statuses = ['present', 'absent', 'excused']

    for _ in range(num_attendance):
        student_id = random.choice(student_ids)
        schedule_id = random.choice(schedule_ids)
        attendance_date = fake.date_between(start_date='-1y', end_date='today')
        status = random.choice(statuses)

        sql = "INSERT INTO Attendance (student_id, schedule_id, attendance_date, status) VALUES (%s, %s, %s, %s)"
        val = (student_id, schedule_id, attendance_date, status)
        cursor.execute(sql, val)
    db.commit()

def generate_assignments(num_assignments=200):
    """Генерирует данные учебных заданий"""
    cursor.execute("SELECT course_id FROM Courses")
    course_ids = [row[0] for row in cursor.fetchall()]

    assignment_types = ['лабораторная', 'практическая', 'доклад', 'реферат', 'другое']

    for _ in range(num_assignments):
        course_id = random.choice(course_ids)
        assignment_type = random.choice(assignment_types)
        title = fake.sentence(nb_words=4)
        description = fake.text()
        max_score = random.randint(50, 100)
        due_date = fake.date_between(start_date='+1d', end_date='+30d')

        sql = "INSERT INTO Assignments (course_id, assignment_type, title, description, max_score, due_date) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (course_id, assignment_type, title, description, max_score, due_date)
        cursor.execute(sql, val)
    db.commit()

def generate_assignment_grades(num_grades=3000):
    """Генерирует данные оценок за учебные задания"""
    cursor.execute("SELECT assignment_id FROM Assignments")
    assignment_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT student_id FROM Students")
    student_ids = [row[0] for row in cursor.fetchall()]

    for _ in range(num_grades):
        assignment_id = random.choice(assignment_ids)
        student_id = random.choice(student_ids)
        score = round(random.uniform(0, 100), 1)
        submission_date = fake.date_between(start_date='-1y', end_date='today')
        feedback = fake.text()

        sql = "INSERT INTO AssignmentGrades (assignment_id, student_id, score, submission_date, feedback) VALUES (%s, %s, %s, %s, %s)"
        val = (assignment_id, student_id, score, submission_date, feedback)
        cursor.execute(sql, val)
    db.commit()

def generate_all(num_teachers=50, num_students=1000, num_courses=50, num_entries=200, num_enrollments=2000, num_grades=3000, num_attendance=5000, num_assignments=200, num_assignment_grades=3000):
    """Основной метод генерации данных"""
    generate_teachers(num_teachers)
    generate_departments()
    generate_students(num_students)
    generate_courses(num_courses)
    generate_schedule(num_entries)
    generate_enrollments(num_enrollments)
    generate_grades(num_grades)
    generate_attendance(num_attendance)
    generate_assignments(num_assignments)
    generate_assignment_grades(num_assignment_grades)

if __name__ == "__main__":
    generate_all()
    cursor.close()
    db.close()
