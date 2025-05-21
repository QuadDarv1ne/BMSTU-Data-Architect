"""
Генератор учебных данных с сохранением в БД и CSV

Установка зависимостей:
pip install faker mysql-connector-python tqdm python-dotenv
"""

from __future__ import annotations
import os
import csv
import logging
import argparse
import random
from datetime import datetime, timedelta
from typing import Generator, List, Tuple, Dict, Any
from pathlib import Path
from dataclasses import dataclass
import mysql.connector
from mysql.connector.pooling import PooledMySQLConnection
from faker import Faker
from tqdm import tqdm
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("data_gen.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

@dataclass
class DatabaseConfig:
    host: str
    user: str
    password: str
    database: str
    pool_size: int = 5

@dataclass
class AppConfig:
    db_config: DatabaseConfig
    csv_dir: Path
    batch_size: int
    num_students: int
    num_teachers: int
    max_enrollments: int
    min_grades: int
    max_grades: int

class DataGenerator:
    def __init__(self, config: AppConfig):
        self.config = config
        self.fake = Faker("ru_RU")
        self.db_pool = self._create_db_pool()
        self._prepare_filesystem()

    def _prepare_filesystem(self) -> None:
        self.config.csv_dir.mkdir(parents=True, exist_ok=True)

    def _create_db_pool(self) -> mysql.connector.pooling.MySQLConnectionPool:
        return mysql.connector.pooling.MySQLConnectionPool(
            pool_name="main_pool",
            pool_size=self.config.db_config.pool_size,
            host=self.config.db_config.host,
            user=self.config.db_config.user,
            password=self.config.db_config.password,
            database=self.config.db_config.database,
            buffered=True  # Добавляем буферизацию на уровне пула
        )

    def _get_db_connection(self) -> PooledMySQLConnection:
        return self.db_pool.get_connection()

    @staticmethod
    def _chunk_data(data: List[Tuple], chunk_size: int) -> Generator[List[Tuple], None, None]:
        for i in range(0, len(data), chunk_size):
            yield data[i : i + chunk_size]

    def _generate_phone(self) -> str:
        return f"+7{random.randint(900, 999)}{random.randint(1_000_000, 9_999_999):07d}"

    def _save_to_csv(self, table: str, headers: List[str], rows: List[Tuple]) -> None:
        file_path = self.config.csv_dir / f"{table}.csv"
        write_header = not file_path.exists()

        with open(file_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(headers)
            writer.writerows(rows)

    def _execute_batch(
        self,
        query: str,
        data: List[Tuple],
        table: str,
        cursor_description: List[Tuple[str, Any]],
    ) -> None:
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()
                for chunk in self._chunk_data(data, self.config.batch_size):
                    cursor.executemany(query, chunk)
                    conn.commit()
                    self._save_to_csv(
                        table=table,
                        headers=[desc[0] for desc in cursor_description],
                        rows=chunk,
                    )
        except Exception as e:
            logger.error(f"Ошибка при вставке в {table}: {e}")
            raise
        finally:
            cursor.close()

    def generate_teachers(self) -> None:
        logger.info("Генерация преподавателей...")
        data = []
        query = """
            INSERT INTO Teachers 
            (first_name, last_name, email, phone, qualification, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        qualifications = ["Доктор наук", "Кандидат наук", "Профессор", "Доцент"]
        
        for _ in tqdm(range(self.config.num_teachers), desc="Преподаватели"):
            first = self.fake.first_name()
            last = self.fake.last_name()
            data.append((
                first,
                last,
                f"{first[0].lower()}.{last.lower()}@uni.ru",
                self._generate_phone(),
                random.choice(qualifications),
                self.fake.date_between("-30y", "-1y"),
            ))

        with self._get_db_connection() as conn:
            with conn.cursor(buffered=True) as cursor:
                cursor.execute("SELECT * FROM Teachers LIMIT 0")
                self._execute_batch(query, data, "Teachers", cursor.description)

    def generate_departments(self) -> None:
        logger.info("Генерация факультетов...")
        with self._get_db_connection() as conn:
            with conn.cursor(buffered=True) as cursor:
                cursor.execute("SELECT teacher_id FROM Teachers ORDER BY RAND() LIMIT 10")
                heads = [row[0] for row in cursor.fetchall()]

                # Явно закрываем курсор после использования
                cursor.close()

        departments = [
            ("Физико-математический", "ФМФ"),
            ("Филологический", "ФФ"),
            ("Информационных технологий", "ФИТ"),
            ("Химический", "ХФ"),
            ("Биологический", "БФ"),
            ("Экономический", "ЭФ"),
            ("Исторический", "ИФ"),
            ("Психологический", "ПФ"),
            ("Юридический", "ЮФ"),
            ("Медицинский", "МФ"),
        ]

        data = [
            (f"{name} факультет", abbr, head)
            for (name, abbr), head in zip(departments, heads)
        ]

        query = """
            INSERT INTO Departments 
            (department_name, abbreviation, head_id)
            VALUES (%s, %s, %s)
        """
        
        with self._get_db_connection() as conn:
            with conn.cursor(buffered=True) as cursor:
                cursor.execute("SELECT * FROM Departments LIMIT 0")
                self._execute_batch(query, data, "Departments", cursor.description)

    def generate_students(self) -> None:
        logger.info("Генерация студентов...")
        data = []
        query = """
            INSERT INTO Students 
            (first_name, last_name, date_of_birth, email, phone, enrollment_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for _ in tqdm(range(self.config.num_students), desc="Студенты"):
            first = self.fake.first_name()
            last = self.fake.last_name()
            enroll_date = self.fake.date_between("-5y", "-6m")
            birth_date = self.fake.date_of_birth(minimum_age=16, maximum_age=25)
            
            if birth_date > enroll_date - timedelta(days=365*16):
                birth_date = enroll_date - timedelta(days=365*16 + random.randint(1, 365))

            data.append((
                first,
                last,
                birth_date,
                f"{first[0].lower()}.{last.lower()}@stud.uni.ru",
                self._generate_phone(),
                enroll_date,
            ))

        with self._get_db_connection() as conn:
            with conn.cursor(buffered=True) as cursor:
                cursor.execute("SELECT * FROM Students LIMIT 0")
                self._execute_batch(query, data, "Students", cursor.description)

    def generate_all(self) -> None:
        try:
            self.generate_teachers()
            self.generate_departments()
            self.generate_students()
            logger.info("Генерация данных успешно завершена")
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            raise

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Генератор учебных данных")
    parser.add_argument(
        "--students", 
        type=int, 
        default=1000,
        help="Количество студентов",
    )
    parser.add_argument(
        "--teachers", 
        type=int, 
        default=50,
        help="Количество преподавателей",
    )
    return parser.parse_args()

def load_config(args: argparse.Namespace) -> AppConfig:
    return AppConfig(
        db_config=DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "university_db"),
            pool_size=int(os.getenv("DB_POOL_SIZE", 5)),
        ),
        csv_dir=Path(os.getenv("CSV_DIR", "data")),
        batch_size=int(os.getenv("BATCH_SIZE", 1000)),
        num_students=args.students,
        num_teachers=args.teachers,
        max_enrollments=int(os.getenv("MAX_ENROLLMENTS", 8)),
        min_grades=int(os.getenv("MIN_GRADES", 3)),
        max_grades=int(os.getenv("MAX_GRADES", 10)),
    )

if __name__ == "__main__":
    args = parse_args()
    config = load_config(args)
    
    try:
        generator = DataGenerator(config)
        generator.generate_all()
    except Exception as e:
        logger.error(f"Ошибка выполнения: {e}")
        exit(1)

"""
python add_data_faker_csv.py --students 5000 --teachers 100
"""
