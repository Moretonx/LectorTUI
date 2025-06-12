#!/bin/bash

echo "===================================="
echo "   Instalación de entorno virtual"
echo "===================================="

# Verifica si Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Cancela la instalación."
    exit 1
fi

# Crea entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "🔧 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activa entorno virtual
echo "📦 Activando entorno virtual..."
source venv/bin/activate

# Instala requerimientos
if [ -f requirements.txt ]; then
    echo "📦 Instalando dependencias desde requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "⚠️ No se encontró el archivo requirements.txt"
fi

# Ejecutar la aplicación principal
echo "🚀 Ejecutando aplicación Beca-UV.py..."
python Beca-UV.py

# Al cerrar la aplicación
echo "👋 Cerrando entorno virtual"
deactivate
