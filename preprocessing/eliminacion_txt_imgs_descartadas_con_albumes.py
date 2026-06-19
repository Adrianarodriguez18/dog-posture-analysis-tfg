# En este documento se procederá con la lectura de las imágenes
# que se han clasificado y crearemos un álbum con los .txt que 
# aparecen en cada uno de los albumes con las imgs clasificadas.

import os
import shutil

carpeta_txt = r"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\labels_train_val"
nombre_album="up"
carpeta_imagenes = fr"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\{nombre_album}"
carpeta_destino = fr"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\labels_{nombre_album}"

os.makedirs(carpeta_destino, exist_ok=True)

# Guardamos los nombres de imágenes del álbum
imagenes_album = set()

for imagen in os.listdir(carpeta_imagenes):
    if imagen.lower().endswith((".jpg", ".jpeg", ".png")):
        nombre_sin_extension = os.path.splitext(imagen)[0]
        imagenes_album.add(nombre_sin_extension)

# Recorremos los .txt
for archivo_txt in os.listdir(carpeta_txt):
    if archivo_txt.lower().endswith(".txt"):

        nombre_txt = os.path.splitext(archivo_txt)[0]

        if nombre_txt in imagenes_album:
            ruta_origen = os.path.join(carpeta_txt, archivo_txt)
            ruta_destino = os.path.join(carpeta_destino, archivo_txt)

            shutil.copy(ruta_origen, ruta_destino)
            print(f"Copiado: {archivo_txt}")
        else:
            print(f"No aparece imagen para: {archivo_txt}")