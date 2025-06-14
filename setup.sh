#!/bin/bash

# Nombre del archivo principal
MAIN_SCRIPT="Beca-UV.py"

echo "===================================="
echo "   Instalación de entorno virtual"
echo "===================================="

PYTHON_BIN="python3.7"

# Verifica si Python 3.7 está instalado
if ! command -v $PYTHON_BIN &> /dev/null; then
    echo "⚠️ Python 3.7 no encontrado."
    read -p "¿Quieres que intente instalar Python 3.7 automáticamente? (s/n): " confirmar
    if [[ "$confirmar" == "s" ]]; then
        echo "🔧 Instalando Python 3.7 (esto puede tardar más de 30 minutos)..."
        sudo apt update
        sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
            libnss3-dev libssl-dev libreadline-dev libffi-dev wget
        cd /tmp
        wget https://www.python.org/ftp/python/3.7.17/Python-3.7.17.tgz
        tar -xf Python-3.7.17.tgz
        cd Python-3.7.17
        ./configure --enable-optimizations
        make -j $(nproc)
        sudo make altinstall
        cd ~
        echo "✅ Python 3.7 instalado como python3.7"
    else
        echo "⛔ Instalación cancelada. Debes instalar Python 3.7 manualmente."
        exit 1
    fi
fi

echo "🔧 Usando Python: $PYTHON_BIN"
echo "🧪 Creando entorno virtual..."
$PYTHON_BIN -m venv venv

echo "📦 Activando entorno virtual..."
source venv/bin/activate

echo "📦 Instalando dependencias desde requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Ejecutando aplicación Beca-UV.py..."
python "$(dirname "$0")/$MAIN_SCRIPT"

echo "👋 Cerrando entorno virtual"
deactivate
