import os
import csv
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker
from tqdm import tqdm
import numpy as np

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('edu_data_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EducationalDataGenerator:
    def __init__(self, output_dir: str = 'edu_data'):
        self.fake = Faker()
        random.seed(42)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Кэш для уникальных значений
        self.used_emails = set()
        self.used_phones = set()
        
        # Структуры для хранения данных
        self.universities = []
        self.departments = []
        self.study_groups = []
        self.teachers = []
        self.students = []
        self.courses = []
        self.schedule = []
        self.enrollments = []
        self.grades = []
        self.attendance = []
        self.assignments = []
        self.assignment_grades = []
        
        # Мэппинги для быстрого доступа
        self.university_departments = {}
        self.department_students = {}
        self.course_schedules = {}
        self.student_enrollments = {}
        self.course_assignments = {}

        # Инициализация реалистичных данных
        self._init_realistic_data()

    def _init_realistic_data(self):
        """Инициализация реалистичных данных для университетов и факультетов"""
        # Список университетов (30)
        moscow_top = [
            ('Московский государственный университет', 'Москва', 'Россия', 1755),
            ('МИРЭА — Российский технологический университет', 'Москва', 'Россия', 1947),
            ('Московский авиационный институт', 'Москва', 'Россия', 1930),
            ('Московский физико-технический институт', 'Долгопрудный', 'Россия', 1946),
            ('МГТУ им. Баумана', 'Москва', 'Россия', 1830),
            ('Санкт-Петербургский государственный университет', 'Санкт-Петербург', 'Россия', 1724),
            ('Университет ИТМО', 'Санкт-Петербург', 'Россия', 1900),
            ('РАНХиГС', 'Москва', 'Россия', 1977),
            ('Высшая школа экономики', 'Москва', 'Россия', 1992),
            ('МГИМО', 'Москва', 'Россия', 1944)
        ]
        regions_top = [
            ('Новосибирский государственный университет', 'Новосибирск', 'Россия', 1959),
            ('Томский политехнический университет', 'Томск', 'Россия', 1896),
            ('Казанский федеральный университет', 'Казань', 'Россия', 1804),
            ('Уральский федеральный университет', 'Екатеринбург', 'Россия', 1920),
            ('Самарский национальный исследовательский университет', 'Самара', 'Россия', 1942),
            ('Дальневосточный федеральный университет', 'Владивосток', 'Россия', 1899),
            ('Южный федеральный университет', 'Ростов-на-Дону', 'Россия', 1915),
            ('Сибирский федеральный университет', 'Красноярск', 'Россия', 2006),
            ('Пермский государственный университет', 'Пермь', 'Россия', 1916),
            ('Воронежский государственный университет', 'Воронеж', 'Россия', 1918)
        ]
        world_top = [
            ('Назарбаев Университет', 'Астана', 'Казахстан', 2010),
            ('Белорусский государственный университет', 'Минск', 'Беларусь', 1921),
            ('Киевский национальный университет им. Тараса Шевченко', 'Киев', 'Украина', 1834),
            ('Ереванский государственный университет', 'Ереван', 'Армения', 1919),
            ('Тбилисский государственный университет', 'Тбилиси', 'Грузия', 1918),
            ('Harvard University', 'Cambridge', 'США', 1636),
            ('University of Oxford', 'Оксфорд', 'Великобритания', 1096),
            ('Sorbonne University', 'Париж', 'Франция', 1257),
            ('The University of Tokyo', 'Токио', 'Япония', 1877),
            ('Peking University', 'Пекин', 'Китай', 1898)
        ]
        
        # Создаем список университетов
        self.universities_list = []
        for i, (name, city, country, year) in enumerate(moscow_top + regions_top + world_top, 1):
            self.universities_list.append({
                'university_id': i,
                'university_name': name,
                'city': city,
                'country': country,
                'founded_year': year
            })
        
        # Список факультетов (60 уникальных)
        self.faculty_names = [
            'Факультет информационных технологий', 'Физико-математический факультет', 'Экономический факультет',
            'Юридический факультет', 'Факультет иностранных языков', 'Факультет журналистики',
            'Факультет психологии', 'Факультет биологии', 'Факультет химии',
            'Факультет физики', 'Факультет математики', 'Факультет истории',
            'Факультет социологии', 'Факультет политологии', 'Факультет философии',
            'Факультет менеджмента', 'Факультет государственного управления', 'Факультет педагогики',
            'Факультет медицины', 'Факультет стоматологии', 'Факультет фармации',
            'Факультет экологии', 'Факультет географии', 'Факультет геологии',
            'Факультет архитектуры', 'Факультет дизайна', 'Факультет искусств',
            'Факультет музыки', 'Факультет театра', 'Факультет туризма',
            'Факультет физической культуры', 'Факультет прикладной математики', 'Факультет вычислительной техники',
            'Факультет робототехники', 'Факультет электроники', 'Факультет энергетики',
            'Факультет машиностроения', 'Факультет авиации', 'Факультет космонавтики',
            'Факультет материаловедения', 'Факультет нанотехнологий', 'Факультет статистики',
            'Факультет международных отношений', 'Факультет востоковедения', 'Факультет права',
            'Факультет рекламы и связей с общественностью', 'Факультет логистики', 'Факультет пищевых технологий',
            'Факультет агрономии', 'Факультет ветеринарии', 'Факультет зоотехнии',
            'Факультет лесного хозяйства', 'Факультет рыбного хозяйства', 'Факультет землеустройства',
            'Факультет строительства', 'Факультет транспорта', 'Факультет связи',
            'Факультет безопасности', 'Факультет управления качеством',
            'Факультет педагогики и психологии', 'Факультет компьютерных наук', 'Факультет прикладной информатики',
            'Факультет лингвистики', 'Факультет социальных наук', 'Факультет управления проектами',
            'Факультет биомедицинских технологий', 'Факультет землеустройства и кадастра', 'Факультет пищевой инженерии',
            'Факультет цифровых технологий', 'Факультет транспортных систем', 'Факультет урбанистики',
            'Факультет педагогического образования', 'Факультет физической реабилитации', 'Факультет спортивного менеджмента',
            'Факультет музыкального искусства', 'Факультет театрального искусства', 'Факультет изобразительных искусств',
            'Факультет экотехнологий', 'Факультет биотехнологий', 'Факультет химической инженерии',
            'Факультет вычислительной математики', 'Факультет искусственного интеллекта', 'Факультет цифровой экономики',
            'Факультет управления данными', 'Факультет кибербезопасности', 'Факультет инженерной физики',
            'Факультет материалов и технологий', 'Факультет медицинской биохимии', 'Факультет фармакологии',
            'Факультет молекулярной биологии', 'Факультет генетики', 'Факультет нейротехнологий',
            'Факультет когнитивных наук', 'Факультет педагогической психологии', 'Факультет дошкольного образования',
            'Факультет начального образования', 'Факультет специальной педагогики', 'Факультет коррекционной педагогики'
        ][:60]

    def _generate_unique_email(self, prefix: str) -> str:
        """Генерирует уникальный email"""
        while True:
            email = f"{prefix}{random.randint(1000, 9999)}@{self.fake.free_email_domain()}"
            if email not in self.used_emails:
                self.used_emails.add(email)
                return email

    def _generate_unique_phone(self) -> str:
        """Генерирует уникальный номер телефона"""
        while True:
            phone = self.fake.unique.phone_number()
            if phone not in self.used_phones:
                self.used_phones.add(phone)
                return phone

    def _save_to_csv(self, table_name: str, headers: list[str], data: list[tuple]):
        """Сохраняет данные в CSV файл"""
        file_path = self.output_dir / f"{table_name}.csv"
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        logger.info(f"Сгенерирован файл {file_path} с {len(data)} записями")
        return data

    def generate_universities(self):
        """Генерирует данные университетов"""
        logger.info("Генерация университетов...")
        universities = []
        
        for uni in self.universities_list:
            universities.append([
                uni['university_id'],
                uni['university_name'],
                uni['city'],
                uni['country'],
                uni['founded_year']
            ])

        headers = ['university_id', 'university_name', 'city', 'country', 'founded_year']
        self.universities = self._save_to_csv('Universities', headers, universities)
        return universities

    def generate_study_groups(self, count: int = 400):
        """Генерирует данные учебных групп"""
        logger.info(f"Генерация {count} учебных групп...")
        study_groups = []
        group_types = ['Б', 'М', 'А']  # Бакалавриат, Магистратура, Аспирантура
        
        for i in tqdm(range(1, count + 1)):
            group_type = random.choice(group_types)
            year = random.randint(1, 6) if group_type == 'Б' else random.randint(1, 2)
            group_number = random.randint(1, 20)
            study_groups.append([
                i,
                f"{group_type}{year}-{group_number:02d}"
            ])

        headers = ['study_group_id', 'group_name']
        self.study_groups = self._save_to_csv('Study_Groups', headers, study_groups)
        return study_groups

    def generate_departments(self):
        """Генерирует данные факультетов"""
        logger.info("Генерация факультетов...")
        departments = []
        
        # Распределяем факультеты по университетам (2 на университет)
        departments_per_university = {uni['university_id']: [] for uni in self.universities_list}
        
        for i in range(1, 61):
            university_id = (i - 1) // 2 + 1
            dept_name = self.faculty_names[i-1]
            
            departments_per_university[university_id].append(dept_name)
            
            departments.append([
                i,
                dept_name,
                university_id,
                None,  # head_of_department (заполнится позже)
                self.fake.date_time_this_decade().isoformat(sep=' '),
                self.fake.date_time_this_decade().isoformat(sep=' ')
            ])

        headers = ['department_id', 'department_name', 'university_id', 'head_of_department', 'created_at', 'updated_at']
        self.departments = self._save_to_csv('Departments', headers, departments)
        
        # Сохраняем мэппинг университет-факультеты
        self.university_departments = departments_per_university
        return departments

    def generate_teachers(self, count: int = 600):
        """Генерирует данные преподавателей"""
        logger.info(f"Генерация {count} преподавателей...")
        qualifications = ['Профессор', 'Доцент', 'Старший преподаватель', 'Преподаватель']
        teachers = []
        
        # Распределение по факультетам (10 на факультет)
        departments_count = {dept[0]: 0 for dept in self.departments}
        
        for i in tqdm(range(1, count + 1)):
            # Выбираем факультет с наименьшим количеством преподавателей
            department_id = min(departments_count, key=departments_count.get)
            departments_count[department_id] += 1
            
            department = next(dept for dept in self.departments if dept[0] == department_id)
            university_id = department[2]
            
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            gender = random.choice(['male', 'female'])
            
            # Рассчитываем дату приема
            hire_date = self.fake.date_between(start_date='-40y', end_date='-1y')
            
            teachers.append([
                i,
                first_name,
                last_name,
                gender,
                self.fake.country(),
                self._generate_unique_email(f"{first_name[0].lower()}.{last_name.lower()}"),
                self._generate_unique_phone(),
                random.choice(qualifications),
                hire_date.isoformat(),
                department_id,
                university_id,
                self.fake.text(80)
            ])

        headers = [
            'teacher_id', 'first_name', 'last_name', 'gender', 'nationality', 
            'email', 'phone', 'qualification', 'hire_date', 'department_id', 
            'university_id', 'biography'
        ]
        self.teachers = self._save_to_csv('Teachers', headers, teachers)
        return teachers

    def assign_department_heads(self):
        """Назначает руководителей факультетов"""
        logger.info("Назначение руководителей факультетов...")
        updated_departments = []
        
        # Группируем преподавателей по факультетам
        teachers_by_department = {}
        for teacher in self.teachers:
            dept_id = teacher[9]  # department_id
            if dept_id not in teachers_by_department:
                teachers_by_department[dept_id] = []
            teachers_by_department[dept_id].append(teacher)
        
        # Обновляем факультеты с назначенными руководителями
        for dept in self.departments:
            dept_id = dept[0]
            teachers_in_dept = teachers_by_department.get(dept_id, [])
            
            # Выбираем только профессоров и доцентов
            qualified_teachers = [t for t in teachers_in_dept if t[7] in ['Профессор', 'Доцент']]
            
            if qualified_teachers:
                head = random.choice(qualified_teachers)
                head_id = head[0]
            else:
                head_id = random.choice(teachers_in_dept)[0] if teachers_in_dept else None
            
            updated_dept = dept.copy()
            updated_dept[3] = head_id  # head_of_department
            updated_departments.append(updated_dept)
        
        # Сохраняем обновленные данные
        headers = ['department_id', 'department_name', 'university_id', 'head_of_department', 'created_at', 'updated_at']
        self.departments = self._save_to_csv('Departments', headers, updated_departments)
        return updated_departments

    def generate_students(self, count: int = 12000):
        """Генерирует данные студентов"""
        logger.info(f"Генерация {count} студентов...")
        statuses = ['обучается', 'отчислен', 'академический_отпуск']
        students = []
        
        # Распределение студентов по группам (20-40 на группу)
        group_capacities = {}
        for group in self.study_groups:
            group_id = group[0]
            group_capacities[group_id] = random.randint(20, 40)
        
        # Распределение групп по факультетам
        department_groups = {}
        for dept in self.departments:
            dept_id = dept[0]
            # Каждый факультет получает 6-7 групп
            department_groups[dept_id] = random.sample(self.study_groups, random.randint(6, 7))
        
        # Сохраняем распределение студентов по факультетам
        self.department_students = {dept[0]: 0 for dept in self.departments}
        
        student_id = 1
        for group in tqdm(self.study_groups, desc="Группы"):
            group_id = group[0]
            capacity = group_capacities[group_id]
            
            # Находим факультет для этой группы
            department_id = next(
                dept_id for dept_id, groups in department_groups.items() 
                if any(g[0] == group_id for g in groups)
            )
            department = next(dept for dept in self.departments if dept[0] == department_id)
            university_id = department[2]
            
            for _ in range(capacity):
                first_name = self.fake.first_name()
                last_name = self.fake.last_name()
                gender = random.choice(['male', 'female'])
                
                # Генерация даты зачисления
                enrollment_date = self.fake.date_between(start_date='-6y', end_date='-6m')
                
                # Генерация даты рождения (16-25 лет на момент зачисления)
                min_birth_date = enrollment_date - timedelta(days=365*25)
                max_birth_date = enrollment_date - timedelta(days=365*16)
                date_of_birth = self.fake.date_between_dates(min_birth_date, max_birth_date)
                
                # Генерация email и телефона
                email = self._generate_unique_email(f"{first_name[0].lower()}.{last_name.lower()}.stud")
                phone = self._generate_unique_phone() if random.random() > 0.1 else ""  # 10% без телефона
                
                students.append([
                    student_id,
                    first_name,
                    last_name,
                    gender,
                    self.fake.country(),
                    date_of_birth.isoformat(),
                    email,
                    phone,
                    enrollment_date.isoformat(),
                    department_id,
                    university_id,
                    group_id,
                    random.choices(statuses, weights=[0.85, 0.1, 0.05])[0],
                    self.fake.text(60)
                ])
                
                self.department_students[department_id] += 1
                student_id += 1

        headers = [
            'student_id', 'first_name', 'last_name', 'gender', 'nationality', 
            'date_of_birth', 'email', 'phone', 'enrollment_date', 'department_id', 
            'university_id', 'study_group_id', 'status', 'biography'
        ]
        self.students = self._save_to_csv('Students', headers, students)
        return students

    def generate_courses(self, count: int = 800):
        """Генерирует данные курсов"""
        logger.info(f"Генерация {count} курсов...")
        courses = []
        course_types = ['Базовая', 'Профильная', 'Спецкурс', 'Факультатив', 'Практикум']
        
        # Распределение по факультетам (10-20 на факультет)
        departments_count = {dept[0]: 0 for dept in self.departments}
        courses_per_department = {
            dept_id: random.randint(10, 20) 
            for dept_id in departments_count.keys()
        }
        
        course_id = 1
        for department_id, course_count in tqdm(courses_per_department.items(), desc="Факультеты"):
            department = next(dept for dept in self.departments if dept[0] == department_id)
            university_id = department[2]
            
            # Выбираем преподавателей этого факультета
            dept_teachers = [t for t in self.teachers if t[9] == department_id]
            
            for _ in range(course_count):
                # Выбираем случайного преподавателя
                teacher = random.choice(dept_teachers) if dept_teachers else None
                teacher_id = teacher[0] if teacher else None
                
                # Генерация дат курса
                start_date = self.fake.date_between(start_date='-3y', end_date='-1y')
                end_date = start_date + timedelta(days=random.randint(90, 180))
                
                course_type = random.choice(course_types)
                courses.append([
                    course_id,
                    f"{course_type} курс: {self.fake.catch_phrase()}",
                    self.fake.text(80),
                    random.randint(1, 5),  # credits
                    teacher_id,
                    department_id,
                    start_date.isoformat(),
                    end_date.isoformat()
                ])
                course_id += 1

        headers = [
            'course_id', 'course_name', 'description', 'credits', 
            'teacher_id', 'department_id', 'start_date', 'end_date'
        ]
        self.courses = self._save_to_csv('Courses', headers, courses)
        return courses

    def generate_schedule(self, count: int = 5000):
        """Генерирует расписание занятий"""
        logger.info(f"Генерация {count} записей расписания...")
        schedule = []
        durations = [45, 60, 90, 120, 180]
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        # Распределение занятий по курсам
        courses_count = {course[0]: 0 for course in self.courses}
        classes_per_course = {
            course_id: random.randint(5, 8) 
            for course_id in courses_count.keys()
        }
        
        # Сохраняем расписание по курсам для посещаемости
        self.course_schedules = {course_id: [] for course_id in courses_count.keys()}
        
        schedule_id = 1
        for course in tqdm(self.courses, desc="Курсы"):
            course_id = course[0]
            start_date = datetime.strptime(course[6], '%Y-%m-%d').date()
            end_date = datetime.strptime(course[7], '%Y-%m-%d').date()
            
            # Выбираем преподавателя курса
            teacher_id = course[4]
            
            # Генерация занятий для курса
            for _ in range(classes_per_course[course_id]):
                # Выбираем день недели
                class_day = random.choice(days_of_week)
                
                # Генерация времени занятия
                class_time = datetime.combine(
                    self.fake.date_between_dates(start_date, end_date),
                    datetime.strptime(f"{random.randint(8, 20)}:{random.choice([0, 15, 30, 45]):02d}", "%H:%M").time()
                )
                
                schedule.append([
                    schedule_id,
                    course_id,
                    teacher_id,
                    f"Корпус-{random.randint(1,6)} ауд-{random.randint(100,599)}",
                    class_time.isoformat(sep=' '),
                    random.choice(durations)
                ])
                
                self.course_schedules[course_id].append(schedule_id)
                schedule_id += 1

        # Дополняем до нужного количества
        while schedule_id <= count:
            course = random.choice(self.courses)
            course_id = course[0]
            teacher_id = course[4]
            start_date = datetime.strptime(course[6], '%Y-%m-%d').date()
            end_date = datetime.strptime(course[7], '%Y-%m-%d').date()
            
            class_time = datetime.combine(
                self.fake.date_between_dates(start_date, end_date),
                datetime.strptime(f"{random.randint(8, 20)}:{random.choice([0, 15, 30, 45]):02d}", "%H:%M").time()
            )
            
            schedule.append([
                schedule_id,
                course_id,
                teacher_id,
                f"Корпус-{random.randint(1,6)} ауд-{random.randint(100,599)}",
                class_time.isoformat(sep=' '),
                random.choice(durations)
            ])
            
            self.course_schedules[course_id].append(schedule_id)
            schedule_id += 1

        headers = [
            'schedule_id', 'course_id', 'teacher_id', 
            'classroom', 'class_time', 'duration'
        ]
        self.schedule = self._save_to_csv('Schedule', headers, schedule)
        return schedule

    def generate_enrollments(self, count: int = 40000):
        """Генерирует записи о зачислениях на курсы"""
        logger.info(f"Генерация {count} зачислений на курсы...")
        enrollments = []
        
        # Создаем структуру для отслеживания зачислений
        self.student_enrollments = {student[0]: [] for student in self.students}
        
        # Распределяем курсы по студентам
        enrollments_per_student = np.random.normal(3.3, 1.0, len(self.students))
        enrollments_per_student = np.clip(enrollments_per_student, 1, 8).astype(int)
        
        enrollment_id = 1
        for i, student in tqdm(enumerate(self.students), total=len(self.students), desc="Студенты"):
            student_id = student[0]
            department_id = student[9]
            university_id = student[10]
            
            # Выбираем курсы того же факультета (80%) или другого факультета того же университета (20%)
            same_department_courses = [c for c in self.courses if c[5] == department_id]
            same_university_courses = [c for c in self.courses if 
                                      any(dept[2] == university_id for dept in self.departments if dept[0] == c[5])]
            
            # Выбираем курсы для студента
            selected_courses = set()
            for _ in range(enrollments_per_student[i]):
                if same_department_courses and (random.random() < 0.8 or not same_university_courses):
                    course = random.choice(same_department_courses)
                elif same_university_courses:
                    course = random.choice(same_university_courses)
                else:
                    course = random.choice(self.courses)
                
                # Убедимся, что курс не дублируется
                if course[0] not in selected_courses:
                    selected_courses.add(course[0])
                    enrollments.append([
                        enrollment_id,
                        student_id,
                        course[0],
                        student[8]  # enrollment_date
                    ])
                    self.student_enrollments[student_id].append(course[0])
                    enrollment_id += 1
        
        # Дополняем до нужного количества
        while enrollment_id <= count:
            student = random.choice(self.students)
            student_id = student[0]
            department_id = student[9]
            
            # Выбираем курс
            same_department_courses = [c for c in self.courses if c[5] == department_id]
            course = random.choice(same_department_courses) if same_department_courses else random.choice(self.courses)
            
            # Проверяем, что студент еще не записан на этот курс
            if course[0] not in self.student_enrollments[student_id]:
                enrollments.append([
                    enrollment_id,
                    student_id,
                    course[0],
                    student[8]  # enrollment_date
                ])
                self.student_enrollments[student_id].append(course[0])
                enrollment_id += 1

        headers = ['enrollment_id', 'student_id', 'course_id', 'enrollment_date']
        self.enrollments = self._save_to_csv('Enrollments', headers, enrollments)
        return enrollments

    def generate_grades(self, count: int = 40000):
        """Генерирует оценки студентов"""
        logger.info(f"Генерация {count} оценок...")
        grades = []
        exam_types = ['экзамен', 'зачет', 'курсовая']
        
        # Используем существующие зачисления как основу
        grade_id = 1
        for enrollment in tqdm(random.sample(self.enrollments, min(count, len(self.enrollments)))):
            student_id = enrollment[1]
            course_id = enrollment[2]
            
            # Находим дату окончания курса
            course = next(c for c in self.courses if c[0] == course_id)
            end_date = datetime.strptime(course[7], '%Y-%m-%d').date()
            
            # Генерируем оценку и дату оценки
            grade = round(random.uniform(2.0, 5.0), 1)
            grade_date = self.fake.date_between_dates(
                start_date=end_date - timedelta(days=30),
                end_date=end_date
            )
            
            grades.append([
                grade_id,
                student_id,
                course_id,
                grade,
                grade_date.isoformat(),
                random.choice(exam_types),
                self.fake.sentence() if random.random() > 0.7 else ""
            ])
            grade_id += 1

        # Дополняем до нужного количества
        while grade_id <= count:
            enrollment = random.choice(self.enrollments)
            student_id = enrollment[1]
            course_id = enrollment[2]
            
            course = next(c for c in self.courses if c[0] == course_id)
            end_date = datetime.strptime(course[7], '%Y-%m-%d').date()
            
            grade = round(random.uniform(2.0, 5.0), 1)
            grade_date = self.fake.date_between_dates(
                start_date=end_date - timedelta(days=30),
                end_date=end_date + timedelta(days=30)
            )
            
            grades.append([
                grade_id,
                student_id,
                course_id,
                grade,
                grade_date.isoformat(),
                random.choice(exam_types),
                self.fake.sentence() if random.random() > 0.7 else ""
            ])
            grade_id += 1

        headers = [
            'grade_id', 'student_id', 'course_id', 'grade', 
            'grade_date', 'exam_type', 'feedback'
        ]
        self.grades = self._save_to_csv('Grades', headers, grades)
        return grades

    def generate_attendance(self, count: int = 120000):
        """Генерирует данные о посещаемости"""
        logger.info(f"Генерация {count} записей посещаемости...")
        attendance = []
        statuses = ['присутствовал', 'отсутствовал', 'уважительная_причина', 'опоздал']
        
        # Генерируем посещения на основе расписания и зачислений
        attendance_id = 1
        
        # Для каждого студента
        for student in tqdm(self.students, desc="Студенты"):
            student_id = student[0]
            
            # Пропускаем отчисленных студентов
            if student[12] != 'обучается':
                continue
                
            enrolled_courses = self.student_enrollments.get(student_id, [])
            
            # Для каждого курса, на который записан студент
            for course_id in enrolled_courses:
                # Выбираем несколько занятий по этому курсу
                course_schedules = self.course_schedules.get(course_id, [])
                if not course_schedules:
                    continue
                    
                # Студент посещает 70-90% занятий
                attendance_per_course = max(1, int(len(course_schedules) * random.uniform(0.7, 0.9)))
                selected_schedules = random.sample(course_schedules, min(attendance_per_course, len(course_schedules)))
                
                for schedule_id in selected_schedules:
                    # Находим занятие
                    schedule_item = next(s for s in self.schedule if s[0] == schedule_id)
                    class_time = datetime.fromisoformat(schedule_item[4])
                    
                    # Статус посещения
                    status = random.choices(
                        statuses, 
                        weights=[0.75, 0.15, 0.05, 0.05]
                    )[0]
                    
                    # Время отметки
                    check_time = None
                    if status in ['присутствовал', 'опоздал']:
                        # Случайное отклонение от времени занятия
                        time_diff = random.randint(-30, 30)
                        check_time = (class_time + timedelta(minutes=time_diff)).time()
                    
                    attendance.append([
                        attendance_id,
                        student_id,
                        schedule_id,
                        class_time.date().isoformat(),
                        status,
                        check_time.isoformat() if check_time else None,
                        self.fake.sentence() if random.random() > 0.9 else None
                    ])
                    attendance_id += 1
                    
                    if attendance_id > count:
                        break
                if attendance_id > count:
                    break
            if attendance_id > count:
                break

        # Дополняем до нужного количества
        while attendance_id <= count:
            student = random.choice([s for s in self.students if s[12] == 'обучается'])
            student_id = student[0]
            
            # Выбираем случайный курс студента
            enrolled_courses = self.student_enrollments.get(student_id, [])
            if not enrolled_courses:
                continue
                
            course_id = random.choice(enrolled_courses)
            course_schedules = self.course_schedules.get(course_id, [])
            if not course_schedules:
                continue
                
            schedule_id = random.choice(course_schedules)
            schedule_item = next(s for s in self.schedule if s[0] == schedule_id)
            class_time = datetime.fromisoformat(schedule_item[4])
            
            status = random.choices(
                statuses, 
                weights=[0.75, 0.15, 0.05, 0.05]
            )[0]
            
            check_time = None
            if status in ['присутствовал', 'опоздал']:
                time_diff = random.randint(-30, 30)
                check_time = (class_time + timedelta(minutes=time_diff)).time()
            
            attendance.append([
                attendance_id,
                student_id,
                schedule_id,
                class_time.date().isoformat(),
                status,
                check_time.isoformat() if check_time else None,
                self.fake.sentence() if random.random() > 0.9 else None
            ])
            attendance_id += 1

        headers = [
            'attendance_id', 'student_id', 'schedule_id', 'attendance_date', 
            'status', 'check_time', 'notes'
        ]
        self.attendance = self._save_to_csv('Attendance', headers, attendance)
        return attendance

    def generate_assignments(self, count: int = 2000):
        """Генерирует учебные задания"""
        logger.info(f"Генерация {count} заданий...")
        assignments = []
        assignment_types = ['лабораторная', 'практическая', 'доклад', 'реферат', 'другое']
        
        # Распределение заданий по курсам
        courses_count = {course[0]: 0 for course in self.courses}
        assignments_per_course = {
            course_id: random.randint(2, 4) 
            for course_id in courses_count.keys()
        }
        
        # Сохраняем задания по курсам для оценок
        self.course_assignments = {course_id: [] for course_id in courses_count.keys()}
        
        assignment_id = 1
        for course in tqdm(self.courses, desc="Курсы"):
            course_id = course[0]
            start_date = datetime.strptime(course[6], '%Y-%m-%d').date()
            end_date = datetime.strptime(course[7], '%Y-%m-%d').date()
            
            for _ in range(assignments_per_course[course_id]):
                assignment_type = random.choice(assignment_types)
                
                # Срок сдачи - в период проведения курса
                due_date = self.fake.date_between_dates(start_date, end_date)
                due_datetime = datetime.combine(due_date, datetime.strptime("23:59", "%H:%M").time())
                
                assignments.append([
                    assignment_id,
                    course_id,
                    assignment_type,
                    f"Задание по {assignment_type}",
                    self.fake.text(60),
                    100.0,  # max_score
                    due_datetime.isoformat(sep=' '),
                    self.fake.date_time_this_year().isoformat(sep=' ')
                ])
                
                self.course_assignments[course_id].append(assignment_id)
                assignment_id += 1

        # Дополняем до нужного количества
        while assignment_id <= count:
            course = random.choice(self.courses)
            course_id = course[0]
            start_date = datetime.strptime(course[6], '%Y-%m-%d').date()
            end_date = datetime.strptime(course[7], '%Y-%m-%d').date()
            
            assignment_type = random.choice(assignment_types)
            due_date = self.fake.date_between_dates(start_date, end_date)
            due_datetime = datetime.combine(due_date, datetime.strptime("23:59", "%H:%M").time())
            
            assignments.append([
                assignment_id,
                course_id,
                assignment_type,
                f"Дополнительное задание",
                self.fake.text(60),
                100.0,
                due_datetime.isoformat(sep=' '),
                self.fake.date_time_this_year().isoformat(sep=' ')
            ])
            
            self.course_assignments[course_id].append(assignment_id)
            assignment_id += 1

        headers = [
            'assignment_id', 'course_id', 'assignment_type', 'title', 
            'description', 'max_score', 'due_date', 'created_at'
        ]
        self.assignments = self._save_to_csv('Assignments', headers, assignments)
        return assignments

    def generate_assignment_grades(self, count: int = 40000):
        """Генерирует оценки за задания"""
        logger.info(f"Генерация {count} оценок за задания...")
        assignment_grades = []
        
        # Генерируем оценки на основе заданий и студентов
        assignment_grade_id = 1
        
        # Для каждого задания
        for assignment in tqdm(self.assignments, desc="Задания"):
            assignment_id = assignment[0]
            course_id = assignment[1]
            
            # Находим студентов, записанных на курс
            course_enrollments = [e for e in self.enrollments if e[2] == course_id]
            if not course_enrollments:
                continue
                
            # Студенты, выполнившие задание (60-90%)
            completion_rate = random.uniform(0.6, 0.9)
            num_students = max(1, int(len(course_enrollments) * completion_rate))
            selected_students = random.sample(course_enrollments, num_students)
            
            due_date = datetime.fromisoformat(assignment[6])
            
            for enrollment in selected_students:
                student_id = enrollment[1]
                
                # Дата сдачи (до или немного после срока)
                submission_date = due_date + timedelta(days=random.randint(-7, 2))
                
                # Оценка (50-100% от максимальной)
                score = round(random.uniform(50, 100), 2)
                
                # Дата оценки (1-7 дней после сдачи)
                graded_at = submission_date + timedelta(days=random.randint(1, 7))
                
                assignment_grades.append([
                    assignment_grade_id,
                    assignment_id,
                    student_id,
                    score,
                    submission_date.isoformat(sep=' '),
                    self.fake.sentence() if random.random() > 0.7 else None,
                    graded_at.isoformat(sep=' ')
                ])
                assignment_grade_id += 1
                
                if assignment_grade_id > count:
                    break
            if assignment_grade_id > count:
                break

        # Дополняем до нужного количества
        while assignment_grade_id <= count:
            assignment = random.choice(self.assignments)
            assignment_id = assignment[0]
            course_id = assignment[1]
            
            course_enrollments = [e for e in self.enrollments if e[2] == course_id]
            if not course_enrollments:
                continue
                
            enrollment = random.choice(course_enrollments)
            student_id = enrollment[1]
            
            due_date = datetime.fromisoformat(assignment[6])
            submission_date = due_date + timedelta(days=random.randint(-7, 2))
            score = round(random.uniform(50, 100), 2)
            graded_at = submission_date + timedelta(days=random.randint(1, 7))
            
            assignment_grades.append([
                assignment_grade_id,
                assignment_id,
                student_id,
                score,
                submission_date.isoformat(sep=' '),
                self.fake.sentence() if random.random() > 0.7 else None,
                graded_at.isoformat(sep=' ')
            ])
            assignment_grade_id += 1

        headers = [
            'assignment_grade_id', 'assignment_id', 'student_id', 'score', 
            'submission_date', 'feedback', 'graded_at'
        ]
        self.assignment_grades = self._save_to_csv('AssignmentGrades', headers, assignment_grades)
        return assignment_grades

    def generate_all_data(self):
        """Генерирует все данные для базы"""
        logger.info("Начало генерации образовательных данных...")
        
        self.generate_universities()
        self.generate_study_groups(400)
        self.generate_departments()
        self.generate_teachers(600)
        self.assign_department_heads()
        self.generate_students(12000)
        self.generate_courses(800)
        self.generate_schedule(5000)
        self.generate_enrollments(40000)
        self.generate_grades(40000)
        self.generate_attendance(120000)
        self.generate_assignments(2000)
        self.generate_assignment_grades(40000)
        
        logger.info("Генерация данных успешно завершена!")
        return {
            'universities': len(self.universities),
            'departments': len(self.departments),
            'study_groups': len(self.study_groups),
            'teachers': len(self.teachers),
            'students': len(self.students),
            'courses': len(self.courses),
            'schedule': len(self.schedule),
            'enrollments': len(self.enrollments),
            'grades': len(self.grades),
            'attendance': len(self.attendance),
            'assignments': len(self.assignments),
            'assignment_grades': len(self.assignment_grades)
        }

if __name__ == "__main__":
    generator = EducationalDataGenerator()
    stats = generator.generate_all_data()
    
    # Выводим статистику
    logger.info("\nРезультаты генерации данных:")
    for table, count in stats.items():
        logger.info(f"{table.rjust(20)}: {count}")
