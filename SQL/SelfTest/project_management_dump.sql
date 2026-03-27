-- Дамп схемы project_management
CREATE SCHEMA IF NOT EXISTS project_management;

SET search_path TO project_management;

CREATE TABLE IF NOT EXISTS assignments (assigned_date date, assignment_id integer NOT NULL, employee_id integer, task_id integer);

CREATE TABLE IF NOT EXISTS projects (end_date date, project_id integer NOT NULL, start_date date, project_name character varying NOT NULL, status character varying);

CREATE TABLE IF NOT EXISTS tasks (title character varying NOT NULL, task_id integer NOT NULL, due_date date, priority integer, project_id integer);

CREATE TABLE IF NOT EXISTS employees (role character varying, first_name character varying NOT NULL, employee_id integer NOT NULL, email character varying, last_name character varying NOT NULL);

INSERT INTO employees (employee_id, first_name, last_name, email, role) VALUES (1, 'Иван', 'Петров', 'i.petrov@company.com', 'Менеджер проекта');
INSERT INTO employees (employee_id, first_name, last_name, email, role) VALUES (2, 'Анна', 'Сидорова', 'a.sidorova@company.com', 'Разработчик');
INSERT INTO employees (employee_id, first_name, last_name, email, role) VALUES (3, 'Петр', 'Иванов', 'p.ivanov@company.com', 'Тестировщик');

INSERT INTO projects (project_id, project_name, start_date, end_date, status) VALUES (1, 'Разработка CRM', '2023-09-01', '2024-03-01', 'В работе');
INSERT INTO projects (project_id, project_name, start_date, end_date, status) VALUES (2, 'Внедрение BI', '2024-01-15', NULL, 'Планируется');
INSERT INTO projects (project_id, project_name, start_date, end_date, status) VALUES (3, 'Мобильное приложение', '2024-02-01', '2024-06-01', 'В работе');

INSERT INTO tasks (task_id, project_id, title, due_date, priority) VALUES (1, 1, 'Проектирование БД', '2023-10-15', 1);
INSERT INTO tasks (task_id, project_id, title, due_date, priority) VALUES (2, 1, 'Разработка UI', '2023-11-30', 1);
INSERT INTO tasks (task_id, project_id, title, due_date, priority) VALUES (3, 2, 'Сбор требований', '2024-02-10', 2);
INSERT INTO tasks (task_id, project_id, title, due_date, priority) VALUES (4, 3, 'Дизайн приложения', '2024-03-01', 1);
INSERT INTO tasks (task_id, project_id, title, due_date, priority) VALUES (5, 3, 'Разработка API', '2024-04-15', 2);

INSERT INTO assignments (assignment_id, task_id, employee_id, assigned_date) VALUES (1, 1, 1, '2026-03-27');
INSERT INTO assignments (assignment_id, task_id, employee_id, assigned_date) VALUES (2, 2, 2, '2026-03-27');
INSERT INTO assignments (assignment_id, task_id, employee_id, assigned_date) VALUES (3, 3, 1, '2026-03-27');
INSERT INTO assignments (assignment_id, task_id, employee_id, assigned_date) VALUES (4, 4, 2, '2026-03-27');
INSERT INTO assignments (assignment_id, task_id, employee_id, assigned_date) VALUES (5, 5, 2, '2026-03-27');

