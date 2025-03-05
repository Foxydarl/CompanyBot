# install_and_run.ps1

# Установка политики исполнения для текущего процесса
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

# Функция для проверки существования команды (с одобренным глаголом Test)
function Test-CommandExists {
    param(
        [Parameter(Mandatory=$true)]
        [string]$CommandName
    )
    return ($null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue))
}

# Проверка и установка Chocolatey, если не установлен
if (-not (Test-CommandExists choco)) {
    Write-Host "Chocolatey не найден, устанавливаю Chocolatey..."
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
} else {
    Write-Host "Chocolatey уже установлен."
}

# Проверка и установка Git, если не установлен
if (-not (Test-CommandExists git)) {
    Write-Host "Git не найден, устанавливаю Git через Chocolatey..."
    choco install git -y
} else {
    Write-Host "Git уже установлен."
}

# Проверка и установка Python, если не установлен
if (-not (Test-CommandExists python)) {
    Write-Host "Python не найден, устанавливаю Python 3.12 через Chocolatey..."
    choco install python --version=3.12.0 -y
} else {
    Write-Host "Python уже установлен."
}

# Проверка и установка Node.js, если не установлен
if (-not (Test-CommandExists node)) {
    Write-Host "Node.js не найден, устанавливаю Node.js через Chocolatey..."
    choco install nodejs -y
} else {
    Write-Host "Node.js уже установлен."
}

# Выполняем начальный git pull для обновления репозитория
Write-Host "Выполняю начальный git pull..."
git pull

# Устанавливаем зависимости Python из requirements.txt
Write-Host "Устанавливаю Python-зависимости из requirements.txt..."
pip install -r requirements.txt

# Устанавливаем localtunnel глобально через npm
Write-Host "Устанавливаю localtunnel глобально..."
npm install -g localtunnel

# Создаём задачу планировщика (Task Scheduler) для выполнения git pull каждую минуту
$repoDir = (Get-Location).Path
$taskName = "GitPullTask"

# Формируем команду для выполнения git pull в репозитории:
# powershell.exe -NoProfile -Command "cd 'C:\Path\To\Repo'; git pull"
$action = "powershell.exe -NoProfile -Command `"cd '$repoDir'; git pull`""

# Удаляем задачу с таким именем, если она уже существует
schtasks /delete /tn $taskName /f | Out-Null

Write-Host "Создаю задачу планировщика для git pull каждые 1 минуту..."
schtasks /create /sc minute /mo 1 /tn $taskName /tr $action /ru "SYSTEM"

# Запускаем ботов
Write-Host "Запускаю Telegram-бот..."
Start-Process powershell -ArgumentList "python telegram2.py"

Write-Host "Запускаю WhatsApp-бот..."
Start-Process powershell -ArgumentList "python whatsapp2.py"

Write-Host "Установка и запуск завершены."
