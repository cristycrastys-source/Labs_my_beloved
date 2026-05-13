import pika
import sys

# Параметры подключения к RabbitMQ
credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = connection.channel()

# Объявление очереди (durable=True - сообщения не теряются при перезапуске)
channel.queue_declare(queue='task_queue', durable=True)

# Формирование сообщения из аргументов командной строки
# Пример: python producer.py fact:5
message = ' '.join(sys.argv[1:]) or "Hello World"

# Отправка сообщения в очередь
channel.basic_publish(
    exchange='',                      # используется очередь по умолчанию
    routing_key='task_queue',         # имя очереди
    body=message,                     # тело сообщения
    properties=pika.BasicProperties(
        delivery_mode=2,              # сообщение сохраняется на диск (persistent)
    )
)

print(f" [x] Отправлено сообщение: '{message}'")
connection.close()
