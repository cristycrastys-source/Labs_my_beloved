#!/usr/bin/env python3

# Импорт класса Fernet из библиотеки cryptography
# Fernet реализует симметричное шифрование AES-128 в режиме CBC
# с добавлением HMAC-SHA256 для проверки целостности
from cryptography.fernet import Fernet

# ГЕНЕРАЦИЯ КЛЮЧА
# Fernet.generate_key() создаёт случайный ключ длиной 32 байта (256 бит)
# Ключ кодируется в base64 для удобного хранения и передачи
key = Fernet.generate_key()

# СОХРАНЕНИЕ КЛЮЧА В ФАЙЛ
# Режим 'wb' (write binary) — запись в бинарном режиме
# Ключ сохраняется в байтовом виде, не в текстовом
with open("encryption_key.txt", "wb") as f:
    f.write(key)

# ВЫВОД ПОДТВЕРЖДЕНИЯ В КОНСОЛЬ
# f-строка для отображения статуса операции
print("✓ Ключ создан: encryption_key.txt")
