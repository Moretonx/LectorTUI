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
        echo "🔧 Instalando dependencias previas para Python 3.7..."
        sudo apt update
        sudo apt install -y build-essential wget autoconf automake libtool             zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev             libreadline-dev libsqlite3-dev tk-dev liblzma-dev uuid-dev

        echo "📦 Compilando e instalando libffi..."
        wget ftp://sourceware.org/pub/libffi/libffi-3.4.2.tar.gz
        tar -xzf libffi-3.4.2.tar.gz
        cd libffi-3.4.2
        ./configure --prefix=/usr/local
        make -j$(nproc)
        sudo make install
        cd ..
        rm -rf libffi-3.4.2 libffi-3.4.2.tar.gz

        echo "📦 Compilando e instalando bzip2..."
        wget https://sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz
        tar -xzf bzip2-1.0.8.tar.gz
        cd bzip2-1.0.8
        make -f Makefile-libbz2_so
        make clean
        make
        sudo make install PREFIX=/usr/local
        cd ..
        rm -rf bzip2-1.0.8 bzip2-1.0.8.tar.gz

        echo "🐍 Descargando e instalando Python 3.7.17..."
        cd /tmp
        wget https://www.python.org/ftp/python/3.7.17/Python-3.7.17.tgz
        tar -xf Python-3.7.17.tgz
        cd Python-3.7.17
        ./configure --enable-optimizations --with-ensurepip=install
        make -j$(nproc)
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
