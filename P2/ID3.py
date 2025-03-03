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

#Mostrar los datos
print("Atributos:", atributos)
print("Datos:")
for fila in datos: # es una matriz
    print(fila)

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
    if(len(listaEjemplos) == 0):
        return None

    # Si todos sos negativos o positivos se devuelve no o si respectivamente
    todos_negativos = all(fila[4] == 'no' for fila in listaEjemplos)
    todos_positivos = all(fila[4] == 'si' for fila in listaEjemplos)

    if todos_positivos:
        return 'si'
    if todos_negativos:
        return 'no'
    
    if len(listaAtributos) == 0:
        return None
    
    # Calculamos todas los meritos y cogemos el mejor
    mejorAtributo = listaAtributos[0]
    meritoMejor = 1
    for atributo in listaAtributos:
        valor = merito(atributo, listaEjemplos)
        if valor < meritoMejor:
            mejorAtributo = atributo
            meritoMejor = valor


    # Atributo Escogido
    print("Siguiente Paso ID3: ", mejorAtributo )

    indice = atributos.index(mejorAtributo)
    valoresPosibles = set(ejemplo[indice] for ejemplo in listaEjemplos)
    
    # Hacemos una nueva lista sin el atributo de mejor merito
    atributosSinSeleccionado = [atributo for atributo in listaAtributos if atributo != mejorAtributo]

    #Generamos un subarbol con los ejemplos para cada posible valor del atributo seleccionado
    for valor in valoresPosibles:
        ejemplosSubarbol = [ejemplo for ejemplo in listaEjemplos if ejemplo[indice] == valor]
        
        print(f"\nSubárbol para valor '{valor}':")
        ID3(atributosSinSeleccionado, ejemplosSubarbol)


ID3(atributos[:-1], datos) 

#Queda guardar el arbol de agluna manera y hacer las consultas :)

