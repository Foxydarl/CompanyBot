#!/usr/bin/env bash
set -e

# Функция для проверки существования команды
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Обновляю список пакетов..."
sudo apt-get update

# Проверка и установка Python 3.12 и python3.12-venv
if ! command_exists python3.12; then
    echo "Python3.12 не найден, устанавливаю Python 3.12 и python3.12-venv..."
    sudo apt-get install -y python3.12 python3.12-venv
else
    # Проверяем, установлен ли venv (если нет, создаст ошибку)
    if ! python3.12 -m venv --help >/dev/null 2>&1; then
        echo "Пакет python3.12-venv отсутствует, устанавливаю его..."
        sudo apt-get install -y python3.12-venv
    else
        echo "Python3.12 и python3.12-venv уже установлены."
    fi
fi

# Проверка и установка Node.js и npm
if ! command_exists node; then
    echo "Node.js не найден, устанавливаю Node.js и npm..."
    sudo apt-get install -y nodejs npm
else
    echo "Node.js уже установлен."
fi

# Проверка и установка Git
if ! command_exists git; then
    echo "Git не найден, устанавливаю Git..."
    sudo apt-get install -y git
else
    echo "Git уже установлен."
fi

# Создание и активация виртуального окружения Python
if [ -d "venv" ]; then
    echo "Виртуальное окружение уже существует, удаляю его..."
    rm -rf venv
fi
echo "Создаю виртуальное окружение..."
python3.12 -m venv venv
echo "Активирую виртуальное окружение..."
source venv/bin/activate

# Установка и запуск cron
if ! command_exists cron; then
    echo "Cron не найден, устанавливаю cron..."
    sudo apt-get install -y cron
fi
echo "Включаю и запускаю сервис cron..."
sudo systemctl enable cron
sudo systemctl start cron

# Добавление cron-задачи для выполнения git pull каждую минуту
REPO_DIR="$(pwd)"
CRON_JOB="*/1 * * * * cd ${REPO_DIR} && git pull"
# Если такой записи ещё нет, добавляем её:
(crontab -l 2>/dev/null | grep -F "$CRON_JOB") || (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
echo "Cron-задача добавлена: $CRON_JOB"

# Установка Python-зависимостей
echo "Обновляю pip и устанавливаю зависимости из requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# Установка localtunnel глобально через npm (если требуется)
if ! command_exists lt; then
    echo "localtunnel не найден, устанавливаю его глобально..."
    sudo npm install -g localtunnel
else
    echo "localtunnel уже установлен."
fi

# Запуск ботов параллельно
echo "Запускаю Telegram-бот..."
python telegram2.py &
echo "Запускаю WhatsApp-бот..."
python whatsapp2.py &

echo "Оба бота запущены!"
