"""
Установите зависимости:
```bash
pip install faker mysql-connector-python
```
"""

from faker import Faker
import mysql.connector
import random
from datetime import datetime, timedelta
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AcademicDataGenerator:
    def __init__(self, config: dict):
        self.fake = Faker('ru_RU')
        self.config = config
        self.connection = None
        self.cursor = None

    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['db_host'],
                user=self.config['db_user'],
                password=self.config['db_password'],
                database=self.config['db_name']
            )
            self.cursor = self.connection.cursor()
            logger.info("Успешное подключение к базе данных")
        except Exception as e:
            logger.error(f"Ошибка подключения: {str(e)}")
            raise

    def _execute_batch(self, query: str, data: list, batch_size: int = 1000):
        """Пакетное выполнение запросов"""
        try:
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                self.cursor.executemany(query, batch)
                self.connection.commit()
                logger.debug(f"Вставлено {len(batch)} записей")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Ошибка при выполнении пакета: {str(e)}")
            raise

    def generate_phone(self) -> str:
        """Генерация российского номера телефона"""
        return f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999):07d}"

    def generate_teachers(self):
        """Генерация преподавателей"""
        logger.info("Генерация преподавателей...")
        data = []
        
        for _ in range(self.config['num_teachers']):
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            
            data.append((
                first_name,
                last_name,
                f"{first_name[0].lower()}.{last_name.lower()}@uni.ru",
                self.generate_phone(),
                random.choice([
                    'Доктор наук',
                    'Кандидат наук',
                    'Профессор',
                    'Доцент'
                ]),
                self.fake.date_between(start_date='-30y', end_date='-1y')
            ))

        self._execute_batch(
            """INSERT INTO Teachers 
            (first_name, last_name, email, phone, qualification, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            data
        )

    def generate_departments(self):
        """Генерация факультетов"""
        logger.info("Генерация факультетов...")
        self.cursor.execute("SELECT teacher_id FROM Teachers ORDER BY RAND() LIMIT 10")
        heads = [row[0] for row in self.cursor.fetchall()]
        
        departments = [
            ('Физико-математический факультет',),
            ('Филологический факультет',),
            ('Факультет информационных технологий',),
            ('Химический факультет',),
            ('Биологический факультет',),
            ('Экономический факультет',),
            ('Исторический факультет',),
            ('Психологический факультет',),
            ('Юридический факультет',),
            ('Медицинский факультет',)
        ]
        
        data = [(name, head) for (name,), head in zip(departments, heads)]
        
        self._execute_batch(
            """INSERT INTO Departments 
            (department_name, head_of_department)
            VALUES (%s, %s)""",
            data
        )

    def generate_students(self):
        """Генерация студентов"""
        logger.info("Генерация студентов...")
        data = []
        
        for _ in range(self.config['num_students']):
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            enrollment_date = self.fake.date_between(start_date='-5y', end_date='-6m')
            date_of_birth = self.fake.date_of_birth(minimum_age=16, maximum_age=25)
            
            # Корректировка даты рождения
            min_birth_date = enrollment_date - timedelta(days=365*16)
            if date_of_birth > min_birth_date:
                date_of_birth = min_birth_date - timedelta(days=random.randint(1, 365))

            data.append((
                first_name,
                last_name,
                date_of_birth,
                f"{first_name[0].lower()}.{last_name.lower()}@stud.uni.ru",
                self.generate_phone(),
                enrollment_date
            ))

        self._execute_batch(
            """INSERT INTO Students 
            (first_name, last_name, date_of_birth, email, phone, enrollment_date)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            data
        )

    def generate_courses(self):
        """Генерация курсов"""
        logger.info("Генерация курсов...")
        self.cursor.execute("SELECT teacher_id FROM Teachers")
        teachers = [row[0] for row in self.cursor.fetchall()]
        
        course_templates = [
            ('Математический анализ', 'Основы математического анализа', 5),
            ('Программирование', 'Базовые концепции программирования', 6),
            ('История', 'Мировая история', 4),
            ('Химия', 'Общая химия', 5),
            ('Биология', 'Основы биологии', 4),
            ('Экономика', 'Принципы экономики', 5),
            ('Психология', 'Введение в психологию', 4),
            ('Право', 'Основы юриспруденции', 5),
            ('Медицина', 'Основы медицинских знаний', 6),
            ('Литература', 'Мировая литература', 3)
        ]
        
        data = []
        for teacher_id in teachers:
            course = random.choice(course_templates)
            data.append((
                f"{course[0]} {self.fake.random_int(100, 999)}",
                course[1],
                course[2],
                teacher_id
            ))

        self._execute_batch(
            """INSERT INTO Courses 
            (course_name, description, credits, teacher_id)
            VALUES (%s, %s, %s, %s)""",
            data
        )

    def generate_enrollments(self):
        """Генерация записей о зачислениях"""
        logger.info("Генерация зачислений...")
        self.cursor.execute("SELECT student_id FROM Students")
        students = [row[0] for row in self.cursor.fetchall()]
        
        self.cursor.execute("SELECT course_id FROM Courses")
        courses = [row[0] for row in self.cursor.fetchall()]
        
        data = []
        for student_id in students:
            num_enrollments = random.randint(3, self.config['max_enrollments_per_student'])
            selected_courses = random.sample(courses, num_enrollments)
            for course_id in selected_courses:
                enrollment_date = self.fake.date_between(
                    start_date='-2y', 
                    end_date='today'
                )
                data.append((
                    student_id,
                    course_id,
                    enrollment_date
                ))

        self._execute_batch(
            """INSERT INTO Enrollments 
            (student_id, course_id, enrollment_date)
            VALUES (%s, %s, %s)""",
            data
        )

    def generate_grades(self):
        """Генерация оценок"""
        logger.info("Генерация оценок...")
        self.cursor.execute("""
            SELECT e.student_id, e.course_id 
            FROM Enrollments e
            JOIN Courses c ON e.course_id = c.course_id
        """)
        enrollments = self.cursor.fetchall()
        
        data = []
        for student_id, course_id in enrollments:
            num_grades = random.randint(
                self.config['min_grades_per_course'],
                self.config['max_grades_per_course']
            )
            
            base_date = self.fake.date_between(start_date='-1y', end_date='today')
            
            for i in range(num_grades):
                grade = round(random.uniform(2.0, 5.0), 1)
                data.append((
                    student_id,
                    course_id,
                    grade,
                    base_date + timedelta(days=i*7)
                ))

        self._execute_batch(
            """INSERT INTO Grades 
            (student_id, course_id, grade, grade_date)
            VALUES (%s, %s, %s, %s)""",
            data
        )

    def generate_schedule(self):
        """Генерация расписания"""
        logger.info("Генерация расписания...")
        self.cursor.execute("SELECT course_id, teacher_id FROM Courses")
        courses = self.cursor.fetchall()
        
        data = []
        for course_id, teacher_id in courses:
            for _ in range(random.randint(10, 20)):  # 10-20 занятий на курс
                data.append((
                    course_id,
                    teacher_id,
                    f"Ауд. {random.randint(100, 500)}",
                    self.fake.date_time_between(
                        start_date='-3y',
                        end_date='+1y'
                    )
                ))

        self._execute_batch(
            """INSERT INTO Schedule 
            (course_id, teacher_id, classroom, class_time)
            VALUES (%s, %s, %s, %s)""",
            data
        )

    def generate_realistic_data(self):
        """Основной метод генерации данных"""
        try:
            self.connect()
            
            self.generate_teachers()
            self.generate_departments()
            self.generate_students()
            self.generate_courses()
            self.generate_enrollments()
            self.generate_schedule()
            self.generate_grades()
            
            logger.info("Генерация данных успешно завершена")
            
        except Exception as e:
            logger.error(f"Ошибка генерации данных: {str(e)}")
            raise
        finally:
            if self.connection:
                self.cursor.close()
                self.connection.close()

# Конфигурация
CONFIG = {
    'db_host': 'localhost',
    'db_user': 'root',
    'db_password': 'password',
    'db_name': 'educational_institution',
    'num_teachers': 100,
    'num_students': 10000,
    'max_enrollments_per_student': 8,
    'min_grades_per_course': 3,
    'max_grades_per_course': 10
}

if __name__ == "__main__":
    generator = AcademicDataGenerator(CONFIG)
    generator.generate_realistic_data()
