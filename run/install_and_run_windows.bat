# install_and_run.ps1

# Установка Chocolatey, если не стоит
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = "Tls12"
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Установка Python3, Node.js
choco install python --version=3.12.0 -y
choco install nodejs -y

# Установка зависимостей Python
pip install -r requirements.txt

# Установка localtunnel или чего нужно
npm install -g localtunnel

# Запуск ботов
Start-Process powershell -ArgumentList "python telegram2.py"
Start-Process powershell -ArgumentList "python whatsapp2.py"
