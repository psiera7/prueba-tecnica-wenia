SOLUCION DE PRUEBA TECNICA - AUTOMATIZACION OPERATIVA PARA EL PROCESAMIENTO DE DOCUMENTOS

SITUACION PROBLEMA
Este proyecto es una solución para automatizar el procesamiento de cientos de miles de documentos de clientes, aliviando la carga operativa al automatizar la extracción de direcciones.

SOLUCION PROPUESTA

Este script en Python automatiza un flujo de trabajo de geocodificación, transformando un proceso manual en una tarea automatizada y precisa. Es una solución integral, escalable y enfocada en la eficiencia operativa.

CARACTERISTICAS CLAVE DEL ALGORITMO

Subida a Almacenamiento en la Nube: Sube documentos a AWS S3 para un almacenamiento seguro y centralizado.

Extracción de Datos: Lee y extrae direcciones de archivos de texto, Excel, y CSV.

Normalización y Validación: Usa FuzzyWuzzy para validar direcciones, aceptando solo las que superan un 90% de similitud.

Geocodificación: Usa la API de Google Maps para obtener coordenadas exactas y enriquecer los datos.

Visualización de Datos: Genera un mapa interactivo en HTML que muestra todas las ubicaciones procesadas.

TECNOLOGIAS UTILIZADAS:
Python 3.x
boto3
pandas
requests
fuzzywuzzy
folium

GUIA DE INICIO:
Instalacion de Dependencias
Asegurate de tener Python instalado y ejecuta:
pip install pandas requests fuzzywuzzy folium boto3

Configuración:
Reemplaza la clave de la API de Google Maps en el script.

Por qué necesitas una clave de API de Google Maps válida?

La geocodificación de direcciones consume recursos de Google. La clave de API es un identificador único que autentica tus solicitudes y permite a Google rastrear el uso. Sin una clave válida, la API deniega el acceso, y la funcionalidad de mapeo del script no funcionará.

Asegurate de tener tus credenciales de AWS configuradas.

Ejecucion
Ejecuta el script desde la terminal, indicando la ruta del archivo de datos:
python tu_script.py "ruta/a/documento_de_direcciones.xlsx"

El script creara un archivo "mapa_de_direcciones.html" en el mismo directorio.