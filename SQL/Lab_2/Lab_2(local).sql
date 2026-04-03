-- ============================================================================
-- Лабораторная работа №2
-- Использование соединений (JOIN), подзапросов и функций преобразования данных
-- Вариант: 21
-- ============================================================================

-- ============================================================================
-- Задание 2.3. Создание витрины данных (Data Transformation)
-- ============================================================================
-- Подготовить "плоскую" таблицу для аналитиков данных.
-- 1. Соединить sales (основа), customers, products, dealerships (Left Join).
create table sales_flat as
select *
from sales s
left join customers c on s.customer_id = c.customer_id
left join products p on s.product_id = p.product_id 
left join dealerships d on s.dealership_id = d.dealership_id;

-- 2. Очистить данные:
--    Если dealership_id в продажах NULL, заменить на -1 (используйте COALESCE).
create table sales_flat as
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
drop table sales_flat

create table sales_flat as
select s.product_id,
s.sales_amount,
s.sales_transaction_date,
c.customer_id,
c.first_name as customer_first_name,
c.last_name as customer_last_name,
c.email as customer_email,
c.phone as customer_phone,
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
