# Con las imágenes se llama a YOLO y se detectan los puntos, con la fórmula matemática
# estudiará en que posición se encuentra y añadirá la imagen a un csv con el nombre del álbum,
# que es la clase, y con la predicción, si fue correcta o no por la fórmula matemática.

import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO
from pathlib import Path
import os
import math
import csv

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

    # Si no es visible el punto de cruz, buscamos el cuello o el mentón
    if withers is None:
        alt_point = obtener_punto_valido(puntos_xyv, 23)    # cuello
        # Si no es posible con el cuello, probamos con el mentón:
        if alt_point is None:
            alt_point = obtener_punto_valido(puntos_xyv, 17)    # mentón
        if alt_point is not None:
            withers = alt_point

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
    # Descargamos el modelo
    # Tenemos que indicar que modelo vamos a usar
    tipo_modelo="small"
    ruta_modelo=rf"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\best_yolo26_{tipo_modelo}.pt"
    modelo_perros=YOLO(ruta_modelo) 

    # Carpeta de imágenes que vamos a estudiar
    nombre_carpeta="sit"
    carpeta=Path(rf"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\{nombre_carpeta}")
    resultados_perros = modelo_perros.predict(str(carpeta/"*.jpg"),save=False, stream=True)

    # Carpeta donde queremos guardar el csv
    carpeta_destino=fr"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\resultadosYOLO_{tipo_modelo}"
    # Crea la carpeta en caso de no existir:
    os.makedirs(carpeta_destino, exist_ok=True)
    # Ruta completa del csv:
    ruta_csv=os.path.join(carpeta_destino, f"imgs_{nombre_carpeta}.csv")

    # Creamos el .csv:
    with open(ruta_csv, mode="w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo, delimiter=";")
        # Cabecera
        escritor.writerow(["name", "class", "prediction"])

        for resultado in resultados_perros:
            # Cargamos la imagen
            img_ruta =  resultado.path
            img_nombre = os.path.basename(img_ruta)

            if resultado.keypoints is None or len(resultado.keypoints.data)==0:
                print(f"Imagen {img_nombre} no tiene perro")
            
            else:
                puntos_xyv = resultado.keypoints.data.numpy()[0]

                # Si el perro está de pie:
                # Down o Sit: Incorrecta si detecta que está de pie
                # Up: Correcta si detecta que está de pie
                if is_dog_standing(puntos_xyv):
                    escritor.writerow([img_nombre, nombre_carpeta, "Incorrecta"])
                    
                else:
                    escritor.writerow([img_nombre, nombre_carpeta, "Correcta"])


if __name__ == "__main__":
    main()