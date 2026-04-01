-- ============================================================================
-- Лабораторная работа №1
-- Основы работы с SQL-запросами: создание запросов и манипуляции с данными
-- Вариант: 21
-- ============================================================================

-- ============================================================================
-- Задание 1.3. Спецпроект (CRUD)
-- ============================================================================
-- 1. CREATE TABLE customers_nyc AS ... (копия клиентов из NYC).
drop table if exists customers_nyc;

create table customers_nyc as
select *
from customers
where city = 'New York City' and state = 'NY';

-- 2. DELETE клиентов с индексом 10014.
delete from customers_nyc
where postal_code = '10014';

-- 3. ALTER TABLE ... ADD COLUMN event text.
alter table customers_nyc add column event text;

-- 4. UPDATE ... SET event = 'thank-you party'.
update customers_nyc set event = 'thank-you party';

-- ============================================================================
-- Задание 2.3. (CRUD - Локально)
-- ============================================================================
-- 1. Создание таблицы failed_emails (bounced) на основе отскочивших писем.
drop table if exists failed_emails;

create table failed_emails as
select *
from emails
where bounced in ('t', 'Yes');

-- 2. Добавление столбца retry.
alter table failed_emails add column retry varchar(1);

-- 3. Заполнение столбца retry значением 'N'.
update failed_emails set retry = 'N';

-- 4. Удаление писем с темой 'Welcome'.
select *
from failed_emails
limit 10;

delete from failed_emails
where email_subject = 'Welcome';

-- 5. Финальная проверка.
select * from failed_emails;