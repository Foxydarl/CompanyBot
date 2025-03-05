#!/usr/bin/env bash

# 1. Установка Python 3.12 + Node + npm (пример для Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv nodejs npm

# 2. Создать виртуальное окружение Python (по желанию)
python3.12 -m venv venv
source venv/bin/activate

# 3. Установить зависимости из requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

# 4. Установить глобально localtunnel (если нужно)
sudo npm install -g localtunnel

# 5. Запустить скрипты
#   Если хотите оба параллельно:
python telegram.py &
python whatsapp.py

echo "Both bots are running now!"
