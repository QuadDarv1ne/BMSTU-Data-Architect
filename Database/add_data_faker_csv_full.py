"""
Генератор данных для базы данных учебного заведения
Сохраняет данные в CSV файлы для всех таблиц
"""

import os
import csv
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker
from tqdm import tqdm

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataGenerator:
    def __init__(self, output_dir: str = 'data'):
        self.fake = Faker('ru_RU')
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _generate_phone(self) -> str:
        """Генерирует российский номер телефона"""
        return f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999):07d}"
    
    def _save_to_csv(self, table_name: str, headers: list[str], data: list[tuple]):
        """Сохраняет данные в CSV файл"""
        file_path = self.output_dir / f"{table_name}.csv"
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
        logger.info(f"Сгенерирован файл {file_path} с {len(data)} записями")

    def generate_teachers(self, count: int = 50):
        """Генерирует данные преподавателей"""
        logger.info(f"Генерация {count} преподавателей...")
        data = []
        qualifications = ['Доктор наук', 'Кандидат наук', 'Профессор', 'Доцент']
        
        for _ in tqdm(range(count)):
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            data.append((
                first_name,
                last_name,
                f"{first_name[0].lower()}.{last_name.lower()}@uni.ru",
                self._generate_phone(),
                random.choice(qualifications),
                self.fake.date_between(start_date='-30y', end_date='-1y')
            ))

        headers = ['first_name', 'last_name', 'email', 'phone', 'qualification', 'hire_date']
        self._save_to_csv('Teachers', headers, data)
        return data

    def generate_departments(self, teachers: list[tuple]):
        """Генерирует данные факультетов"""
        logger.info("Генерация факультетов...")
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
        
        # Берем первых 10 преподавателей в качестве руководителей
        heads = [t[0] for t in teachers[:10]]  # teacher_id будет сгенерирован автоматически
        
        data = [(name, head) for name, head in zip(departments, heads)]
        headers = ['department_name', 'head_of_department']
        self._save_to_csv('Departments', headers, data)
        return data

    def generate_students(self, count: int = 1000):
        """Генерирует данные студентов"""
        logger.info(f"Генерация {count} студентов...")
        data = []
        
        for _ in tqdm(range(count)):
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
                self._generate_phone(),
                enrollment_date
            ))

        headers = ['first_name', 'last_name', 'date_of_birth', 'email', 'phone', 'enrollment_date']
        self._save_to_csv('Students', headers, data)
        return data

    def generate_courses(self, teachers: list[tuple], count_per_teacher: int = 2):
        """Генерирует данные курсов"""
        logger.info(f"Генерация курсов ({count_per_teacher} на преподавателя)...")
        courses = [
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
        for teacher in teachers:
            for _ in range(count_per_teacher):
                course = random.choice(courses)
                data.append((
                    f"{course[0]} {self.fake.random_int(100, 999)}",
                    course[1],
                    course[2],
                    teacher[0]  # teacher_id
                ))

        headers = ['course_name', 'description', 'credits', 'teacher_id']
        self._save_to_csv('Courses', headers, data)
        return data

    def generate_schedule(self, courses: list[tuple], weeks: int = 16):
        """Генерирует расписание занятий"""
        logger.info(f"Генерация расписания на {weeks} недель...")
        data = []
        
        for course in courses:
            for week in range(weeks):
                data.append((
                    course[0],  # course_id
                    course[3],  # teacher_id
                    f"Ауд. {random.randint(100, 500)}",
                    (datetime.now() + timedelta(weeks=week)).replace(hour=random.randint(8, 18), minute=0, second=0)
                ))

        headers = ['course_id', 'teacher_id', 'classroom', 'class_time']
        self._save_to_csv('Schedule', headers, data)
        return data

    def generate_enrollments(self, students: list[tuple], courses: list[tuple], max_per_student: int = 5):
        """Генерирует записи о зачислениях на курсы"""
        logger.info(f"Генерация зачислений (до {max_per_student} курсов на студента)...")
        data = []
        
        for student in students:
            num_courses = random.randint(1, max_per_student)
            selected_courses = random.sample(courses, num_courses)
            for course in selected_courses:
                data.append((
                    student[0],  # student_id
                    course[0],   # course_id
                    self.fake.date_between(start_date='-1y', end_date='today')
                ))

        headers = ['student_id', 'course_id', 'enrollment_date']
        self._save_to_csv('Enrollments', headers, data)
        return data

    def generate_grades(self, enrollments: list[tuple], min_grades: int = 3, max_grades: int = 10):
        """Генерирует оценки студентов"""
        logger.info(f"Генерация оценок ({min_grades}-{max_grades} на курс)...")
        data = []
        
        for enrollment in enrollments:
            num_grades = random.randint(min_grades, max_grades)
            base_date = self.fake.date_between(start_date='-6m', end_date='today')
            for i in range(num_grades):
                data.append((
                    enrollment[0],  # student_id
                    enrollment[1],  # course_id
                    round(random.uniform(2.0, 5.0), 1),
                    (base_date + timedelta(weeks=i)).isoformat()
                ))

        headers = ['student_id', 'course_id', 'grade', 'grade_date']
        self._save_to_csv('Grades', headers, data)
        return data

    def generate_attendance(self, enrollments: list[tuple], schedule: list[tuple]):
        """Генерирует данные о посещаемости"""
        logger.info("Генерация посещаемости...")
        data = []
        statuses = ['present', 'absent', 'excused']
        
        for enrollment in enrollments:
            student_id = enrollment[0]
            course_id = enrollment[1]
            
            # Находим занятия по этому курсу
            course_schedule = [s for s in schedule if s[0] == course_id]
            
            for lesson in course_schedule:
                data.append((
                    student_id,
                    lesson[0],  # schedule_id
                    lesson[3].date(),  # class_time как date
                    random.choices(statuses, weights=[0.8, 0.15, 0.05])[0]
                ))

        headers = ['student_id', 'schedule_id', 'attendance_date', 'status']
        self._save_to_csv('Attendance', headers, data)
        return data

    def generate_assignments(self, courses: list[tuple], count_per_course: int = 3):
        """Генерирует учебные задания"""
        logger.info(f"Генерация заданий ({count_per_course} на курс)...")
        data = []
        assignment_types = ['лабораторная', 'практическая', 'доклад', 'реферат', 'другое']
        
        for course in courses:
            for _ in range(count_per_course):
                assignment_type = random.choice(assignment_types)
                data.append((
                    course[0],  # course_id
                    assignment_type,
                    f"{assignment_type.capitalize()} по {course[1].split()[0]}",
                    f"Подробное описание {assignment_type} работы по курсу {course[1]}",
                    100 if assignment_type in ['лабораторная', 'практическая'] else random.randint(20, 50),
                    (datetime.now() + timedelta(weeks=random.randint(1, 8))).date()
                ))

        headers = ['course_id', 'assignment_type', 'title', 'description', 'max_score', 'due_date']
        self._save_to_csv('Assignments', headers, data)
        return data

    def generate_assignment_grades(self, assignments: list[tuple], enrollments: list[tuple]):
        """Генерирует оценки за задания"""
        logger.info("Генерация оценок за задания...")
        data = []
        
        for assignment in assignments:
            course_id = assignment[0]
            
            # Находим студентов, записанных на этот курс
            course_enrollments = [e for e in enrollments if e[1] == course_id]
            
            for enrollment in course_enrollments:
                if random.random() > 0.1:  # 90% chance of submission
                    data.append((
                        assignment[0],  # assignment_id
                        enrollment[0],  # student_id
                        round(random.uniform(assignment[4]*0.5, assignment[4])),  # score
                        (assignment[5] - timedelta(days=random.randint(0, 7))).isoformat(),
                        self.fake.paragraph() if random.random() > 0.7 else None  # feedback
                    ))

        headers = ['assignment_id', 'student_id', 'score', 'submission_date', 'feedback']
        self._save_to_csv('AssignmentGrades', headers, data)
        return data

    def generate_all_data(self, num_teachers=50, num_students=1000):
        """Генерирует все данные для базы"""
        logger.info("Начало генерации данных...")
        
        teachers = self.generate_teachers(num_teachers)
        departments = self.generate_departments(teachers)
        students = self.generate_students(num_students)
        courses = self.generate_courses(teachers)
        schedule = self.generate_schedule(courses)
        enrollments = self.generate_enrollments(students, courses)
        grades = self.generate_grades(enrollments)
        attendance = self.generate_attendance(enrollments, schedule)
        assignments = self.generate_assignments(courses)
        assignment_grades = self.generate_assignment_grades(assignments, enrollments)
        
        logger.info("Генерация данных завершена!")
        return {
            'teachers': teachers,
            'departments': departments,
            'students': students,
            'courses': courses,
            'schedule': schedule,
            'enrollments': enrollments,
            'grades': grades,
            'attendance': attendance,
            'assignments': assignments,
            'assignment_grades': assignment_grades
        }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Генератор данных для базы учебного заведения')
    parser.add_argument('--teachers', type=int, default=150, help='Количество преподавателей')
    parser.add_argument('--students', type=int, default=10000, help='Количество студентов')
    parser.add_argument('--output', type=str, default='data', help='Директория для сохранения CSV файлов')
    
    args = parser.parse_args()
    
    generator = DataGenerator(args.output)
    generator.generate_all_data(num_teachers=args.teachers, num_students=args.students)
