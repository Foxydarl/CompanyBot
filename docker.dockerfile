# Базовый образ с Python 3.12 (Debian/Ubuntu slim)
FROM python:3.12-slim

# Установка Node.js и npm (через apt)
RUN apt-get update && apt-get install -y nodejs npm

# (Если нужно) Установка localtunnel или других npm-пакетов
RUN npm install -g localtunnel

# Создадим рабочую папку внутри контейнера
WORKDIR /app

# Скопируем список Python-зависимостей
COPY requirements.txt ./

# Установим зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем ВСЁ из текущей папки проекта в /app
COPY . .

# Если WhatsApp-бот (Flask) слушает порт 5000, «декларируем» его
EXPOSE 5000

# По умолчанию запускаем два скрипта параллельно
# Если один из них — Flask, он будет на 5000-м порту
CMD ["sh", "-c", "python telegram2.py & python whatsapp2.py"]
