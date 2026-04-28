-- ============================================================================
-- Лабораторная работа №4
-- Оконные функции для анализа данных
-- Вариант: 21
-- ============================================================================
-- Цель работы: Изучить концепцию оконных функций в SQL и научиться применять
-- их для выполнения сложных аналитических расчетов: ранжирования, вычисления
-- скользящих средних, нарастающих итогов и сравнительного анализа строк без
-- группировки данных.

-- Оконные функции (PostgreSQL):
-- ROW_NUMBER() - присваивает уникальный номер каждой строке в окне (1, 2, 3...).
-- RANK() - присваивает ранг. При равных значениях ранги одинаковы, следующий пропускается (1, 1, 3...).
-- DENSE_RANK() - присваивает ранг. При равных значениях ранги одинаковы, следующий не пропускается (1, 1, 2...).
-- NTILE(n) - разбивает отсортированные строки на n примерно равных групп (бакетов).
-- LAG(col, offset) - возвращает значение из строки, находящейся на offset позиций перед текущей.
-- LEAD(col, offset) - возвращает значение из строки, находящейся на offset позиций после текущей.
-- SUM() OVER() - вычисляет нарастающий итог или скользящую сумму.
-- AVG() OVER() - вычисляет скользящее среднее.
-- COUNT() OVER() - вычисляет накопительный подсчет строк.

-- Синтаксис оконной функции:
-- {window_func} OVER (PARTITION BY {partition_key} ORDER BY {order_key} {frame_clause})

-- Параметры:
-- PARTITION BY - разделяет набор данных на группы (окна), внутри которых производятся вычисления.
-- ORDER BY - определяет порядок строк внутри окна.
-- ROWS BETWEEN ... AND ... - задает оконный фрейм (границы окна относительно текущей строки).

-- Данные: bi_sql_data_student_dump.sql
-- ============================================================================

-- ============================================================================
-- Часть 1. Общие задания (Guided Labs)
-- ============================================================================

-- ============================================================================
-- Задание 4.1. Ранжирование сотрудников по стажу
-- ============================================================================
-- Менеджмент хочет оценить сотрудников (salespeople) в каждом дилерском центре
-- на основе даты их найма.
select salesperson_id,
	dealership_id,
    first_name,
    hire_date,
rank() over (partition by dealership_id order by hire_date) as hire_rank
from salespeople
where termination_date is null;

-- ============================================================================
-- Задание 4.2. Анализ динамики заполнения адресов
-- ============================================================================
-- Посмотреть накопительный итог (Running Total) количества клиентов,
-- заполнивших поле street_address, в разбивке по датам регистрации.
select date_added::date,
	count(case when street_address is not null then 1 end)
    over (order by date_added::date) as total_addresses_filled
from customers
order by date_added::date
limit 50;

-- ============================================================================
-- Задание 4.3. Скользящее среднее продаж (7 дней)
-- ============================================================================
-- Рассчитать 7-дневное скользящее среднее суммы продаж.
with daily_sales as (
	select sales_transaction_date::date as sale_date,
    	sum(sales_amount) as daily_sum
    from sales
    group by 1
)
select sale_date,
	daily_sum,
	avg(daily_sum) over (order by sale_date rows between 6 preceding and current row) as moving_avg_7
from daily_sales
order by sale_date;

-- ============================================================================
-- Часть 2. Индивидуальные задания (Вариант 21)
-- ============================================================================

-- ============================================================================
-- Задание 2.1. Ранжирование (ROW_NUMBER)
-- ============================================================================
-- Пропумеровать сотрудников, у которых не указана дата увольнения,
-- по salesperson_id.
select salesperson_id,
	first_name,
    last_name,
    hire_date,
    dealership_id,
    row_number() over (order by salesperson_id) as row_num
from salespeople
where termination_date is null
order by salesperson_id;

-- ============================================================================
-- Задание 2.2. Смещение и сравнение (LEAD)
-- ============================================================================
-- Для каждого письма показать тему текущего и тему следующего письма клиенту.
with customer_emails as (
	select customer_id,
    	email_subject,
        sent_date,
        row_number() over (partition by customer_id order by sent_date) as email_seq
    from emails
    where email_subject is not null
)
select customer_id,
       email_subject as current_subject,
       lead(email_subject) over (partition by customer_id order by sent_date) as next_subject,
       sent_date
from customer_emails
order by customer_id, sent_date;

-- ============================================================================
-- Задание 2.3. Скользящий COUNT за последние 3 дня по дилеру
-- ============================================================================
-- Скользящий подсчет количества продаж (COUNT) за последние 3 дня по каждому дилеру.
with daily_dealer_sales as (
	select dealership_id,
    	sales_transaction_date::date as sale_date,
        count(*) as daily_sales_count
    from sales
    group by dealership_id, sales_transaction_date::date
)
select dealership_id,
    sale_date,
    daily_sales_count,
    sum(daily_sales_count) over (
    	partition by dealership_id
        order by sale_date
        rows between 2 preceding and current row
    ) as sales_last_3_days
from daily_dealer_sales
order by dealership_id, sale_date;