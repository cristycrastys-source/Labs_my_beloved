-- ============================================================================
-- Лабораторная работа №2
-- Использование соединений (JOIN), подзапросов и функций преобразования данных
-- Вариант: 21
-- ============================================================================
-- Цель работы: Освоить методы объединения таблиц (JOIN, UNION), работу с подзапросами и функции преобразования данных (CASE, COALESCE) в PostgreSQL.
-- Теория: Chapter 3. SQL for Data Preparation.

-- JOIN (объединение таблиц):
-- INNER JOIN - возвращает только строки, где есть совпадение в обеих таблицах.
-- LEFT JOIN - возвращает все строки из левой таблицы и совпадающие из правой.
-- RIGHT JOIN - возвращает все строки из правой таблицы и совпадающие из левой.
-- FULL JOIN - возвращает все строки из обеих таблиц.
-- CROSS JOIN - декартово произведение таблиц.

-- UNION (объединение результатов):
-- UNION - объединяет результаты двух запросов, удаляя дубликаты.
-- UNION ALL - объединяет результаты двух запросов, оставляя дубликаты.
-- Требование: количество и типы столбцов в запросах должны совпадать.

-- Подзапросы (Subqueries):
-- Подзапрос в WHERE - используется для фильтрации.
-- Подзапрос в FROM - используется как временная таблица.
-- Подзапрос в SELECT - используется для вычисления значения.
-- EXISTS / NOT EXISTS - проверка наличия строк в подзапросе.

-- Функции преобразования данных:
-- COALESCE(value1, value2, ...) - возвращает первое не NULL значение.
-- NULLIF(value1, value2) - возвращает NULL, если value1 = value2.
-- CASE - условное выражение.
--   CASE WHEN condition1 THEN result1
--        WHEN condition2 THEN result2
--        ELSE result_default END
-- CAST(expression AS type) - преобразование типа данных.

-- Данные: bi_sql_data_student_dump.sql
-- ============================================================================

-- ============================================================================
-- Задание 2.1. Поиск покупателей авто (INNER JOIN)
-- ============================================================================
-- Получить контактные данные всех клиентов, купивших автомобиль, для обзвона.
-- Использовать таблицу sales, customers, products.
select *
from sales s
inner join customers c on s.customer_id = c.customer_id
inner join products p on s.product_id = p.product_id;

-- Условие: product_type = 'automobile'.
select *
from sales s
inner join customers c on s.customer_id = c.customer_id
inner join products p on s.product_id = p.product_id
where p.product_type = 'automobile';

-- Условие: phone is not null.
select *
from sales s
inner join customers c on s.customer_id = c.customer_id
inner join products p on s.product_id = p.product_id
where p.product_type = 'automobile'
and c.phone is not null;

-- Вывести: customer_id, first_name, last_name, phone.
select c.customer_id,
c.first_name,
c.last_name,
c.phone
from sales s
inner join customers c on s.customer_id = c.customer_id
inner join products p on s.product_id = p.product_id
where p.product_type = 'automobile'
and c.phone is not null;

-- ============================================================================
-- Задание 2.2. Вечеринка в Лос-Анджелесе (UNION)
-- ============================================================================
-- Составить список приглашенных на мероприятие. Это клиенты И сотрудники из Лос-Анджелеса.
-- Запрос 1: Клиенты из city = 'Los Angeles'.
select city
limit 10;

select 
customer_id,
first_name,
last_name
from customers
where city = 'Los Angeles';

-- Запрос 2: Продавцы (salespeople), работающие в дилерских центрах (dealerships) в city = 'Los Angeles'.
select sp.salesperson_id,
sp.first_name,
sp.last_name
from salespeople sp
inner join dealerships d on sp.dealership_id = d.dealership_id
where d.city = 'Los Angeles';

-- Добавить поле guest_type ('Customer' или 'Employee').
select customer_id,
first_name,
last_name,
'Customer' as guest_type
from customers
where city = 'Los Angeles';

select sp.salesperson_id,
sp.first_name,
sp.last_name,
'Employee' as guest_type
from salespeople sp
inner join dealerships d on sp.dealership_id = d.dealership_id
where city = 'Los Angeles';

-- Объединить через UNION.
select customer_id,
first_name,
last_name,
'Customer' as guest_type
from customers
where city = 'Los Angeles'
union
select sp.salesperson_id,
sp.first_name,
sp.last_name,
'Employee' as guest_type
from salespeople sp
inner join dealerships d on sp.dealership_id = d.dealership_id
where city = 'Los Angeles';

-- Отсортировать.
select customer_id,
first_name,
last_name,
'Customer' as guest_type
from customers
where city = 'Los Angeles'
union
select sp.salesperson_id,
sp.first_name,
sp.last_name,
'Employee' as guest_type
from salespeople sp
inner join dealerships d on sp.dealership_id = d.dealership_id
where city = 'Los Angeles'
order by guest_type, last_name;

-- ============================================================================
-- Задание 2.3. Создание витрины данных (Data Transformation)
-- ============================================================================
-- Подготовить "плоскую" таблицу для аналитиков данных.
-- 1. Соединить sales (основа), customers, products, dealerships (Left Join).
select *
from sales s
left join customers c on s.customer_id = c.customer_id
left join products p on s.product_id = p.product_id 
left join dealerships d on s.dealership_id = d.dealership_id;

-- 2. Очистить данные:
--    Если dealership_id в продажах NULL, заменить на -1 (используйте COALESCE).
select s.product_id,
s.sales_amount,
s.sales_transaction_date,
c.customer_id,
c.first_name as customer_frist_name,
c.last_name as customer_last_name,
c.email as customer_email,
c.phone as customer_phone,
p.product_id,
p.product_type,
p.base_msrp,
coalesce(d.dealership_id, -1) as dealership_id,
d.city as dealership_city,
d.state as dealership_state
from sales s
left join customers c on s.customer_id = c.customer_id
left join products p on s.product_id = p.product_id 
left join dealerships d on s.dealership_id = d.dealership_id;

-- 3. Создать признак (Feature Engineering):
-- Столбец high_savings: равен 1, если (base_msrp - sales_amount) > 500. Иначе 0.
select s.product_id,
s.sales_amount,
s.sales_transaction_date,
c.customer_id,
c.first_name as customer_first_name,
c.last_name as customer_last_name,
c.email as customer_email,
c.phone as customer_phone,
p.product_id,
p.product_type,
p.base_msrp,
coalesce(d.dealership_id, -1) as dealership_id,
d.city as dealership_city,
d.state as dealership_state,
case
	when (p.base_msrp - s.sales_amount) > 500 then 1
	else 0
end as high_savings
from sales s
left join customers c on s.customer_id = c.customer_id
left join products p on s.product_id = p.product_id 
left join dealerships d on s.dealership_id = d.dealership_id;

-- ============================================================================
-- Индивидуальные задания (Вариант 21)
-- ============================================================================
-- Задача 1. Использование JOIN (соединение 2-3 таблиц).
-- Вывести детали продаж (клиент, товар) для дилера с ID=10.
select s.customer_id,
s.product_id,
s.dealership_id,
c.first_name,
c.last_name,
p.product_type,
p.product_id,
p.base_msrp,
p.model
from sales s
inner join products p on s.product_id = p.product_id
inner join customers c on s.customer_id = c.customer_id
where s.dealership_id = 10;

-- Задача 2. Использование подзапросов или UNION.
-- Найдите клиентов, у которых сумма одной покупки превышала 50 000 (подзапрос).
select customer_id,
sales_amount
from sales
where sales_amount > 50000;
--
select distinct customer_id
from sales
where sales_amount > 50000;
--
select customer_id,
first_name,
last_name,
email
from customers
where customer_id in (
select distinct customer_id
from sales
where sales_amount > 50000
);
--
select customer_id,
first_name,
last_name,
email
from customers
where customer_id in (
select distinct customer_id
from sales
where sales_amount > 50000
)
order by customer_id;

-- Задача 3. Преобразование данных (CASE, COALESCE, CAST).
-- Приведите sales_transaction_id_date к формату 'YYYY-MM-DD' (через ::DATE).
select sales_transaction_date
from sales
limit 10;
--
select sales_transaction_date as original_date,
sales_transaction_date::date as converted_date
from sales
limit 10;
--
select sales_transaction_date as original_date,
sales_transaction_date::date as converted_date
from sales
where sales_transaction_date is not null;
--
select sales_transaction_date as original_date,
sales_transaction_date::date as converted_date
from sales
where sales_transaction_date is not null
order by sales_transaction_date;