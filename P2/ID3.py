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

def ID3(listaAtributos, listaEjemplos):
    if not listaEjemplos:
        return None
    
    todos_negativos = all(fila[4] == 'no' for fila in listaEjemplos)
    todos_positivos = all(fila[4] == 'si' for fila in listaEjemplos)

    if todos_positivos:
        return '✅ si'
    if todos_negativos:
        return '❌ no'

    if not listaAtributos:
        return None

    mejorAtributo = min(listaAtributos, key=lambda attr: merito(attr, listaEjemplos))
    indice = atributos.index(mejorAtributo)

    arbol = {mejorAtributo: {}}
    valoresPosibles = set(ejemplo[indice] for ejemplo in listaEjemplos)

    for valor in valoresPosibles:
        ejemplosSubarbol = [ejemplo for ejemplo in listaEjemplos if ejemplo[indice] == valor]
        atributosRestantes = [attr for attr in listaAtributos if attr != mejorAtributo]
        arbol[mejorAtributo][valor] = ID3(atributosRestantes, ejemplosSubarbol)

    return arbol

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

def consultar_arbol():
    entrada = simpledialog.askstring("Consulta", "Introduce la consulta (Ej: TiempoExterior=soleado, Temperatura=caluroso, Humedad=alta, Viento=falso)")
    if entrada:
        try:
            ejemplo = dict(pair.split("=") for pair in entrada.split(", "))
            resultado = clasificar(arbol_decision, ejemplo)
            messagebox.showinfo("Resultado", f"Clasificación: {resultado}")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la consulta: {e}")

def mostrar_arbol(arbol, nivel=0):
    if isinstance(arbol, dict):
        atributo = next(iter(arbol))
        resultado_text.insert(tk.END, f"{'  ' * nivel}➤ {atributo}\n")
        for valor, subarbol in arbol[atributo].items():
            resultado_text.insert(tk.END, f"{'  ' * (nivel+1)}- {valor}\n")
            mostrar_arbol(subarbol, nivel+2)
    else:
        resultado_text.insert(tk.END, f"{'  ' * nivel}✔ {arbol}\n")

def generar_arbol():
    global arbol_decision
    arbol_decision = ID3(atributos[:-1], datos)
    resultado_text.delete(1.0, tk.END)
    resultado_text.insert(tk.END, "📖 Árbol de Decisión Generado:\n\n")
    mostrar_arbol(arbol_decision)

# Interfaz gráfica
root = tk.Tk()
root.title("Árbol de Decisión ID3")
root.geometry("600x500")

frame = tk.Frame(root)
frame.pack(pady=10)

generar_btn = tk.Button(frame, text="Generar Árbol", command=generar_arbol)
generar_btn.pack(side=tk.LEFT, padx=5)

consultar_btn = tk.Button(frame, text="Consultar Árbol", command=consultar_arbol)
consultar_btn.pack(side=tk.LEFT, padx=5)

resultado_text = tk.Text(root, height=20, width=70)
resultado_text.pack(pady=10)

root.mainloop()