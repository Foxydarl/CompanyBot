#!/usr/bin/env bash
set -e  # Прерывать выполнение при ошибке

# 1️⃣ Функция для проверки существования команды
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 📍 2️⃣ Переход в корень проекта
cd "$(dirname "$0")/.."
REPO_DIR="$(pwd)"
echo "📍 Запуск из директории: $REPO_DIR"

echo "🔄 Обновляю список пакетов..."
sudo apt-get update && sudo apt-get upgrade -y

# 🐍 3️⃣ Проверка установки Python 3.12
if ! command_exists python3.12; then
    echo "🐍 Python 3.12 не найден, устанавливаю..."
    sudo apt-get install -y python3.12 python3.12-venv
fi

PYTHON_CMD=$(which python3.12 || echo "python3")
echo "✅ Используется Python: $PYTHON_CMD"

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
$PYTHON_CMD -m venv venv
source venv/bin/activate

# 📥 7️⃣ Установка pip
pip install --upgrade pip
echo "✅ pip обновлен."

# 🔄 8️⃣ Очистка зависимостей перед установкой
pip uninstall -y googletrans httpx httpcore openai || true

# 📥 9️⃣ Установка зависимостей Python
if [ ! -f "$REPO_DIR/requirements.txt" ]; then
    echo "❌ Ошибка: Файл requirements.txt не найден в $REPO_DIR!"
    exit 1
fi
pip install -r "$REPO_DIR/requirements.txt"
echo "✅ Python-зависимости установлены."

# 🌍 🔟 Установка localtunnel через npm
if ! command_exists lt; then
    echo "📦 Устанавливаю localtunnel..."
    sudo npm install -g localtunnel
fi
echo "✅ localtunnel установлен."

# 📂 1️⃣1️⃣ Создаём папку logs (если её нет)
mkdir -p logs

# 🚀 1️⃣2️⃣ Запуск ботов в фоне с логами
echo "🚀 Запускаю Telegram-бот..."
nohup python telegram2.py > logs/telegram.log 2>&1 &

echo "🚀 Запускаю WhatsApp-бот..."
nohup python whatsapp2.py > logs/whatsapp.log 2>&1 &

echo "✅ Оба бота запущены!"

echo 'echo "API_KEY=your_api_key_here" >> .env'

