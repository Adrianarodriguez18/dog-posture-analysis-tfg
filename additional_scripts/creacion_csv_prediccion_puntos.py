# En este documento se estudia el estado del perro sin YOLO.
# El archivo lee los puntos clave de las partes del perro del .csv.
# Con estos puntos se los manda a la fórmula matemática y así, 
# poder ver si tiene mayor porcentaje de aciertos sin llamar a YOLO.

import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO
from pathlib import Path
import os
import math
import csv
import pandas as pd

def obtener_punto_valido(puntos_xyv, indice):
    # Comprobamos que existe ese punto en el rango
    if indice < len(puntos_xyv):
        punto = puntos_xyv[indice]
        # Comprobamos la visibilidad mayor a 0.3 del punto
        if punto[2] > 0.3:
            return punto
        
def is_dog_standing(puntos_xyv):
    # Obtenemos los puntos clave comprobando con la función obtener_punto_valido si es posible emplearlo
    # Le pasamos a la función, los puntos y el índice correspondiente al punto
    # Por ejemplo: fl_paw, front left paw corresponde con el índice 0

    # Patas
    fl_paw = obtener_punto_valido(puntos_xyv, 0)
    fr_paw = obtener_punto_valido(puntos_xyv, 6)
    rl_paw = obtener_punto_valido(puntos_xyv, 3)
    rr_paw = obtener_punto_valido(puntos_xyv, 9)
    # Cruz
    withers = obtener_punto_valido(puntos_xyv, 22)
    # Comienzo cola
    tail_start = obtener_punto_valido(puntos_xyv, 12)
    # Puntos de los codos delanteros
    fl_elbow = obtener_punto_valido(puntos_xyv, 2)
    fr_elbow = obtener_punto_valido(puntos_xyv, 8)

    # Comprobamos que los puntos de la coordenada Y de las patas son visibles y los guardamos en una lista
    # Patas delanteras:
    front_paws_y = []
    if fl_paw is not None: 
        front_paws_y.append(fl_paw[1])
    if fr_paw is not None: 
        front_paws_y.append(fr_paw[1])
    # Patas traseras:
    rear_paws_y = []
    if rl_paw is not None: 
        rear_paws_y.append(rl_paw[1])
    if rr_paw is not None: 
        rear_paws_y.append(rr_paw[1])

    # Si no es visible el punto de cruz, buscamos el cuello o el mentón
    if withers is None:
        alt_point = obtener_punto_valido(puntos_xyv, 23)    # cuello
        # Si no es posible con el cuello, probamos con el mentón:
        if alt_point is None:
            alt_point = obtener_punto_valido(puntos_xyv, 17)    # mentón
        if alt_point is not None:
            withers = alt_point

    # Si faltan puntos críticos, no podemos evaluar con seguridad
    # Comprobamos si:
    #       · Existen puntos en la coordenada Y en las patas delanteras
    #       · Existen puntos en la coordenada Y en las patas traseras
    #       · Existe punto en la cuz
    #       · Existe punto en la cola
    # Si no existe ninguno de ellos, no se evalúa la posición
    if len(front_paws_y) == 0 or len(rear_paws_y) == 0 or withers is None or tail_start is None:
        return False
    
    # Hacemos la media de las coordenadas Y de las patas delanteras para saber cuanto miden:
    avg_front_paw_y = sum(front_paws_y) / len(front_paws_y)
    withers_y = withers[1]

    # Comprobamos cual es la diferencia que hay entre la medida de las patas y la cruz
    # Si el resultado es un valor grande el perro está de pie y si es pequeño está tumbado:
    front_height = avg_front_paw_y - withers_y
    # Si es <= 0 significa que el perro está tumbado: Tiene el lomo por debajo de las patas o están alineados
    if front_height <= 0: 
        return False

    # Comprobamos si está tumbado pero con las patas estiradas:
    # Lo haremos con las coordenadas X e Y, si la componente X > componente Y: Patas estiradas horizontalmente: Tumbado
    # Entramos en este condicional si existen puntos de las patas y de los codos
    # Pata izquierda delantera
    if fl_paw is not None and fl_elbow is not None:
        # Calculamos las diferencias en los diferentes ejes
        dif_x = abs(fl_paw[0] - fl_elbow[0])
        dif_y = abs(fl_paw[1] - fl_elbow[1])
        if dif_y > 0 and dif_x > 1.5 * dif_y: 
            return False
    # Pata derecha delantera  
    if fr_paw is not None and fr_elbow is not None:
        dif_x = abs(fr_paw[0] - fr_elbow[0])
        dif_y = abs(fr_paw[1] - fr_elbow[1])
        if dif_y > 0 and dif_x > 1.5 * dif_y: 
            return False
            
    # Comprobamos las alturas verticales:
    # El perro puede tener las patas recogidas o aplastadas
    # Utilizamos los codos:
    front_elbows_y = []
    if fl_elbow is not None: 
        front_elbows_y.append(fl_elbow[1])
    if fr_elbow is not None: 
        front_elbows_y.append(fr_elbow[1])
    
    # Si tenemos los puntos de los codos del eje Y:
    if len(front_elbows_y) > 0:
        avg_elbow_y = sum(front_elbows_y) / len(front_elbows_y)
        # Distancia entre pata y codo
        lower_leg_height = avg_front_paw_y - avg_elbow_y
        # Distancia entre codo y cruz
        upper_leg_height = avg_elbow_y - withers_y
        
        # Si distancia entre codo y cruz positiva y si la parte inferior de la pierna es muy pequeña respecto a la superior: Tumbado
        if upper_leg_height > 0 and lower_leg_height < 0.4 * upper_leg_height:
            return False
    
    # Mediante la hipotenusa, calculamos la longitud real del perro, del lomo:
    body_length = math.hypot(withers[0] - tail_start[0], withers[1] - tail_start[1])
    # Si la distancia es positiva y 
    if body_length > 0 and front_height < 0.6 * body_length:
        return False
    
    # Si supera todas estas pruebas tan estrictas, está de pie de verdad
    return True

def main():
    # ruta del csv que vamos a estudiar:
    csv_path=r"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\resultados_sin_YOLO\puntos_imgs_con_v.csv"

    df=pd.read_csv(csv_path)

    # Creamos un índice con las columnas de nuestro csv:
    columnas_puntos = {

    0: ("front_left_paw_x", "front_left_paw_y", "front_left_paw_v"),
    1: ("front_left_knee_x", "front_left_knee_y", "front_left_knee_v"),
    2: ("front_left_elbow_x", "front_left_elbow_y", "front_left_elbow_v"),

    3: ("rear_left_paw_x", "rear_left_paw_y", "rear_left_paw_v"),
    4: ("rear_left_knee_x", "rear_left_knee_y", "rear_left_knee_v"),
    5: ("rear_left_elbow_x", "rear_left_elbow_y", "rear_left_elbow_v"),

    6: ("front_right_paw_x", "front_right_paw_y", "front_right_paw_v"),
    7: ("front_right_knee_x", "front_right_knee_y", "front_right_knee_v"),
    8: ("front_right_elbow_x", "front_right_elbow_y", "front_right_elbow_v"),

    9: ("rear_right_paw_x", "rear_right_paw_y", "rear_right_paw_v"),
    10: ("rear_right_knee_x", "rear_right_knee_y", "rear_right_knee_v"),
    11: ("rear_right_elbow_x", "rear_right_elbow_y", "rear_right_elbow_v"),

    12: ("tail_start_x", "tail_start_y", "tail_start_v"),

    17: ("chin_x", "chin_y", "chin_v"),

    22: ("withers_x", "withers_y", "withers_v"),

    23: ("throat_x", "throat_y", "throat_v")
}
    
    # Carpeta donde queremos guardar el csv
    carpeta_destino=r"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\resultados_sin_YOLO"
    # Crea la carpeta en caso de no existir:
    os.makedirs(carpeta_destino, exist_ok=True)
    # Ruta completa del csv:
    ruta_csv=os.path.join(carpeta_destino, "imgs_clasificadas_sin_YOLO_12junio.csv")

    with open(ruta_csv, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        # Cabecera
        escritor.writerow(["name", "class", "prediction"])

        for indice, fila in df.iterrows():
            img_nombre=fila["name"]
            clase_real=int(fila["class"])

            # Creamos una lista vacía para añadir los puntos
            puntos_xyv=[]

            # Recorremos todos los puntos en el csv con la ayuda del índice de las columnas:
            for i in range(24):
                if i in columnas_puntos:
                    # Nombres de la columna x e y que estamos estudiando en este momento:
                    col_x, col_y, col_v=columnas_puntos[i]
                    # Buscamos los valores del punto:
                    x=fila[col_x]
                    y=fila[col_y]
                    v=fila[col_v]
                    # Los añadimos a la lista:
                    puntos_xyv.append([x, y, v])
                # Si no se detecta punto se añade 0.0, 0.0
                else:
                    puntos_xyv.append([0.0, 0.0, 0.0])

            esta_de_pie=is_dog_standing(puntos_xyv)

            if esta_de_pie == True:
                if clase_real == 1:
                    prediccion="Correcta"
                else:
                    prediccion="Incorrecta"
            elif esta_de_pie == False:
                if clase_real == 1:
                    prediccion="Incorrecta"
                else:
                    prediccion="Correcta"

            escritor.writerow([img_nombre, clase_real, prediccion])


if __name__ == "__main__":
    main()