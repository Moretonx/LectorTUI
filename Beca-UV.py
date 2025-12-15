import tkinter
import tkinter.font as TkFont
from tkinter import PhotoImage, Toplevel, ttk
import requests
import time
import signal
import threading
import RPi.GPIO as GPIO
import MFRC522

# Variables globales encapsuladas en un diccionario de contexto
contexto = {
    "continue_reading": True,
    "rut": None,
    "cantidad": 0,
    "url": "",
    "imagen": None,
    "imagen1": None,
    "letra": None,
    "letra1": None,
    "letra2": None,
    "ventana": None
}

# Capture SIGINT for cleanup when the script is aborted
def end_read(sig, frame):
    contexto["continue_reading"] = False
    try:
        GPIO.cleanup()
    except:
        pass

def mostrar_rechazo(titulo_texto, mensaje):
    ventanaR = Toplevel(contexto["ventana"])
    ventanaR.geometry('1000x900')
    ventanaR.configure(bg='white')
    ventanaR.title('Canje fallido')
    tkinter.Label(ventanaR, image=contexto["imagen"], bg='white').pack()

    titulo3 = tkinter.Label(ventanaR, text=titulo_texto, bg='white')
    titulo3.pack()
    titulo3.configure(font=contexto["letra"])

    rechazar = PhotoImage(file="img/rechazar.png")
    tkinter.Label(ventanaR, image=rechazar, bg='white').pack()
    ventanaR.rechazar = rechazar

    titulo5 = tkinter.Label(ventanaR, text=mensaje, bg="white")
    titulo5.pack()
    titulo5.configure(font=contexto["letra2"])

    boton4 = tkinter.Button(ventanaR, text="Salir", command=ventanaR.destroy, bg="red", fg="white")
    boton4.pack()

def lectura():
    casino = str(combobox.get())
    idCasino = casino.split(' - ')[0]

    contexto["url"] = f'https://becauv-production-393b.up.railway.app/api/canjes/{contexto["rut"]}/{idCasino}'
    response = requests.get(contexto["url"])
    contexto["rut"] = None

    if response.status_code == 200:
        data = response.json()
        nombre = data['nombre']
        contexto["cantidad"] = data['cantidad']

        if contexto["cantidad"] > 0:
            ventanaNueva = Toplevel(contexto["ventana"])
            ventanaNueva.geometry('1000x900')
            ventanaNueva.configure(bg='white')
            ventanaNueva.title('Lectura Exitosa')
            tkinter.Label(ventanaNueva, image=contexto["imagen"], bg='white').pack()

            tkinter.Label(ventanaNueva, text=nombre, bg="white", font=contexto["letra1"]).pack()
            tkinter.Label(
                ventanaNueva,
                text=f"Almuerzos disponibles este mes: {contexto['cantidad']}",
                bg="white",
                font=contexto["letra2"]
            ).pack()
            tkinter.Label(ventanaNueva, image=contexto["imagen1"], bg='white').pack()
            tkinter.Label(ventanaNueva, text="¿Desea canjear su beca?", bg="white", font=contexto["letra2"]).pack()

            tkinter.Button(ventanaNueva, text="Canjear beca",
                           command=lambda: canjear(ventanaNueva),
                           bg="green", fg="white").pack()
            tkinter.Button(ventanaNueva, text="No", command=ventanaNueva.destroy, bg="red", fg="white").pack()
        else:
            mostrar_rechazo("¡Beca rechazada!", "¡ACCIÓN INVÁLIDA! Usted no posee más almuerzos este mes")

    elif response.status_code == 201:
        mostrar_rechazo("¡Beca rechazada!", "¡ACCIÓN INVÁLIDA! Usted ya canjeó su beca hoy")

    else:
        mostrar_rechazo("¡Beca rechazada!", "Usted no posee beca")

def lectura_desde_rut(rut_leido, ventanaLector):
    # rut_leido puede venir como lista de ints/bytes
    if isinstance(rut_leido, (list, tuple)):
        # convierte ints a chars y quita basura
        rut_str = ''.join(chr(x) for x in rut_leido if isinstance(x, int) and 32 <= x <= 126).strip()
    elif isinstance(rut_leido, (bytes, bytearray)):
        rut_str = rut_leido.decode('utf-8', errors='ignore').strip()
    else:
        rut_str = str(rut_leido).strip()

    contexto["rut"] = rut_str

    try:
        ventanaLector.destroy()
    except:
        pass

    lectura()

def canjear(ventanaNueva):
    ventanaN = Toplevel(contexto["ventana"])
    ventanaN.geometry('1000x900')
    ventanaN.configure(bg='white')
    ventanaN.title('Canje Exitoso')
    tkinter.Label(ventanaN, image=contexto["imagen"], bg='white').pack()

    tkinter.Label(ventanaN, text="¡Beca aceptada!", bg='white', font=contexto["letra"]).pack()
    aprobar = PhotoImage(file="img/aprobar.png")
    tkinter.Label(ventanaN, image=aprobar, bg='white').pack()
    ventanaN.aprobar = aprobar

    canje = contexto["cantidad"] - 1
    tkinter.Label(ventanaN, text=f"Almuerzos restantes de este mes: {canje}", bg="white", font=contexto["letra2"]).pack()

    tkinter.Button(ventanaN, text="Salir", command=ventanaN.destroy, bg="red", fg="white").pack()

    try:
        requests.patch(contexto["url"])
    except Exception as e:
        mostrar_rechazo("Error de red", f"No se pudo registrar el canje: {e}")

    ventanaNueva.destroy()

# =========================
# LECTOR RFID EN HILO
# =========================

def lector_loop(ventanaLector):
    key = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5]

    # Asegura lectura en esta sesión
    contexto["continue_reading"] = True

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    MIFAREReader = MFRC522.MFRC522()

    try:
        while contexto["continue_reading"]:
            (status, _) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            # algunas libs/devuelven bytes
            if isinstance(uid, (bytes, bytearray)):
                uid = list(uid)

            if status == MIFAREReader.MI_OK:
                #MIFAREReader.MFRC522_SelectTag(uid)

                numero = 68
                st = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, numero, key, uid)

                if st == MIFAREReader.MI_OK:
                    rut_leido = MIFAREReader.MFRC522_Read(numero)
                    MIFAREReader.MFRC522_StopCrypto1()

                    # corta loop inmediatamente para evitar doble lectura
                    contexto["continue_reading"] = False

                    # UI siempre en hilo principal
                    contexto["ventana"].after(
                        0, lambda: lectura_desde_rut(rut_leido, ventanaLector)
                    )
                    return

                else:
                    MIFAREReader.MFRC522_StopCrypto1()
                    contexto["continue_reading"] = False
                    contexto["ventana"].after(
                        0, lambda: mostrar_rechazo("¡Beca rechazada!", "Usted no posee beca")
                    )
                    return

            time.sleep(0.2)

    except Exception as e:
        contexto["continue_reading"] = False
        mensaje_error = str(e)
        contexto["ventana"].after(0, lambda: mostrar_rechazo("Error lector", mensaje_error))

    finally:
        # Cierra SPI si tu clase lo expone (en tu mfrc522.py existe Close_MFRC522)
        try:
            MIFAREReader.Close_MFRC522()
        except:
            pass

        try:
            GPIO.cleanup()
        except:
            pass

def iniciar_lector():
    # Reinicia bandera por si quedó en False por una lectura anterior
    contexto["continue_reading"] = True

    ventanaLector = Toplevel(contexto["ventana"])
    ventanaLector.geometry('1000x900')
    ventanaLector.configure(bg='white')
    ventanaLector.title('Beca de Almuerzo UV')
    tkinter.Label(ventanaLector, image=contexto["imagen"], bg='white').pack()

    tkinter.Label(ventanaLector, text="¡Bienvenido!", bg="white", font=contexto["letra"]).pack()
    tkinter.Label(ventanaLector, text="Acerque su tarjeta al lector", bg="white", font=contexto["letra"]).pack()

    lectorImage = PhotoImage(file="img/lector.png")
    tkinter.Label(ventanaLector, image=lectorImage, bg='white').pack()
    ventanaLector.lectorImage = lectorImage

    def cerrar():
        contexto["continue_reading"] = False
        try:
            GPIO.cleanup()
        except:
            pass
        ventanaLector.destroy()

    ventanaLector.protocol("WM_DELETE_WINDOW", cerrar)

    threading.Thread(target=lector_loop, args=(ventanaLector,), daemon=True).start()

# =========================
# INICIO DEL PROGRAMA (UI)
# =========================

contexto["ventana"] = tkinter.Tk()
contexto["ventana"].geometry('1000x900')
contexto["ventana"].configure(bg='white')
contexto["ventana"].title('Beca de Almuerzo UV')

contexto["imagen"] = PhotoImage(file="img/uv.png")
tkinter.Label(contexto["ventana"], image=contexto["imagen"], bg='white').pack()

titulo0 = tkinter.Label(contexto["ventana"], text="Por favor seleccione el Casino donde se encuentra", bg="white")
titulo0.pack()

contexto["letra"] = TkFont.Font(family="Arial", size=20, weight="bold")
contexto["letra1"] = TkFont.Font(family="Arial", size=16, weight="bold")
contexto["letra2"] = TkFont.Font(family="Arial", size=16, weight="normal")
titulo0.configure(font=contexto["letra"])

contexto["imagen1"] = PhotoImage(file="img/desea.png")
tkinter.Label(contexto["ventana"], image=contexto["imagen1"], bg='white').pack()

# Cargar casinos
contexto["url"] = 'https://becauv-production-393b.up.railway.app/api/casinos'
response = requests.get(contexto["url"])
casinos = response.json()
nombres = [(objeto['id'], objeto['nombre']) for objeto in casinos]
opciones = [f"{id} - {nombre}" for id, nombre in nombres]

combobox = ttk.Combobox(contexto["ventana"], values=opciones, width=48)
combobox.set("Seleccione una opción")
combobox.pack(pady=10)

def habilitar_boton(event):
    seleccion = combobox.get()
    boton_obtener_seleccion['state'] = 'normal' if seleccion != "Seleccione una opción" else 'disabled'

combobox.bind("<<ComboboxSelected>>", habilitar_boton)

boton_obtener_seleccion = tkinter.Button(
    contexto["ventana"],
    text="Seleccionar Casino",
    state='disabled',
    command=iniciar_lector,
    bg="blue",
    fg="white"
)
boton_obtener_seleccion.pack(pady=5)

contexto["ventana"].mainloop()
