import csv
import os
from tqdm import tqdm
import random
import time
from datetime import datetime, timedelta, date
from faker import Faker
import mysql.connector
from mysql.connector import pooling, Error
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import argparse
import logging
import sys
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Any, Optional
from dateutil.relativedelta import relativedelta

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_generation.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DataGenerator:
    """
    Класс для генерации и заполнения базы данных тестовыми данными образовательного учреждения.
    """

    def __init__(self, config):
        """
        Инициализация генератора данных с настройками конфигурации.

        Args:
            config: Объект конфигурации, содержащий настройки базы данных и генерации.
        """
        self.config = config
        self.fake = Faker('ru_RU')
        random.seed(config.seed)
        self.cache = defaultdict(set)
        self.used_phones = set()
        self.ids_cache = defaultdict(list)

        self.connection_pool = pooling.MySQLConnectionPool(
            pool_name="edu_pool",
            pool_size=30,  # Increased pool size
            host=config.db_host,
            user=config.db_user,
            password=config.db_password,
            database=config.db_name,
            autocommit=False,
            charset='utf8mb4'
        )

    def execute_batch(self, query: str, data: List[Tuple], desc: str = None) -> None:
        """
        Выполнение пакета SQL-запросов.

        Args:
            query: SQL-запрос для выполнения.
            data: Список кортежей, содержащих данные для вставки.
            desc: Описание для прогресс-бара.
        """
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    conn.start_transaction()
                    for i in tqdm(range(0, len(data), self.config.batch_size), desc=desc, unit="batch", leave=False):
                        batch = data[i:i + self.config.batch_size]
                        cursor.executemany(query, batch)
                    conn.commit()
                except Error as e:
                    conn.rollback()
                    logger.error(f"Ошибка: {str(e)}")
                    raise

    def clear_database(self) -> None:
        """
        Очистка всех данных из базы данных.
        """
        tables = [
            'Attendance', 'AssignmentGrades', 'Grades',
            'Enrollments', 'Schedule', 'Assignments',
            'Courses', 'Students', 'Teachers', 'Departments'
        ]

        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                    for table in tables:
                        cursor.execute(f"TRUNCATE TABLE {table}")
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                    conn.commit()
                    logger.info("База данных очищена")
                except Error as e:
                    conn.rollback()
                    logger.error(f"Ошибка очистки БД: {str(e)}")
                    raise

    def generate_departments(self) -> None:
        """
        Генерация и вставка факультетов в базу данных.
        """
        logger.info("Генерация факультетов...")
        departments = [
            ('Факультет информационных технологий',),
            ('Экономический факультет',),
            ('Гуманитарный факультет',),
            ('Инженерный факультет',),
            ('Медицинский факультет',)
        ]
        self.execute_batch(
            "INSERT IGNORE INTO Departments (department_name) VALUES (%s)",
            departments,
            desc="Вставка факультетов"
        )
        self.ids_cache["department_ids"] = self._fetch_ids("SELECT department_id FROM Departments")

    def generate_teachers(self) -> None:
        """
        Генерация и вставка преподавателей в базу данных.
        """
        logger.info("Генерация преподавателей...")
        qualifications = ['Профессор', 'Доцент', 'Старший преподаватель', 'Преподаватель']
        batch = []

        for _ in tqdm(range(self.config.num_teachers), desc="Создание преподавателей"):
            gender = random.choice(['male', 'female'])
            first = self.fake.first_name_male() if gender == 'male' else self.fake.first_name_female()
            last = self.fake.last_name_male() if gender == 'male' else self.fake.last_name_female()

            batch.append((
                first,
                last,
                self._generate_unique_value('emails', f"{first[0].lower()}.{last.lower()}@faculty.uni.ru"),
                self._generate_phone(),
                random.choice(qualifications),
                self.fake.date_between(start_date='-30y', end_date='-1y'),
                random.choice(self.ids_cache["department_ids"]),
                self.fake.paragraph(nb_sentences=3)
            ))

        self.execute_batch(
            """INSERT INTO Teachers
            (first_name, last_name, email, phone, qualification, hire_date, department_id, biography)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            batch,
            desc="Вставка преподавателей"
        )
        self.ids_cache["teacher_ids"] = self._fetch_ids("SELECT teacher_id FROM Teachers")

    def update_department_heads(self) -> None:
        """
        Обновление деканов факультетов в базе данных.
        """
        logger.info("Назначение деканов факультетов...")
        batch = []
        for dept_id in self.ids_cache["department_ids"]:
            teachers = self._fetch_ids(f"SELECT teacher_id FROM Teachers WHERE department_id = {dept_id}")
            if teachers:
                batch.append((random.choice(teachers), dept_id))

        self.execute_batch(
            "UPDATE Departments SET head_of_department = %s WHERE department_id = %s",
            batch,
            desc="Обновление деканов"
        )

    def generate_students(self) -> None:
        """
        Генерация и вставка студентов в базу данных.
        """
        logger.info("Генерация студентов...")
        batch = []
        academic_start = self.config.academic_year["start"].date()
        min_age_date = (academic_start - timedelta(days=30)) - relativedelta(years=16)

        for _ in tqdm(range(self.config.num_students), desc="Создание студентов"):
            gender = random.choice(['male', 'female'])
            first = self.fake.first_name_male() if gender == 'male' else self.fake.first_name_female()
            last = self.fake.last_name_male() if gender == 'male' else self.fake.last_name_female()

            enroll_date = self.fake.date_between(
                start_date=academic_start - timedelta(days=30),
                end_date=academic_start + timedelta(days=30)
            )

            max_birth_date = enroll_date - relativedelta(years=16)
            birth_date = self.fake.date_between(min_age_date, max_birth_date)

            batch.append((
                first,
                last,
                birth_date,
                self._generate_unique_value('emails', f"{first[0].lower()}.{last.lower()}@student.uni.ru"),
                self._generate_phone(),
                enroll_date,
                random.choice(self.ids_cache["department_ids"]),
                self.fake.paragraph(nb_sentences=2)
            ))

        self.execute_batch(
            """INSERT INTO Students
            (first_name, last_name, date_of_birth, email, phone, enrollment_date, department_id, biography)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            batch,
            desc="Вставка студентов"
        )
        self.ids_cache["student_ids"] = self._fetch_ids("SELECT student_id FROM Students")

    def generate_courses(self) -> None:
        """
        Генерация и вставка курсов в базу данных.
        """
        logger.info("Генерация курсов...")
        batch = []

        for dept_id in self.ids_cache["department_ids"]:
            for _ in range(random.randint(8, 12)):
                start_date = self.fake.date_between(
                    start_date=self.config.academic_year["start"],
                    end_date=self.config.academic_year["end"] - timedelta(days=90)
                )
                end_date = start_date + timedelta(days=random.randint(60, 120))

                batch.append((
                    self.fake.catch_phrase(),
                    self.fake.paragraph(nb_sentences=3),
                    random.randint(1, 5),
                    random.choice(self.ids_cache["teacher_ids"]),
                    dept_id,
                    start_date,
                    end_date
                ))

        self.execute_batch(
            """INSERT INTO Courses
            (course_name, description, credits, teacher_id, department_id, start_date, end_date)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            batch,
            desc="Вставка курсов"
        )
        self.ids_cache["course_ids"] = self._fetch_ids("SELECT course_id FROM Courses")

    def generate_schedule(self) -> None:
        """
        Генерация и вставка расписания в базу данных.
        """
        logger.info("Генерация расписания...")
        batch = []
        timeslots = [('09:00', 90), ('11:00', 90), ('13:30', 90), ('15:30', 90), ('17:30', 120)]
        used_schedule_entries = set()

        courses = self._fetch_rows("SELECT course_id, teacher_id FROM Courses")

        for _ in tqdm(range(self.config.num_schedule), desc="Создание расписания"):
            course_id, teacher_id = random.choice(courses)
            classroom = f"Корпус-{random.randint(1,5)} ауд-{random.randint(100, 599)}"
            start_time, duration = random.choice(timeslots)

            class_date = self.fake.date_between(
                start_date=self.config.academic_year["start"],
                end_date=self.config.academic_year["end"]
            )

            while class_date.weekday() >= 5:
                class_date += timedelta(days=1)

            class_time = datetime.combine(class_date, datetime.strptime(start_time, "%H:%M").time())

            # Create a unique key for the schedule entry
            schedule_entry_key = f"{classroom}-{class_time}"

            # Check if the schedule entry is unique
            if schedule_entry_key not in used_schedule_entries:
                used_schedule_entries.add(schedule_entry_key)
                batch.append((
                    course_id,
                    teacher_id,
                    classroom,
                    class_time,
                    duration
                ))
            else:
                # If not unique, try generating a new one
                continue

        self.execute_batch(
            """INSERT INTO Schedule
            (course_id, teacher_id, classroom, class_time, duration)
            VALUES (%s,%s,%s,%s,%s)""",
            batch,
            desc="Вставка расписания"
        )
        self.ids_cache["schedule_ids"] = self._fetch_ids("SELECT schedule_id FROM Schedule")

    def generate_enrollments(self) -> None:
        """
        Генерация и вставка записей на курсы в базу данных.
        """
        logger.info("Генерация записей на курсы...")
        batch = []

        with ThreadPoolExecutor(max_workers=15) as executor:  # Limit the number of concurrent threads
            futures = [executor.submit(self._process_course_enrollments, course_id)
                      for course_id in self.ids_cache["course_ids"]]

            for future in tqdm(futures, desc="Обработка курсов"):
                batch.extend(future.result())

        self.execute_batch(
            """INSERT INTO Enrollments
            (student_id, course_id, enrollment_date)
            VALUES (%s,%s,%s)""",
            batch,
            desc="Вставка записей"
        )

    def _process_course_enrollments(self, course_id: int) -> List[Tuple]:
        """
        Обработка записей на конкретный курс.

        Args:
            course_id: ID курса для обработки записей.

        Returns:
            Список кортежей, содержащих данные о записях.
        """
        dept_id = self._fetch_ids(f"SELECT department_id FROM Courses WHERE course_id = {course_id}")[0]
        students = self._fetch_ids(f"SELECT student_id FROM Students WHERE department_id = {dept_id}")

        return [
            (
                student_id,
                course_id,
                self.fake.date_between(
                    start_date=self.config.academic_year["start"] - timedelta(days=30),
                    end_date=self.config.academic_year["start"] + timedelta(days=30)
                )
            )
            for student_id in random.sample(students, k=min(200, len(students)))
        ]

    def generate_grades(self) -> None:
        """
        Генерация и вставка оценок в базу данных.
        """
        logger.info("Генерация оценок...")
        enrollments = self._fetch_rows("SELECT student_id, course_id FROM Enrollments")
        batch = []
        used_grade_entries = set()

        for _ in tqdm(range(self.config.num_grades), desc="Создание оценок"):
            student_id, course_id = random.choice(enrollments)
            exam_type = random.choice(['экзамен', 'зачет', 'курсовая'])

            # Create a unique key for the grade entry
            grade_entry_key = f"{student_id}-{course_id}-{exam_type}"

            # Check if the grade entry is unique
            if grade_entry_key not in used_grade_entries:
                used_grade_entries.add(grade_entry_key)
                batch.append((
                    student_id,
                    course_id,
                    round(random.uniform(2.0, 5.0), 1),
                    self.fake.date_between(
                        start_date=self.config.academic_year["start"],
                        end_date=self.config.academic_year["end"]
                    ),
                    exam_type
                ))
            else:
                # If not unique, try generating a new one
                continue

        self.execute_batch(
            """INSERT INTO Grades
            (student_id, course_id, grade, grade_date, exam_type)
            VALUES (%s,%s,%s,%s,%s)""",
            batch,
            desc="Вставка оценок"
        )

    def generate_attendance(self) -> None:
        """
        Генерация и вставка посещаемости в базу данных.
        """
        logger.info("Генерация посещаемости...")
        batch = []

        with ThreadPoolExecutor(max_workers=15) as executor:  # Limit the number of concurrent threads
            futures = [executor.submit(self._process_schedule_attendance, schedule_id)
                      for schedule_id in self.ids_cache["schedule_ids"]]

            for future in tqdm(futures, desc="Обработка занятий"):
                batch.extend(future.result())

        self.execute_batch(
            """INSERT INTO Attendance
            (student_id, schedule_id, status, attendance_date, check_time, notes)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            batch,
            desc="Вставка посещаемости"
        )

    def _process_schedule_attendance(self, schedule_id: int) -> List[Tuple]:
        """
        Обработка посещаемости для конкретного расписания.

        Args:
            schedule_id: ID расписания для обработки посещаемости.

        Returns:
            Список кортежей, содержащих данные о посещаемости.
        """
        course_id = self._fetch_ids(f"SELECT course_id FROM Schedule WHERE schedule_id = {schedule_id}")[0]
        students = self._fetch_ids(f"SELECT student_id FROM Enrollments WHERE course_id = {course_id}")
        statuses = ['present', 'absent', 'excused', 'late']
        weights = [0.75, 0.15, 0.05, 0.05]

        attendance = []
        for student_id in random.sample(students, k=min(30, len(students))):
            status = random.choices(statuses, weights=weights)[0]
            check_time = self.fake.time_object() if status in ['present', 'late'] else None

            attendance.append((
                student_id,
                schedule_id,
                status,
                self._fetch_ids(f"SELECT class_time FROM Schedule WHERE schedule_id = {schedule_id}")[0].date(),
                check_time.strftime('%H:%M:%S') if check_time else None,
                self.fake.sentence() if status == 'excused' else None
            ))
        return attendance

    def generate_assignments(self) -> None:
        """
        Генерация и вставка заданий в базу данных.
        """
        logger.info("Генерация заданий...")
        batch = []

        for course_id in self.ids_cache["course_ids"]:
            start_date = self._fetch_ids(f"SELECT start_date FROM Courses WHERE course_id = {course_id}")[0]

            for _ in range(random.randint(3, 8)):
                due_date = self.fake.date_between(
                    start_date=start_date,
                    end_date=self.config.academic_year["end"]
                )

                batch.append((
                    course_id,
                    random.choice(['лабораторная', 'практическая', 'доклад', 'реферат', 'другое']),
                    self.fake.sentence(nb_words=4),
                    self.fake.paragraph(nb_sentences=3),
                    round(random.uniform(50.0, 100.0), 2),
                    due_date
                ))

        self.execute_batch(
            """INSERT INTO Assignments
            (course_id, assignment_type, title, description, max_score, due_date)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            batch,
            desc="Вставка заданий"
        )

    def generate_assignment_grades(self) -> None:
        """
        Генерация и вставка оценок за задания в базу данных.
        """
        logger.info("Генерация оценок за задания...")
        batch = []

        with ThreadPoolExecutor(max_workers=15) as executor:  # Limit the number of concurrent threads
            assignments = self._fetch_rows("""
                SELECT a.assignment_id, c.course_id, a.due_date
                FROM Assignments a
                JOIN Courses c ON a.course_id = c.course_id
            """)

            futures = [executor.submit(self._process_assignment_grades, *assignment)
                      for assignment in assignments]

            for future in tqdm(futures, desc="Обработка заданий"):
                batch.extend(future.result())

        self.execute_batch(
            """INSERT INTO AssignmentGrades
            (assignment_id, student_id, score, submission_date, feedback)
            VALUES (%s,%s,%s,%s,%s)""",
            batch,
            desc="Вставка оценок заданий"
        )

    def _process_assignment_grades(self, assignment_id: int, course_id: int, due_date: date) -> List[Tuple]:
        """
        Обработка оценок за конкретное задание.

        Args:
            assignment_id: ID задания для обработки оценок.
            course_id: ID курса, к которому относится задание.
            due_date: Срок сдачи задания.

        Returns:
            Список кортежей, содержащих данные об оценках за задания.
        """
        students = self._fetch_ids(f"SELECT student_id FROM Enrollments WHERE course_id = {course_id}")

        return [
            (
                assignment_id,
                student_id,
                round(random.uniform(0.0, 100.0), 2),
                self.fake.date_time_between(
                    start_date=self._fetch_ids(f"SELECT start_date FROM Courses WHERE course_id = {course_id}")[0],
                    end_date=due_date
                ).strftime('%Y-%m-%d %H:%M:%S'),
                self.fake.paragraph(nb_sentences=1)
            )
            for student_id in random.sample(students, k=min(50, len(students)))
        ]

    def _generate_unique_value(self, cache_key: str, pattern: str) -> str:
        """
        Генерация уникального значения на основе шаблона.

        Args:
            cache_key: Ключ для использования в кэше.
            pattern: Шаблон для генерации значения.

        Returns:
            Уникальное значение на основе шаблона.
        """
        counter = 1
        value = pattern
        while value in self.cache[cache_key]:
            value = f"{pattern}_{counter}"
            counter += 1
        self.cache[cache_key].add(value)
        return value

    def _generate_phone(self) -> str:
        """
        Генерация случайного номера телефона.

        Returns:
            Случайно сгенерированный номер телефона.
        """
        codes = ['901', '902', '904', '908', '915', '916', '919', '920', '921', '922']
        while True:
            phone = f"+7{random.choice(codes)}{random.randint(1000000, 9999999):07d}"
            if phone not in self.used_phones:
                self.used_phones.add(phone)
                return phone

    def _fetch_ids(self, query: str) -> List[Any]:
        """
        Получение ID из базы данных на основе запроса.

        Args:
            query: SQL-запрос для выполнения.

        Returns:
            Список ID, полученных из базы данных.
        """
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return [row[0] for row in cursor.fetchall()]

    def _fetch_rows(self, query: str) -> List[Tuple]:
        """
        Получение строк из базы данных на основе запроса.

        Args:
            query: SQL-запрос для выполнения.

        Returns:
            Список строк, полученных из базы данных.
        """
        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def _write_to_csv(self, filename: str, query: str, headers: List[str]) -> None:
        """
        Запись данных из базы данных в CSV файл.

        Args:
            filename: Имя файла для записи.
            query: SQL-запрос для выполнения.
            headers: Заголовки для CSV файла.
        """
        # Ensure the directory exists
        os.makedirs('data', exist_ok=True)

        with self.connection_pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

        with open(f'data/{filename}', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(rows)

        logger.info(f"Данные записаны в файл data/{filename}")

def parse_args() -> argparse.Namespace:
    """
    Парсинг аргументов командной строки.

    Returns:
        Разобранные аргументы командной строки.
    """
    parser = argparse.ArgumentParser(description='Генератор тестовых данных для образовательного учреждения')
    parser.add_argument('--host', default='localhost', help='Хост базы данных')
    parser.add_argument('--user', default=os.getenv('DB_USER'), help='Пользователь базы данных')
    parser.add_argument('--password', default=os.getenv('DB_PASSWORD'), required=True, help='Пароль базы данных')
    parser.add_argument('--db', default='educational_institution', help='Название базы данных')
    parser.add_argument('--students', type=int, default=10000, help='Количество студентов для генерации')
    parser.add_argument('--teachers', type=int, default=200, help='Количество преподавателей для генерации')
    parser.add_argument('--courses', type=int, default=50, help='Количество курсов для генерации')
    parser.add_argument('--schedule', type=int, default=2000, help='Количество записей расписания для генерации')
    parser.add_argument('--grades', type=int, default=5000, help='Количество оценок для генерации')
    parser.add_argument('--batch', type=int, default=1000, help='Размер пакета для вставки в базу данных')
    parser.add_argument('--seed', type=int, default=42, help='Seed для генерации случайных данных')
    return parser.parse_args()

def main() -> None:
    """
    Основная функция для запуска процесса генерации данных.
    """
    args = parse_args()
    start_time = time.time()

    config = argparse.Namespace(
        db_host=args.host,
        db_user=args.user,
        db_password=args.password,
        db_name=args.db,
        num_teachers=args.teachers,
        num_students=args.students,
        num_courses=args.courses,
        num_schedule=args.schedule,
        num_grades=args.grades,  # Ensure this line is included
        batch_size=args.batch,
        seed=args.seed,
        academic_year={
            "start": datetime(datetime.now().year - 1, 9, 1),
            "end": datetime(datetime.now().year, 6, 30)
        }
    )

    try:
        generator = DataGenerator(config)
        generator.clear_database()

        generator.generate_departments()
        generator.generate_teachers()
        generator.update_department_heads()
        generator.generate_students()
        generator.generate_courses()
        generator.generate_schedule()
        generator.generate_enrollments()
        generator.generate_grades()
        generator.generate_attendance()
        generator.generate_assignments()
        generator.generate_assignment_grades()

        # Write data to CSV files
        generator._write_to_csv('departments.csv', "SELECT * FROM Departments", ['department_id', 'department_name', 'head_of_department'])
        generator._write_to_csv('teachers.csv', "SELECT * FROM Teachers", ['teacher_id', 'first_name', 'last_name', 'email', 'phone', 'qualification', 'hire_date', 'department_id', 'biography'])
        generator._write_to_csv('students.csv', "SELECT * FROM Students", ['student_id', 'first_name', 'last_name', 'date_of_birth', 'email', 'phone', 'enrollment_date', 'department_id', 'biography'])
        generator._write_to_csv('courses.csv', "SELECT * FROM Courses", ['course_id', 'course_name', 'description', 'credits', 'teacher_id', 'department_id', 'start_date', 'end_date'])
        generator._write_to_csv('schedule.csv', "SELECT * FROM Schedule", ['schedule_id', 'course_id', 'teacher_id', 'classroom', 'class_time', 'duration'])
        generator._write_to_csv('enrollments.csv', "SELECT * FROM Enrollments", ['enrollment_id', 'student_id', 'course_id', 'enrollment_date'])
        generator._write_to_csv('grades.csv', "SELECT * FROM Grades", ['grade_id', 'student_id', 'course_id', 'grade', 'grade_date', 'exam_type'])
        generator._write_to_csv('attendance.csv', "SELECT * FROM Attendance", ['attendance_id', 'student_id', 'schedule_id', 'status', 'attendance_date', 'check_time', 'notes'])
        generator._write_to_csv('assignments.csv', "SELECT * FROM Assignments", ['assignment_id', 'course_id', 'assignment_type', 'title', 'description', 'max_score', 'due_date'])
        generator._write_to_csv('assignment_grades.csv', "SELECT * FROM AssignmentGrades", ['assignment_grade_id', 'assignment_id', 'student_id', 'score', 'submission_date', 'feedback'])

        duration = timedelta(seconds=time.time() - start_time)
        logger.info(f"Общее время выполнения: {duration}")
        logger.info("Генерация данных завершена успешно!")

    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
