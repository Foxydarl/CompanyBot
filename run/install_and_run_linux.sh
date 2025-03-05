#!/usr/bin/env bash
set -e  # Прерывать выполнение при ошибке

# 🛠 1️⃣ Функция для проверки существования команды
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 📍 2️⃣ Переход в корень проекта
cd "$(dirname "$0")/.."
REPO_DIR="$(pwd)"
echo "📍 Запуск из директории: $REPO_DIR"

echo "🔄 Обновляю список пакетов..."
sudo apt-get update && sudo apt-get upgrade -y

# 🐍 3️⃣ Установка Python 3.12 и python3.12-venv
if ! command_exists python3.12; then
    echo "🐍 Python 3.12 не найден, устанавливаю..."
    sudo apt-get install -y python3.12 python3.12-venv
fi

# Проверка и установка python3.12-venv (если нет)
if ! python3.12 -m venv --help >/dev/null 2>&1; then
    echo "📦 Устанавливаю python3.12-venv..."
    sudo apt-get install -y python3.12-venv
fi
echo "✅ Python 3.12 и venv установлены."

# 📦 4️⃣ Установка Node.js и npm
if ! command_exists node; then
    echo "📦 Node.js не найден, устанавливаю..."
    sudo apt-get install -y nodejs npm
fi
echo "✅ Node.js установлен."

# 🔄 5️⃣ Установка Git
if ! command_exists git; then
    echo "📦 Git не найден, устанавливаю..."
    sudo apt-get install -y git
fi
echo "✅ Git установлен."

# 🧹 6️⃣ Создание и активация виртуального окружения Python
if [ -d "venv" ]; then
    echo "🧹 Виртуальное окружение уже существует, удаляю..."
    rm -rf venv
fi
echo "🌱 Создаю новое виртуальное окружение..."
python3.12 -m venv venv
source venv/bin/activate

# 📥 7️⃣ Установка pip внутри venv (если нет)
if ! command_exists pip; then
    echo "📥 Устанавливаю pip в виртуальное окружение..."
    curl -s https://bootstrap.pypa.io/get-pip.py | python3
fi
echo "✅ pip установлен."

# 🔄 8️⃣ Установка и запуск Cron (если не установлен)
if ! command_exists cron; then
    echo "📦 Cron не найден, устанавливаю..."
    sudo apt-get install -y cron
fi
echo "✅ Cron установлен."
sudo systemctl enable cron
sudo systemctl start cron
echo "🚀 Cron запущен."

# 🔄 9️⃣ Настройка Cron-задачи для git pull
CRON_JOB="*/1 * * * * cd ${REPO_DIR} && git pull"
# Добавляем задачу, если её нет
(crontab -l 2>/dev/null | grep -F "$CRON_JOB") || (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
echo "✅ Cron-задача добавлена: git pull каждую минуту."

# 📥 🔟 Установка зависимостей Python
if [ ! -f "$REPO_DIR/requirements.txt" ]; then
    echo "❌ Ошибка: Файл requirements.txt не найден в $REPO_DIR!"
    exit 1
fi

echo "📥 Устанавливаю зависимости Python..."
pip install --upgrade pip
pip install -r "$REPO_DIR/requirements.txt"
echo "✅ Python-зависимости установлены."

# 🌍 1️⃣1️⃣ Установка localtunnel через npm (если требуется)
if ! command_exists lt; then
    echo "📦 Устанавливаю localtunnel..."
    sudo npm install -g localtunnel
fi
echo "✅ localtunnel установлен."

# 🚀 1️⃣2️⃣ Запуск ботов в фоне с логами
echo "🚀 Запускаю Telegram-бот..."
nohup python telegram2.py > logs/telegram.log 2>&1 &
echo "🚀 Запускаю WhatsApp-бот..."
nohup python whatsapp2.py > logs/whatsapp.log 2>&1 &
echo "✅ Оба бота запущены!"

echo "🎉 Установка и запуск завершены!"
