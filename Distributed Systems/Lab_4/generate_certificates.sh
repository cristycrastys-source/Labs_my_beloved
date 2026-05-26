#!/bin/bash
# Прерывание выполнения скрипта при любой ошибке (set -e)
set -e

echo "=== Генерация PKI для mTLS ==="

# 1. ГЕНЕРАЦИЯ ПРИВАТНОГО КЛЮЧА ЦЕНТРА СЕРТИФИКАЦИИ (CA)
#    - 2048 бит (достаточно для учебных целей)
#    - Ключ хранится в секрете, используется только для подписи
openssl genrsa -out ca_key.pem 2048

# 2. СОЗДАНИЕ САМОПОДПИСАННОГО СЕРТИФИКАТА CA
#    - -new -x509: создание самоподписанного сертификата
#    - -days 365: срок действия 1 год
#    - -subj: информация о владельце (страна, город, организация, Common Name)
openssl req -new -x509 -days 365 -key ca_key.pem -out ca_cert.pem \
  -subj "/C=RU/ST=Moscow/L=Moscow/O=Lab4/OU=IT/CN=CA"

# 3. ГЕНЕРАЦИЯ ПРИВАТНОГО КЛЮЧА СЕРВЕРА
openssl genrsa -out server_key.pem 2048

# 4. СОЗДАНИЕ ЗАПРОСА НА СЕРТИФИКАТ (CSR) ДЛЯ СЕРВЕРА
#    - CN=localhost: сервер будет доступен по localhost
openssl req -new -key server_key.pem -out server_csr.pem \
  -subj "/C=RU/ST=Moscow/L=Moscow/O=Lab4/OU=Server/CN=localhost"

# 5. ПОДПИСАНИЕ СЕРТИФИКАТА СЕРВЕРА ЦЕНТРОМ СЕРТИФИКАЦИИ (CA)
#    - -extfile: добавление расширения SAN (Subject Alternative Name)
#    - SAN необходимо для корректной работы на localhost и 127.0.0.1
openssl x509 -req -days 365 -in server_csr.pem -CA ca_cert.pem \
  -CAkey ca_key.pem -CAcreateserial -out server_cert.pem \
  -extfile <(printf "subjectAltName=DNS:localhost,IP:127.0.0.1")

# 6. ГЕНЕРАЦИЯ ПРИВАТНОГО КЛЮЧА КЛИЕНТА
openssl genrsa -out client_key.pem 2048

# 7. СОЗДАНИЕ ЗАПРОСА НА СЕРТИФИКАТ (CSR) ДЛЯ КЛИЕНТА
#    - CN=client: идентификатор клиента
openssl req -new -key client_key.pem -out client_csr.pem \
  -subj "/C=RU/ST=Moscow/L=Moscow/O=Lab4/OU=Client/CN=client"

# 8. ПОДПИСАНИЕ СЕРТИФИКАТА КЛИЕНТА ЦЕНТРОМ СЕРТИФИКАЦИИ (CA)
openssl x509 -req -days 365 -in client_csr.pem -CA ca_cert.pem \
  -CAkey ca_key.pem -CAcreateserial -out client_cert.pem

# УДАЛЕНИЕ ВРЕМЕННЫХ ФАЙЛОВ
#    - CSR-файлы больше не нужны после подписания
#    - ca_key.srl - файл с серийными номерами выданных сертификатов
rm -f server_csr.pem client_csr.pem ca_key.srl

echo "=== Готово ==="
ls -la *.pem
