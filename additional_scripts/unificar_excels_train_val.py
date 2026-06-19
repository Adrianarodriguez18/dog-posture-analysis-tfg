import pandas as pd
import os

modelo="small"
carpeta_origen=fr"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\resultadosYOLO_{modelo}"
carpeta_destino=fr"C:\Users\18adr\OneDrive - Universidade da Coruña\Documentos\Curso 25-26\tfg\imgClasificadas\train_val\resultadosYOLO_{modelo}"
# Comprobamos que la carpeta de destino extista
if not os.path.exists(carpeta_destino):
    os.makedirs(carpeta_destino)

# Creamos variable para almacenar los archivos de entrada en la carpeta:
lista_archivos=os.listdir(carpeta_origen)

# Ahora mismo lista_archivos_excel tiene todos los archivos que hay en la carpeta

# Creamos el marco de datos principal
df=pd.DataFrame()

archivos_objetivos=["imgs_down.csv","imgs_up.csv","imgs_sit.csv"]

for archivo in lista_archivos:
    if archivo in archivos_objetivos:
        print(f"Leyendo {archivo}")
        # Cogemos bien la ruta del archivo
        ruta_archivo=os.path.join(carpeta_origen, archivo)
        # Creamos un nuevo marco de datos para leer y almacenarlos individualmente:
        df1=pd.read_csv(ruta_archivo, sep=";")
        # Añadimos el archivo al marco de datos principal:
        df=pd.concat([df, df1], ignore_index=True)

# Ruta salida correcta:
ruta_salida=os.path.join(carpeta_destino, f"imgs_clasificadas_{modelo}.xlsx")

# Ahora convertimos el archivo en .xlsx y lo exportamos:
df.to_excel(ruta_salida, index=False)

print("Archivos unificados")
