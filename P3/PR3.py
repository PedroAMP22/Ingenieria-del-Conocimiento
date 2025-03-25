from collections import defaultdict

def leerDatos(nombre_archivo):
    datos_por_clase = defaultdict(list)
    
    with open(nombre_archivo, 'r') as archivo:
        for linea in archivo:
            valores = linea.strip().split(',')
            if len(valores) == 5:
                caracteristicas = list(map(float, valores[:4]))
                clase = valores[4]
                datos_por_clase[clase].append(caracteristicas)
    
    return datos_por_clase


def kMedias(datos):

    e = 0.01 # tolerancia
    b = 2 # peso exponencial



def bayes(datos):

    
    return None


def lloyd(datos):
    e = 10e-10 # tolerancia
    kmax = 10 # numero maximo de iteraciones
    r = 0.1 # razon de aprendizaje




nombre_archivo = './P3/Iris2Clases.txt'  
resultado = leerDatos(nombre_archivo)
print(resultado)