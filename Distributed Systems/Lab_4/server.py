from flask import Flask, request
import ssl
import sys
import threading
import time
from cryptography.fernet import Fernet

app = Flask(__name__)

# Хранилище задач для варианта 21 (отложенная обработка)
tasks = {}
task_counter = 0

def decrypt_data(encrypted_data):
    """Расшифровка данных Fernet с использованием ключа из файла"""
    with open('encryption_key.txt', 'rb') as f:
        key = f.read()
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_data.encode()).decode()

# Базовый эндпоинт (синхронная обработка)
@app.route('/api/data', methods=['POST'])
def get_data():
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return {'error': 'Data not provided'}, 400
        decrypted = decrypt_data(data['data'])
        print(f"[SERVER] Синхронный: {decrypted}")
        return {'status': 'ok', 'decrypted': decrypted}
    except Exception as e:
        return {'error': str(e)}, 500

# ========== ВАРИАНТ 21 (ОТЛОЖЕННАЯ ОБРАБОТКА) ==========

# Создание отложенной задачи
@app.route('/api/task', methods=['POST'])
def create_task():
    global task_counter
    data = request.get_json()
    encrypted_data = data.get('data')
    decrypted = decrypt_data(encrypted_data)
    
    # Присвоение уникального ID задачи
    task_counter += 1
    task_id = task_counter
    tasks[task_id] = {'status': 'processing', 'result': None}
    
    # Фоновая обработка (имитация долгой операции 5 секунд)
    def process():
        time.sleep(5)
        tasks[task_id]['status'] = 'completed'
        tasks[task_id]['result'] = f"Обработано: {decrypted}"
    
    threading.Thread(target=process).start()
    return {'task_id': task_id, 'status': 'processing'}

# Получение статуса задачи по ID
@app.route('/api/task/<int:task_id>/status', methods=['GET'])
def get_task_status(task_id):
    if task_id not in tasks:
        return {'error': 'Task not found'}, 404
    return tasks[task_id]

# ========================================================

if __name__ == '__main__':
    # Чтение порта из аргумента командной строки
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    
    # Настройка mTLS
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('server_cert.pem', 'server_key.pem')  # Сертификат сервера
    context.verify_mode = ssl.CERT_REQUIRED  # Требование сертификата от клиента
    context.load_verify_locations('ca_cert.pem')  # CA для проверки клиентских сертификатов
    
    print(f"[SERVER] Запуск на порту {port} с mTLS")
    app.run(host='0.0.0.0', port=port, ssl_context=context)
