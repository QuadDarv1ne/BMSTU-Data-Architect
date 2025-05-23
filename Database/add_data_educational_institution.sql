-- #####################################################################
-- #                 ТЕСТОВЫЕ ДАННЫЕ ДЛЯ УЧЕБНОГО ЗАВЕДЕНИЯ            #
-- #                ╔══════════════════════════════════╗               #
-- #                ║         ГЕНЕРАЦИЯ ДАННЫХ         ║               #
-- #                ╚══════════════════════════════════╝               #
-- #####################################################################

-- Начинаем транзакцию для обеспечения целостности данных
START TRANSACTION;

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ТАБЛИЦЫ ПРЕПОДАВАТЕЛЕЙ (Teachers)        #
-- *******************************************************
INSERT INTO Teachers (first_name, last_name, email, phone, qualification, hire_date) VALUES
('Иван', 'Петров', 'i.petrov@university.ru', '+7 999 111-22-33', 'Доктор физико-математических наук', '2010-09-01'),
('Мария', 'Сидорова', 'm.sidorova@university.ru', '+7 912 345-67-89', 'Кандидат филологических наук', '2015-03-15'),
('Алексей', 'Козлов', 'a.kozlov@university.ru', '+7 917 654-32-10', 'Профессор компьютерных наук', '2008-12-01'),
('Елена', 'Иванова', 'e.ivanova@university.ru', '+7 927 123-45-67', 'Доктор химических наук', '2012-05-10'),
('Сергей', 'Смирнов', 's.smirnov@university.ru', '+7 937 234-56-78', 'Кандидат биологических наук', '2014-07-22'),
('Ольга', 'Кузнецова', 'o.kuznetsova@university.ru', '+7 947 345-67-89', 'Профессор экономических наук', '2009-11-30'),
('Анна', 'Попова', 'a.popova@university.ru', '+7 957 456-78-90', 'Доктор исторических наук', '2011-02-14'),
('Дмитрий', 'Васильев', 'd.vasiliev@university.ru', '+7 967 567-89-01', 'Кандидат психологических наук', '2013-04-18'),
('Наталья', 'Новикова', 'n.novikova@university.ru', '+7 977 678-90-12', 'Профессор юридических наук', '2016-08-25'),
('Екатерина', 'Морозова', 'e.morozova@university.ru', '+7 987 789-01-23', 'Доктор медицинских наук', '2017-10-30');

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
INSERT INTO Students (first_name, last_name, date_of_birth, email, phone, enrollment_date) VALUES
('Анна', 'Иванова', '2003-05-15', 'a.ivanova@edu.ru', '+7 900 111-22-33', '2021-09-01'),
('Дмитрий', 'Смирнов', '2002-11-23', 'd.smirnov@edu.ru', '+7 901 234-56-78', '2021-09-01'),
('Екатерина', 'Васильева', '2004-02-10', 'e.vasileva@edu.ru', '+7 902 345-67-89', '2022-09-01'),
('Алексей', 'Петров', '2003-08-12', 'a.petrov@edu.ru', '+7 903 456-78-90', '2021-09-01'),
('Мария', 'Кузнецова', '2002-09-18', 'm.kuznetsova@edu.ru', '+7 904 567-89-01', '2021-09-01'),
('Иван', 'Новиков', '2004-03-22', 'i.novikov@edu.ru', '+7 905 678-90-12', '2022-09-01'),
('Ольга', 'Соколова', '2003-07-30', 'o.sokolova@edu.ru', '+7 906 789-01-23', '2021-09-01'),
('Сергей', 'Морозов', '2002-10-14', 's.morozov@edu.ru', '+7 907 890-12-34', '2021-09-01'),
('Наталья', 'Волкова', '2004-04-25', 'n.volkova@edu.ru', '+7 908 901-23-45', '2022-09-01'),
('Елена', 'Лебедева', '2003-12-05', 'e.lebedeva@edu.ru', '+7 909 012-34-56', '2021-09-01');

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ТАБЛИЦЫ КУРСОВ (Courses)                 #
-- *******************************************************
INSERT INTO Courses (course_name, description, credits, teacher_id) VALUES
('Высшая математика', 'Дифференциальные уравнения и математический анализ', 5, 1),
('Современная литература', 'Анализ произведений XXI века', 4, 2),
('Программирование на Python', 'Основы ООП и алгоритмов', 6, 3),
('Общая химия', 'Основы химических процессов', 5, 4),
('Биология клетки', 'Строение и функции клетки', 4, 5),
('Экономическая теория', 'Основы микро- и макроэкономики', 6, 6),
('История России', 'Основные этапы развития России', 5, 7),
('Общая психология', 'Основы психологических процессов', 4, 8),
('Гражданское право', 'Основы гражданского законодательства', 6, 9),
('Анатомия человека', 'Строение и функции организма человека', 5, 10);

-- *******************************************************
-- # ЗАПОЛНЕНИЕ РАСПИСАНИЯ (Schedule)                    #
-- *******************************************************
INSERT INTO Schedule (course_id, teacher_id, classroom, class_time) VALUES
(1, 1, 'Ауд. 301', '2024-09-02 09:00:00'),
(2, 2, 'Ауд. 205', '2024-09-02 11:30:00'),
(3, 3, 'Комп. класс 101', '2024-09-03 14:00:00'),
(4, 4, 'Ауд. 401', '2024-09-04 09:00:00'),
(5, 5, 'Ауд. 206', '2024-09-04 11:30:00'),
(6, 6, 'Ауд. 302', '2024-09-05 14:00:00'),
(7, 7, 'Ауд. 402', '2024-09-06 09:00:00'),
(8, 8, 'Ауд. 207', '2024-09-06 11:30:00'),
(9, 9, 'Ауд. 303', '2024-09-07 14:00:00'),
(10, 10, 'Ауд. 403', '2024-09-08 09:00:00');

-- *******************************************************
-- # ЗАПОЛНЕНИЕ РЕГИСТРАЦИЙ (Enrollments)                #
-- *******************************************************
INSERT INTO Enrollments (student_id, course_id, enrollment_date) VALUES
(1, 1, '2024-08-25'),  -- Анна → Высшая математика
(1, 3, '2024-08-26'),  -- Анна → Программирование
(2, 1, '2024-08-25'),  -- Дмитрий → Высшая математика
(3, 2, '2024-08-27'),  -- Екатерина → Литература
(4, 4, '2024-08-25'),  -- Алексей → Общая химия
(5, 5, '2024-08-26'),  -- Мария → Биология клетки
(6, 6, '2024-08-27'),  -- Иван → Экономическая теория
(7, 7, '2024-08-25'),  -- Ольга → История России
(8, 8, '2024-08-26'),  -- Сергей → Общая психология
(9, 9, '2024-08-27'),  -- Наталья → Гражданское право
(10, 10, '2024-08-25'); -- Елена → Анатомия человека

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ОЦЕНОК (Grades)                          #
-- *******************************************************
INSERT INTO Grades (student_id, course_id, grade, grade_date) VALUES
(1, 1, 4.5, '2024-12-25'),  -- Анна: Математика
(1, 3, 5.0, '2024-12-26'),  -- Анна: Программирование
(2, 1, 3.8, '2024-12-25'),  -- Дмитрий: Математика
(3, 2, 4.2, '2024-12-27'),  -- Екатерина: Литература
(4, 4, 4.7, '2024-12-25'),  -- Алексей: Химия
(5, 5, 3.9, '2024-12-26'),  -- Мария: Биология
(6, 6, 4.5, '2024-12-27'),  -- Иван: Экономика
(7, 7, 4.8, '2024-12-25'),  -- Ольга: История
(8, 8, 3.7, '2024-12-26'),  -- Сергей: Психология
(9, 9, 4.3, '2024-12-27'),  -- Наталья: Право
(10, 10, 4.9, '2024-12-25'); -- Елена: Анатомия

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ПОСЕЩАЕМОСТИ (Attendance)                #
-- *******************************************************
INSERT INTO Attendance (student_id, schedule_id, attendance_date, status) VALUES
(1, 1, '2024-09-02', 'present'),   -- Анна на математике
(1, 3, '2024-09-03', 'excused'),   -- Анна пропустила программирование (уважительно)
(2, 1, '2024-09-02', 'absent'),    -- Дмитрий отсутствовал
(3, 2, '2024-09-02', 'present'),   -- Екатерина на литературе
(4, 4, '2024-09-04', 'present'),   -- Алексей на химии
(5, 5, '2024-09-04', 'excused'),   -- Мария пропустила биологию (уважительно)
(6, 6, '2024-09-05', 'absent'),    -- Иван отсутствовал
(7, 7, '2024-09-06', 'present'),   -- Ольга на истории
(8, 8, '2024-09-06', 'excused'),   -- Сергей пропустил психологию (уважительно)
(9, 9, '2024-09-07', 'absent'),    -- Наталья отсутствовала
(10, 10, '2024-09-08', 'present'); -- Елена на анатомии

-- ************************************************************
-- # ЗАПОЛНЕНИЕ ИНФОРМАЦИИ ОБ УЧЕБНЫХ ЗАДАНИЯХ (Assignments) #
-- ************************************************************
INSERT INTO Assignments (course_id, assignment_type, title, description, max_score, due_date) VALUES
(1, 'лабораторная', 'Лабораторная работа №1', 'Решение дифференциальных уравнений', 100, '2024-10-01'),
(2, 'реферат', 'Реферат по современной литературе', 'Анализ произведений XXI века', 100, '2024-10-15'),
(3, 'практическая', 'Практическая работа по Python', 'Реализация алгоритмов', 100, '2024-10-20'),
(4, 'лабораторная', 'Лабораторная работа №2', 'Химические реакции', 100, '2024-10-05'),
(5, 'реферат', 'Реферат по биологии клетки', 'Строение и функции клетки', 100, '2024-10-18'),
(6, 'практическая', 'Практическая работа по экономике', 'Анализ экономических показателей', 100, '2024-10-22'),
(7, 'лабораторная', 'Лабораторная работа №3', 'Анализ исторических событий', 100, '2024-10-10'),
(8, 'реферат', 'Реферат по психологии', 'Основы психологических процессов', 100, '2024-10-25'),
(9, 'практическая', 'Практическая работа по праву', 'Анализ гражданского законодательства', 100, '2024-10-28'),
(10, 'лабораторная', 'Лабораторная работа №4', 'Строение и функции организма человека', 100, '2024-11-01');

-- *******************************************************
-- # ЗАПОЛНЕНИЕ ТИПИЗИРОВАННЫХ ОЦЕНОК (AssignmentGrades) #
-- *******************************************************
INSERT INTO AssignmentGrades (assignment_id, student_id, score, submission_date, feedback) VALUES
(1, 1, 95, '2024-09-25', 'Отличная работа!'),
(2, 3, 88, '2024-10-10', 'Хороший анализ, но можно лучше.'),
(3, 2, 76, '2024-10-18', 'Неплохо, но есть ошибки.'),
(4, 4, 90, '2024-10-03', 'Отлично выполнено!'),
(5, 5, 85, '2024-10-15', 'Хорошая работа, но есть недочеты.'),
(6, 6, 80, '2024-10-20', 'Неплохо, но можно улучшить.'),
(7, 7, 92, '2024-10-08', 'Отличная работа!'),
(8, 8, 87, '2024-10-23', 'Хороший анализ, но можно лучше.'),
(9, 9, 78, '2024-10-26', 'Неплохо, но есть ошибки.'),
(10, 10, 94, '2024-10-30', 'Отличная работа!');

-- Завершаем транзакцию
COMMIT;

-- ####################################################################
-- #                      ДАННЫЕ УСПЕШНО ДОБАВЛЕНЫ                    #
-- #                ╔══════════════════════════════════╗              #
-- #                ║    ТЕСТИРУЙТЕ СИСТЕМУ СЕЙЧАС     ║              #
-- #                ╚══════════════════════════════════╝              #
-- ####################################################################
