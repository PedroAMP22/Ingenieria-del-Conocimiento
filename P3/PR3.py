import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from collections import defaultdict
import random
import numpy as np

# --- Funciones de lectura de ficheros ---

def leerDatosConClase(nombre_archivo):
    """
    Lee el fichero y agrupa los datos por clase.
    Cada línea tiene: f1,f2,f3,f4,clase
    """
    datos_por_clase = defaultdict(list)
    try:
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                valores = linea.strip().split(',')
                if len(valores) >= 5:
                    # Convertir las 4 primeras columnas a float
                    caracteristicas = list(map(float, valores[:4]))
                    clase = valores[4]
                    datos_por_clase[clase].append(caracteristicas)
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo: {nombre_archivo}")
    return datos_por_clase

def leerDatosSinClase(nombre_archivo):
    """
    Lee el fichero y devuelve una lista de características.
    Se ignora la etiqueta (último valor de cada línea).
    """
    datos = []
    try:
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                valores = linea.strip().split(',')
                if len(valores) >= 4:
                    # Se toman las 4 primeras columnas como características
                    caracteristicas = list(map(float, valores[:4]))
                    datos.append(caracteristicas)
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo: {nombre_archivo}")
    return datos

# --- Algoritmo de K-Medias Fuzzy (Agrupamiento borroso) ---

def kMedias(datos, c=2, b=2, tolerancia=0.01, max_iter=100, centros_iniciales=None):
    """
    Implementa el algoritmo K-Medias Fuzzy.
    Si 'datos' es un diccionario, se unen sus valores; de lo contrario, se asume que es una lista.
    
    Parámetros:
        datos: conjunto de datos (lista o diccionario)
        c: número de centroides
        b: peso exponencial (por defecto 2)
        tolerancia: criterio de convergencia (por defecto 0.01)
        max_iter: número máximo de iteraciones (por defecto 100)
        centros_iniciales: lista de centros iniciales (opcional)
    
    Retorna:
        centroides: array de centroides finales
        P: matriz de pertenencia (forma: n_datos x c)
    """
    # Unificar los datos en un único array
    if isinstance(datos, dict):
        todos_los_datos = np.array([punto for lista in datos.values() for punto in lista])
    else:
        todos_los_datos = np.array(datos)
    
    n = len(todos_los_datos)
    
    if centros_iniciales is None:
        if n < c:
            messagebox.showerror("Error", f"Se requieren al menos {c} datos para inicializar los centroides, pero se han encontrado solo {n}.")
            return None, None
        # Inicializar centroides a partir de los datos, de forma aleatoria
        indices = random.sample(range(n), c)
        centroides = todos_los_datos[indices]
    else:
        # Usar los centros iniciales proporcionados, aunque n < c
        centroides = np.array(centros_iniciales, dtype=float)
    
    epsilon = 1e-10  # Para evitar división por cero

    for _ in range(max_iter):
        # Calcular la distancia al cuadrado entre cada dato y cada centroide
        distancias = np.linalg.norm(todos_los_datos[:, np.newaxis] - centroides, axis=2) ** 2
        distancias = np.maximum(distancias, epsilon)
        
        # Cálculo de la matriz de pertenencia (fuzzy)
        P = 1 / (distancias ** (1 / (b - 1)))
        P = P / np.sum(P, axis=1, keepdims=True)
        
        centroides_anteriores = np.copy(centroides)
        # Actualizar cada centroide usando la fórmula ponderada
        for i in range(c):
            pesos = (P[:, i] ** b).reshape(-1, 1)
            numerador = np.sum(pesos * todos_los_datos, axis=0)
            denominador = np.sum(P[:, i] ** b) + epsilon
            centroides[i] = numerador / denominador
        
        if np.isnan(centroides).any():
            messagebox.showerror("Error", "Se han generado NaN en los centroides. Abortando...")
            return None, None
        
        if np.linalg.norm(centroides - centroides_anteriores) < tolerancia:
            break

    return centroides, P

# --- Clasificador Bayes ---

def calcular_medias_varianzas(datos):
    """
    Calcula medias, varianzas y priors a partir de datos agrupados por clase.
    """
    medias = {}
    varianzas = {}
    priors = {}
    total_muestras = sum(len(muestras) for muestras in datos.values())
    
    for clase, muestras in datos.items():
        muestras_array = np.array(muestras)
        medias[clase] = np.mean(muestras_array, axis=0)
        varianzas[clase] = np.var(muestras_array, axis=0) + 1e-6  # Evitar división por cero
        priors[clase] = len(muestras) / total_muestras
    
    return medias, varianzas, priors

def clasificarBayes(muestra, medias, varianzas, priors):
    def probabilidad_gaussiana(x, media, varianza):
        return (1 / np.sqrt(2 * np.pi * varianza)) * np.exp(-((x - media) ** 2) / (2 * varianza))

    probabilidades = {}
    for clase in medias:
        prob = np.log(priors[clase])
        prob += np.sum(np.log(probabilidad_gaussiana(muestra, medias[clase], varianzas[clase])))
        probabilidades[clase] = prob
    
    return max(probabilidades, key=probabilidades.get)

# --- Algoritmo de Lloyd Competitivo ---

def lloyd(data, centers, learning_rate=0.1, tol=1e-10, max_iter=10):
    """
    Algoritmo de Lloyd Competitivo.
    Parámetros:
      - centers: centros iniciales (lista o array)
      - learning_rate: tasa de aprendizaje (0.1)
      - tol: tolerancia (1e-10)
      - max_iter: número máximo de iteraciones (10)
    """
    centers = np.array(centers, dtype=float)
    data = np.array(data, dtype=float)
    
    for _ in range(max_iter):
        prev_centers = centers.copy()
        for x in data:
            # Encuentra el centroide más cercano
            j = np.argmin(np.linalg.norm(x - centers, axis=1))
            # Actualización suave del centroide ganador
            centers[j] += learning_rate * (x - centers[j])
        if np.linalg.norm(centers - prev_centers) < tol:
            break
    return centers

# --- Función para ejecutar el algoritmo seleccionado ---

def ejecutar_algoritmo():
    salida.delete(1.0, tk.END)  # Limpiar área de resultados
    alg = algoritmo_var.get()
    nombre_archivo = archivo_entry.get().strip()
    
    if not nombre_archivo:
        messagebox.showerror("Error", "Debe especificar la ruta del archivo.")
        return
    
    # Para clustering (K-Medias Fuzzy y Lloyd) solo se leen las características;
    # para Bayes se requiere la información de las clases.
    if alg == "Bayes":
        datos = leerDatosConClase(nombre_archivo)
    else:
        datos = leerDatosSinClase(nombre_archivo)
    
    if not datos:
        salida.insert(tk.END, "No se pudieron cargar datos.\n")
        return

    if alg == "K-Medias Fuzzy":
        # Usar los centros iniciales sugeridos en el enunciado
        centros_iniciales = [
            [4.6, 3.0, 4.0, 0.0],
            [6.8, 3.4, 4.6, 0.7]
        ]
        centroides, P = kMedias(datos, c=2, b=2, tolerancia=0.01, max_iter=100, centros_iniciales=centros_iniciales)
        if centroides is not None:
            salida.insert(tk.END, "K-Medias Fuzzy:\n")
            salida.insert(tk.END, f"Centroides finales:\n{centroides}\n")
        else:
            salida.insert(tk.END, "Error en K-Medias Fuzzy.\n")
    elif alg == "Bayes":
        # Calcular parámetros Bayes y clasificar una muestra de prueba
        medias, varianzas, priors = calcular_medias_varianzas(datos)
        # Ejemplo de muestra de prueba (ajustar según corresponda)
        muestra_prueba = [5.1, 3.5, 1.4, 0.2]
        clase_predicha = clasificarBayes(muestra_prueba, medias, varianzas, priors)
        salida.insert(tk.END, "Bayes:\n")
        salida.insert(tk.END, f"Muestra de prueba: {muestra_prueba}\n")
        salida.insert(tk.END, f"Clase predicha: {clase_predicha}\n")
    elif alg == "Lloyd Competitivo":
        # Para Lloyd se utilizan únicamente las características
        todos_los_datos = leerDatosSinClase(nombre_archivo)
        # Centros iniciales sugeridos según el enunciado
        centros_iniciales = [
            [4.6, 3.0, 4.0, 0.0],
            [6.8, 3.4, 4.6, 0.7]
        ]
        centros_finales = lloyd(todos_los_datos, centros_iniciales, learning_rate=0.1, tol=1e-10, max_iter=10)
        salida.insert(tk.END, "Lloyd Competitivo:\n")
        salida.insert(tk.END, f"Centros finales:\n{centros_finales}\n")
    else:
        salida.insert(tk.END, "Seleccione un algoritmo.\n")

# --- Configuración de la interfaz gráfica ---

ventana = tk.Tk()
ventana.title("Comparativa de Algoritmos de Clasificación y Clustering")
ventana.geometry("750x500")

# Selección de archivo
frame_archivo = ttk.Frame(ventana)
frame_archivo.pack(padx=10, pady=10, fill=tk.X)
ttk.Label(frame_archivo, text="Ruta del archivo:").pack(side=tk.LEFT)
archivo_entry = ttk.Entry(frame_archivo, width=50)
archivo_entry.insert(0, "TestIris01.txt")  # Archivo por defecto
archivo_entry.pack(side=tk.LEFT, padx=5)

# Selección de algoritmo
frame_alg = ttk.Frame(ventana)
frame_alg.pack(padx=10, pady=10, fill=tk.X)
ttk.Label(frame_alg, text="Selecciona el algoritmo:").pack(side=tk.LEFT)
algoritmo_var = tk.StringVar()
algoritmos = ["K-Medias Fuzzy", "Bayes", "Lloyd Competitivo"]
combo_alg = ttk.Combobox(frame_alg, textvariable=algoritmo_var, values=algoritmos, state="readonly")
combo_alg.current(0)
combo_alg.pack(side=tk.LEFT, padx=5)

# Botón de ejecución
btn_ejecutar = ttk.Button(ventana, text="Ejecutar", command=ejecutar_algoritmo)
btn_ejecutar.pack(padx=10, pady=10)

# Área de resultados
salida = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, width=90, height=25)
salida.pack(padx=10, pady=10)

ventana.mainloop()
