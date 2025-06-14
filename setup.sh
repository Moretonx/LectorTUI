#!/bin/bash

echo "===================================="
echo "   Instalación de entorno virtual"
echo "===================================="

# Verificar si python3.7 está instalado
if command -v python3.7 &>/dev/null; then
    PYTHON_BIN=python3.7
    echo "✅ Python 3.7 encontrado."
else
    echo "⚠️ Python 3.7 no encontrado."
    echo "⏬ Instalando Python 3.7 desde fuente..."

    sudo apt update
    sudo apt install -y wget build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
        libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev

    wget https://www.python.org/ftp/python/3.7.17/Python-3.7.17.tgz
    tar -xf Python-3.7.17.tgz
    cd Python-3.7.17
    ./configure --enable-optimizations
    make -j$(nproc)
    sudo make altinstall
    cd ..
    rm -rf Python-3.7.17 Python-3.7.17.tgz

    PYTHON_BIN=python3.7
fi

echo "🔧 Creando entorno virtual..."
$PYTHON_BIN -m venv venv

echo "📦 Activando entorno virtual..."
source venv/bin/activate

echo "📦 Instalando dependencias desde requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Ejecutando aplicación Beca-UV.py..."
$PYTHON_BIN App-RFID.py

echo "👋 Cerrando entorno virtual"
deactivate
