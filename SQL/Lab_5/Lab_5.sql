-- ============================================================================
-- Лабораторная работа №5
-- Оптимизация запросов с помощью индексов и анализа плана выполнения
-- Вариант: 21
-- ============================================================================
-- Цель работы: Научиться анализировать производительность SQL-запросов, 
-- интерпретировать план выполнения (Query Plan) и оптимизировать работу 
-- базы данных с помощью различных типов индексов (B-tree, Hash).
-- ============================================================================

-- ============================================================================
-- Теоретическая часть
-- ============================================================================
-- 1. Планирование запросов (Query Planning):
--    - explain query - показывает предполагаемый план без выполнения
--    - explain analyze query - выполняет запрос и показывает реальное время
--
-- 2. Стоимость (Cost): cost=0.00..123.45
--    - 0.00 - затраты на старт (получение первой строки)
--    - 123.45 - общие затраты на получение всех строк
--
-- 3. Методы сканирования:
--    - Seq Scan (Sequential Scan): полный перебор, медленно для точечных запросов
--    - Index Scan / Bitmap Heap Scan: использование индекса, быстро для малой выборки
--    - Bitmap Index Scan: комбинирование нескольких индексов
--
-- 4. Типы индексов:
--    - B-Tree: стандартный, подходит для сравнений (=, <, >) и сортировки (order by)
--    - Hash: только для точного равенства (=)
-- ============================================================================

-- ============================================================================
-- ============================================================================
-- ЧАСТЬ 1. На сервере
-- ============================================================================
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Задание 1. Анализ производительности ДО оптимизации
-- ----------------------------------------------------------------------------
-- Описание: Найти сотрудников по username (точечный поиск без индекса)
-- Ожидаемый план: Seq Scan (полный перебор таблицы)
-- Фиксация: стоимость (Cost) и время выполнения (Execution Time)

-- 1.1. Запрос для анализа (точечный поиск по username)
select username from salespeople limit 5;

explain analyze
select * 
from salespeople 
where username = 'eelleyne0';

-- 1.2. Проверка структуры таблицы
select
    column_name,
    data_type,
    is_nullable
from information_schema.columns
where table_name = 'salespeople'
order by ordinal_position;

-- 1.3. Статистика таблицы (количество строк для оценки)
select 
    count(*) as total_salespeople,
    count(*) filter (where username = 'eelleyne0') as matching_count
from salespeople;

-- ============================================================================
-- ЧАСТЬ 2. Локально
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Задание 2. Оптимизация поиска по username (B-Tree индекс)
-- ----------------------------------------------------------------------------

-- 2.1. Создание B-Tree индекса для ускорения поиска по username
create unique index idx_salespeople_username 
on salespeople(username);

-- 2.2. Повторный анализ ПОСЛЕ создания индекса
-- Ожидаемый план: Index Scan (использование индекса)
-- Ожидаемый результат: значительное снижение Execution Time
explain analyze
select * 
from salespeople 
where username = 'eelleyne0';

-- 2.3. Верификация использования индекса (анализ плана)
explain (analyze, buffers, verbose)
select * 
from salespeople 
where username = 'eelleyne0';

-- ----------------------------------------------------------------------------
-- Задание 3. Сложная оптимизация (JOIN + диапазон дат)
-- ----------------------------------------------------------------------------
-- Примечание: в таблице sales отсутствует salesperson_id, 
-- JOIN выполняется по полю dealership_id

-- 3.1. Анализ "медленного" сложного запроса ДО создания индексов
-- Ожидаемый план: Hash Join + Seq Scan на sales (полный перебор)
explain analyze
select 
    s.sales_transaction_date as sale_date,
    s.sales_amount,
    sp.first_name,
    sp.last_name,
    sp.username
from sales s
join salespeople sp on s.dealership_id = sp.dealership_id
where sp.username = 'eelleyne0'
  and s.sales_transaction_date between '2024-01-01' and '2024-12-31'
order by s.sales_transaction_date desc;

-- 3.2. Создание составного индекса для оптимизации JOIN и диапазона
-- Индекс покрывает: условие JOIN (dealership_id) + фильтр по дате (sales_transaction_date)
create index idx_sales_dealership_date 
on sales(dealership_id, sales_transaction_date);

-- 3.3. Повторный анализ ПОСЛЕ создания индексов
-- Ожидаемый план: Nested Loop + Index Scan (использование составного индекса)
-- Ожидаемый результат: снижение Cost и Time
explain analyze
select 
    s.sales_transaction_date as sale_date,
    s.sales_amount,
    sp.first_name,
    sp.last_name,
    sp.username
from sales s
join salespeople sp on s.dealership_id = sp.dealership_id
where sp.username = 'eelleyne0'
  and s.sales_transaction_date between '2024-01-01' and '2024-12-31'
order by s.sales_transaction_date desc;

-- 3.4. Детальный анализ с дополнительной информацией
explain (analyze, buffers, timing)
select 
    s.sales_transaction_date as sale_date,
    s.sales_amount,
    sp.first_name,
    sp.last_name
from sales s
join salespeople sp on s.dealership_id = sp.dealership_id
where sp.username = 'eelleyne0'
  and s.sales_transaction_date between '2024-01-01' and '2024-12-31';

-- ----------------------------------------------------------------------------
-- Дополнительные запросы для анализа
-- ----------------------------------------------------------------------------

-- 4.1. Проверка созданных индексов
select 
    schemaname,
    tablename,
    indexname,
    indexdef
from pg_indexes
where tablename in ('salespeople', 'sales')
    and indexname in ('idx_salespeople_username', 'idx_sales_dealership_date')
order by tablename, indexname;

-- 4.2. Сравнение размера таблиц и индексов
select 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as total_size,
    pg_size_pretty(pg_indexes_size(tablename::regclass)) as indexes_size
from (values ('salespeople'), ('sales')) as t(tablename);

-- 4.3. Статистика использования индексов
select 
    schemaname,
    relname as tablename,
    indexrelname as indexname,
    idx_scan as number_of_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
from pg_stat_user_indexes
where indexrelname in ('idx_salespeople_username', 'idx_sales_dealership_date');

-- ----------------------------------------------------------------------------
-- Очистка (удаление индексов после завершения работы)
-- ----------------------------------------------------------------------------
drop index if exists idx_salespeople_username;
drop index if exists idx_sales_dealership_date;