import csv
import math
import tkinter as tk
from tkinter import messagebox, simpledialog

# Leer el archivo de atributos
with open("./P2/AtributosJuego.txt", "r", encoding="utf-8") as f:
    atributos = f.readline().strip().split(",")

# Leer el archivo de datos
datos = []
with open("./P2/Juego.txt", "r", encoding="utf-8") as f:
    reader = csv.reader(f)  # Lee el archivo como CSV
    for fila in reader:
        datos.append(fila)

# Fórmula de información o entropía
def infor(listaEjemplos):
    total = len(listaEjemplos)
    if total == 0:
        return 0
    count_si = sum(1 for ejemplo in listaEjemplos if ejemplo[4] == 'si')
    count_no = total - count_si  
    p_si = count_si / total
    p_no = count_no / total
    if p_si == 0 or p_no == 0:
        return 0
    return -(p_si * math.log2(p_si) + p_no * math.log2(p_no))

# Fórmula del mérito
def merito(atributo, listaEjemplos):
    indice_atributo = atributos.index(atributo)
    valores = set(ejemplo[indice_atributo] for ejemplo in listaEjemplos)
    entropia_total = infor(listaEjemplos)
    entropia_condicional = 0
    for valor in valores:
        ejemplos_filtrados = [ejemplo for ejemplo in listaEjemplos if ejemplo[indice_atributo] == valor]
        p_valor = len(ejemplos_filtrados) / len(listaEjemplos)
        entropia_condicional += p_valor * infor(ejemplos_filtrados)
    return entropia_total - entropia_condicional

# Algoritmo ID3 modificado para retornar 'SI' o 'NO'
def ID3(listaAtributos, listaEjemplos):
    if not listaEjemplos:
        return None
    todos_negativos = all(fila[4] == 'no' for fila in listaEjemplos)
    todos_positivos = all(fila[4] == 'si' for fila in listaEjemplos)
    if todos_positivos:
        return 'SI'
    if todos_negativos:
        return 'NO'
    if not listaAtributos:
        return None
    # Seleccionar el mejor atributo (se usa min para elegir el que minimiza la entropía condicional)
    mejorAtributo = min(listaAtributos, key=lambda attr: merito(attr, listaEjemplos))
    indice = atributos.index(mejorAtributo)
    arbol = {mejorAtributo: {}}
    valoresPosibles = set(ejemplo[indice] for ejemplo in listaEjemplos)
    for valor in valoresPosibles:
        ejemplosSubarbol = [ejemplo for ejemplo in listaEjemplos if ejemplo[indice] == valor]
        atributosRestantes = [attr for attr in listaAtributos if attr != mejorAtributo]
        arbol[mejorAtributo][valor] = ID3(atributosRestantes, ejemplosSubarbol)
    return arbol

# Función para clasificar un ejemplo usando el árbol
def clasificar(arbol, ejemplo):
    if not isinstance(arbol, dict):
        return arbol
    atributo = next(iter(arbol))
    if atributo not in ejemplo:
        return f"⚠️ Falta el atributo '{atributo}'"
    valor = ejemplo[atributo]
    if valor not in arbol[atributo]:
        return f"⚠️ Valor '{valor}' no válido para '{atributo}'"
    return clasificar(arbol[atributo][valor], ejemplo)

# ----------------------- Visualización del árbol -----------------------

# Clase para representar los nodos del árbol para la visualización
class Node:
    def __init__(self, label):
        self.label = label
        self.children = []    # Lista de nodos hijos
        self.edge_labels = [] # Etiquetas de las ramas (valor del atributo)
        self.x = 0
        self.y = 0

# Función para convertir el árbol (diccionario) a una estructura de nodos
def convert_tree(arbol):
    if isinstance(arbol, dict):
        atributo = next(iter(arbol))
        nodo = Node(atributo)
        for edge, subarbol in arbol[atributo].items():
            nodo.children.append(convert_tree(subarbol))
            nodo.edge_labels.append(edge)
        return nodo
    else:
        return Node(arbol)

# Función para asignar posiciones a cada nodo (layout horizontal y vertical)
def compute_positions(node, depth, x_counter, horizontal_spacing, vertical_spacing, margin_y):
    node.y = depth * vertical_spacing + margin_y
    if not node.children:
        node.x = x_counter[0]
        x_counter[0] += horizontal_spacing
    else:
        for child in node.children:
            compute_positions(child, depth+1, x_counter, horizontal_spacing, vertical_spacing, margin_y)
        node.x = sum(child.x for child in node.children) / len(node.children)

# Función para obtener los límites del árbol (para configurar el scroll)
def get_bounds(node):
    min_x = node.x
    max_x = node.x
    min_y = node.y
    max_y = node.y
    for child in node.children:
        c_min_x, c_max_x, c_min_y, c_max_y = get_bounds(child)
        min_x = min(min_x, c_min_x)
        max_x = max(max_x, c_max_x)
        min_y = min(min_y, c_min_y)
        max_y = max(max_y, c_max_y)
    return (min_x, max_x, min_y, max_y)

# Función para dibujar el árbol en el canvas
def draw_node(canvas, node, node_radius):
    # Nodos internos (con hijos) se dibujan como óvalos
    if node.children:
        canvas.create_oval(node.x - node_radius, node.y - node_radius,
                           node.x + node_radius, node.y + node_radius,
                           fill="lightblue", outline="black")
        canvas.create_text(node.x, node.y, text=node.label, font=("Helvetica", 10, "bold"))
    else:
        # Para las hojas se dibuja un rectángulo con estilo según su etiqueta
        if node.label.upper() == "NO":
            fill_color = "red"
            display_text = "✖ NO"
        elif node.label.upper() == "SI":
            fill_color = "lightgreen"
            display_text = "✓ SI"
        else:
            fill_color = "lightgreen"
            display_text = node.label
        canvas.create_rectangle(node.x - node_radius, node.y - node_radius,
                                node.x + node_radius, node.y + node_radius,
                                fill=fill_color, outline="black")
        canvas.create_text(node.x, node.y, text=display_text, font=("Helvetica", 10))
    
    # Dibujar las ramas y llamar recursivamente para cada hijo
    num_children = len(node.children)
    for i, (child, edge) in enumerate(zip(node.children, node.edge_labels)):
        canvas.create_line(node.x, node.y + node_radius, child.x, child.y - node_radius, arrow=tk.LAST)
        midx = (node.x + child.x) / 2
        midy = (node.y + child.y) / 2
        # Desplazamiento vertical para separar los textos de las ramas si hay varios hijos
        offset = (i - (num_children - 1) / 2) * 15  
        canvas.create_text(midx, midy + offset, text=str(edge).upper(), fill="blue", font=("Helvetica", 8))
        draw_node(canvas, child, node_radius)

# Función para dibujar el árbol en la interfaz gráfica
def dibujar_arbol():
    tree_canvas.delete("all")
    if arbol_decision is None:
        return
    # Convertir el árbol de decisión a la estructura Node
    root_node = convert_tree(arbol_decision)
    # Parámetros de layout
    horizontal_spacing = 80
    vertical_spacing = 100
    margin_y = 50
    x_counter = [50]  # posición inicial x
    compute_positions(root_node, 0, x_counter, horizontal_spacing, vertical_spacing, margin_y)
    # Ajustar scrollregion del canvas según los límites del árbol
    min_x, max_x, min_y, max_y = get_bounds(root_node)
    tree_canvas.config(scrollregion=(min_x - 50, min_y - 50, max_x + 50, max_y + 50))
    node_radius = 20
    draw_node(tree_canvas, root_node, node_radius)

# Función para generar el árbol de decisión y dibujarlo, habilitando la consulta
def generar_arbol():
    global arbol_decision
    arbol_decision = ID3(atributos[:-1], datos)
    dibujar_arbol()
    consultar_btn.config(state=tk.NORMAL)

# Función de consulta modificada: se piden solo los valores en orden
def consultar_arbol():
    entrada = simpledialog.askstring("Consulta", 
                                     f"Introduce la consulta (Ej: soleado, caluroso, alta, falso)\nOrden: {', '.join(atributos[:-1])}")
    if entrada:
        try:
            valores = [valor.strip() for valor in entrada.split(",")]
            if len(valores) != len(atributos[:-1]):
                raise ValueError(f"Se requieren {len(atributos[:-1])} valores, se recibieron {len(valores)}")
            ejemplo = {atributos[i]: valores[i] for i in range(len(valores))}
            resultado = clasificar(arbol_decision, ejemplo)
            messagebox.showinfo("Resultado", f"Clasificación: {resultado}")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la consulta: {e}")

# ----------------------- Interfaz Gráfica Mejorada -----------------------

root = tk.Tk()
root.title("Árbol de Decisión ID3")
root.geometry("900x700")
root.configure(bg="#f0f0f0")

# Frame superior con botones
top_frame = tk.Frame(root, bg="#f0f0f0")
top_frame.pack(pady=10)

generar_btn = tk.Button(top_frame, text="Generar Árbol", command=generar_arbol,
                        bg="#4CAF50", fg="white", font=("Helvetica", 12), padx=10, pady=5)
generar_btn.pack(side=tk.LEFT, padx=10)

# Se inicia el botón de consulta deshabilitado
consultar_btn = tk.Button(top_frame, text="Consultar Árbol", command=consultar_arbol,
                          bg="#2196F3", fg="white", font=("Helvetica", 12), padx=10, pady=5, state=tk.DISABLED)
consultar_btn.pack(side=tk.LEFT, padx=10)

# Frame para el canvas con scrollbars
canvas_frame = tk.Frame(root)
canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

tree_canvas = tk.Canvas(canvas_frame, bg="white")
tree_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar vertical
v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=tree_canvas.yview)
v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
tree_canvas.config(yscrollcommand=v_scroll.set)

# Scrollbar horizontal
h_scroll = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=tree_canvas.xview)
h_scroll.pack(fill=tk.X)
tree_canvas.config(xscrollcommand=h_scroll.set)

arbol_decision = None
root.mainloop()
