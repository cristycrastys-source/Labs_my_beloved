-- ============================================================================
-- Практическая работа №1
-- Геопространственный анализ данных. Аналитика с использованием сложных типов данных
-- Выбранные задания: А1, Б6, В11, Г16
-- ============================================================================
-- Цель работы: Научиться применять продвинутые возможности PostgreSQL для анализа 
-- данных, выходящих за рамки стандартных чисел и строк. Освоить работу с 
-- временными рядами, геопространственными данными, массивами, JSON/JSONB 
-- структурами и полнотекстовым поиском.
-- ============================================================================

-- ============================================================================
-- Часть 0. Предварительная настройка
-- ============================================================================

-- Установка расширений для геопространственного анализа
create extension if not exists cube;
create extension if not exists earthdistance;

-- ============================================================================
-- Часть 1. Индивидуальные задания (А1, Б6, В11, Г16)
-- ============================================================================

-- ============================================================================
-- Задание А1. Дни недели продаж
-- ============================================================================
-- Определить, в какой день недели (понедельник, вторник и т.д.) совершается наибольшее количество продаж (sales). Вывести день недели и количество транзакций.
-- TO_CHAR(date, 'Day') - преобразует дату в строку с названием дня недели
-- EXTRACT(DOW FROM date) - извлекает номер дня недели (0-6 или 1-7)
-- COUNT(*) - агрегатная функция для подсчета строк
-- GROUP BY - группировка данных по заданным столбцам
-- ORDER BY - сортировка результатов
-- LIMIT 1 - ограничение вывода одной записью
-- ============================================================================

-- Шаг 1. Базовая группировка с номером дня недели
select 
    extract(dow from sales_transaction_date) as dow_number,
    to_char(sales_transaction_date, 'Day') as day_of_week,
    count(*) as number_of_sales
from sales
group by 
    extract(dow from sales_transaction_date),
    to_char(sales_transaction_date, 'Day')
order by dow_number;

-- Шаг 2. Добавление сортировки по убыванию количества продаж
select 
    to_char(sales_transaction_date, 'Day') as day_of_week,
    count(*) as number_of_sales
from sales
group by 
    extract(dow from sales_transaction_date),
    to_char(sales_transaction_date, 'Day')
order by number_of_sales desc;

-- Шаг 3. Финальный запрос - день с максимальным количеством продаж
select 
    to_char(sales_transaction_date, 'Day') as day_of_week,
    count(*) as number_of_sales
from sales
group by 
    extract(dow from sales_transaction_date),
    to_char(sales_transaction_date, 'Day')
order by number_of_sales desc
limit 1;

-- ============================================================================
-- Задание Б6. Ближайший дилер для клиентов из New York City
-- ============================================================================
-- Описание: Для каждого клиента из города 'New York City' найти ближайший 
-- дилерский центр (dealerships) и расстояние до него.
-- Теория:
-- point(longitude, latitude) - создает геометрическую точку на плоскости
-- point1 <@> point2 - оператор вычисления расстояния между точками в милях
-- CROSS JOIN - декартово произведение таблиц (каждый с каждым)
-- ROW_NUMBER() - оконная функция для нумерации строк в группе
-- PARTITION BY - разделение на группы внутри оконной функции
-- COALESCE - замена NULL значений на указанное значение
-- ============================================================================

-- Шаг 1. Базовый запрос с cross join для расчета всех расстояний
select
    c.customer_id,
    c.first_name,
    c.last_name,
    d.dealership_id,
    d.street_address as dealership_address,
    d.city as dealership_city
from customers c
cross join dealerships d
where c.city = 'New York City'
limit 10;


-- Шаг 2. Добавление вычисления расстояния между точками
select
    c.customer_id,
    c.first_name,
    c.last_name,
    d.dealership_id,
    d.street_address as dealership_address,
    point(c.longitude, c.latitude) <@> point(d.longitude, d.latitude) as distance_miles
from customers c
cross join dealerships d
where c.city = 'New York City'
limit 10;

-- Шаг 3. Финальный запрос - выбор ближайшего дилера для каждого клиента
with distances as (
    select
        c.customer_id,
        concat(c.first_name, ' ', c.last_name) as customer_name,
        d.dealership_id,
        concat(d.street_address, ', ', d.city, ', ', d.state) as dealership_location,
        point(c.longitude, c.latitude) <@> point(d.longitude, d.latitude) as distance_miles,
        row_number() over (partition by c.customer_id order by 
            point(c.longitude, c.latitude) <@> point(d.longitude, d.latitude)) as rn
    from customers c
    cross join dealerships d
    where c.city = 'New York City'
)
select
    customer_id,
    customer_name,
    dealership_id,
    dealership_location,
    round(distance_miles::numeric, 2) as distance_miles
from distances
where rn = 1
order by distance_miles;

-- ============================================================================
-- Задание В11. История покупок в JSON
-- ============================================================================
-- Описание: Создать запрос, который формирует JSON-объект для каждого клиента:
-- { "id": 1, "name": "Ivan", "products": ["Car", "Scooter"] }
-- используя агрегацию массивов.
-- Теория:
-- jsonb_build_object() - создает JSON-объект из пар ключ-значение
-- jsonb_agg() - агрегирует значения в JSON-массив
-- DISTINCT - исключает дубликаты при агрегации
-- COALESCE - заменяет NULL на пустой JSON-массив
-- Подзапрос - вложенный SELECT для агрегации данных из связанной таблицы
-- ============================================================================

-- Шаг 1. Базовый запрос с формированием простого json-объекта
select
    jsonb_build_object(
        'id', customer_id,
        'name', concat(first_name, ' ', last_name)
    ) as customer_info
from customers
limit 5;

-- Шаг 2. Добавление подзапроса для агрегации продуктов
select
    jsonb_build_object(
        'id', c.customer_id,
        'name', concat(c.first_name, ' ', c.last_name),
        'products', (select jsonb_agg(distinct p.product_type)
                     from sales s
                     join products p on s.product_id = p.product_id
                     where s.customer_id = c.customer_id)
    ) as customer_history
from customers c
where c.customer_id <= 5
order by c.customer_id;

-- Шаг 3. Финальный запрос - обработка клиентов без покупок
select
    jsonb_build_object(
        'id', c.customer_id,
        'name', concat(c.first_name, ' ', c.last_name),
        'products', coalesce(
            (select jsonb_agg(distinct p.product_type)
             from sales s
             join products p on s.product_id = p.product_id
             where s.customer_id = c.customer_id),
            '[]'::jsonb
        )
    ) as customer_history
from customers c
order by c.customer_id;

-- ============================================================================
-- Задание Г16. Частотный словарь топ-10 слов из отзывов
-- ============================================================================
-- Описание: Составить топ-10 самых часто встречающихся слов в таблице 
-- customer_survey (столбец feedback), исключив слова короче 3 символов.
-- Теория:
-- STRING_TO_ARRAY(string, delimiter) - разбивает строку на массив по разделителю
-- UNNEST(array) - разворачивает массив в набор строк (одна строка на элемент)
-- REGEXP_REPLACE() - заменяет подстроки по регулярному выражению
-- LOWER() - преобразует строку в нижний регистр
-- LENGTH() - возвращает длину строки
-- GROUP BY - группировка для агрегации
-- COUNT(*) - подсчет частоты встречаемости
-- ORDER BY ... LIMIT - сортировка и ограничение вывода
-- ============================================================================

-- Шаг 1. Базовый запрос с разбиением текста на слова
select 
    unnest(string_to_array(feedback, ' ')) as word
from customer_survey
where feedback is not null
limit 20;

-- Шаг 2. Добавление очистки от знаков препинания и нормализации регистра
select 
    lower(unnest(string_to_array(
        regexp_replace(feedback, '[^a-zA-Zа-яА-Я\s]', '', 'g'),
        ' '
    ))) as word
from customer_survey
where feedback is not null
limit 20;

-- Шаг 3. Финальный запрос - подсчет частоты и фильтрация коротких слов
select 
    lower(word) as word,
    count(*) as frequency
from (
    select 
        unnest(string_to_array(
            regexp_replace(feedback, '[^a-zA-Zа-яА-Я\s]', '', 'g'),
            ' '
        )) as word
    from customer_survey
    where feedback is not null
) as words
where length(word) >= 3
group by lower(word)
order by frequency desc
limit 10;Ы

-- ============================================================================
-- Часть 2. Дополнительные запросы для проверки корректности
-- ============================================================================

-- Проверка наличия расширений
select * from pg_extension where extname in ('cube', 'earthdistance');