#!/bin/bash

echo "===================================="
echo "   Instalación de entorno virtual"
echo "===================================="

# Verifica si python3.7 está disponible
if command -v python3.7 &> /dev/null; then
    PYTHON=python3.7
    echo "✅ Usando Python 3.7"
else
    PYTHON=python3
    echo "⚠️ Python 3.7 no encontrado. Usando Python por defecto: $PYTHON"
fi

# Crea entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "🔧 Creando entorno virtual..."
    $PYTHON -m venv venv
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
