#!/bin/bash

echo "===================================="
echo "     Instalación de entorno virtual"
echo "===================================="

# Buscar Python 3.7 si está disponible
if command -v python3.7 &>/dev/null; then
    PYTHON=python3.7
    echo "✅ Python 3.7 encontrado."
else
    echo "⚠️  Python 3.7 no encontrado."
    echo ""
    echo "👉 Para instalar Python 3.7 fácilmente en tu Raspberry Pi, ejecuta:"
    echo ""
    echo "   sudo apt update && sudo apt install -y curl git"
    echo "   curl https://pyenv.run | bash"
    echo ""
    echo "Luego agrega esto a tu ~/.bashrc:"
    echo "   export PATH=\"\$HOME/.pyenv/bin:\$PATH\""
    echo "   eval \"\$(pyenv init -)\""
    echo "   eval \"\$(pyenv virtualenv-init -)\""
    echo ""
    echo "Aplica los cambios con:"
    echo "   source ~/.bashrc"
    echo ""
    echo "E instala Python 3.7 con:"
    echo "   pyenv install 3.7.17 && pyenv global 3.7.17"
    echo ""
    echo "Luego vuelve a ejecutar este script."
    exit 1
fi

echo "🔧 Creando entorno virtual..."
$PYTHON -m venv venv

echo "📦 Activando entorno virtual..."
source venv/bin/activate

echo "📦 Instalando dependencias desde requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🚀 Ejecutando aplicación Beca-UV.py..."
$PYTHON Beca-UV.py

echo "👋 Cerrando entorno virtual"
deactivate
