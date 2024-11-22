import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient  # Importar MongoClient

# Función para mostrar los resultados en el Treeview dentro de la misma ventana
def mostrar_en_treeview(resultados, columnas):
    # Limpiar el Treeview antes de agregar nuevos datos
    for item in tree.get_children():
        tree.delete(item)

    # Configurar las columnas en el Treeview
    tree["columns"] = columnas
    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, minwidth=0, width=150, stretch=True)  # Permitir que las columnas se estiren

    # Agregar los datos en el Treeview
    for fila in resultados:
        tree.insert("", "end", values=fila)

    # Ajustar el ancho de las columnas según el contenido
    ajustar_ancho_columnas()

def ajustar_ancho_columnas():
    for col in tree["columns"]:
        max_width = max([len(str(item[col])) for item in tree.get_children()]) if tree.get_children() else 0
        tree.column(col, width=max(max_width * 10, 150))  # Multiplica por 10 para aumentar el tamaño de la columna

# Función para conectarse a MongoDB y mostrar los datos
def obtener_datos_mongodb():
    try:
        # Conectar a MongoDB
        client = MongoClient('mongodb://localhost:27017/')  # Cambia la URI según tu configuración
        db = client['registroMaterial']  # Cambia el nombre de la base de datos
        coleccion = db['meses']  # Cambia el nombre de la colección

        # Obtener todos los documentos de la colección
        resultados = list(coleccion.find({}))
        
        if not resultados:
            messagebox.showinfo("Información", "No se encontraron datos en la colección.")
            return
        
        # Obtener nombres de las columnas a partir de la primera fila
        columnas = list(resultados[0].keys())
        # Convertir los resultados a una lista de listas
        datos = [[fila[col] for col in columnas] for fila in resultados]

        # Mostrar los resultados en el Treeview
        mostrar_en_treeview(datos, columnas)

    except Exception as e:
        messagebox.showerror("Error", f"Error al conectarse a MongoDB: {e}")

# Función para abrir la ventana de entrada de datos
def abrir_ventana_ingreso():
    ventana_ingreso = tk.Toplevel(ventana)
    ventana_ingreso.title("Ingresar Datos")
    ventana_ingreso.geometry("400x400")

    # Entradas para cada campo
    campos = []
    for i in range(1, 6):
        tk.Label(ventana_ingreso, text=f"Campo {i}:").pack(pady=5)
        campo_entry = tk.Entry(ventana_ingreso)
        campo_entry.pack(pady=5)
        campos.append(campo_entry)

    # Botón para agregar datos a la base de datos
    tk.Button(ventana_ingreso, text="Agregar Datos", 
              command=lambda: agregar_datos([campo.get() for campo in campos], ventana_ingreso)).pack(pady=10)

# Función para agregar datos a la base de datos
def agregar_datos(campos, ventana_ingreso):
    if all(campos):  # Verificar que todos los campos estén llenos
        try:
            client = MongoClient('mongodb://localhost:27017/')  # Cambia la URI según tu configuración
            db = client['registroMaterial']  # Cambia el nombre de la base de datos
            coleccion = db['meses']  # Cambia el nombre de la colección

            # Insertar un nuevo documento con cinco campos
            coleccion.insert_one({
                "campo1": campos[0],
                "campo2": campos[1],
                "campo3": campos[2],
                "campo4": campos[3],
                "campo5": campos[4]
            })
            messagebox.showinfo("Éxito", "Datos agregados correctamente.")
            ventana_ingreso.destroy()  # Cerrar la ventana de ingreso

            # Obtener datos actualizados
            obtener_datos_mongodb()  # Actualizar el Treeview

        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar datos a MongoDB: {e}")
    else:
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Conexión a MongoDB")
ventana.geometry("800x600")  # Tamaño de la ventana para mayor visualización

# Botón para obtener datos de MongoDB
boton_mongodb = tk.Button(ventana, text="Datos de material Usado", command=obtener_datos_mongodb)
boton_mongodb.pack(pady=10, anchor="w")

# Botón para abrir la ventana de ingreso de datos
boton_ingreso = tk.Button(ventana, text="Ingresar Datos", command=abrir_ventana_ingreso)
boton_ingreso.pack(pady=10, anchor="w")

# Crear un Treeview para mostrar los datos
tree = ttk.Treeview(ventana)
tree.pack(pady=20, fill="both", expand=True)

# Scrollbar para el Treeview
scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

ventana.mainloop()




