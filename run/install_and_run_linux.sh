#!/usr/bin/env bash
set -e

# Функция для проверки существования команды
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "Обновляю список пакетов..."
sudo apt-get update

# 1. Проверка и установка Python 3.12 (и venv)
if ! command_exists python3.12; then
    echo "Python3.12 не найден, устанавливаю Python 3.12 и python3.12-venv..."
    sudo apt-get install -y python3.12 python3.12-venv
else
    echo "Python3.12 уже установлен."
fi

# 2. Проверка и установка Node.js и npm
if ! command_exists node; then
    echo "Node.js не найден, устанавливаю Node.js и npm..."
    sudo apt-get install -y nodejs npm
else
    echo "Node.js уже установлен."
fi

# 3. Проверка и установка Git
if ! command_exists git; then
    echo "Git не найден, устанавливаю Git..."
    sudo apt-get install -y git
else
    echo "Git уже установлен."
fi

# 4. Создание и активация виртуального окружения Python (если не создано)
if [ ! -d "venv" ]; then
    echo "Создаю виртуальное окружение..."
    python3.12 -m venv venv
fi
echo "Активирую виртуальное окружение..."
source venv/bin/activate

# 5. Установка и запуск cron, если он не установлен
if ! command_exists cron; then
    echo "Cron не найден, устанавливаю cron..."
    sudo apt-get install -y cron
fi
echo "Включаю и запускаю сервис cron..."
sudo systemctl enable cron
sudo systemctl start cron

# 6. Добавление cron-задачи для выполнения git pull каждые 1 минуту
# Получаем текущую директорию (репозиторий должен быть клонирован сюда)
REPO_DIR="$(pwd)"
CRON_JOB="*/1 * * * * cd ${REPO_DIR} && git pull"
# Если такой записи ещё нет в crontab, добавляем её:
(crontab -l 2>/dev/null | grep -F "$CRON_JOB") || (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
echo "Cron-задача добавлена: $CRON_JOB"

# 7. Установка Python-зависимостей
echo "Обновляю pip и устанавливаю зависимости из requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 8. Установка localtunnel глобально через npm (если требуется)
if ! command_exists lt; then
    echo "localtunnel не найден, устанавливаю его глобально..."
    sudo npm install -g localtunnel
else
    echo "localtunnel уже установлен."
fi

# 9. Запуск ботов параллельно
echo "Запускаю Telegram-бот..."
python telegram2.py &
echo "Запускаю WhatsApp-бот..."
python whatsapp2.py &

echo "Оба бота запущены!"
