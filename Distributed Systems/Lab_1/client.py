import grpc

# Импорт сгенерированных классов
import order_pb2
import order_pb2_grpc

def run():
    """Подключение к серверу и выполнение запросов"""
    # Создание канала связи с сервером
    with grpc.insecure_channel('localhost:50051') as channel:
        # Создание заглушки (stub) — для вызова методов
        stub = order_pb2_grpc.OrderManagerStub(channel)

        # Тестовые ID заказов для проверки
        test_ids = ['001', '002', '005']

        for order_id in test_ids:
            print(f"\n--- Запрос статуса заказа {order_id} ---")

            # Запрос
            request = order_pb2.OrderRequest(order_id=order_id)

            # Удаленный метод (Unary RPC)
            response = stub.GetOrderStatus(request)

            # Вывод ответа
            print(f"ID заказа: {response.order_id}")
            print(f"Статус: {response.status}")
            print(f"Сообщение: {response.message}")

if __name__ == "__main__":
    run()
