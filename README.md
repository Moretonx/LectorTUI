# BecaUV-Raspberry

Autor: Francisco Moretti  
Contacto: francisco.moretti@email.com  <!-- puedes reemplazar por el real -->
Versión: 1.0  
Fecha: 2025-06-03


Este proyecto permite la interacción entre una Raspberry Pi 4 y un lector RFID-RC522 para registrar y consultar becas de alimentación mediante tarjetas NFC.

## 📦 Requisitos del sistema

- Raspberry Pi con lector MFRC522 correctamente conectado
- SPI habilitado (ver instrucciones más abajo)
- Python 3.7 o superior
- Dependencias instaladas desde `requirements.txt`
- Archivo `MFRC522.py` disponible en el mismo directorio del script o correctamente importado

## 🔧 Instalación de dependencias

Ejecuta el siguiente comando en la terminal para instalar los requerimientos del proyecto:

    pip3 install -r requirements.txt

---

## 🔌 Activar SPI en la Raspberry Pi

El lector MFRC522 se comunica a través del protocolo SPI. Debes habilitar la interfaz SPI para que el lector funcione correctamente.

### Pasos para habilitar SPI:

1. Abre la terminal de tu Raspberry Pi.
2. Ejecuta:

       sudo raspi-config

3. Selecciona: `3 Interface Options`
4. Luego: `P4 SPI`
5. Confirma con `Yes` para habilitar SPI.
6. Reinicia tu Raspberry Pi:

       sudo reboot

### Verificar si SPI está activo:

Después del reinicio, ejecuta:

    ls /dev/spidev*

Deberías ver:

    /dev/spidev0.0
    /dev/spidev0.1

Si aparecen, ¡SPI está correctamente habilitado y listo para usarse!

---

## ⚖️ Licencia

Este proyecto hace uso del archivo `MFRC522.py`, derivado del repositorio original bajo licencia **GNU Lesser General Public License v3.0 (LGPL-3.0)**.

Puedes consultar los términos completos de la licencia aquí:  
🔗 https://www.gnu.org/licenses/lgpl-3.0.html

Esto significa que puedes:
- Usar, modificar y distribuir el código
- Siempre que mantengas la licencia LGPL en las partes derivadas