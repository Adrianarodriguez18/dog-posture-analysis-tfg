# dog-posture-analysis-tfg
## Descripción
Este repositorio contiene el desarrollo realizado para llegar a una solución válida para el TFG. Se centra en los entrenamientos de detección de pose, de detección de postura de riesgo y en la clasificación de imágenes.
## Estructura del proyecto
**additional_scripts**

Contiene scripts auxiliares empleados para clasificar las imágenes según la postura del perro. Con los puntos clave del perro estudia su posición con una fórmula matemática. Las imágenes que se estudian fueron clasificadas manualmente anteriormente, por lo que, la clasificación será si el sistema ha predicho la posición del perro correctamente.

**pose_detection**

Contiene el cuaderno de júpiter que se encarga de entrenar el modelo de YOLO para detectar los puntos clave. Además, también se encuentra el archivo `yaml` que se emplea para poder realizar el entreno.

**risk_posture_detection**

Incluye los entrenamientos y los análisis de los diferentes modelos empleados parra clasificar la postura del perro. Asimismo, también se encuentra el entrenamiento del mejor modelo donde se realiza el test con el mismo.
