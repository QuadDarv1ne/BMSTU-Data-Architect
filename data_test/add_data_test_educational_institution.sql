-- #####################################################################
-- #                 ТЕСТОВЫЕ ДАННЫЕ ДЛЯ УЧЕБНОГО ЗАВЕДЕНИЯ            #
-- #####################################################################

START TRANSACTION;

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ТАБЛИЦЫ ПРЕПОДАВАТЕЛЕЙ (Teachers)        #
-- *******************************************************
INSERT INTO Teachers (first_name, last_name, email, phone, qualification, hire_date) VALUES
('Иван', 'Петров', 'i.petrov@university.ru', '+79991112233', 'Доктор физико-математических наук', '2010-09-01'),
('Мария', 'Сидорова', 'm.sidorova@university.ru', '+79123456789', 'Кандидат филологических наук', '2015-03-15'),
('Алексей', 'Козлов', 'a.kozlov@university.ru', '+79176543210', 'Профессор компьютерных наук', '2008-12-01'),
('Елена', 'Иванова', 'e.ivanova@university.ru', '+79271234567', 'Доктор химических наук', '2012-05-10'),
('Сергей', 'Смирнов', 's.smirnov@university.ru', '+79372345678', 'Кандидат биологических наук', '2014-07-22'),
('Ольга', 'Кузнецова', 'o.kuznetsova@university.ru', '+79473456789', 'Профессор экономических наук', '2009-11-30'),
('Анна', 'Попова', 'a.popova@university.ru', '+79574567890', 'Доктор исторических наук', '2011-02-14'),
('Дмитрий', 'Васильев', 'd.vasiliev@university.ru', '+79675678901', 'Кандидат психологических наук', '2013-04-18'),
('Наталья', 'Новикова', 'n.novikova@university.ru', '+79776789012', 'Профессор юридических наук', '2016-08-25'),
('Екатерина', 'Морозова', 'e.morozova@university.ru', '+79877890123', 'Доктор медицинских наук', '2017-10-30');

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ТАБЛИЦЫ ФАКУЛЬТЕТОВ (Departments)        #
-- *******************************************************
INSERT INTO Departments (department_name, head_of_department) VALUES
('Физико-математический факультет', 1),
('Филологический факультет', 2),
('Факультет информационных технологий', 3),
('Химический факультет', 4),
('Биологический факультет', 5),
('Экономический факультет', 6),
('Исторический факультет', 7),
('Психологический факультет', 8),
('Юридический факультет', 9),
('Медицинский факультет', 10);

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ТАБЛИЦЫ СТУДЕНТОВ (Students)             #
-- *******************************************************
-- Генерация 2000 студентов
INSERT INTO Students (first_name, last_name, date_of_birth, email, phone, enrollment_date)
WITH RECURSIVE numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 2000
)
SELECT 
    CONCAT('Студент_', n),
    CONCAT('Фамилия_', n),
    DATE_ADD('1980-01-01', INTERVAL FLOOR(RAND() * 14600) DAY),
    CONCAT('student', n, '@edu.ru'),
    CONCAT('+79', FLOOR(RAND() * 900000000) + 10000000),
    DATE_ADD('2018-09-01', INTERVAL FLOOR(RAND() * 5) YEAR)
FROM numbers;

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ТАБЛИЦЫ КУРСОВ (Courses)                 #
-- *******************************************************
-- Генерация 200 курсов
INSERT INTO Courses (course_name, description, credits, teacher_id)
WITH RECURSIVE numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 200
)
SELECT 
    CONCAT('Курс ', n, ' по ', 
           CASE 
               WHEN n % 10 = 0 THEN 'математике'
               WHEN n % 10 = 1 THEN 'физике'
               WHEN n % 10 = 2 THEN 'информатике'
               WHEN n % 10 = 3 THEN 'химии'
               WHEN n % 10 = 4 THEN 'биологии'
               WHEN n % 10 = 5 THEN 'экономике'
               WHEN n % 10 = 6 THEN 'истории'
               WHEN n % 10 = 7 THEN 'психологии'
               WHEN n % 10 = 8 THEN 'праву'
               ELSE 'медицине'
           END),
    CONCAT('Описание курса ', n, '. Этот курс охватывает основные аспекты дисциплины.'),
    FLOOR(2 + RAND() * 5),
    FLOOR(1 + RAND() * 10)
FROM numbers;

-- *******************************************************
-- # ЗАПОЛНЕНИЕ РАСПИСАНИЯ (Schedule)                    #
-- *******************************************************
-- Генерация 5000 записей расписания
INSERT INTO Schedule (course_id, teacher_id, classroom, class_time)
WITH RECURSIVE numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 5000
)
SELECT 
    FLOOR(1 + RAND() * 200),
    FLOOR(1 + RAND() * 10),
    CONCAT('Ауд. ', FLOOR(100 + RAND() * 500)),
    DATE_ADD('2024-09-01 08:00:00', INTERVAL FLOOR(RAND() * 120) DAY)
FROM numbers;

-- *******************************************************
-- # ЗАПОЛНЕНИЕ РЕГИСТРАЦИЙ (Enrollments)                #
-- *******************************************************
-- Генерация 10000 регистраций
INSERT INTO Enrollments (student_id, course_id, enrollment_date)
WITH RECURSIVE numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 10000
)
SELECT 
    FLOOR(1 + RAND() * 2000),
    FLOOR(1 + RAND() * 200),
    DATE_ADD('2024-08-20', INTERVAL FLOOR(RAND() * 30) DAY)
FROM numbers;

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ОЦЕНОК (Grades)                          #
-- *******************************************************
-- Генерация 15000 оценок
INSERT INTO Grades (student_id, course_id, grade, grade_date)
SELECT 
    e.student_id,
    e.course_id,
    ROUND(2 + RAND() * 3, 1),
    DATE_ADD(e.enrollment_date, INTERVAL FLOOR(30 + RAND() * 120) DAY)
FROM Enrollments e
ORDER BY RAND()
LIMIT 15000;

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ПОСЕЩАЕМОСТИ (Attendance)                #
-- *******************************************************
-- Генерация 20000 записей посещаемости
INSERT INTO Attendance (student_id, schedule_id, attendance_date, status)
SELECT 
    e.student_id,
    s.schedule_id,
    DATE(s.class_time),
    CASE 
        WHEN RAND() < 0.7 THEN 'present'
        WHEN RAND() < 0.85 THEN 'excused'
        ELSE 'absent'
    END
FROM Enrollments e
JOIN Schedule s ON e.course_id = s.course_id
ORDER BY RAND()
LIMIT 20000;

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ЗАДАНИЙ (Assignments)                    #
-- *******************************************************
-- Генерация 1000 заданий
INSERT INTO Assignments (course_id, assignment_type, title, description, max_score, due_date)
WITH RECURSIVE numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 1000
)
SELECT 
    FLOOR(1 + RAND() * 200),
    CASE 
        WHEN n % 5 = 0 THEN 'лабораторная'
        WHEN n % 5 = 1 THEN 'контрольная'
        WHEN n % 5 = 2 THEN 'реферат'
        WHEN n % 5 = 3 THEN 'курсовая'
        ELSE 'экзамен'
    END,
    CONCAT('Задание ', n),
    CONCAT('Описание задания ', n, '. Это задание проверяет знания студентов по теме.'),
    CASE 
        WHEN n % 5 = 0 THEN 100
        WHEN n % 5 = 1 THEN 50
        WHEN n % 5 = 2 THEN 80
        WHEN n % 5 = 3 THEN 200
        ELSE 150
    END,
    DATE_ADD('2024-09-01', INTERVAL FLOOR(30 + RAND() * 120) DAY)
FROM numbers;

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ОЦЕНОК ЗА ЗАДАНИЯ (AssignmentGrades)     #
-- *******************************************************
-- Генерация 10000 оценок за задания
INSERT INTO AssignmentGrades (assignment_id, student_id, score, submission_date, feedback)
SELECT 
    a.assignment_id,
    e.student_id,
    FLOOR(50 + RAND() * 50),
    DATE_SUB(a.due_date, INTERVAL FLOOR(RAND() * 7) DAY),
    CASE 
        WHEN RAND() < 0.3 THEN 'Отличная работа!'
        WHEN RAND() < 0.6 THEN 'Хорошо, но есть замечания'
        WHEN RAND() < 0.8 THEN 'Удовлетворительно'
        ELSE 'Требуется доработка'
    END
FROM Assignments a
JOIN Enrollments e ON a.course_id = e.course_id
ORDER BY RAND()
LIMIT 10000;

COMMIT;

-- ####################################################################
-- #             БОЛЬШОЙ НАБОР ТЕСТОВЫХ ДАННЫХ УСПЕШНО СОЗДАН         #
-- ####################################################################
