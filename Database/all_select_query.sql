/* Студенты (Students) */
-- Базовая выборка
SELECT * FROM Students;

-- Студенты младше 20 лет
SELECT student_id, first_name, last_name, date_of_birth, email 
FROM Students 
WHERE date_of_birth > DATE_SUB(CURDATE(), INTERVAL 20 YEAR);

-- Количество студентов по годам зачисления
SELECT YEAR(enrollment_date) AS year, COUNT(*) AS students_count
FROM Students
GROUP BY YEAR(enrollment_date)
ORDER BY year DESC;


/* Преподаватели (Teachers) */
-- Все преподаватели
SELECT * FROM Teachers;

-- Преподаватели с ученой степенью
SELECT teacher_id, CONCAT(first_name, ' ', last_name) AS full_name,
       qualification, hire_date
FROM Teachers
WHERE qualification IN ('Доктор наук', 'Кандидат наук');

-- Статистика по квалификациям
SELECT qualification, COUNT(*) AS count
FROM Teachers
GROUP BY qualification;


/* Курсы (Courses) */
-- Все курсы
SELECT * FROM Courses;

-- Курсы с преподавателями
SELECT c.course_id, c.course_name, c.credits,
       CONCAT(t.first_name, ' ', t.last_name) AS teacher_name
FROM Courses c
JOIN Teachers t ON c.teacher_id = t.teacher_id;

-- Количество курсов на преподавателя
SELECT teacher_id, COUNT(*) AS courses_count
FROM Courses
GROUP BY teacher_id;


/* Расписание (Schedule) */
-- Полное расписание
SELECT s.schedule_id, c.course_name, 
       CONCAT(t.first_name, ' ', t.last_name) AS teacher_name,
       s.classroom, s.class_time
FROM Schedule s
JOIN Courses c ON s.course_id = c.course_id
JOIN Teachers t ON s.teacher_id = t.teacher_id;

-- Расписание на текущую неделю
SELECT * FROM Schedule
WHERE class_time BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY);


/* Зачисления (Enrollments) */
-- Все зачисления
SELECT * FROM Enrollments;

-- Студенты на курсе (пример для course_id = 5)
SELECT s.student_id, CONCAT(s.first_name, ' ', s.last_name) AS student_name,
       e.enrollment_date
FROM Enrollments e
JOIN Students s ON e.student_id = s.student_id
WHERE e.course_id = 5;


/* Оценки (Grades) */
-- Все оценки
SELECT * FROM Grades;

-- Средний балл студентов
SELECT student_id, AVG(grade) AS average_grade
FROM Grades
GROUP BY student_id
ORDER BY average_grade DESC;

-- Детализированные оценки с информацией о студенте и курсе
SELECT g.grade_id, 
       CONCAT(s.first_name, ' ', s.last_name) AS student_name,
       c.course_name, g.grade, g.grade_date
FROM Grades g
JOIN Students s ON g.student_id = s.student_id
JOIN Courses c ON g.course_id = c.course_id;


/* Посещаемость (Attendance) */
-- Вся посещаемость
SELECT * FROM Attendance;

-- Статистика посещаемости для студента
SELECT status, COUNT(*) AS count
FROM Attendance
WHERE student_id = 123
GROUP BY status;

-- Пропуски по уважительной причине за последний месяц
SELECT a.attendance_date, c.course_name, s.classroom
FROM Attendance a
JOIN Schedule s ON a.schedule_id = s.schedule_id
JOIN Courses c ON s.course_id = c.course_id
WHERE a.status = 'excused'
  AND a.attendance_date > DATE_SUB(CURDATE(), INTERVAL 1 MONTH);


/* Факультеты (Departments) */
-- Все факультеты
SELECT * FROM Departments;

-- Факультеты с заведующими
SELECT d.department_name, 
       CONCAT(t.first_name, ' ', t.last_name) AS head_name
FROM Departments d
LEFT JOIN Teachers t ON d.head_of_department = t.teacher_id;


/* Задания (Assignments) */
-- Все задания
SELECT * FROM Assignments;

-- Задания с истекающим сроком
SELECT a.title, c.course_name, a.due_date
FROM Assignments a
JOIN Courses c ON a.course_id = c.course_id
WHERE a.due_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY);


/* Оценки за задания (AssignmentGrades) */
-- Все оценки за задания
SELECT * FROM AssignmentGrades;

-- Результаты задания (пример для assignment_id = 10)
SELECT ag.score, ag.submission_date,
       CONCAT(s.first_name, ' ', s.last_name) AS student_name,
       a.title
FROM AssignmentGrades ag
JOIN Students s ON ag.student_id = s.student_id
JOIN Assignments a ON ag.assignment_id = a.assignment_id
WHERE ag.assignment_id = 10;


/* Пример сложного аналитического запроса */
-- Топ студентов по среднему баллу с количеством курсов
SELECT s.student_id,
       CONCAT(s.first_name, ' ', s.last_name) AS student_name,
       COUNT(DISTINCT e.course_id) AS courses_count,
       AVG(g.grade) AS avg_grade,
       AVG(ag.score) AS avg_assignment_score
FROM Students s
LEFT JOIN Enrollments e ON s.student_id = e.student_id
LEFT JOIN Grades g ON s.student_id = g.student_id
LEFT JOIN AssignmentGrades ag ON s.student_id = ag.student_id
GROUP BY s.student_id
HAVING avg_grade IS NOT NULL
ORDER BY avg_grade DESC
LIMIT 10;
