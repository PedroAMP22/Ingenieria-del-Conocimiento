import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from collections import defaultdict, Counter
import random
import numpy as np

# --- Funciones de lectura de ficheros ---

def leerDatosConClase(nombre_archivo):
    """
    Lee el fichero y agrupa los datos por clase.
    Cada línea tiene: f1,f2,f3,f4,clase
    Retorna un diccionario {clase: [lista_de_muestras]}.
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
    Lee el fichero y devuelve una lista de muestras.
    Si la línea incluye etiqueta (más de 4 valores), se ignora la etiqueta.
    """
    datos = []
    try:
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                valores = linea.strip().split(',')
                if len(valores) >= 4:
                    caracteristicas = list(map(float, valores[:4]))
                    datos.append(caracteristicas)
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo: {nombre_archivo}")
    return datos

def leerDatosTest(nombre_archivo):
    """
    Lee el fichero de test, devolviendo una lista de tuplas (caracteristicas, etiqueta)
    Si la línea no tiene etiqueta, etiqueta será None.
    """
    datos = []
    try:
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                valores = linea.strip().split(',')
                if len(valores) >= 4:
                    caracteristicas = list(map(float, valores[:4]))
                    etiqueta = valores[4] if len(valores) >= 5 else None
                    datos.append((caracteristicas, etiqueta))
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo: {nombre_archivo}")
    return datos

# --- Algoritmo de K-Medias Fuzzy (Agrupamiento borroso) ---

def kMedias(datos, c=2, b=2, tolerancia=0.01, max_iter=100, centros_iniciales=None):
    """
    Implementa el algoritmo K-Medias Fuzzy.
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
        indices = random.sample(range(n), c)
        centroides = todos_los_datos[indices]
    else:
        centroides = np.array(centros_iniciales, dtype=float)
    
    epsilon = 1e-10  # Para evitar división por cero

    for _ in range(max_iter):
        # Calcular distancia al cuadrado entre cada dato y cada centroide
        distancias = np.linalg.norm(todos_los_datos[:, np.newaxis] - centroides, axis=2) ** 2
        distancias = np.maximum(distancias, epsilon)
        # Calcular matriz de pertenencia
        P = 1 / (distancias ** (1 / (b - 1)))
        P = P / np.sum(P, axis=1, keepdims=True)
        
        centroides_anteriores = np.copy(centroides)
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
    Calcula medias, varianzas a partir de datos agrupados por clase.
    """
    medias = {}
    varianzas = {}
    
    for clase, muestras in datos.items():
        muestras_array = np.array(muestras)
        medias[clase] = np.mean(muestras_array, axis=0)
        varianzas[clase] = np.var(muestras_array, axis=0) + 1e-6  # Para evitar división por cero
    
    return medias, varianzas

def clasificarBayes(muestra, medias, varianzas, priors):
    """
    Dada una muestra, calcula la probabilidad logarítmica de pertenecer a cada clase 
    y retorna la clase con mayor probabilidad.
    """
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
      - learning_rate: tasa de aprendizaje
      - tol: tolerancia
      - max_iter: número máximo de iteraciones
    """
    centers = np.array(centers, dtype=float)
    data = np.array(data, dtype=float)
    
    for _ in range(max_iter):
        prev_centers = centers.copy()
        for x in data:
            j = np.argmin(np.linalg.norm(x - centers, axis=1))
            centers[j] += learning_rate * (x - centers[j])
        if np.linalg.norm(centers - prev_centers) < tol:
            break
    return centers

# --- Funciones para clasificación basada en clustering ---

def clasificarPorCluster(muestra, centros):
    """
    Dada una muestra y un conjunto de centros, retorna el índice del centro 
    (cluster) más cercano.
    """
    distancias = np.linalg.norm(np.array(centros) - np.array(muestra), axis=1)
    return np.argmin(distancias)

# --- Función para ejecutar el algoritmo seleccionado sobre datos de entrenamiento y test ---

def ejecutar_algoritmo():
    salida.delete(1.0, tk.END)  # Limpiar área de resultados
    alg = algoritmo_var.get()
    # Archivos de entrada
    entrenamiento_file = entrenamiento_entry.get().strip()
    test_file = test_entry.get().strip()
    
    if not entrenamiento_file or not test_file:
        messagebox.showerror("Error", "Se deben especificar ambos archivos: entrenamiento y test.")
        return

    # Leer datos de test (se espera formato: f1,f2,f3,f4,etiqueta)
    datos_test = leerDatosTest(test_file)
    if not datos_test:
        salida.insert(tk.END, "No se pudieron cargar datos de test.\n")
        return

    salida.insert(tk.END, f"Ejecutando {alg}...\n\n")
    
    if alg == "K-Medias Fuzzy":
        # Para clustering, leemos los datos de entrenamiento con etiquetas
        datos_entrenamiento_conclase = leerDatosConClase(entrenamiento_file)
        if not datos_entrenamiento_conclase:
            salida.insert(tk.END, "No se pudieron cargar datos de entrenamiento.\n")
            return
        # Extraer características y etiquetas
        features_training = []
        labels_training = []
        for clase, muestras in datos_entrenamiento_conclase.items():
            for muestra in muestras:
                features_training.append(muestra)
                labels_training.append(clase)
        
        # Ejecutar K-Medias Fuzzy sobre las características
        centros_iniciales = [
            [4.6, 3.0, 4.0, 0.0],
            [6.8, 3.4, 4.6, 0.7]
        ]
        centroides, P = kMedias(features_training, c=2, b=2, tolerancia=0.01, max_iter=100, centros_iniciales=centros_iniciales)
        if centroides is None:
            salida.insert(tk.END, "Error en K-Medias Fuzzy.\n")
            return
        
        # Asignar etiqueta a cada cluster mediante mayoría en el conjunto de entrenamiento
        asignaciones = [clasificarPorCluster(x, centroides) for x in features_training]
        cluster_labels = {}
        for cluster in range(len(centroides)):
            etiquetas_cluster = [labels_training[i] for i, clus in enumerate(asignaciones) if clus == cluster]
            if etiquetas_cluster:
                cluster_labels[cluster] = Counter(etiquetas_cluster).most_common(1)[0][0]
            else:
                cluster_labels[cluster] = "Desconocido"
                
        salida.insert(tk.END, "K-Medias Fuzzy:\n")
        salida.insert(tk.END, f"Centroides finales:\n{centroides}\n\n")
        for i, (carac, real) in enumerate(datos_test):
            cluster = clasificarPorCluster(carac, centroides)
            pred_label = cluster_labels.get(cluster, "Desconocido")
            salida.insert(tk.END, f"Test {i+1}: Predicción = {pred_label} | Valor real = {real}\n")
    
    elif alg == "Bayes":
        datos_entrenamiento = leerDatosConClase(entrenamiento_file)
        if not datos_entrenamiento:
            salida.insert(tk.END, "No se pudieron cargar datos de entrenamiento.\n")
            return
        medias, varianzas = calcular_medias_varianzas(datos_entrenamiento)
        total = sum(len(muestras) for muestras in datos_entrenamiento.values())
        priors = {clase: len(muestras) / total for clase, muestras in datos_entrenamiento.items()}
        salida.insert(tk.END, "Bayes:\n")
        salida.insert(tk.END, f"Medias: Setosa={medias.get('Iris-setosa')}, Versicolor={medias.get('Iris-versicolor')}\n\n")
        for i, (carac, real) in enumerate(datos_test):
            pred = clasificarBayes(carac, medias, varianzas, priors)
            salida.insert(tk.END, f"Test {i+1}: Predicción = {pred} | Valor real = {real}\n")
    
    elif alg == "Lloyd Competitivo":
        # Para Lloyd, se lee también el conjunto con etiquetas para asignar nombre al cluster
        datos_entrenamiento_conclase = leerDatosConClase(entrenamiento_file)
        if not datos_entrenamiento_conclase:
            salida.insert(tk.END, "No se pudieron cargar datos de entrenamiento.\n")
            return
        features_training = []
        labels_training = []
        for clase, muestras in datos_entrenamiento_conclase.items():
            for muestra in muestras:
                features_training.append(muestra)
                labels_training.append(clase)
        
        centros_iniciales = [
            [4.6, 3.0, 4.0, 0.0],
            [6.8, 3.4, 4.6, 0.7]
        ]
        centros_finales = lloyd(features_training, centros_iniciales, learning_rate=0.1, tol=1e-10, max_iter=10)
        
        # Asignar etiqueta a cada cluster según los datos de entrenamiento
        asignaciones = [clasificarPorCluster(x, centros_finales) for x in features_training]
        cluster_labels = {}
        for cluster in range(len(centros_finales)):
            etiquetas_cluster = [labels_training[i] for i, clus in enumerate(asignaciones) if clus == cluster]
            if etiquetas_cluster:
                cluster_labels[cluster] = Counter(etiquetas_cluster).most_common(1)[0][0]
            else:
                cluster_labels[cluster] = "Desconocido"
                
        salida.insert(tk.END, "Lloyd Competitivo:\n")
        salida.insert(tk.END, f"Centros finales:\n{centros_finales}\n\n")
        for i, (carac, real) in enumerate(datos_test):
            cluster = clasificarPorCluster(carac, centros_finales)
            pred_label = cluster_labels.get(cluster, "Desconocido")
            salida.insert(tk.END, f"Test {i+1}: Predicción = {pred_label} | Valor real = {real}\n")
    else:
        salida.insert(tk.END, "Seleccione un algoritmo.\n")

# --- Configuración de la interfaz gráfica ---

ventana = tk.Tk()
ventana.title("Comparativa de Algoritmos de Clasificación y Clustering")
ventana.geometry("800x600")

# Selección de archivo de entrenamiento
frame_entrenamiento = ttk.Frame(ventana)
frame_entrenamiento.pack(padx=10, pady=5, fill=tk.X)
ttk.Label(frame_entrenamiento, text="Archivo de Entrenamiento:").pack(side=tk.LEFT)
entrenamiento_entry = ttk.Entry(frame_entrenamiento, width=50)
entrenamiento_entry.insert(0, "Iris2Clases.txt")  # Por defecto
entrenamiento_entry.pack(side=tk.LEFT, padx=5)

# Selección de archivo de test
frame_test = ttk.Frame(ventana)
frame_test.pack(padx=10, pady=5, fill=tk.X)
ttk.Label(frame_test, text="Archivo de Test:").pack(side=tk.LEFT)
test_entry = ttk.Entry(frame_test, width=50)
test_entry.insert(0, "TestIris01.txt")
test_entry.pack(side=tk.LEFT, padx=5)

# Selección de algoritmo
frame_alg = ttk.Frame(ventana)
frame_alg.pack(padx=10, pady=5, fill=tk.X)
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
