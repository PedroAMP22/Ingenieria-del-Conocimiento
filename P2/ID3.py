import csv

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
for fila in datos:
    print(fila)


