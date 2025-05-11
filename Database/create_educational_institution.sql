-- *****************************************************************
-- # СКРИПТ СОЗДАНИЯ УЛУЧШЕННОЙ БАЗЫ ДАННЫХ ДЛЯ УЧЕБНОГО ЗАВЕДЕНИЯ #
-- *****************************************************************
-- УДАЛЕНИЕ СУЩЕСТВУЮЩЕЙ БАЗЫ ДЛЯ ПЕРЕСОЗДАНИЯ
DROP DATABASE IF EXISTS educational_institution;

CREATE DATABASE educational_institution
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE educational_institution;

-- *******************************************************
-- # Таблица для хранения информации о студентах         #
-- *******************************************************
CREATE TABLE Students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,   -- Уникальный идентификатор студента
    first_name VARCHAR(50) NOT NULL,              -- Имя студента
    last_name VARCHAR(50) NOT NULL,               -- Фамилия студента
    date_of_birth DATE,                          -- Дата рождения студента
    email VARCHAR(100) NOT NULL,                 -- Электронная почта студента
    phone VARCHAR(20),                           -- Телефон студента
    enrollment_date DATE NOT NULL,               -- Дата зачисления студента
    INDEX idx_student_name (last_name, first_name) -- Индекс для ускорения поиска по имени и фамилии
);

-- *******************************************************
-- # Таблица для хранения информации о преподавателях    #
-- *******************************************************
CREATE TABLE Teachers (
    teacher_id INT PRIMARY KEY AUTO_INCREMENT,  -- Уникальный идентификатор преподавателя
    first_name VARCHAR(50) NOT NULL,             -- Имя преподавателя
    last_name VARCHAR(50) NOT NULL,              -- Фамилия преподавателя
    email VARCHAR(100) NOT NULL,                 -- Электронная почта преподавателя
    phone VARCHAR(20),                          -- Телефон преподавателя
    qualification VARCHAR(100),                 -- Квалификация преподавателя
    hire_date DATE NOT NULL,                    -- Дата найма преподавателя
    INDEX idx_teacher_name (last_name, first_name) -- Индекс для ускорения поиска по имени и фамилии
);

-- *******************************************************
-- # Таблица для хранения информации о курсах            #
-- *******************************************************
CREATE TABLE Courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT,    -- Уникальный идентификатор курса
    course_name VARCHAR(100) NOT NULL,           -- Название курса
    description TEXT,                            -- Описание курса
    credits INT NOT NULL,                        -- Количество кредитов за курс
    teacher_id INT,                              -- Идентификатор преподавателя
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id),
    INDEX idx_course_name (course_name)          -- Индекс для ускорения поиска по названию курса
);

-- ********************************************************
-- # Таблица для хранения информации о расписании занятий #
-- ********************************************************
CREATE TABLE Schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,   -- Уникальный идентификатор расписания
    course_id INT NOT NULL,                       -- Идентификатор курса
    teacher_id INT NOT NULL,                      -- Идентификатор преподавателя
    classroom VARCHAR(50),                        -- Номер аудитории
    class_time DATETIME NOT NULL,                -- Время проведения занятия
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id),
    INDEX idx_schedule_time (class_time)          -- Индекс для ускорения поиска по времени
);

-- **********************************************************
-- # Таблица для хранения информации о регистрации на курсы #
-- **********************************************************
CREATE TABLE Enrollments (
    enrollment_id INT PRIMARY KEY AUTO_INCREMENT,   -- Уникальный идентификатор регистрации
    student_id INT NOT NULL,                        -- Идентификатор студента
    course_id INT NOT NULL,                         -- Идентификатор курса
    enrollment_date DATE NOT NULL,                 -- Дата регистрации
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    INDEX idx_enrollment_student (student_id)     -- Индекс для ускорения поиска по студенту
);

-- ********************************************************
-- # Таблица для хранения информации об оценках студентов #
-- ********************************************************
CREATE TABLE Grades (
    grade_id INT PRIMARY KEY AUTO_INCREMENT,   -- Уникальный идентификатор оценки
    student_id INT NOT NULL,                   -- Идентификатор студента
    course_id INT NOT NULL,                    -- Идентификатор курса
    grade FLOAT,                               -- Оценка студента
    grade_date DATE NOT NULL,                 -- Дата выставления оценки
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    INDEX idx_grade_student (student_id)      -- Индекс для ускорения поиска по студенту
);

-- ************************************************************
-- # Таблица для хранения информации о посещаемости студентов #
-- ************************************************************
CREATE TABLE Attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,  -- Уникальный идентификатор посещаемости
    student_id INT NOT NULL,                       -- Идентификатор студента
    schedule_id INT NOT NULL,                     -- Идентификатор расписания
    attendance_date DATE NOT NULL,                 -- Дата посещения
    status ENUM('present', 'absent', 'excused') NOT NULL, -- Статус посещаемости
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id),
    INDEX idx_attendance_student (student_id)   -- Индекс для ускорения поиска по студенту
);

-- *******************************************************
-- # Таблица для хранения информации о факультетах       #
-- *******************************************************
CREATE TABLE Departments (
    department_id INT PRIMARY KEY AUTO_INCREMENT,   -- Уникальный идентификатор факультета
    department_name VARCHAR(100) NOT NULL,         -- Название факультета
    head_of_department INT,                        -- Идентификатор руководителя факультета
    INDEX idx_department_name (department_name)    -- Индекс для ускорения поиска по названию факультета
);

-- **********************************************************
-- # Таблица для хранения информации об учебных заданиях    #
-- **********************************************************
CREATE TABLE Assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,     -- Уникальный идентификатор задания
    course_id INT NOT NULL,                           -- Идентификатор курса
    assignment_type ENUM('лабораторная', 'практическая', 'доклад', 'реферат', 'другое') NOT NULL, -- Тип задания
    title VARCHAR(255) NOT NULL,                      -- Название задания
    description TEXT,                                 -- Подробное описание
    max_score FLOAT DEFAULT 100,                      -- Максимальный балл за задание
    due_date DATE,                                    -- Срок выполнения
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,    -- Дата создания записи
    FOREIGN KEY (course_id) REFERENCES Courses(course_id),
    INDEX idx_assignment_title (title)              -- Индекс для ускорения поиска по названию задания
);

-- **********************************************************
-- # Таблица для хранения оценок за учебные задания         #
-- **********************************************************
CREATE TABLE AssignmentGrades (
    assignment_grade_id INT PRIMARY KEY AUTO_INCREMENT, -- Уникальный идентификатор оценки
    assignment_id INT NOT NULL,                         -- Идентификатор задания
    student_id INT NOT NULL,                            -- Идентификатор студента
    score FLOAT,                                        -- Полученный балл
    submission_date DATE,                               -- Дата сдачи
    feedback TEXT,                                      -- Комментарий преподавателя
    graded_at DATETIME DEFAULT CURRENT_TIMESTAMP,       -- Дата выставления оценки
    FOREIGN KEY (assignment_id) REFERENCES Assignments(assignment_id),
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    INDEX idx_assignment_grades (student_id, assignment_id) -- Индекс для быстрого поиска оценок студента
);
