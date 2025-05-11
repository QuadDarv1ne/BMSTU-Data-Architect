-- #####################################################################
-- #                 АНАЛИТИЧЕСКИЕ ЗАПРОСЫ ДЛЯ УЧЕБНОГО ЗАВЕДЕНИЯ      #
-- #                ╔══════════════════════════════════╗               #
-- #                ║         АНАЛИТИКА ДАННЫХ         ║               #
-- #                ╚══════════════════════════════════╝               #
-- #####################################################################

-- *******************************************************
-- # 1. Средняя оценка по каждому курсу                  #
-- *******************************************************
SELECT
    c.course_name,
    AVG(g.grade) AS average_grade
FROM
    Courses c
JOIN
    Grades g ON c.course_id = g.course_id
GROUP BY
    c.course_name;

-- *******************************************************
-- # 2. Количество студентов на каждом курсе             #
-- *******************************************************
SELECT
    c.course_name,
    COUNT(e.student_id) AS student_count
FROM
    Courses c
JOIN
    Enrollments e ON c.course_id = e.course_id
GROUP BY
    c.course_name;

-- *******************************************************
-- # 3. Посещаемость студентов                           #
-- *******************************************************
SELECT
    s.first_name,
    s.last_name,
    COUNT(a.attendance_id) AS attendance_count
FROM
    Students s
JOIN
    Attendance a ON s.student_id = a.student_id
WHERE
    a.status = 'present'
GROUP BY
    s.student_id;

-- *******************************************************
-- # 4. Средняя оценка по каждому преподавателю          #
-- *******************************************************
SELECT
    t.first_name,
    t.last_name,
    AVG(g.grade) AS average_grade
FROM
    Teachers t
JOIN
    Courses c ON t.teacher_id = c.teacher_id
JOIN
    Grades g ON c.course_id = g.course_id
GROUP BY
    t.teacher_id;

-- *******************************************************
-- # 5. Количество курсов на каждом факультете           #
-- *******************************************************
SELECT
    d.department_name,
    COUNT(c.course_id) AS course_count
FROM
    Departments d
JOIN
    Teachers t ON d.head_of_department = t.teacher_id
JOIN
    Courses c ON t.teacher_id = c.teacher_id
GROUP BY
    d.department_name;

-- *******************************************************
-- # 6. Средняя оценка по каждому типу задания           #
-- *******************************************************
SELECT
    a.assignment_type,
    AVG(ag.score) AS average_score
FROM
    Assignments a
JOIN
    AssignmentGrades ag ON a.assignment_id = ag.assignment_id
GROUP BY
    a.assignment_type;

-- *******************************************************
-- # 7. Количество заданий на каждом курсе               #
-- *******************************************************
SELECT
    c.course_name,
    COUNT(a.assignment_id) AS assignment_count
FROM
    Courses c
JOIN
    Assignments a ON c.course_id = a.course_id
GROUP BY
    c.course_name;

-- *******************************************************
-- # 8. Средняя оценка по каждому студенту               #
-- *******************************************************
SELECT
    s.first_name,
    s.last_name,
    AVG(g.grade) AS average_grade
FROM
    Students s
JOIN
    Grades g ON s.student_id = g.student_id
GROUP BY
    s.student_id;

-- *******************************************************
-- # 9. Количество студентов на каждом факультете        #
-- *******************************************************
SELECT
    d.department_name,
    COUNT(DISTINCT e.student_id) AS student_count
FROM
    Departments d
JOIN
    Teachers t ON d.head_of_department = t.teacher_id
JOIN
    Courses c ON t.teacher_id = c.teacher_id
JOIN
    Enrollments e ON c.course_id = e.course_id
GROUP BY
    d.department_name;

-- *******************************************************
-- # 10. Средняя оценка по каждому статусу посещаемости  #
-- *******************************************************
SELECT
    a.status,
    AVG(g.grade) AS average_grade
FROM
    Attendance a
JOIN
    Students s ON a.student_id = s.student_id
JOIN
    Grades g ON s.student_id = g.student_id
GROUP BY
    a.status;

-- ####################################################################
-- #                      АНАЛИТИКА УСПЕШНО ВЫПОЛНЕНА                 #
-- #                ╔══════════════════════════════════╗              #
-- #                ║    АНАЛИЗИРУЙТЕ ДАННЫЕ СЕЙЧАС    ║              #
-- #                ╚══════════════════════════════════╝              #
-- ####################################################################
