import pika
import grpc
import sys
import os

# Добавление пути к папке с gRPC файлами
sys.path.append(os.path.join(os.path.dirname(__file__), '../grpc_sync'))

import message_service_pb2
import message_service_pb2_grpc

# Подключение к RabbitMQ
credentials = pika.PlainCredentials('user', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=credentials))
channel = connection.channel()

# Объявление очереди
channel.queue_declare(queue='task_queue', durable=True)

print(' [*] Ожидание сообщений. Для выхода нажмите CTRL+C')

# Функция обработки одного сообщения
def callback(ch, method, properties, body):
    message_text = body.decode()
    print(f" [x] Получено: {message_text}")
    
    # Подключение к gRPC серверу
    with grpc.insecure_channel('localhost:50051') as grpc_channel:
        stub = message_service_pb2_grpc.MessageServiceStub(grpc_channel)
        
        # Проверка префикса сообщения
        if message_text.startswith('cache:'):
            # Пример: cache:city=Moscow
            parts = message_text[6:].split('=')
            if len(parts) == 2:
                response = stub.CacheSet(message_service_pb2.CacheRequest(key=parts[0], value=parts[1]))
                print(f" [✓] Кэш сохранён: {response.status}")
        
        elif message_text.startswith('encode:'):
            # Пример: encode:Hello
            text = message_text[7:]
            response = stub.Base64Process(message_service_pb2.Base64Request(action="encode", data=text))
            print(f" [✓] Base64: {response.result}")
        
        elif message_text.startswith('decode:'):
            # Пример: decode:SGVsbG8=
            text = message_text[7:]
            response = stub.Base64Process(message_service_pb2.Base64Request(action="decode", data=text))
            print(f" [✓] Decode: {response.result}")
        
        elif message_text.startswith('chars:'):
            # Пример: chars:Hello World
            text = message_text[6:]
            response = stub.CountChars(message_service_pb2.TextRequest(text=text))
            print(f" [✓] Символов без пробелов: {response.count}")
        
        else:
            print(" [✗] Неизвестный формат. Используй: cache:, encode:, decode:, chars:")
    
    # Подтверждение обработки
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Настройка: брать по 1 сообщению за раз
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

# Запуск ожидания
channel.start_consuming()
