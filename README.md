# prueba-tecnica-wenia

Este proyecto demuestra la automatización de procesos operativos. El script lee direcciones de archivos de datos (.xlsx, .txt), las geocodifica con la API de Google Maps, validándolas con FuzzyWuzzy, y las visualiza en un mapa interactivo. Una solución completa para transformar datos brutos en inteligencia geográfica.

## SOLUCIÓN DE PRUEBA TÉCNICA - AUTOMATIZACIÓN OPERATIVA PARA EL PROCESAMIENTO DE DOCUMENTOS

### SITUACIÓN PROBLEMA
Este proyecto es una solución para automatizar el procesamiento de cientos de miles de documentos de clientes, aliviando la carga operativa al automatizar la extracción de direcciones.

### SOLUCIÓN PROPUESTA

Este script en Python automatiza un flujo de trabajo de geocodificación, transformando un proceso manual en una tarea automatizada y precisa. Es una solución integral, escalable y enfocada en la eficiencia operativa.

## CARACTERÍSTICAS CLAVE DEL ALGORITMO

- **Subida a Almacenamiento en la Nube**: Sube documentos a AWS S3 para un almacenamiento seguro y centralizado.

- **Extracción de Datos**: Lee y extrae direcciones de archivos de texto, Excel, y CSV.

- **Normalización y Validación**: Usa FuzzyWuzzy para validar direcciones, aceptando solo las que superan un 90% de similitud.

- **Geocodificación**: Usa la API de Google Maps para obtener coordenadas exactas y enriquecer los datos.

- **Visualización de Datos**: Genera un mapa interactivo en HTML que muestra todas las ubicaciones procesadas.

## TECNOLOGÍAS UTILIZADAS

- Python 3.x
- boto3
- pandas
- requests
- fuzzywuzzy
- folium

## GUÍA DE INICIO

### Instalación de Dependencias
Asegúrate de tener Python instalado y ejecuta:
```bash
pip install -r requirements.txt
```

### Configuración

1. **Configuración de AWS**:
   - Asegúrate de tener tus credenciales de AWS configuradas (usando AWS CLI, variables de entorno del sistema, o archivo de credenciales)

2. **Configuración de Google Maps API**:
   - Obtén una clave de API de Google Maps desde la [Google Cloud Console](https://console.cloud.google.com/)
   - Habilita la API de Geocoding para tu proyecto

**¿Por qué necesitas una clave de API de Google Maps válida?**
La geocodificación de direcciones consume recursos de Google. La clave de API es un identificador único que autentica tus solicitudes y permite a Google rastrear el uso. Sin una clave válida, la API deniega el acceso, y la funcionalidad de mapeo del script no funcionará.

### Ejecución
Ejecuta el script desde la terminal, indicando la ruta del archivo de datos:
```bash
python document_processor.py "ruta/a/documento_de_direcciones.xlsx"
```
