import tkinter as tk
from tkinter import simpledialog, messagebox
import RPi.GPIO as GPIO
import MFRC522
import signal
import datetime
import os
import time

reader = MFRC522.MFRC522()
continue_reading = True

def end_read(signal, frame):
    global continue_reading
    continue_reading = False
    GPIO.cleanup()

signal.signal(signal.SIGINT, end_read)

def escanear_y_autenticar(block):
    while continue_reading:
        (status, TagType) = reader.MFRC522_Request(reader.PICC_REQIDL)
        if status == reader.MI_OK:
            (status, uid) = reader.MFRC522_Anticoll()
            if status == reader.MI_OK:
                reader.MFRC522_SelectTag(uid)
                key = [0xFF] * 6
                status = reader.MFRC522_Auth(reader.PICC_AUTHENT1A, block, key, uid)
                if status == reader.MI_OK:
                    return uid
                else:
                    messagebox.showerror("Error", "Falló la autenticación.")
                    return None
    return None

def grabar_rut():
    rut = simpledialog.askstring("Grabar RUT", "Ingresa el RUT (máx 16 caracteres):")
    if not rut or len(rut) > 16:
        messagebox.showerror("Error", "RUT inválido.")
        return
    data = [ord(c) for c in rut] + [0] * (16 - len(rut))
    uid = escanear_y_autenticar(8)
    if uid:
        reader.MFRC522_Write(8, data)
        reader.MFRC522_StopCrypto1()
        log_action(f"RUT '{rut}' grabado en el bloque 8")
        messagebox.showinfo("Éxito", f"RUT '{rut}' grabado en la tarjeta.")

def leer_rut():
    uid = escanear_y_autenticar(8)
    if uid:
        data = reader.MFRC522_Read(8)
        rut = ''.join([chr(b) for b in data if b != 0])
        reader.MFRC522_StopCrypto1()
        log_action(f"RUT leído: {rut}")
        messagebox.showinfo("RUT leído", f"Contenido: {rut}")

def borrar_bloque():
    bloque = simpledialog.askinteger("Borrar bloque", "Número de bloque (0–63):", minvalue=0, maxvalue=63)
    if bloque is None:
        return
    if bloque % 4 == 3:
        messagebox.showwarning("Advertencia", "Este es un bloque de control. No se recomienda borrarlo.")
        return
    uid = escanear_y_autenticar(bloque)
    if uid:
        reader.MFRC522_Write(bloque, [0] * 16)
        reader.MFRC522_StopCrypto1()
        log_action(f"Bloque {bloque} borrado")
        messagebox.showinfo("Éxito", f"Bloque {bloque} borrado correctamente.")

# Interfaz principal
root = tk.Tk()
root.title("Herramientas RFID - MFRC522")
root.geometry("300x250")

tk.Label(root, text="Seleccione una acción:", font=("Arial", 14)).pack(pady=10)
tk.Button(root, text="Grabar RUT", command=grabar_rut, bg="green", fg="white").pack(pady=5)
tk.Button(root, text="Leer RUT", command=leer_rut, bg="blue", fg="white").pack(pady=5)
tk.Button(root, text="Borrar bloque", command=borrar_bloque, bg="red", fg="white").pack(pady=5)

tk.Button(root, text="Ver historial", command=ver_log, bg="gray", fg="white").pack(pady=5)
tk.Button(root, text="Limpiar historial", command=limpiar_log, bg="orange", fg="black").pack(pady=5)
tk.Button(root, text="Exportar historial a PDF", command=exportar_log_pdf, bg="purple", fg="white").pack(pady=5)
tk.Button(root, text="Salir", command=root.destroy).pack(pady=20)


root.mainloop()


def log_action(text):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logline = f"[{timestamp}] {text}\n"
    with open("rfid_log.txt", "a") as logfile:
        logfile.write(logline)

def ver_log():
    if not os.path.exists("rfid_log.txt"):
        messagebox.showinfo("Historial", "No hay historial disponible.")
        return
    with open("rfid_log.txt", "r") as f:
        contenido = f.read()
    ventana = tk.Toplevel()
    ventana.title("Historial de acciones")
    ventana.geometry("500x400")
    text = tk.Text(ventana, wrap="word")
    text.insert("1.0", contenido)
    text.config(state="disabled")
    text.pack(expand=True, fill="both")

def limpiar_log():
    if os.path.exists("rfid_log.txt"):
        os.remove("rfid_log.txt")
        messagebox.showinfo("Historial", "Historial eliminado.")
    else:
        messagebox.showinfo("Historial", "No hay historial para eliminar.")

def exportar_log_pdf():
    if not os.path.exists("rfid_log.txt"):
        messagebox.showinfo("Exportar", "No hay historial para exportar.")
        return
    from fpdf import FPDF
    import datetime

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt="Historial RFID - Exportado el " + fecha, ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=12)
    with open("rfid_log.txt", "r") as f:
        for line in f:
            pdf.cell(200, 10, txt=line.strip(), ln=True)

    nombre_archivo = f"rfid_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(nombre_archivo)
    messagebox.showinfo("Exportar", f"Historial exportado como '{nombre_archivo}'.")
