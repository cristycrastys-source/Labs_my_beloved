from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Список серверов (порядок важен: сначала основной, потом резервный)
SERVERS = ['https://127.0.0.1:5001', 'https://127.0.0.1:5002']

def proxy_to_server(path, method='POST', json_data=None):
    """Проксирование запроса к серверам с реализацией failover"""
    for server in SERVERS:
        try:
            if method == 'POST':
                resp = requests.post(f"{server}{path}", json=json_data,
                                     verify='ca_cert.pem',           # Проверка сертификата сервера
                                     cert=('client_cert.pem', 'client_key.pem'),  # Сертификат координатора для mTLS
                                     timeout=5)                     # Таймаут 5 секунд
            else:
                resp = requests.get(f"{server}{path}",
                                    verify='ca_cert.pem',
                                    cert=('client_cert.pem', 'client_key.pem'),
                                    timeout=5)
            
            if resp.status_code == 200:
                return jsonify(resp.json())  # Успешный ответ клиенту
        except Exception as e:
            print(f"[COORDINATOR] {server} недоступен: {e}")
            continue  # Переход к следующему серверу
    
    # Все серверы недоступны
    return jsonify({'error': 'Все серверы недоступны'}), 503

# Базовый эндпоинт (синхронная обработка)
@app.route('/api/data', methods=['POST'])
def proxy_data():
    return proxy_to_server('/api/data', 'POST', request.get_json())

# Эндпоинты для варианта 21 (отложенная обработка)
@app.route('/api/task', methods=['POST'])
def proxy_task():
    return proxy_to_server('/api/task', 'POST', request.get_json())

@app.route('/api/task/<int:task_id>/status', methods=['GET'])
def proxy_status(task_id):
    return proxy_to_server(f'/api/task/{task_id}/status', 'GET')

if __name__ == '__main__':
    print("[COORDINATOR] Запуск на порту 8000 (HTTP)")
    app.run(host='0.0.0.0', port=8000)
