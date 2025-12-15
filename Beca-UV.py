import tkinter
import tkinter.font as TkFont
from tkinter import PhotoImage, Toplevel, ttk
import requests
import time
import threading
import RPi.GPIO as GPIO
import MFRC522

# =========================
# CONTEXTO GLOBAL
# =========================
contexto = {
    "continue_reading": True,
    "rut": None,
    "cantidad": 0,
    "url": "",
    "imagen_uv": None,
    "imagen_desea": None,
    "font_title": None,
    "font_bold": None,
    "font_normal": None,
    "ventana": None,
}

# =========================
# UI HELPERS
# =========================
def mostrar_rechazo(titulo_texto, mensaje):
    ventanaR = Toplevel(contexto["ventana"])
    ventanaR.attributes('-zoomed', True)
    ventanaR.configure(bg="white")
    ventanaR.title("Canje fallido")

    tkinter.Label(ventanaR, image=contexto["imagen_uv"], bg="white").pack()

    tkinter.Label(ventanaR, text=titulo_texto, bg="white", font=contexto["font_title"]).pack()

    rechazar = PhotoImage(file="img/rechazar.png")
    tkinter.Label(ventanaR, image=rechazar, bg="white").pack()
    ventanaR.rechazar = rechazar

    tkinter.Label(ventanaR, text=mensaje, bg="white", font=contexto["font_normal"]).pack()
    tkinter.Button(ventanaR, text="Salir", command=lambda: (ventanaR.destroy(), volver_a_lector()), bg="red", fg="white").pack()


def mostrar_aprobacion(nombre, cantidad, on_canjear, on_salir):
    ventanaNueva = Toplevel(contexto["ventana"])
    ventanaNueva.attributes('-zoomed', True)
    ventanaNueva.configure(bg="white")
    ventanaNueva.title("Lectura Exitosa")

    tkinter.Label(ventanaNueva, image=contexto["imagen_uv"], bg="white").pack()

    tkinter.Label(ventanaNueva, text=nombre, bg="white", font=contexto["font_bold"]).pack()

    tkinter.Label(
        ventanaNueva,
        text=f"Almuerzos disponibles este mes: {cantidad}",
        bg="white",
        font=contexto["font_normal"],
    ).pack()

    tkinter.Label(ventanaNueva, image=contexto["imagen_desea"], bg="white").pack()
    tkinter.Label(ventanaNueva, text="¿Desea canjear su beca?", bg="white", font=contexto["font_normal"]).pack()

    tkinter.Button(ventanaNueva, text="Canjear beca", command=lambda: on_canjear(ventanaNueva),
                   bg="green", fg="white").pack()
    tkinter.Button(ventanaNueva, text="No", command=lambda: on_salir(ventanaNueva),
                   bg="red", fg="white").pack()


def mostrar_canje_exitoso(cantidad_restante, ventanaPadre):
    ventanaN = Toplevel(contexto["ventana"])
    ventanaN.attributes('-zoomed', True)
    ventanaN.configure(bg="white")
    ventanaN.title("Canje Exitoso")

    tkinter.Label(ventanaN, image=contexto["imagen_uv"], bg="white").pack()
    tkinter.Label(ventanaN, text="¡Beca aceptada!", bg="white", font=contexto["font_title"]).pack()

    aprobar = PhotoImage(file="img/aprobar.png")
    tkinter.Label(ventanaN, image=aprobar, bg="white").pack()
    ventanaN.aprobar = aprobar

    tkinter.Label(
        ventanaN,
        text=f"Almuerzos restantes de este mes: {cantidad_restante}",
        bg="white",
        font=contexto["font_normal"],
    ).pack()

    tkinter.Button(ventanaN, text="Salir", command=lambda: (ventanaN.destroy(), volver_a_lector()), width=20,
    height=2, bg="red", fg="white").pack()

    try:
        ventanaPadre.destroy()
    except:
        pass


# =========================
# API
# =========================
def lectura():
    casino = str(combobox.get())
    if " - " not in casino:
        mostrar_rechazo("Error", "Debe seleccionar un casino válido.")
        return

    idCasino = casino.split(" - ")[0].strip()

    rut = (contexto["rut"] or "").strip()
    if not rut or rut.lower() == "none":
        mostrar_rechazo("Error lector", "No se pudo obtener el RUT desde la tarjeta.")
        return

    contexto["url"] = f"https://becauv-production-393b.up.railway.app/api/canjes/{rut}/{idCasino}"

    try:
        response = requests.get(contexto["url"], timeout=8)
    except Exception as e:
        mostrar_rechazo("Error de red", f"No se pudo conectar: {e}")
        return
    finally:
        contexto["rut"] = None

    if response.status_code == 200:
        data = response.json()
        nombre = data.get("nombre", "Alumno")
        contexto["cantidad"] = int(data.get("cantidad", 0))

        if contexto["cantidad"] > 0:
            mostrar_aprobacion(
                nombre=nombre,
                cantidad=contexto["cantidad"],
                on_canjear=canjear,
                on_salir=lambda v: v.destroy()
            )
        else:
            mostrar_rechazo("¡Beca rechazada!", "¡ACCIÓN INVÁLIDA! Usted no posee más almuerzos este mes")

    elif response.status_code == 201:
        mostrar_rechazo("¡Beca rechazada!", "¡ACCIÓN INVÁLIDA! Usted ya canjeó su beca hoy")

    else:
        mostrar_rechazo("¡Beca rechazada!", "Usted no posee beca")


def canjear(ventanaNueva):
    canje_restante = max(contexto["cantidad"] - 1, 0)

    try:
        requests.patch(contexto["url"], timeout=8)
    except Exception as e:
        mostrar_rechazo("Error de red", f"No se pudo registrar el canje: {e}")
        try:
            ventanaNueva.destroy()
        except:
            pass
        return

    mostrar_canje_exitoso(canje_restante, ventanaNueva)


# =========================
# LECTOR RFID (HILO)
# =========================
def lector_loop(ventanaLector):
    key = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5]

    contexto["continue_reading"] = True

    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        reader = MFRC522.MFRC522()

        while contexto["continue_reading"]:
            (status, _) = reader.MFRC522_Request(reader.PICC_REQIDL)
            (status, uid) = reader.MFRC522_Anticoll()

            if isinstance(uid, (bytes, bytearray)):
                uid = list(uid)

            if status == reader.MI_OK:
                # Si tu MFRC522.py tiene SelectTag, puedes activarlo.
                if hasattr(reader, "MFRC522_SelectTag"):
                    reader.MFRC522_SelectTag(uid)

                block = 68
                st = reader.MFRC522_Auth(reader.PICC_AUTHENT1A, block, key, uid)

                if st == reader.MI_OK:
                    rut_leido = reader.MFRC522_Read(block)
                    reader.MFRC522_StopCrypto1()

                    if rut_leido is None:
                        contexto["continue_reading"] = False
                        contexto["ventana"].after(0, lambda: mostrar_rechazo("Error lector", "No se pudo leer el bloque 68"))
                        return

                    # Aquí rut_leido DEBE venir como "17760740-1"
                    rut_str = str(rut_leido).strip()
                    print("RUT leído:", rut_str)

                    contexto["rut"] = rut_str
                    contexto["continue_reading"] = False

                    contexto["ventana"].after(0, lambda: finalizar_lector_y_leer(ventanaLector))
                    return

                else:
                    reader.MFRC522_StopCrypto1()
                    contexto["continue_reading"] = False
                    contexto["ventana"].after(0, lambda: mostrar_rechazo("Error lector", f"Fallo autenticación (status={st})"))
                    return

            time.sleep(0.2)

    except Exception as e:
        contexto["continue_reading"] = False
        contexto["ventana"].after(0, lambda: mostrar_rechazo("Error lector", str(e)))

    finally:
        try:
            GPIO.cleanup()
        except:
            pass


def finalizar_lector_y_leer(ventanaLector):
    try:
        ventanaLector.destroy()
    except:
        pass
    lectura()


def iniciar_lector():
    contexto["continue_reading"] = True

    ventanaLector = Toplevel(contexto["ventana"])
    ventanaLector.attributes('-zoomed', True)
    ventanaLector.configure(bg="white")
    ventanaLector.title("Beca de Almuerzo UV")

    tkinter.Label(ventanaLector, image=contexto["imagen_uv"], bg="white").pack()
    tkinter.Label(ventanaLector, text="¡Bienvenido!", bg="white", font=contexto["font_title"]).pack()
    tkinter.Label(ventanaLector, text="Acerque su tarjeta al lector", bg="white", font=contexto["font_title"]).pack()

    lectorImage = PhotoImage(file="img/lector.png")
    tkinter.Label(ventanaLector, image=lectorImage, bg="white").pack()
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

def volver_a_lector():
    # Reinicia estado y vuelve a abrir el lector con el mismo casino ya seleccionado
    contexto["rut"] = None
    contexto["continue_reading"] = True

    # abrir lector en el hilo principal (seguro para Tk)
    contexto["ventana"].after(0, iniciar_lector)


# =========================
# UI PRINCIPAL
# =========================
contexto["ventana"] = tkinter.Tk()
contexto["ventana"].attributes('-zoomed', True)
contexto["ventana"].configure(bg="white")
contexto["ventana"].title("Beca de Almuerzo UV")

contexto["imagen_uv"] = PhotoImage(file="img/uv.png").subsample(1, 1)
tkinter.Label(contexto["ventana"], image=contexto["imagen_uv"], bg="white").pack()

contexto["font_title"] = TkFont.Font(family="Arial", size=20, weight="bold")
contexto["font_bold"] = TkFont.Font(family="Arial", size=16, weight="bold")
contexto["font_normal"] = TkFont.Font(family="Arial", size=16, weight="normal")

titulo0 = tkinter.Label(
    contexto["ventana"],
    text="Por favor seleccione el Casino donde se encuentra",
    bg="white",
    font=contexto["font_title"],
)
titulo0.pack()

contexto["imagen_desea"] = PhotoImage(file="img/desea.png").subsample(2, 2)
tkinter.Label(contexto["ventana"], image=contexto["imagen_desea"], bg="white").pack()

# Cargar casinos
try:
    response = requests.get("https://becauv-production-393b.up.railway.app/api/casinos", timeout=8)
    casinos = response.json()
except Exception as e:
    casinos = []
    mostrar_rechazo("Error de red", f"No se pudieron cargar casinos: {e}")

opciones = [f"{obj.get('id')} - {obj.get('nombre')}" for obj in casinos if "id" in obj and "nombre" in obj]

combobox = ttk.Combobox(contexto["ventana"], values=opciones, width=48, height=2,
style="Grande.TCombobox")
combobox.set("Seleccione una opción")
combobox.pack(pady=15)

boton_obtener_seleccion = tkinter.Button(
    contexto["ventana"],
    text="Seleccionar Casino",
    state="disabled",
    command=iniciar_lector,
    bg="blue",
    fg="white",
    width=20,
    height=2
)
boton_obtener_seleccion.pack(pady=5)

def habilitar_boton(event=None):
    seleccion = combobox.get()
    boton_obtener_seleccion["state"] = "normal" if seleccion != "Seleccione una opción" else "disabled"

combobox.bind("<<ComboboxSelected>>", habilitar_boton)

contexto["ventana"].mainloop()
