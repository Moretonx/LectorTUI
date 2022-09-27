import tkinter
import tkinter.font as TkFont
from tkinter import PhotoImage, Toplevel, messagebox
import requests


#Funcion que se ejecuta al leer tarjeta
def lectura():
    global ventana, ventanaNueva, imagen, cantidad, desea, cajaTexto

    #Peticion GET, se obtienen los datos del alumno
    url = 'http://localhost:4000/alumnos/1'
    response = requests.get(url)
    data = response.json()
    nombre = (data['nombre'])
    Rut = data['rut']
    cantidad = data['cantidad']
    rut = cajaTexto.get()

    if (rut == Rut):
        ventanaNueva = Toplevel(ventana)
        ventanaNueva.geometry('1000x900')
        ventanaNueva.configure(bg = 'white')
        ventanaNueva.title('Lectura Exitosa')
        tkinter.Label(ventanaNueva, image=imagen, bg='white').pack()


        titulo0=tkinter.Label(ventanaNueva, text=nombre, bg="white")
        titulo0.pack()
        titulo0.configure(font=letra1)
        
        titulo1=tkinter.Label(ventanaNueva, text="Almuerzos disponibles este mes: "+str(cantidad), bg="white")
        titulo1.pack()
        titulo1.configure(font=letra2)

        desea=PhotoImage(file="img/desea.png")
        tkinter.Label(ventanaNueva, image=desea, bg='white').pack()

        titulo2=tkinter.Label(ventanaNueva, text="¿Desea canjear su beca?", bg="white")
        titulo2.pack()
        titulo2.configure(font=letra2)
        
        boton=tkinter.Button(ventanaNueva, text="Canjear beca", command=canjear, bg="green", fg="white")
        boton.pack()
        boton1=tkinter.Button(ventanaNueva, text="No", command=ventanaNueva.destroy, bg="red", fg="white")
        boton1.pack()
    else:
        global rechazar

        ventanaR = Toplevel(ventana)
        ventanaR.geometry('1000x900')
        ventanaR.configure(bg = 'white')
        ventanaR.title('Canje fallido')
        tkinter.Label(ventanaR, image=imagen, bg='white').pack()

        titulo3=tkinter.Label(ventanaR, text="¡Beca rechazada!", bg='white')
        titulo3.pack()
        titulo3.configure(font=letra)

        rechazar=PhotoImage(file="img/rechazar.png")
        tkinter.Label(ventanaR, image=rechazar, bg='white').pack()

        titulo5=tkinter.Label(ventanaR, text="Usted no posee beca", bg="white")
        titulo5.pack()
        titulo5.configure(font=letra2)

        boton4=tkinter.Button(ventanaR, text="Salir", command=ventanaR.destroy, bg="red", fg="white")
        boton4.pack()

#Funcion que canjea beca del alumno
def canjear():
    global aprobar

    ventanaN = Toplevel(ventana)
    ventanaN.geometry('1000x900')
    ventanaN.configure(bg = 'white')
    ventanaN.title('Canje Exitoso')
    tkinter.Label(ventanaN, image=imagen, bg='white').pack()
    ventanaNueva.destroy()

#peticion PUT

    #messagebox.showinfo("ACCIÓN INVÁLIDA","¡Ya has canjeado tu beca hoy!")
    titulo3=tkinter.Label(ventanaN, text="¡Beca aceptada!", bg='white')
    titulo3.pack()
    titulo3.configure(font=letra)

    aprobar=PhotoImage(file="img/aprobar.png")
    tkinter.Label(ventanaN, image=aprobar, bg='white').pack()

    canje = cantidad-1
    titulo4=tkinter.Label(ventanaN, text="Almuerzos restantes de este mes: "+str(canje), bg="white")
    titulo4.pack()
    titulo4.configure(font=letra2)

    boton4=tkinter.Button(ventanaN, text="Salir", command=ventanaN.destroy, bg="red", fg="white")
    boton4.pack()

global lector
#Se ejecuta la ventana principal 
ventana = tkinter.Tk()
ventana.geometry('1000x900')
ventana.configure(bg = 'white')
ventana.title('Beca de Almuerzo UV')

imagen=PhotoImage(file="img/uv.png")
tkinter.Label(ventana, image=imagen, bg='white').pack()
titulo=tkinter.Label(ventana, text="¡Bienvenido!", bg="white")
titulo.pack()
titulo0=tkinter.Label(ventana, text="Acerque su tarjeta al lector", bg="white")
titulo0.pack()

letra=TkFont.Font(family="Arial", size=20, weight="bold")
letra1=TkFont.Font(family="Arial", size=16, weight="bold")
letra2=TkFont.Font(family="Arial", size=16, weight="normal")
titulo.configure(font=letra)
titulo0.configure(font=letra)

imagen1=PhotoImage(file="img/lector.png")
tkinter.Label(ventana, image=imagen1, bg='white').pack()

cajaTexto = tkinter.Entry(ventana)
cajaTexto.pack()
boto=tkinter.Button(ventana, text="Canjear beca", command=lectura, bg="blue", fg="white")
boto.pack()

ventana.mainloop()