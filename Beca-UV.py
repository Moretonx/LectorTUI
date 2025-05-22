import tkinter
import tkinter.font as TkFont
from tkinter import PhotoImage, Toplevel, ttk
import requests
import json

def lector():
    global ventana, ventanaLector, lectorImage,cajaTexto

    ventanaLector = Toplevel(ventana)
    ventanaLector.geometry('1000x900')
    ventanaLector.configure(bg = 'white')
    ventanaLector.title('Beca de Almuerzo UV')
    tkinter.Label(ventanaLector, image=imagen, bg='white').pack()

    titulo=tkinter.Label(ventanaLector, text="¡Bienvenido!", bg="white")
    titulo.pack()
    titulo0=tkinter.Label(ventanaLector, text="Acerque su tarjeta al lector", bg="white")
    titulo0.pack()
    titulo.configure(font=letra)
    titulo0.configure(font=letra)

    lectorImage=PhotoImage(file="img/lector.png")
    tkinter.Label(ventanaLector, image=lectorImage, bg='white').pack()

    cajaTexto = tkinter.Entry(ventanaLector)
    cajaTexto.pack()
    boto=tkinter.Button(ventanaLector, text="Canjear beca", command=lectura, bg="blue", fg="white")
    boto.pack()

#Funcion que se ejecuta al leer tarjeta
def lectura():
    global ventana, ventanaNueva, imagen, cantidad, url

    #Peticion GET, se obtienen los datos del alumno
    rut = str(cajaTexto.get())
    casino = str(combobox.get())
    idCasino = casino.split(' - ')[0]
    url = 'http://192.168.94.187:4000/api/canjes/'+rut+'/'+idCasino
    response = requests.get(url)

    #Si existe el rut existe en la BD se obtienen los datos, siempre que no haya hecho un canje hoy
    if (response.status_code == 200):
        data = response.json()
        nombre = data['nombre']
        cantidad = data['cantidad']

        #Se verifica si el alumno posee almuerzos disponibles
        if (cantidad > 0):
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

            tkinter.Label(ventanaNueva, image=imagen1, bg='white').pack()

            titulo2=tkinter.Label(ventanaNueva, text="¿Desea canjear su beca?", bg="white")
            titulo2.pack()
            titulo2.configure(font=letra2)
            
            boton=tkinter.Button(ventanaNueva, text="Canjear beca", command=canjear, bg="green", fg="white")
            boton.pack()
            boton1=tkinter.Button(ventanaNueva, text="No", command=ventanaNueva.destroy, bg="red", fg="white")
            boton1.pack()
    
        #Cuando no posee almuerzos disponibles
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

            titulo5=tkinter.Label(ventanaR, text="¡ACCIÓN INVÁLIDA!" +" "+ "Usted no posee más almuerzos este mes", bg="white")
            titulo5.pack()
            titulo5.configure(font=letra2)

            boton4=tkinter.Button(ventanaR, text="Salir", command=ventanaR.destroy, bg="red", fg="white")
            boton4.pack()

    #Si ya ha hecho un canje hoy
    elif (response.status_code == 201):
        
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

        titulo5=tkinter.Label(ventanaR, text="¡ACCIÓN INVÁLIDA!"+" "+ "Usted ya canjeó su beca hoy", bg="white")
        titulo5.pack()
        titulo5.configure(font=letra2)

        boton4=tkinter.Button(ventanaR, text="Salir", command=ventanaR.destroy, bg="red", fg="white")
        boton4.pack()

    #Si el rut no existe en la BD
    else:

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

    #peticion PATCH que descuenta un almuerzo, efectuando así el canje de la beca
    requests.patch(url)
    ventanaNueva.destroy()


#------------------- Inicio del programa ------------------------#

#Se ejecuta la ventana principal 
ventana = tkinter.Tk()
ventana.geometry('1000x900')
ventana.configure(bg = 'white')
ventana.title('Beca de Almuerzo UV')

imagen=PhotoImage(file="img/uv.png")
tkinter.Label(ventana, image=imagen, bg='white').pack()
titulo0=tkinter.Label(ventana, text="Por favor selecione el Casino donde se encuentra", bg="white")
titulo0.pack()

letra=TkFont.Font(family="Arial", size=20, weight="bold")
letra1=TkFont.Font(family="Arial", size=16, weight="bold")
letra2=TkFont.Font(family="Arial", size=16, weight="normal")
titulo0.configure(font=letra)

imagen1=PhotoImage(file="img/desea.png")
tkinter.Label(ventana, image=imagen1, bg='white').pack()

def habilitar_boton(event):
    seleccion = combobox.get()
    if seleccion and seleccion != "Seleccione una opción":
        boton_obtener_seleccion['state'] = 'normal'
    else:
        boton_obtener_seleccion['state'] = 'disabled'

# Se obtienen los casinos disponibles
url = 'http://192.168.94.187:4000/api/casinos'
response = requests.get(url)
casinos = response.json()
nombres = [(objeto['id'], objeto['nombre']) for objeto in casinos]

# Crear una lista de opciones disponibles
opciones = [f"{id} - {nombre}" for id, nombre in nombres]

# Crear la entrada de texto con menú desplegable
combobox = ttk.Combobox(ventana, values=opciones, width=48)
combobox.set("Seleccione una opción")
combobox.pack(pady=10)

combobox.bind("<<ComboboxSelected>>", habilitar_boton)

boton_obtener_seleccion = tkinter.Button(ventana, text="Selecionar Casino", state='disabled', command=lector, bg="blue", fg="white")
boton_obtener_seleccion.pack(pady=5)

ventana.mainloop()