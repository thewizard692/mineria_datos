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
                "Mes": nuevos_datos[0],
                "Semana": nuevos_datos[1],
                "Personal": nuevos_datos[2],
                "Solvente": nuevos_datos[3],
                "Trapos": nuevos_datos[4],
                "Cartón generado": nuevos_datos[5],
                "B. basura generada": nuevos_datos[6],
                "Plástico generado": nuevos_datos[7],
                "Plástico reciclable": nuevos_datos[8]
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
etiquetas_nuevas = ["Mes", "Semana", "Personal", "Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]
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

# Contenedor principal con diseño de grid
contenedor_principal = ttk.Frame(tab5)
contenedor_principal.pack(fill="both", expand=True, padx=10, pady=10)

# Columna izquierda: Selección de datos y colores
seleccion_frame = ttk.Frame(contenedor_principal)
seleccion_frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

grafica_label = tk.Label(seleccion_frame, text="Seleccionar columnas para gráfica de pastel:")
grafica_label.pack(anchor="w")

# Lista de atributos disponibles
atributos = ["Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]

# Diccionario para almacenar los estados de los checkboxes
checkbox_vars = {atributo: tk.BooleanVar() for atributo in atributos}

# Crear Checkboxes para cada atributo
for atributo in atributos:
    checkbox = tk.Checkbutton(seleccion_frame, text=atributo, variable=checkbox_vars[atributo])
    checkbox.pack(anchor="w")

# Añadir espacio entre checkboxes y selección de colores
espacio = tk.Label(seleccion_frame, text="")
espacio.pack(pady=10)

# Crear etiquetas y botones para seleccionar colores
color_labels = {}
color_buttons = {}

def seleccionar_color(atributo):
    color = colorchooser.askcolor()[1]  # Obtiene el color elegido
    if color:
        color_labels[atributo].config(bg=color)  # Cambiar el fondo de la etiqueta al color seleccionado
        color_buttons[atributo].config(bg=color)  # Cambiar el color de fondo del botón

# Crear sección de selección de colores
for atributo in atributos:
    color_frame = ttk.Frame(seleccion_frame)
    color_frame.pack(anchor="w", pady=5)
    
    color_label = tk.Label(color_frame, text=f"Color para {atributo}: ", width=20, anchor="w")
    color_label.pack(side="left", padx=5)
    color_labels[atributo] = color_label
    
    color_button = tk.Button(color_frame, text="Seleccionar color", command=lambda a=atributo: seleccionar_color(a))
    color_button.pack(side="left")
    color_buttons[atributo] = color_button

# Botones para generar y reiniciar gráfica
boton_grafica = ttk.Button(seleccion_frame, text="Generar Gráfica", command=lambda: generar_grafica_pastel())
boton_grafica.pack(pady=10, padx=5, anchor="center")

boton_reiniciar = ttk.Button(seleccion_frame, text="Reiniciar Gráfica", command=lambda: reiniciar_grafica())
boton_reiniciar.pack(pady=5, padx=5, anchor="center")

# Columna derecha: Contenedor de la gráfica
grafica_frame = ttk.LabelFrame(contenedor_principal, text="Visualización de Gráfica", padding=10)
grafica_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
contenedor_principal.columnconfigure(1, weight=1)
contenedor_principal.rowconfigure(0, weight=1)

# Función para generar la gráfica
def generar_grafica_pastel():
    for widget in grafica_frame.winfo_children():
        widget.destroy()

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
            axs = [axs]

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

        canvas = FigureCanvasTkAgg(fig, master=grafica_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB o procesar datos: {e}")

# Función para reiniciar la gráfica
def reiniciar_grafica():
    for widget in grafica_frame.winfo_children():
        widget.destroy()
    messagebox.showinfo("Reinicio", "La gráfica ha sido reiniciada.")


# Pestaña de Ojiva Normal
tab6_normal = ttk.Frame(notebook)
notebook.add(tab6_normal, text="Ojiva")

# Etiqueta para instrucciones de Ojiva Normal
ojiva_label_normal = tk.Label(tab6_normal, text="Selecciona un atributo para generar la ojiva:")
ojiva_label_normal.pack(pady=5, padx=10, anchor="w")

# Combobox para seleccionar el atributo en Ojiva Normal
atributo_combobox_normal = ttk.Combobox(tab6_normal, state="readonly")
atributo_combobox_normal['values'] = ["Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]
atributo_combobox_normal.current(0)
atributo_combobox_normal.pack(pady=5, padx=10, fill="x")

# Frame para la gráfica de Ojiva Normal
ojiva_frame_normal = ttk.LabelFrame(tab6_normal, text="Visualización de Ojiva", padding=10)
ojiva_frame_normal.pack(pady=20, padx=10, fill="both", expand=True)

# Función para generar la ojiva normal
def generar_ojiva():
    for widget in ojiva_frame_normal.winfo_children():
        widget.destroy()

    atributo = atributo_combobox_normal.get()

    if not atributo:
        messagebox.showwarning("Advertencia", "Selecciona un atributo para graficar.")
        return

    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        resultados = list(coleccion.find({}, {atributo: 1, "_id": 0}))
        valores = [fila[atributo] for fila in resultados if fila.get(atributo) is not None]

        if not valores:
            messagebox.showinfo("Información", f"No hay datos para el atributo '{atributo}'.")
            return

        valores = sorted(map(float, valores))
        frecuencias_acumuladas = [sum(valores[:i+1]) for i in range(len(valores))]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(valores, frecuencias_acumuladas, marker='o', linestyle='-', color='b')
        ax.set_title(f"Ojiva de {atributo}")
        ax.set_xlabel("Valores")
        ax.set_ylabel("Frecuencia Acumulada")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=ojiva_frame_normal)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB o procesar datos: {e}")

# Botones para Ojiva Normal
boton_ojiva_normal = ttk.Button(tab6_normal, text="Generar Ojiva", command=generar_ojiva)
boton_ojiva_normal.pack(pady=10, padx=10)

def reiniciar_ojiva():
    for widget in ojiva_frame_normal.winfo_children():
        widget.destroy()
    messagebox.showinfo("Reinicio", "La ojiva ha sido reiniciada.")

boton_reiniciar_ojiva_normal = ttk.Button(tab6_normal, text="Reiniciar Ojiva", command=reiniciar_ojiva)
boton_reiniciar_ojiva_normal.pack(pady=10, padx=10)

# Pestaña de Ojiva Menos
tab6_menos = ttk.Frame(notebook)
notebook.add(tab6_menos, text="Ojiva Menos")

# Etiqueta para instrucciones de Ojiva Menos
ojiva_label_menos = tk.Label(tab6_menos, text="Selecciona un atributo para generar la ojiva menos:")
ojiva_label_menos.pack(pady=5, padx=10, anchor="w")

# Combobox para seleccionar el atributo en Ojiva Menos
atributo_combobox_menos = ttk.Combobox(tab6_menos, state="readonly")
atributo_combobox_menos['values'] = ["Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]
atributo_combobox_menos.current(0)
atributo_combobox_menos.pack(pady=5, padx=10, fill="x")

# Frame para la gráfica de Ojiva Menos
ojiva_frame_menos = ttk.LabelFrame(tab6_menos, text="Visualización de Ojiva Menos", padding=10)
ojiva_frame_menos.pack(pady=20, padx=10, fill="both", expand=True)

# Función para generar la ojiva menos
def generar_ojiva_menos():
    for widget in ojiva_frame_menos.winfo_children():
        widget.destroy()

    atributo = atributo_combobox_menos.get()

    if not atributo:
        messagebox.showwarning("Advertencia", "Selecciona un atributo para graficar.")
        return

    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        resultados = list(coleccion.find({}, {atributo: 1, "_id": 0}))
        valores = [fila[atributo] for fila in resultados if fila.get(atributo) is not None]

        if not valores:
            messagebox.showinfo("Información", f"No hay datos para el atributo '{atributo}'.")
            return

        valores = sorted(map(float, valores))
        total = sum(valores)
        frecuencias_acumuladas_menos = [total - sum(valores[:i]) for i in range(len(valores))]

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(valores, frecuencias_acumuladas_menos, marker='o', linestyle='-', color='r')
        ax.set_title(f"Ojiva Menos de {atributo}")
        ax.set_xlabel("Valores")
        ax.set_ylabel("Frecuencia Acumulada Inversa")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=ojiva_frame_menos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB o procesar datos: {e}")

# Botones para Ojiva Menos
boton_ojiva_menos = ttk.Button(tab6_menos, text="Generar Ojiva Menos", command=generar_ojiva_menos)
boton_ojiva_menos.pack(pady=10, padx=10)

def reiniciar_ojiva_menos():
    for widget in ojiva_frame_menos.winfo_children():
        widget.destroy()
    messagebox.showinfo("Reinicio", "La ojiva menos ha sido reiniciada.")

boton_reiniciar_ojiva_menos = ttk.Button(tab6_menos, text="Reiniciar Ojiva Menos", command=reiniciar_ojiva_menos)
boton_reiniciar_ojiva_menos.pack(pady=10, padx=10)

# Pestaña de Histograma
tab6_histograma = ttk.Frame(notebook)
notebook.add(tab6_histograma, text="Histograma")

# Etiqueta para instrucciones de Histograma
histograma_label = tk.Label(tab6_histograma, text="Selecciona un atributo para generar el histograma:")
histograma_label.pack(pady=5, padx=10, anchor="w")

# Combobox para seleccionar el atributo en Histograma
atributo_combobox_histograma = ttk.Combobox(tab6_histograma, state="readonly")
atributo_combobox_histograma['values'] = ["Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]
atributo_combobox_histograma.current(0)
atributo_combobox_histograma.pack(pady=5, padx=10, fill="x")

# Frame para la gráfica de Histograma
histograma_frame = ttk.LabelFrame(tab6_histograma, text="Visualización de Histograma", padding=10)
histograma_frame.pack(pady=20, padx=10, fill="both", expand=True)

# Función para generar el histograma
def generar_histograma():
    for widget in histograma_frame.winfo_children():
        widget.destroy()

    atributo = atributo_combobox_histograma.get()

    if not atributo:
        messagebox.showwarning("Advertencia", "Selecciona un atributo para graficar.")
        return

    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        resultados = list(coleccion.find({}, {atributo: 1, "_id": 0}))
        valores = [fila[atributo] for fila in resultados if fila.get(atributo) is not None]

        if not valores:
            messagebox.showinfo("Información", f"No hay datos para el atributo '{atributo}'.")
            return

        valores = list(map(float, valores))

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(valores, bins=10, color='green', alpha=0.7, rwidth=0.85)
        ax.set_title(f"Histograma de {atributo}")
        ax.set_xlabel("Valores")
        ax.set_ylabel("Frecuencia")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=histograma_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB o procesar datos: {e}")

# Botones para Histograma
boton_histograma = ttk.Button(tab6_histograma, text="Generar Histograma", command=generar_histograma)
boton_histograma.pack(pady=10, padx=10)

def reiniciar_histograma():
    for widget in histograma_frame.winfo_children():
        widget.destroy()
    messagebox.showinfo("Reinicio", "El histograma ha sido reiniciado.")

boton_reiniciar_histograma = ttk.Button(tab6_histograma, text="Reiniciar Histograma", command=reiniciar_histograma)
boton_reiniciar_histograma.pack(pady=10, padx=10)

# Pestaña de Cajas y Bigotes
tab6_cajas = ttk.Frame(notebook)
notebook.add(tab6_cajas, text="Cajas y Bigotes")

# Etiqueta para instrucciones de Cajas y Bigotes
cajas_label = tk.Label(tab6_cajas, text="Selecciona los atributos para generar la gráfica de Cajas y Bigotes:")
cajas_label.pack(pady=5, padx=10, anchor="w")

# Frame para las opciones de selección de datos
seleccion_frame = ttk.Frame(tab6_cajas)
seleccion_frame.pack(pady=5, padx=10, fill="x")

# Definir los atributos disponibles en la base de datos
atributos = ["Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]

# Lista para almacenar los atributos seleccionados
atributos_seleccionados = []

# Crear checkbuttons de selección de datos dispuestos horizontalmente
def actualizar_seleccion():
    atributos_seleccionados.clear()
    for var, atributo in zip(atributo_variables, atributos):
        if var.get() == 1:
            atributos_seleccionados.append(atributo)

atributo_variables = []
for i, atributo in enumerate(atributos):
    var = tk.IntVar()
    checkbutton = tk.Checkbutton(seleccion_frame, text=atributo, variable=var, command=actualizar_seleccion)
    checkbutton.grid(row=0, column=i, padx=5, pady=5)  # Distribución horizontal
    atributo_variables.append(var)

# Frame para la gráfica de Cajas y Bigotes
cajas_frame = ttk.LabelFrame(tab6_cajas, text="Visualización de Cajas y Bigotes", padding=10)
cajas_frame.pack(pady=20, padx=10, fill="both", expand=True)

# Frame para mostrar estadísticas (ajustado con menor altura)
estadisticas_frame = ttk.LabelFrame(tab6_cajas, text="Estadísticas", padding=10)
estadisticas_frame.pack(pady=5, padx=10, fill="x", expand=False)  # Expand=False para reducir altura

# Función para generar la gráfica de Cajas y Bigotes con estadísticas
def generar_cajas_bigotes():
    for widget in cajas_frame.winfo_children():
        widget.destroy()
    for widget in estadisticas_frame.winfo_children():
        widget.destroy()

    if not atributos_seleccionados:
        messagebox.showwarning("Advertencia", "Selecciona al menos un atributo para graficar.")
        return

    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        datos = []
        etiquetas = []

        # Obtener los valores de los atributos seleccionados
        for atributo in atributos_seleccionados:
            resultados = list(coleccion.find({}, {atributo: 1, "_id": 0}))
            valores = [fila[atributo] for fila in resultados if fila.get(atributo) is not None]

            if not valores:
                messagebox.showinfo("Información", f"No hay datos para el atributo '{atributo}'.")
                return

            valores = list(map(float, valores))
            datos.append(valores)
            etiquetas.append(atributo)

        # Crear la gráfica de Cajas y Bigotes
        fig, ax = plt.subplots(figsize=(6, 4))
        bp = ax.boxplot(datos, patch_artist=True, boxprops=dict(facecolor="#cce7ff", color="#1f77b4"))
        ax.set_title("Cajas y Bigotes")
        ax.set_ylabel("Valores")
        ax.set_xlabel("Atributos")
        ax.set_xticklabels(etiquetas)
        ax.grid(True)

        # Mostrar la gráfica en la interfaz
        canvas = FigureCanvasTkAgg(fig, master=cajas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

       # Calcular y mostrar estadísticas (mediana y valores externos)
        for i, (valores, box) in enumerate(zip(datos, bp['medians'])):
            mediana = box.get_ydata()[0]  # Mediana
            valores_externos = [outlier.get_ydata()[0] for outlier in bp['fliers'] if len(outlier.get_ydata()) > 0]
            
            # Mostrar estadísticas de manera más compacta
            stats_label = tk.Label(estadisticas_frame, text=f"{etiquetas[i]} - Mediana: {mediana:.2f}, "
                                                             f"Externos: {', '.join(map(str, valores_externos)) if valores_externos else 'Ninguno'}",
                                    anchor="w", justify="left", wraplength=400)
            stats_label.pack(anchor="w")

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB o procesar datos: {e}")

# Botón para generar la gráfica de Cajas y Bigotes
boton_cajas = ttk.Button(tab6_cajas, text="Generar Cajas y Bigotes", command=generar_cajas_bigotes)
boton_cajas.pack(pady=10, padx=10)

# Función para reiniciar la gráfica de Cajas y Bigotes
def reiniciar_cajas_bigotes():
    for widget in cajas_frame.winfo_children():
        widget.destroy()
    for widget in estadisticas_frame.winfo_children():
        widget.destroy()
    messagebox.showinfo("Reinicio", "La gráfica y estadísticas de Cajas y Bigotes han sido reiniciadas.")

# Botón para reiniciar la gráfica
boton_reiniciar_cajas = ttk.Button(tab6_cajas, text="Reiniciar Cajas y Bigotes", command=reiniciar_cajas_bigotes)
boton_reiniciar_cajas.pack(pady=10, padx=10)

# Crear un frame específico para las estadísticas
estadisticas_frame = ttk.LabelFrame(contenedor_principal, text="Estadísticas de Datos", padding=10)
estadisticas_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

# Configurar el layout del contenedor principal para expansión
contenedor_principal.rowconfigure(0, weight=1)  # Primer fila (gráficas y selección)
contenedor_principal.rowconfigure(1, weight=0)  # Segunda fila (estadísticas)
contenedor_principal.columnconfigure(0, weight=1)
contenedor_principal.columnconfigure(1, weight=1)

# Función para calcular la suma y mostrar los meses con valores más altos
def calcular_suma_y_top_meses():
    for widget in estadisticas_frame.winfo_children():
        widget.destroy()  # Limpia el contenido previo del frame de estadísticas

    seleccionados = [atributo for atributo, var in checkbox_vars.items() if var.get()]
    if not seleccionados:
        messagebox.showwarning("Advertencia", "Selecciona al menos una columna para calcular estadísticas.")
        return

    try:
        # Conexión a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        # Diccionario para almacenar la suma por mes
        resultados_totales = {}

        # Iterar sobre los atributos seleccionados
        for atributo in seleccionados:
            resultados = list(coleccion.find({}, {atributo: 1, "Mes": 1, "_id": 0}))
            for fila in resultados:
                mes = fila.get("Mes")
                valor = fila.get(atributo)
                if mes and valor is not None:
                    resultados_totales[mes] = resultados_totales.get(mes, 0) + valor

        # Ordenar los meses por valores totales descendentes
        meses_ordenados = sorted(resultados_totales.items(), key=lambda x: x[1], reverse=True)

        # Mostrar los resultados en el apartado de estadísticas
        ttk.Label(estadisticas_frame, text="Meses con valores más altos:", font=("Arial", 10, "bold")).pack(anchor="w", pady=5)

        for mes, suma in meses_ordenados[:5]:  # Mostrar los 5 meses con valores más altos
            ttk.Label(estadisticas_frame, text=f"{mes}: {suma:.2f}").pack(anchor="w")

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB o procesar datos: {e}")

# Botón para calcular estadísticas (ubicado en el frame de selección de datos)
boton_estadisticas = ttk.Button(seleccion_frame, text="Calcular Estadísticas", command=calcular_suma_y_top_meses)
boton_estadisticas.grid(row=20, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

import tkinter as tk
from tkinter import messagebox, ttk
from pymongo import MongoClient

## Pestaña de Estadísticas
tab7_estadisticas = ttk.Frame(notebook)
notebook.add(tab7_estadisticas, text="Estadística")

# Etiqueta para instrucciones de la pestaña de Estadísticas
estadisticas_label = tk.Label(tab7_estadisticas, text="Selecciona los atributos para calcular estadísticas:")
estadisticas_label.pack(pady=5, padx=10, anchor="w")

# Frame para las opciones de selección de datos
estadisticas_seleccion_frame = ttk.Frame(tab7_estadisticas)
estadisticas_seleccion_frame.pack(pady=5, padx=10, fill="x")

# Lista de atributos (puedes ajustarlo según lo que necesites)
atributos_estadisticas = ["Solvente", "Trapos", "Cartón generado", "B. basura generada", "Plástico generado", "Plástico reciclable"]

# Diccionario para almacenar las variables de los checkbuttons de la pestaña "Estadística"
checkbox_vars_estadisticas = {}

# Función para actualizar los atributos seleccionados
def actualizar_estadisticas_seleccion():
    atributos_seleccionados.clear()
    for atributo, var in checkbox_vars_estadisticas.items():
        if var.get() == 1:
            atributos_seleccionados.append(atributo)

# Crear checkbuttons de selección de datos para la pestaña de estadísticas
atributos_seleccionados = []
for i, atributo in enumerate(atributos_estadisticas):
    var = tk.IntVar()
    checkbox_vars_estadisticas[atributo] = var
    checkbutton = tk.Checkbutton(estadisticas_seleccion_frame, text=atributo, variable=var, command=actualizar_estadisticas_seleccion)
    checkbutton.grid(row=0, column=i, padx=5, pady=5)  # Distribución horizontal

# Frame para mostrar las estadísticas
estadisticas_resultado_frame = ttk.LabelFrame(tab7_estadisticas, text="Estadísticas Resultantes", padding=10)
estadisticas_resultado_frame.pack(pady=20, padx=10, fill="both", expand=True)

# Función para calcular las estadísticas y mostrarlas
def calcular_estadisticas():
    for widget in estadisticas_resultado_frame.winfo_children():
        widget.destroy()  # Limpia el contenido previo del frame de estadísticas

    if not atributos_seleccionados:
        messagebox.showwarning("Advertencia", "Selecciona al menos un atributo para calcular las estadísticas.")
        return

    try:
        # Conexión a MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['registroMaterial']
        coleccion = db['meses']

        # Mostrar las estadísticas en el frame de resultados
        for atributo in atributos_seleccionados:
            resultados = list(coleccion.find({}, {atributo: 1, "_id": 0}))
            valores = [fila[atributo] for fila in resultados if fila.get(atributo) is not None]

            if not valores:
                messagebox.showinfo("Información", f"No hay datos para el atributo '{atributo}'.")
                return

            valores = list(map(float, valores))
            media = sum(valores) / len(valores)
            minimo = min(valores)
            maximo = max(valores)

            # Mostrar los resultados
            resultado_label = tk.Label(estadisticas_resultado_frame, text=f"Atributo: {atributo}\n"
                                                                        f"Media: {media:.2f}\n"
                                                                        f"Valor Mínimo: {minimo:.2f}\n"
                                                                        f"Valor Máximo: {maximo:.2f}\n",
                                       anchor="w", justify="left", wraplength=400)
            resultado_label.pack(anchor="w", pady=5)

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB o procesar los datos: {e}")

# Botón para calcular las estadísticas
boton_calcular_estadisticas = ttk.Button(tab7_estadisticas, text="Calcular Estadísticas", command=calcular_estadisticas)
boton_calcular_estadisticas.pack(pady=10, padx=10)

# Iniciar la aplicación
ventana.mainloop()
