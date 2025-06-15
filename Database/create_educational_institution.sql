-- *****************************************************************
-- # СКРИПТ СОЗДАНИЯ УЛУЧШЕННОЙ БАЗЫ ДАННЫХ ДЛЯ УЧЕБНОГО ЗАВЕДЕНИЯ #
-- *****************************************************************

-- Удаление существующей базы для пересоздания
DROP DATABASE IF EXISTS educational_institution;

-- Создание новой базы данных с поддержкой русского языка
CREATE DATABASE educational_institution
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE educational_institution;

-- ***************************************************************
-- # Таблица университетов                                      #
-- ***************************************************************
CREATE TABLE Universities (
    university_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Уникальный идентификатор университета',
    university_name VARCHAR(150) NOT NULL UNIQUE COMMENT 'Название университета',
    city VARCHAR(100) NOT NULL COMMENT 'Город, в котором находится университет',
    country VARCHAR(100) NOT NULL COMMENT 'Страна университета',
    founded_year INT COMMENT 'Год основания университета'
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- ***************************************************************
-- # Таблица факультетов                                        #
-- ***************************************************************
CREATE TABLE Departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Уникальный идентификатор факультета',
    department_name VARCHAR(100) NOT NULL UNIQUE COMMENT 'Название факультета',
    university_id INT NOT NULL COMMENT 'Университет (внешний ключ к Universities)',
    head_of_department INT COMMENT 'Руководитель факультета (внешний ключ к Teachers)',
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Дата создания записи',
    updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Дата последнего обновления записи',
    FOREIGN KEY (university_id) REFERENCES Universities(university_id) ON DELETE CASCADE,
    INDEX idx_department_search (department_name) USING BTREE,
    INDEX idx_department_head (head_of_department) USING BTREE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- ***************************************************************
-- # Таблица студенческих групп                                 #
-- ***************************************************************
CREATE TABLE Study_Groups (
    study_group_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Уникальный идентификатор группы',
    group_name VARCHAR(50) NOT NULL UNIQUE COMMENT 'Название учебной группы'
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- ***************************************************************
-- # Таблица преподавателей                                     #
-- ***************************************************************
CREATE TABLE Teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Уникальный идентификатор преподавателя',
    first_name VARCHAR(50) NOT NULL COMMENT 'Имя преподавателя',
    last_name VARCHAR(50) NOT NULL COMMENT 'Фамилия преподавателя',
    gender ENUM('male', 'female') NOT NULL COMMENT 'Пол преподавателя',
    nationality VARCHAR(50) NOT NULL COMMENT 'Гражданство преподавателя',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT 'Электронная почта (уникальная)',
    phone VARCHAR(20) NOT NULL UNIQUE COMMENT 'Телефон (уникальный)',
    qualification ENUM('Профессор', 'Доцент', 'Старший преподаватель', 'Преподаватель') NOT NULL COMMENT 'Квалификационная категория',
    hire_date DATE NOT NULL COMMENT 'Дата приема на работу',
    department_id INT NOT NULL COMMENT 'Факультет (внешний ключ к Departments)',
    university_id INT NOT NULL COMMENT 'Университет (внешний ключ к Universities)',
    biography TEXT COMMENT 'Краткая биография преподавателя',
    FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE RESTRICT,
    FOREIGN KEY (university_id) REFERENCES Universities(university_id) ON DELETE CASCADE,
    INDEX idx_teacher_name (last_name, first_name) USING BTREE,
    INDEX idx_teacher_department (department_id) USING BTREE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- Добавление внешнего ключа для руководителя факультета
ALTER TABLE Departments 
ADD FOREIGN KEY (head_of_department) 
    REFERENCES Teachers(teacher_id)
    ON DELETE SET NULL;

-- ***************************************************************
-- # Таблица студентов                                          #
-- ***************************************************************
CREATE TABLE Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Уникальный идентификатор студента',
    first_name VARCHAR(50) NOT NULL COMMENT 'Имя студента',
    last_name VARCHAR(50) NOT NULL COMMENT 'Фамилия студента',
    gender ENUM('male', 'female') NOT NULL COMMENT 'Пол студента',
    nationality VARCHAR(50) NOT NULL COMMENT 'Гражданство студента',
    date_of_birth DATE NOT NULL COMMENT 'Дата рождения студента',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT 'Электронная почта (уникальная)',
    phone VARCHAR(20) UNIQUE COMMENT 'Телефон (уникальный)',
    enrollment_date DATE NOT NULL COMMENT 'Дата зачисления',
    department_id INT NOT NULL COMMENT 'Факультет (внешний ключ к Departments)',
    university_id INT NOT NULL COMMENT 'Университет (внешний ключ к Universities)',
    study_group_id INT NOT NULL COMMENT 'Учебная группа (внешний ключ к Study_Groups)',
    status ENUM('обучается', 'отчислен', 'академический_отпуск') NOT NULL DEFAULT 'обучается' COMMENT 'Статус студента',
    biography TEXT COMMENT 'Краткая биография студента',
    FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE RESTRICT,
    FOREIGN KEY (university_id) REFERENCES Universities(university_id) ON DELETE CASCADE,
    FOREIGN KEY (study_group_id) REFERENCES Study_Groups(study_group_id) ON DELETE RESTRICT,
    CONSTRAINT chk_student_age CHECK (date_of_birth <= DATE_SUB(enrollment_date, INTERVAL 16 YEAR)),
    INDEX idx_student_name (last_name, first_name) USING BTREE,
    INDEX idx_student_department (department_id) USING BTREE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- ***************************************************************
-- # Таблица курсов                                             #
-- ***************************************************************
CREATE TABLE Courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Уникальный идентификатор курса',
    course_name VARCHAR(100) NOT NULL COMMENT 'Название курса',
    description TEXT COMMENT 'Описание курса',
    credits TINYINT UNSIGNED NOT NULL COMMENT 'Количество кредитов (1-5)',
    teacher_id INT COMMENT 'Преподаватель (внешний ключ к Teachers)',
    department_id INT NOT NULL COMMENT 'Факультет (внешний ключ к Departments)',
    start_date DATE NOT NULL COMMENT 'Дата начала курса',
    end_date DATE NOT NULL COMMENT 'Дата окончания курса',
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id) ON DELETE SET NULL,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id) ON DELETE CASCADE,
    CONSTRAINT chk_credits_range CHECK (credits BETWEEN 1 AND 5),
    CONSTRAINT chk_dates_order CHECK (start_date < end_date),
    INDEX idx_course_name (course_name),
    INDEX idx_course_dates (start_date, end_date)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- ***************************************************************
-- # Таблица расписания занятий                                 #
-- ***************************************************************
CREATE TABLE Schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Уникальный идентификатор занятия',
    course_id INT NOT NULL COMMENT 'Курс (внешний ключ к Courses)',
    teacher_id INT NOT NULL COMMENT 'Преподаватель (внешний ключ к Teachers)',
    classroom VARCHAR(50) COMMENT 'Аудитория (например, Корпус-А ауд-101)',
    class_time DATETIME NOT NULL COMMENT 'Дата и время начала занятия',
    duration SMALLINT UNSIGNED NOT NULL COMMENT 'Длительность занятия в минутах (45-180)',
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id) ON DELETE RESTRICT,
    CONSTRAINT chk_duration CHECK (duration BETWEEN 45 AND 180),
    INDEX idx_schedule_time (class_time),
    UNIQUE INDEX idx_unique_class (classroom, class_time)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- ***************************************************************
-- # Таблица регистрации на курсы                               #
-- ***************************************************************
CREATE TABLE Enrollments (
    enrollment_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Уникальный идентификатор записи о регистрации',
    student_id INT NOT NULL COMMENT 'Студент (внешний ключ к Students)',
    course_id INT NOT NULL COMMENT 'Курс (внешний ключ к Courses)',
    enrollment_date DATE NOT NULL COMMENT 'Дата регистрации на курс',
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    UNIQUE INDEX idx_unique_enrollment (student_id, course_id)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- ***************************************************************
-- # Таблица оценок студентов                                   #
-- ***************************************************************
CREATE TABLE Grades (
    grade_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Уникальный идентификатор оценки',
    student_id INT NOT NULL COMMENT 'Студент (внешний ключ к Students)',
    course_id INT NOT NULL COMMENT 'Курс (внешний ключ к Courses)',
    grade DECIMAL(3,1) COMMENT 'Оценка по 5-балльной шкале (2.0-5.0)',
    grade_date DATE NOT NULL COMMENT 'Дата получения оценки',
    exam_type ENUM('экзамен', 'зачет', 'курсовая') NOT NULL COMMENT 'Тип аттестации',
    feedback TEXT COMMENT 'Комментарий преподавателя',
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    CONSTRAINT chk_grade_range CHECK (grade BETWEEN 2.0 AND 5.0),
    UNIQUE INDEX idx_unique_grade (student_id, course_id, exam_type)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- ***************************************************************
-- # Таблица посещаемости студентов                             #
-- ***************************************************************
CREATE TABLE Attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Уникальный идентификатор записи посещаемости',
    student_id INT NOT NULL COMMENT 'Студент (внешний ключ к Students)',
    schedule_id INT NOT NULL COMMENT 'Занятие (внешний ключ к Schedule)',
    attendance_date DATE NOT NULL COMMENT 'Дата занятия',
    status ENUM('присутствовал', 'отсутствовал', 'уважительная_причина', 'опоздал') NOT NULL COMMENT 'Статус посещения',
    check_time TIME COMMENT 'Время отметки',
    notes TEXT COMMENT 'Комментарии к посещаемости',
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (schedule_id) REFERENCES Schedule(schedule_id) ON DELETE CASCADE,
    INDEX idx_attendance_date (attendance_date),
    INDEX idx_attendance_status (status)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- ***************************************************************
-- # Таблица учебных заданий                                    #
-- ***************************************************************
CREATE TABLE Assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Уникальный идентификатор задания',
    course_id INT NOT NULL COMMENT 'Курс (внешний ключ к Courses)',
    assignment_type ENUM('лабораторная', 'практическая', 'доклад', 'реферат', 'другое') NOT NULL COMMENT 'Тип задания',
    title VARCHAR(255) NOT NULL COMMENT 'Название задания',
    description TEXT COMMENT 'Описание задания',
    max_score DECIMAL(5,2) DEFAULT 100.00 COMMENT 'Максимальный балл за задание',
    due_date DATETIME COMMENT 'Срок сдачи задания',
    created_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Дата создания задания',
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE,
    INDEX idx_assignment_title (title),
    INDEX idx_assignment_due_date (due_date)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- ***************************************************************
-- # Таблица оценок за учебные задания                          #
-- ***************************************************************
CREATE TABLE AssignmentGrades (
    assignment_grade_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Уникальный идентификатор оценки за задание',
    assignment_id INT NOT NULL COMMENT 'Задание (внешний ключ к Assignments)',
    student_id INT NOT NULL COMMENT 'Студент (внешний ключ к Students)',
    score DECIMAL(5,2) COMMENT 'Полученный балл (0.00-100.00)',
    submission_date DATETIME COMMENT 'Дата и время сдачи задания',
    feedback TEXT COMMENT 'Комментарий преподавателя',
    graded_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Дата выставления оценки',
    FOREIGN KEY (assignment_id) REFERENCES Assignments(assignment_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    CONSTRAINT chk_score_range CHECK (score BETWEEN 0.00 AND 100.00),
    INDEX idx_assignment_grades (student_id, assignment_id),
    INDEX idx_submission_date (submission_date)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC;

-- *******************************************************
-- Создание триггеров для автоматического обновления времени
-- *******************************************************
/*
DELIMITER $$

CREATE TRIGGER update_departments_timestamp
BEFORE UPDATE ON Departments
FOR EACH ROW    
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP(6);
END$$

CREATE TRIGGER update_assignments_timestamp
BEFORE UPDATE ON Assignments
FOR EACH ROW
BEGIN
    SET NEW.created_at = OLD.created_at; -- Запрет изменения created_at
    SET NEW.graded_at = CURRENT_TIMESTAMP(6);
END$$

DELIMITER ;
*/

-- ***************************************************************
-- # Пример создания представления                              #
-- ***************************************************************
CREATE VIEW StudentCourses AS
SELECT 
    s.student_id,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    c.course_id,
    c.course_name,
    t.teacher_id,
    CONCAT(t.first_name, ' ', t.last_name) AS teacher_name,
    d.department_name,
    u.university_name
FROM Students s
JOIN Enrollments e ON s.student_id = e.student_id
JOIN Courses c ON e.course_id = c.course_id
JOIN Teachers t ON c.teacher_id = t.teacher_id
JOIN Departments d ON c.department_id = d.department_id
JOIN Universities u ON d.university_id = u.university_id;
