# En este .py lo que se hará será agrupar todos las etiquetas de los puntos
# en un único .csv, se leerá el excel donde se indica la clase de la imagen
# que se está estudiando y se añadirá.
# Puntos que guardamos: [x, y]

# ---Importamos librerías
import os
import pandas as pd

# ---Asignamos variables a lo que vamos a utilizar:
# Carpeta con todos los puntos de las imágenes (los .txt)
carpeta_txt=r"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\labels_train_val"
# Excel con las imágenes clasificadas, solo nos interesa que tipo de clase es la imagen.
estado_img=fr"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\resultadosYOLO_large\imgs_clasificadas_large.xlsx"
# Carpeta donde guardamos el excel final
ruta_destino=r"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\resultadosYOLO_large"

# Creamos el marco de datos principal
df=pd.DataFrame()

# Columna donde está el nombre de la imagen
col_nombre_img="name"
# Columna donde está indicada la posición del perro
col_estado="class"

parte_perro=("front_left_paw", "front_left_knee", "front_left_elbow", "rear_left_paw", "rear_left_knee", "rear_left_elbow", 
            "front_right_paw", "front_right_knee", "front_right_elbow", "rear_right_paw", "rear_right_knee", "rear_right_elbow", "tail_start",
            "tail_end", "left_ear_base", "right_ear_base", "nose", "chin", "left_ear_tip", "right_ear_tip", "left_eye", "right_eye",
            "withers", "throat")

# ---Creamos el encabezado del excel
columnas=["name"]
for i, pp in enumerate(parte_perro):
    columnas.append(f"{pp}_x [{i}]")
    columnas.append(f"{pp}_y [{i}]")
columnas.append("class")

datos=[]

# Leemos CSV donde están clasificadas las imágenes:
df=pd.read_excel(estado_img)
mapa_estado={}
for i, fila_excel in df.iterrows():
    nombre=str(fila_excel[col_nombre_img]).strip()
    estado=str(fila_excel[col_estado]).strip()
    mapa_estado[nombre]=estado

# ---Leemos los archivos .txt
for archivo_txt in os.listdir(carpeta_txt):
    if archivo_txt.endswith(".txt"):
        # Comprobamos si está en el excel
        nombre_imagen = archivo_txt.replace(".txt", ".jpg")
        estado_val = mapa_estado.get(nombre_imagen)
        # Comprobamos si existe en el excel
        if estado_val is None:
            print(f"La imagen {nombre_imagen} no aparece en el excel")
        else:
            # ---Leemos los puntos del .txt
            ruta_txt=os.path.join(carpeta_txt, archivo_txt)
            fila={"name":nombre_imagen}
            with open(ruta_txt, "r") as f:
                puntos=f.read().strip().split()
                # Contador de puntos
                num_punto=0
                # Contruimos la fila con los valores:
                for i in range(5, len(puntos), 3):
                    if num_punto >= len(parte_perro):
                        print(f"Exceso de puntos. Punto nº: {num_punto}")
                    else:
                        nombre_punto = parte_perro[num_punto]
                        x=puntos[i]
                        y=puntos[i+1]
                        fila[f"{nombre_punto}_x [{num_punto}]"]=x
                        fila[f"{nombre_punto}_y [{num_punto}]"]=y
                        num_punto=num_punto+1
                # sentado
                if estado_val=="2":
                    fila["class"]=2
                    datos.append(fila)
                # de pie
                elif estado_val=="1":
                    fila["class"]=1
                    datos.append(fila)
                # tumbado
                elif estado_val=="0":
                    fila["class"]=0
                    datos.append(fila)

    else:
        print(f"No se puede leer: {archivo_txt}")

# Carpeta donde queremos guardar el csv
carpeta_destino=fr"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\resultados_sin_YOLO"
# Crea la carpeta en caso de no existir:
os.makedirs(carpeta_destino, exist_ok=True)
# Ruta completa del csv:
ruta_csv=os.path.join(carpeta_destino, f"puntos_imgs_sin_v.csv")

df_final=pd.DataFrame(datos, columns=columnas)                

df_final.to_csv(ruta_csv, index=False)
