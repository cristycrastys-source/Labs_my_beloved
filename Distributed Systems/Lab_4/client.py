import requests
import time
from cryptography.fernet import Fernet

def encrypt_data(plaintext):
    """Шифрование данных Fernet перед отправкой"""
    with open('encryption_key.txt', 'rb') as f:
        key = f.read()
    cipher = Fernet(key)
    return cipher.encrypt(plaintext.encode()).decode()

def main():
    print("=== ВАРИАНТ 21: Отложенная обработка ===\n")
    
    # 1. Синхронный запрос (базовая часть лабораторной)
    print("[1] Синхронный запрос:")
    resp = requests.post('http://localhost:8000/api/data',
                         json={'data': encrypt_data("Тестовое сообщение")})
    print(f"    {resp.json()}\n")
    
    # 2. Отложенная задача (индивидуальное задание, вариант 21)
    print("[2] Отложенная задача (5 секунд):")
    resp = requests.post('http://localhost:8000/api/task',
                         json={'data': encrypt_data("Данные для долгой обработки")})
    task = resp.json()
    task_id = task['task_id']
    print(f"    Создана задача {task_id}, статус: {task['status']}")
    
    # Опрос статуса задачи (polling) каждую секунду
    print("    Ожидание:", end="")
    while True:
        time.sleep(1)
        resp = requests.get(f'http://localhost:8000/api/task/{task_id}/status')
        status = resp.json()
        print(f" {status['status']}", end="", flush=True)
        if status['status'] == 'completed':
            print(f"\n    Результат: {status['result']}")
            break

if __name__ == '__main__':
    main()
