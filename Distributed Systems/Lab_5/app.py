# Импорт модуля time для работы с задержками (паузы между попытками подключения)
import time

# Импорт модуля redis для подключения к Redis (in-memory хранилище)
import redis

# Импорт Flask для создания веб-приложения
from flask import Flask

# Создание экземпляра Flask-приложения
app = Flask(__name__)

# Подключение к Redis.
# host='cache' — имя контейнера Redis в docker-compose.yml (сетевой alias)
# port=6379 — стандартный порт Redis
# Примечание: соединение устанавливается при старте приложения
cache = redis.Redis(host='cache', port=6379)


# Функция получения текущего значения счётчика с автоматическим увеличением
def get_hit_count():
    # Количество попыток подключения к Redis при ошибке
    retries = 5

    # Бесконечный цикл с выходом при успехе или исчерпании попыток
    while True:
        try:
            # incr('hits') — атомарная операция:
            # 1. Увеличивает значение ключа 'hits' на 1
            # 2. Возвращает новое значение
            # Если ключа нет — создаёт его со значением 0 и затем увеличивает
            return cache.incr('hits')

        # Перехват ошибки подключения к Redis
        except redis.exceptions.ConnectionError as exc:
            # Если попытки закончились — выбрасываем исключение выше
            if retries == 0:
                raise exc

            # Уменьшаем счётчик оставшихся попыток
            retries -= 1

            # Пауза 0.5 секунды перед следующей попыткой
            time.sleep(0.5)


# Декоратор — привязывает функцию к корневому URL '/'
@app.route('/')
def hello():
    # Получение текущего значения счётчика (с автоматическим увеличением)
    count = get_hit_count()

    # Возврат HTML-страницы с тёмной темой
    # Вариант 21: сохранён зелёный цвет заголовка и футер "ООО Ромашка"
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                /* Тёмный фон страницы */
                background-color: #1a1e2c;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }}
            /* Карточка с тёмной темой */
            .card {{
                background-color: #2a2f3f;
                border-radius: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                padding: 40px;
                text-align: center;
                /* Увеличенная максимальная ширина для вмещения эмодзи */
                max-width: 600px;
                width: 100%;
            }}
            /* Стиль заголовка (зелёный цвет — требование варианта 21) */
            h1 {{
                color: #6fbf6f;
                margin-bottom: 20px;
                /* Запрещаем перенос строки внутри заголовка */
                white-space: nowrap;
            }}
            /* Рамка для отображения счётчика (тёмная тема) */
            .counter-box {{
                background-color: #1e2230;
                border: 3px solid #6fbf6f;
                border-radius: 20px;
                padding: 20px;
                margin: 30px 0;
            }}
            /* Крупное число счётчика (светло-зелёное) */
            .counter-number {{
                font-size: 64px;
                font-weight: bold;
                color: #8fdf8f;
                display: block;
            }}
            /* Подпись под числом (светло-серая) */
            .counter-label {{
                font-size: 18px;
                color: #aaa;
                margin-top: 10px;
                display: block;
            }}
            /* Нижний колонтитул — требование варианта 21 */
            footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #666;
                border-top: 1px solid #3a3f4f;
                padding-top: 20px;
            }}
            /* Эмодзи не будут переноситься */
            .emoji {{
                display: inline-block;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <!-- Заголовок с эмодзи, запрет переноса -->
            <h1>
                <span class="emoji">🌿</span> Бизнес-стенд "инновации" <span class="emoji">🌿</span>
            </h1>
            <!-- Рамка со счётчиком -->
            <div class="counter-box">
                <span class="counter-number">{count}</span>
                <span class="counter-label">посетителей сегодня</span>
            </div>
            <!-- Нижний колонтитул (вариант 21: ООО Ромашка) -->
            <footer>
                ООО Ромашка, 2026
            </footer>
        </div>
    </body>
    </html>
    '''


# Условие: код выполняется только при прямом запуске файла (не при импорте)
if __name__ == "__main__":
    # Запуск Flask-сервера
    # host="0.0.0.0" — слушаем все сетевые интерфейсы (доступно извне контейнера)
    # debug=True — режим отладки (автоматическая перезагрузка при изменении кода)
    app.run(host="0.0.0.0", debug=True)
