import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
from tkinter import messagebox
from pymongo import MongoClient
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Función para mostrar los resultados en el Treeview
def mostrar_en_treeview(resultados, columnas, treeview):
    for item in treeview.get_children():
        treeview.delete(item)

    treeview["columns"] = columnas
    for col in columnas:
        treeview.heading(col, text=col, anchor="center")
        treeview.column(col, minwidth=100, width=120, stretch=True, anchor="center")

    for fila in resultados:
        treeview.insert("", "end", values=fila)

    ajustar_ancho_columnas(treeview)

def ajustar_ancho_columnas(treeview):
    for col in treeview["columns"]:
        max_width = max([len(str(treeview.item(item, "values")[treeview["columns"].index(col)])) for item in treeview.get_children()], default=0)
        treeview.column(col, width=max(max_width * 8, 120))

# Función para conectarse a MongoDB y mostrar los datos en el primer Treeview
def obtener_datos_mongodb():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        resultados = list(coleccion.find({}))
        if not resultados:
            messagebox.showinfo("Información", "No se encontraron datos en la colección.")
            return

        columnas = ["Mes", "Semana", "Personal", "Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]
        datos = [[fila.get(col, "") for col in columnas] for fila in resultados]

        mostrar_en_treeview(datos, columnas, tree1)

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB: {e}")

# Función para obtener los datos específicos y mostrarlos en el segundo Treeview
def obtener_datos_especificos():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        resultados = list(coleccion.find({}))
        if not resultados:
            messagebox.showinfo("Información", "No se encontraron datos en la colección.")
            return

        columnas = ["Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]
        datos = [[fila.get(col, "") for col in columnas] for fila in resultados]

        mostrar_en_treeview(datos, columnas, tree2)

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB: {e}")

# Función para agregar datos a la base de datos desde la segunda pestaña
def agregar_datos():
    campos = [campo.get() for campo in entradas]
    if all(campos):
        try:
            client = MongoClient('mongodb://localhost:27017/')
            db = client['registroMaterial']
            coleccion = db['meses']

            coleccion.insert_one({
                "Mes": campos[0],
                "Semana": campos[1],
                "Personal": campos[2],
                "Solvente": campos[3],
                "Trapos": campos[4],
                "Cartón generado": campos[5],
                "B. basura generada": campos[6],
                "Plástico generado": campos[7],
                "Plástico reciclable": campos[8]
            })
            messagebox.showinfo("Éxito", "Datos agregados correctamente.")
            for entrada in entradas:
                entrada.delete(0, tk.END)

            obtener_datos_mongodb()

        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar datos a MongoDB: {e}")
    else:
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")

# Función para buscar datos por mes
def buscar_por_mes():
    mes = entrada_busqueda.get().strip()
    if not mes:
        messagebox.showwarning("Advertencia", "Por favor, introduce un mes para buscar.")
        return

    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        resultados = list(coleccion.find({"Mes": mes}))
        if not resultados:
            messagebox.showinfo("Información", f"No se encontraron datos para el mes '{mes}'.")
            return

        columnas = ["Mes", "Semana", "Personal", "Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]
        datos = [[fila.get(col, "") for col in columnas] for fila in resultados]

        mostrar_en_treeview(datos, columnas, tree_busqueda)

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB: {e}")

# Función para actualizar datos en la base de datos
def actualizar_datos():
    mes = entrada_busqueda.get().strip()
    if not mes:
        messagebox.showwarning("Advertencia", "Por favor, introduce un mes para buscar.")
        return

    nuevos_datos = [entrada_nuevo.get() for entrada_nuevo in entradas_nuevos]  # Asegúrate de que esta lista se llame entradas_nuevos
    if any(val == "" for val in nuevos_datos):
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos de datos a modificar.")
        return

    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        # Actualizar los datos en la base de datos
        coleccion.update_one(
            {"Mes": mes},
            {"$set": {
                "Semana": nuevos_datos[0],
                "Personal": nuevos_datos[1],
                "Solvente": nuevos_datos[2],
                "Trapos": nuevos_datos[3],
                "Cartón generado": nuevos_datos[4],
                "B. basura generada": nuevos_datos[5],
                "Plástico generado": nuevos_datos[6],
                "Plástico reciclable": nuevos_datos[7]
            }}
        )
        messagebox.showinfo("Éxito", "Datos actualizados correctamente.")
        for entrada in entradas_nuevos:
            entrada.delete(0, tk.END)

        buscar_por_mes()  # Volver a cargar los datos modificados

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar los datos: {e}")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Conexión a MongoDB")
ventana.attributes("-fullscreen", True)

# Crear Notebook para las pestañas
notebook = ttk.Notebook(ventana)
notebook.pack(fill="both", expand=True)

# Primera pestaña: Mostrar datos en Treeview
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Datos de material Usado")

# Crear un PanedWindow para dividir la primera pestaña horizontalmente
paned_window = tk.PanedWindow(tab1, orient="vertical")
paned_window.pack(fill="both", expand=True)

frame_superior = tk.Frame(paned_window)
paned_window.add(frame_superior, height=ventana.winfo_screenheight() // 2)

boton_mongodb = tk.Button(frame_superior, text="Mostrar Datos", command=obtener_datos_mongodb)
boton_mongodb.pack(pady=5, anchor="w")

tree1 = ttk.Treeview(frame_superior, selectmode="browse", show="headings", height=10)
tree1.pack(pady=10, padx=5, fill="both", expand=True)

scrollbar1 = ttk.Scrollbar(frame_superior, orient="vertical", command=tree1.yview)
tree1.configure(yscroll=scrollbar1.set)
scrollbar1.pack(side="right", fill="y")

frame_inferior = tk.Frame(paned_window)
paned_window.add(frame_inferior, height=ventana.winfo_screenheight() // 2)

boton_otros_datos = tk.Button(frame_inferior, text="Datos a utilizar", command=obtener_datos_especificos)
boton_otros_datos.pack(pady=5, anchor="w")

tree2 = ttk.Treeview(frame_inferior, selectmode="browse", show="headings", height=10)
tree2.pack(pady=10, padx=5, fill="both", expand=True)

scrollbar2 = ttk.Scrollbar(frame_inferior, orient="vertical", command=tree2.yview)
tree2.configure(yscroll=scrollbar2.set)
scrollbar2.pack(side="right", fill="y")

# Segunda pestaña: Formulario para ingresar datos
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Ingresar Datos")

etiquetas = ["Mes", "Semana", "Personal", "Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]
entradas = []

for etiqueta in etiquetas:
    tk.Label(tab2, text=f"{etiqueta}:", anchor="w").pack(pady=(5, 0), padx=10, fill="x")
    entrada = tk.Entry(tab2)
    entrada.pack(pady=5, padx=10, fill="x")
    entradas.append(entrada)

boton_agregar = tk.Button(tab2, text="Agregar Datos", command=agregar_datos)
boton_agregar.pack(pady=10, padx=10)

# Tercera pestaña: Actualizar datos
tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="Actualizar Datos")

# Etiquetas de campos nuevos para actualización
etiquetas_nuevas = ["Semana", "Personal", "Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]
entradas_nuevos = []

for etiqueta in etiquetas_nuevas:
    tk.Label(tab3, text=f"{etiqueta}:", anchor="w").pack(pady=(5, 0), padx=10, fill="x")
    entrada_nuevo = tk.Entry(tab3)
    entrada_nuevo.pack(pady=5, padx=10, fill="x")
    entradas_nuevos.append(entrada_nuevo)

# Botón para actualizar los datos
boton_actualizar = tk.Button(tab3, text="Actualizar", command=actualizar_datos)
boton_actualizar.pack(pady=10, padx=10)

# Pestaña de búsqueda por mes o semana
tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="Buscar por Mes/Semana")

# Etiqueta y Combobox para seleccionar el criterio de búsqueda
criterio_label = tk.Label(tab4, text="Buscar por:")
criterio_label.pack(pady=5, padx=10, anchor="w")

criterio_combobox = ttk.Combobox(tab4, state="readonly")
criterio_combobox['values'] = ("Mes", "Semana")  # Opciones de búsqueda
criterio_combobox.current(0)  # Seleccionar "Mes" por defecto
criterio_combobox.pack(pady=5, padx=10, fill="x")

# Campo de entrada para la búsqueda
entrada_busqueda = tk.Entry(tab4)
entrada_busqueda.pack(pady=5, padx=10, fill="x")

# Función para buscar según el criterio seleccionado
def buscar_por_criterio():
    criterio = criterio_combobox.get()
    valor = entrada_busqueda.get().strip()

    if not valor:
        messagebox.showwarning("Advertencia", f"Por favor, introduce un valor para buscar por {criterio}.")
        return

    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        # Construir el filtro según el criterio seleccionado
        filtro = {criterio: valor}
        resultados = list(coleccion.find(filtro))

        if not resultados:
            messagebox.showinfo("Información", f"No se encontraron datos para {criterio} '{valor}'.")
            return

        columnas = ["Mes", "Semana", "Personal", "Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]
        datos = [[fila.get(col, "") for col in columnas] for fila in resultados]

        mostrar_en_treeview(datos, columnas, tree_busqueda)

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB: {e}")

# Botón para realizar la búsqueda
boton_buscar = tk.Button(tab4, text="Buscar", command=buscar_por_criterio)
boton_buscar.pack(pady=5, padx=10)

# Treeview reducido para mostrar los resultados de la búsqueda
tree_busqueda = ttk.Treeview(tab4, selectmode="browse", show="headings", height=5)
tree_busqueda.pack(pady=10, padx=5, fill="both", expand=True)

scrollbar_busqueda = ttk.Scrollbar(tab4, orient="vertical", command=tree_busqueda.yview)
tree_busqueda.configure(yscroll=scrollbar_busqueda.set)
scrollbar_busqueda.pack(side="right", fill="y")

# Pestaña de Gráfica de Pastel
tab5 = ttk.Frame(notebook)
notebook.add(tab5, text="Gráfica de Pastel")

grafica_label = tk.Label(tab5, text="Seleccionar columnas para gráfica de pastel:")
grafica_label.pack(pady=5, padx=10, anchor="w")

# Lista de atributos disponibles
atributos = ["Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]

# Diccionario para almacenar los estados de los checkboxes
checkbox_vars = {atributo: tk.BooleanVar() for atributo in atributos}

# Crear Checkboxes para cada atributo
for atributo in atributos:
    checkbox = tk.Checkbutton(tab5, text=atributo, variable=checkbox_vars[atributo])
    checkbox.pack(anchor="w", padx=10)

# Crear etiquetas y botones para seleccionar colores
color_labels = {}
color_buttons = {}

def seleccionar_color(atributo):
    color = colorchooser.askcolor()[1]  # Obtiene el color elegido
    if color:
        color_labels[atributo].config(bg=color)  # Cambiar el fondo de la etiqueta al color seleccionado
        color_buttons[atributo].config(bg=color)  # Cambiar el color de fondo del botón

# Añadir espacio entre checkboxes y selección de colores
espacio = tk.Label(tab5, text="")
espacio.pack(pady=10)

# Crear sección de selección de colores
for atributo in atributos:
    color_frame = ttk.Frame(tab5)
    color_frame.pack(anchor="w", padx=10, pady=5)
    
    color_label = tk.Label(color_frame, text=f"Color para {atributo}: ", width=20, anchor="w")
    color_label.pack(side="left", padx=10)
    color_labels[atributo] = color_label
    
    color_button = tk.Button(color_frame, text="Seleccionar color", command=lambda a=atributo: seleccionar_color(a))
    color_button.pack(side="left")
    color_buttons[atributo] = color_button

# Función para generar la gráfica
def generar_grafica_pastel():
    seleccionados = [atributo for atributo, var in checkbox_vars.items() if var.get()]
    
    if not seleccionados:
        messagebox.showwarning("Advertencia", "Selecciona al menos una columna para graficar.")
        return

    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        fig, axs = plt.subplots(1, len(seleccionados), figsize=(6 * len(seleccionados), 6))
        if len(seleccionados) == 1:
            axs = [axs]  # Convertir en lista si solo hay una gráfica

        for ax, criterio in zip(axs, seleccionados):
            resultados = list(coleccion.find({}, {criterio: 1, "_id": 0}))
            valores = [fila[criterio] for fila in resultados if fila.get(criterio) is not None]

            if not valores:
                ax.set_title(f"Sin datos para '{criterio}'")
                ax.axis("off")
                continue

            etiquetas = list(set(valores))
            conteos = [valores.count(etiqueta) for etiqueta in etiquetas]

            ax.pie(conteos, labels=etiquetas, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            ax.set_title(f"Distribución de {criterio}")

        canvas = FigureCanvasTkAgg(fig, master=tab5)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10, padx=10, fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB o procesar datos: {e}")

# Botón para generar gráfica usando ttk.Button
style = ttk.Style()
style.configure("TButton", padding=6, relief="flat", background="#4CAF50")

boton_grafica = ttk.Button(tab5, text="Generar Gráfica", command=generar_grafica_pastel, style="TButton")
boton_grafica.pack(pady=10, padx=10)


# Iniciar la aplicación
ventana.mainloop()
