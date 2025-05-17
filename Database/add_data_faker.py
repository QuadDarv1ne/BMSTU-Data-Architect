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
from typing import Dict, List, Tuple
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AcademicDataGenerator:
    def __init__(self, config: Dict):
        self.fake = Faker('ru_RU')
        self.config = config
        self.connection = None
        self.cursor = None
        self._add_custom_providers()
        
        # Кэшированные данные
        self.teacher_specializations = {}
        self.course_types = {}
        self.department_info = {}

    def _add_custom_providers(self):
        """Добавление кастомных провайдеров данных"""
        class RussianAcademicProvider:
            def __init__(self, generator):
                self.generator = generator

            def academic_title(self):
                titles = [
                    ('Доктор наук', 'Профессор'),
                    ('Кандидат наук', 'Доцент'),
                    ('PhD', 'Старший преподаватель')
                ]
                return random.choice(titles)

            def university_department(self):
                departments = [
                    ('Физический', 'технический'),
                    ('Литературный', 'гуманитарный'),
                    ('Экономический', 'социальный'),
                    ('Медицинский', 'естественный')
                ]
                return random.choice(departments)

        self.fake.add_provider(RussianAcademicProvider(self.fake))

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

    def _execute_batch(self, query: str, data: List[Tuple], batch_size: int = 1000):
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
        operators = ['901', '902', '903', '904', '905', '906', '908', '909']
        return f"+7{random.choice(operators)}{self.fake.random_int(1000000, 9999999):07d}"

    def generate_teachers(self):
        """Генерация преподавателей с специализациями"""
        logger.info("Генерация преподавателей...")
        data = []
        specializations = [
            'Физика', 'Математика', 'Информатика', 
            'Литература', 'Экономика', 'Биология'
        ]
        
        for _ in range(self.config['num_teachers']):
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            qualification, position = self.fake.academic_title()
            department, department_type = self.fake.university_department()
            specialization = random.choice(specializations)
            
            self.teacher_specializations[len(data) + 1] = specialization
            
            data.append((
                first_name,
                last_name,
                f"{first_name[0].lower()}.{last_name.lower()}@uni.ru",
                self.generate_phone(),
                qualification,
                position,
                department,
                specialization,
                self.fake.date_between(start_date='-30y', end_date='-1y')
            ))

        self._execute_batch(
            """INSERT INTO Teachers 
            (first_name, last_name, email, phone, qualification, 
             position, department, specialization, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            data
        )

    def generate_courses(self):
        """Генерация курсов с учетом специализации преподавателей"""
        logger.info("Генерация курсов...")
        self.cursor.execute("SELECT teacher_id, specialization FROM Teachers")
        teachers = self.cursor.fetchall()
        
        course_templates = {
            'Физика': [
                ('Квантовая механика', 'Основы квантовой теории', 5),
                ('Термодинамика', 'Изучение тепловых процессов', 4)
            ],
            'Информатика': [
                ('Алгоритмы и структуры данных', 'Базовые алгоритмы', 6),
                ('Машинное обучение', 'Основы ML', 5)
            ],
            'Литература': [
                ('Современная поэзия', 'Анализ современных произведений', 3),
                ('Классическая литература', 'Изучение классики', 4)
            ]
        }
        
        data = []
        for teacher_id, specialization in teachers:
            for _ in range(random.randint(1, self.config['max_courses_per_teacher'])):
                course_template = random.choice(
                    course_templates.get(specialization, [('Общий курс', 'Базовые знания', 4)])
                )
                course_type = 'технический' if specialization in ['Физика', 'Информатика'] else 'гуманитарный'
                
                data.append((
                    f"{course_template[0]} {self.fake.random_int(100, 999)}",
                    course_template[1],
                    course_template[2],
                    teacher_id,
                    course_type
                ))
                self.course_types[len(data) + 1] = course_type

        self._execute_batch(
            """INSERT INTO Courses 
            (course_name, description, credits, teacher_id, course_type)
            VALUES (%s, %s, %s, %s, %s)""",
            data
        )

    def generate_students(self):
        """Генерация студентов с валидацией возраста"""
        logger.info("Генерация студентов...")
        data = []
        
        for _ in range(self.config['num_students']):
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            enrollment_date = self.fake.date_between(start_date='-5y', end_date='-6m')
            date_of_birth = self.fake.date_of_birth(minimum_age=16, maximum_age=25)
            
            # Корректировка даты рождения при необходимости
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

    def generate_grades(self):
        """Генерация реалистичных оценок с разным распределением"""
        logger.info("Генерация оценок...")
        self.cursor.execute("""
            SELECT e.student_id, e.course_id, c.course_type 
            FROM Enrollments e
            JOIN Courses c ON e.course_id = c.course_id
        """)
        enrollments = self.cursor.fetchall()
        
        data = []
        for student_id, course_id, course_type in enrollments:
            # Генерация разного количества оценок
            num_grades = random.randint(
                self.config['min_grades_per_course'],
                self.config['max_grades_per_course']
            )
            
            base_date = self.fake.date_between(start_date='-1y', end_date='today')
            
            for i in range(num_grades):
                # Разное распределение для типов курсов
                if course_type == 'технический':
                    grade = max(2.0, min(5.0, random.normalvariate(3.8, 0.7)))
                else:
                    grade = max(2.0, min(5.0, random.normalvariate(4.2, 0.5)))
                
                data.append((
                    student_id,
                    course_id,
                    round(grade, 1),
                    base_date + timedelta(days=i*7)
                ))

        self._execute_batch(
            """INSERT INTO Grades 
            (student_id, course_id, grade, grade_date)
            VALUES (%s, %s, %s, %s)""",
            data
        )

    def generate_attendance(self):
        """Генерация посещаемости коррелирующей с оценками"""
        logger.info("Генерация посещаемости...")
        self.cursor.execute("SELECT schedule_id, course_id FROM Schedule")
        schedules = self.cursor.fetchall()
        
        data = []
        for schedule_id, course_id in schedules:
            self.cursor.execute(
                "SELECT student_id FROM Enrollments WHERE course_id = %s",
                (course_id,)
            )
            students = [row[0] for row in self.cursor.fetchall()]
            
            for student_id in students:
                # Получение среднего балла студента
                self.cursor.execute(
                    "SELECT AVG(grade) FROM Grades WHERE student_id = %s",
                    (student_id,)
                )
                avg_grade = self.cursor.fetchone()[0] or 3.0
                
                # Вероятность посещения в зависимости от успеваемости
                attendance_prob = 0.7 + (avg_grade - 3.0) * 0.1
                status = 'present' if random.random() < attendance_prob else (
                    'excused' if random.random() < 0.3 else 'absent'
                )
                
                data.append((
                    student_id,
                    schedule_id,
                    self.fake.date_between(start_date='-1y', end_date='today'),
                    status
                ))

        self._execute_batch(
            """INSERT INTO Attendance 
            (student_id, schedule_id, attendance_date, status)
            VALUES (%s, %s, %s, %s)""",
            data
        )

    def generate_realistic_data(self):
        """Основной метод генерации всех данных"""
        try:
            self.connect()
            
            # Порядок генерации важен из-за внешних ключей
            self.generate_teachers()
            self.generate_courses()
            self.generate_students()
            self.generate_enrollments()
            self.generate_schedule()
            self.generate_grades()
            self.generate_assignments()
            self.generate_assignment_grades()
            self.generate_attendance()
            
            logger.info("Генерация данных успешно завершена")
            
        except Exception as e:
            logger.error(f"Ошибка генерации данных: {str(e)}")
            raise
        finally:
            if self.connection:
                self.cursor.close()
                self.connection.close()

# Пример использования
if __name__ == "__main__":
    config = {
        'db_host': 'localhost',
        'db_user': 'root',
        'db_password': 'password',
        'db_name': 'educational_institution',
        'num_teachers': 100,
        'num_students': 5000,
        'max_courses_per_teacher': 3,
        'min_grades_per_course': 5,
        'max_grades_per_course': 10
    }
    
    generator = AcademicDataGenerator(config)
    generator.generate_realistic_data()
