import csv
import math
#Leer el archivo de atributos
with open("./P2/AtributosJuego.txt", "r", encoding="utf-8") as f:
    atributos = f.readline().strip().split(",")

#Leer el archivo de datos
datos = []
with open("./P2/Juego.txt", "r", encoding="utf-8") as f:
    reader = csv.reader(f)  #Lee el archivo como CSV
    for fila in reader:
        datos.append(fila)


# Formula de informacion o entropia
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

# Formula del merito
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
        return None  # Caso base: sin ejemplos

    # Si todos los ejemplos tienen la misma clasificación, devolver ese valor
    todos_negativos = all(fila[4] == 'no' for fila in listaEjemplos)
    todos_positivos = all(fila[4] == 'si' for fila in listaEjemplos)

    if todos_positivos:
        return '✅ si'
    if todos_negativos:
        return '❌ no'

    if not listaAtributos:
        return None  # No quedan atributos para dividir

    # Escoger el mejor atributo según el mérito
    mejorAtributo = min(listaAtributos, key=lambda attr: merito(attr, listaEjemplos))
    indice = atributos.index(mejorAtributo)

    arbol = {mejorAtributo: {}}
    valoresPosibles = set(ejemplo[indice] for ejemplo in listaEjemplos)

    # Hacer la llamada recursiva para cada valor posible del atributo seleccionado
    for valor in valoresPosibles:
        ejemplosSubarbol = [ejemplo for ejemplo in listaEjemplos if ejemplo[indice] == valor]
        atributosRestantes = [attr for attr in listaAtributos if attr != mejorAtributo]
        arbol[mejorAtributo][valor] = ID3(atributosRestantes, ejemplosSubarbol)

    return arbol

# Función para imprimir el árbol como un grafo en consola
def imprimir_arbol_grafo(arbol, prefijo="", es_ultimo=True):
    if isinstance(arbol, dict):
        atributo = next(iter(arbol))  # Obtener el nodo actual

        # Dibujar el nodo
        rama = "└──" if es_ultimo else "├──"
        print(prefijo + rama + " " + atributo)

        # Ajustar el prefijo para la siguiente línea
        prefijo_nuevo = prefijo + ("    " if es_ultimo else "│   ")

        # Dibujar las ramas
        valores = list(arbol[atributo].keys())
        for i, valor in enumerate(valores):
            es_ultima_rama = (i == len(valores) - 1)
            print(prefijo_nuevo + ("└──" if es_ultima_rama else "├──") + f" {valor}")
            imprimir_arbol_grafo(arbol[atributo][valor], prefijo_nuevo + ("    " if es_ultima_rama else "│   "), es_ultima_rama)
    else:
        rama = "└──" if es_ultimo else "├──"
        print(prefijo + rama + " " + arbol)  # Imprime el resultado final (sí/no)


arbol_decision = ID3(atributos[:-1], datos)
print("\n📖 Árbol de Decisión Generado:\n")
imprimir_arbol_grafo(arbol_decision)



#Queda guardar el arbol de agluna manera y hacer las consultas :)

def clasificar(arbol, ejemplo):
    if not isinstance(arbol, dict):
        return arbol  # Se alcanzó una hoja, devolver el resultado

    atributo = next(iter(arbol))  # Tomar el nodo actual

    # Validar que el atributo esté en la consulta
    if atributo not in ejemplo:
        return f"⚠️ Error: Falta el atributo '{atributo}' en la consulta."

    valor = ejemplo[atributo]

    # Validar que el valor del atributo esté en el árbol
    if valor not in arbol[atributo]:
        return f"⚠️ Error: El valor '{valor}' no es válido para '{atributo}'."

    return clasificar(arbol[atributo][valor], ejemplo)  # Llamada recursiva

while True:
    entrada = input("\n🔍 Introduce una consulta (formato: TiempoExterior=soleado, Temperatura=caluroso, Humedad=alta, Viento=falso) o 'salir':\n").strip()
    
    if entrada.lower() == "salir":
        print("👋 ¡Hasta luego!")
        break
    
    try:
        # Convertir la entrada a un diccionario
        ejemplo = dict(pair.split("=") for pair in entrada.split(", "))
        
        # Validar que la consulta tenga todos los atributos necesarios
        atributos_faltantes = [attr for attr in atributos[:-1] if attr not in ejemplo]
        if atributos_faltantes:
            print(f"⚠️ Error: Faltan los atributos {', '.join(atributos_faltantes)} en la consulta.")
            continue

        # Realizar la clasificación
        resultado = clasificar(arbol_decision, ejemplo)
        print(f"📝 Resultado: {resultado}")
    
    except Exception as e:
        print(f"⚠️ Error en la consulta: {e}")

