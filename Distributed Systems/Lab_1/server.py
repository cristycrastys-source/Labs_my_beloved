import grpc
from concurrent import futures
import time

# Импорт сгенерированных классов
import order_pb2
import order_pb2_grpc

# Словарь с заказами — имитация базы данных
ORDERS_DB = {
    "001": {"status": "processing", "message": "Заказ принят, собирается на складе"},
    "002": {"status": "shipped", "message": "Заказ передан в службу доставки"},
    "003": {"status": "delivered", "message": "Заказ доставлен получателю"},
    "004": {"status": "cancelled", "message": "Заказ отменен по запросу клиента"},
}

# Класс-наследник базового сервиса — реализация бизнес-логики
class OrderManagerServicer(order_pb2_grpc.OrderManagerServicer):

    def GetOrderStatus(self, request, context):
        """Unary RPC: получает ID заказа, возвращает его статус"""
        order_id = request.order_id
        print(f"[Сервер] Получен запрос статуса для заказа: {order_id}")

        # Поиск заказа в базе
        order = ORDERS_DB.get(order_id)

        if order:
            # Заказ найден — возврат информации
            print(f"[Сервер] Заказ {order_id} найден: {order['status']}")
            return order_pb2.OrderResponse(
                order_id=order_id,
                status=order["status"],
                message=order["message"]
            )
        else:
            # Заказ не найден — возврат статуса как "not found"
            print(f"[Сервер] Заказ {order_id} не найден")
            return order_pb2.OrderResponse(
                order_id=order_id,
                status="not_found",
                message="Заказ с таким ID не найден"
            )

def serve():
    """Запуск gRPC сервера"""
    # Создание сервера с пулом потоков (до 10 одновременных запросов)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Регистрация сервиса на сервере
    order_pb2_grpc.add_OrderManagerServicer_to_server(
        OrderManagerServicer(), server
    )

    # Порт 50051
    server.add_insecure_port('[::]:50051')
    server.start()
    print("=== Сервер OrderManager запущен на порту 50051 ===")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
