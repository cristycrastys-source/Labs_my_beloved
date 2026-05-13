import grpc
import message_service_pb2
import message_service_pb2_grpc

def run():
    # Создание канала связи с gRPC сервером
    # 'localhost:50051' - сервер запущен на этом же компьютере, порт 50051
    # insecure_channel - соединение без шифрования (для учебных целей)
    channel = grpc.insecure_channel('localhost:50051')
    
    # Stub (заглушка) - объект, через который клиент вызывает удалённые методы
    # Он автоматически сериализует запросы в Protobuf и отправляет на сервер
    stub = message_service_pb2_grpc.MessageServiceStub(channel)
    
    # ========== Задание 1: кэширование ==========
    # Отправка пары ключ-значение для сохранения в кэш сервера
    # CacheRequest - тип сообщения, определённый в .proto файле
    print("=== Тест CacheSet ===")
    response1 = stub.CacheSet(message_service_pb2.CacheRequest(key="city", value="Moscow"))
    # Ответ содержит поле status (строка "OK" при успехе)
    print(f"Результат сохранения: {response1.status}")
    
    # ========== Задание 2: Base64 кодирование ==========
    # Кодирование обычного текста в Base64
    print("\n=== Тест Base64 (кодирование) ===")
    response2 = stub.Base64Process(message_service_pb2.Base64Request(
        action="encode",    # encode - закодировать текст
        data="Hello World"   # исходный текст для кодирования
    ))
    print(f"Закодировано: {response2.result}")
    
    # Раскодирование Base64 обратно в обычный текст
    print("\n=== Тест Base64 (декодирование) ===")
    response3 = stub.Base64Process(message_service_pb2.Base64Request(
        action="decode",                # decode - раскодировать
        data="SGVsbG8gV29ybGQ="         # закодированная строка
    ))
    print(f"Раскодировано: {response3.result}")
    
    # ========== Задание 3: подсчёт символов без пробелов ==========
    # Анализ текста: удаление пробелов и подсчёт оставшихся символов
    print("\n=== Тест CountChars ===")
    response4 = stub.CountChars(message_service_pb2.TextRequest(
        text="Hello World Python"   # строка для анализа
    ))
    # count - количество символов без учёта пробелов (H e l l o W o r l d P y t h o n = 16)
    print(f"Количество символов без пробелов: {response4.count}")

if __name__ == '__main__':
    run()
