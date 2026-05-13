import grpc
from concurrent import futures
import message_service_pb2
import message_service_pb2_grpc
import base64

# Словарь для хранения кэша (имитация базы данных)
cache_storage = {}

class MessageService(message_service_pb2_grpc.MessageServiceServicer):
    
    # Задание 1: сохранение ключа и значения в кэш
    def CacheSet(self, request, context):
        key = request.key
        value = request.value
        cache_storage[key] = value
        return message_service_pb2.CacheResponse(status="OK")
    
    # Задание 2: кодирование или раскодирование Base64
    def Base64Process(self, request, context):
        action = request.action
        data = request.data
        
        if action == "encode":
            # Преобразование строки в байты, затем кодирование в base64
            encoded = base64.b64encode(data.encode()).decode()
            return message_service_pb2.Base64Response(result=encoded)
        elif action == "decode":
            # Раскодирование base64 в строку
            decoded = base64.b64decode(data.encode()).decode()
            return message_service_pb2.Base64Response(result=decoded)
        else:
            # Если действие неизвестно, возвращается ошибка
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Неизвестное действие. Используйте 'encode' или 'decode'")
            return message_service_pb2.Base64Response()
    
    # Задание 3: подсчёт символов без пробелов
    def CountChars(self, request, context):
        text = request.text
        # Удаление всех пробелов и подсчёт оставшихся символов
        chars_without_spaces = [c for c in text if c != ' ']
        count = len(chars_without_spaces)
        return message_service_pb2.CharCountResponse(count=count)

def serve():
    # Создание gRPC сервера с 10 потоками для параллельной обработки
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Добавление реализованного сервиса к серверу
    message_service_pb2_grpc.add_MessageServiceServicer_to_server(MessageService(), server)
    # Прослушивание порта 50051 (стандартный порт для gRPC)
    server.add_insecure_port('[::]:50051')
    print("gRPC сервер запущен на порту 50051...")
    server.start()
    # Бесконечное ожидание запросов
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
