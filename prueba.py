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

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Conexión a MongoDB")
ventana.attributes("-fullscreen", True)

# Crear Notebook para las pestañas
notebook = ttk.Notebook(ventana)
notebook.pack(fill="both", expand=True)

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
import tkinter as tk
from tkinter import messagebox, ttk
from pymongo import MongoClient
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

# Diccionario para almacenar las variables de los checkbuttons
checkbox_vars = {}

# Crear checkbuttons de selección de datos dispuestos horizontalmente
def actualizar_seleccion():
    atributos_seleccionados.clear()
    for atributo, var in checkbox_vars.items():
        if var.get() == 1:
            atributos_seleccionados.append(atributo)

for i, atributo in enumerate(atributos):
    var = tk.IntVar()
    checkbox_vars[atributo] = var
    checkbutton = tk.Checkbutton(seleccion_frame, text=atributo, variable=var, command=actualizar_seleccion)
    checkbutton.grid(row=0, column=i, padx=5, pady=5)  # Distribución horizontal

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


#import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from collections import Counter

# Pestaña de Estadísticas
tab7_estadisticas = ttk.Frame(notebook)
notebook.add(tab7_estadisticas, text="Estadística")

# Estilo para los elementos dentro de la pestaña
style = ttk.Style()
style.configure("TFrame", background="#eaf8e1")  # Fondo verde claro para el frame
style.configure("TButton", background="#8fbc8f", foreground="white", font=("Arial", 10, "bold"))
style.configure("TLabel", background="#eaf8e1", font=("Arial", 10))
style.configure("TCheckbutton", background="#eaf8e1", font=("Arial", 10))

# Etiqueta para instrucciones de la pestaña de Estadísticas
estadisticas_label = tk.Label(tab7_estadisticas, text="Selecciona los atributos para calcular estadísticas:", bg="#eaf8e1", font=("Arial", 12))
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
            resultados = list(coleccion.find({}, {atributo: 1, "_id": 0, "mes": 1}))  # Incluimos el mes
            valores = [fila[atributo] for fila in resultados if fila.get(atributo) is not None]
            meses = [fila["mes"] for fila in resultados if fila.get(atributo) is not None]

            if not valores:
                messagebox.showinfo("Información", f"No hay datos para el atributo '{atributo}'.")
                return

            valores = list(map(float, valores))
            media = sum(valores) / len(valores)
            minimo = min(valores)
            maximo = max(valores)

            # Encontrar el mes con más y menos datos
            mes_count = Counter(meses)
            mes_max = mes_count.most_common(1)[0]
            mes_min = mes_count.most_common()[-1]

            # Mostrar los resultados con formato
            resultado_label = tk.Label(estadisticas_resultado_frame, text=f"Atributo: {atributo}\n"
                                                                        f"Media: {media:.2f}\n"
                                                                        f"Valor Mínimo: {minimo:.2f}\n"
                                                                        f"Valor Máximo: {maximo:.2f}\n"
                                                                        f"Mes con más datos: {mes_max[0]} ({mes_max[1]} registros)\n"
                                                                        f"Mes con menos datos: {mes_min[0]} ({mes_min[1]} registros)\n",
                                       anchor="w", justify="left", wraplength=400, bg="#eaf8e1", font=("Arial", 10))
            resultado_label.pack(anchor="w", pady=5)

    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a MongoDB o procesar los datos: {e}")

# Botón para calcular las estadísticas
boton_calcular_estadisticas = ttk.Button(tab7_estadisticas, text="Calcular Estadísticas", command=calcular_estadisticas)
boton_calcular_estadisticas.pack(pady=10, padx=10)


# Iniciar la aplicación
ventana.mainloop()

