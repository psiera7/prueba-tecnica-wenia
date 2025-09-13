import os
import argparse
import logging
import boto3
import re
from fuzzywuzzy import fuzz
import requests
import folium
import pandas as pd
import datetime

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CONFIGURACIÓN ---
AWS_BUCKET_NAME = "wenia-prueba-tecnica-2025"
GOOGLE_API_KEY = "AIzaSyDvk8Tozv885nwjLS5fYkBd3is67XSVy_8"

# --- 1. SUBIR DOCUMENTOS A AWS S3 ---
def upload_file_to_s3(file_path: str, bucket_name: str) -> str:
    """Sube un archivo a S3 y devuelve su URL."""
    s3_client = boto3.client('s3')
    object_name = os.path.basename(file_path)
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        logging.info(f"Archivo '{file_path}' subido a S3 como '{object_name}'.")
        return f"s3://{bucket_name}/{object_name}"
    except Exception as e:
        logging.error(f"Error al subir el archivo a S3: {e}")
        return ""

# --- 2. LECTURA DE DIRECCIONES (ARCHIVOS DE DATOS) ---
def get_addresses_from_data_file(file_path: str) -> list:
    """Lee direcciones de un archivo de datos (Excel, CSV, TXT)."""
    addresses = []
    file_extension = os.path.splitext(file_path)[1].lower()

    try:
        if file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
            column_name = 'Dirección'
            if column_name in df.columns:
                addresses = df[column_name].dropna().tolist()
            else:
                logging.error(f"La columna '{column_name}' no se encontró en el archivo Excel.")

        elif file_extension in ['.csv']:
            df = pd.read_csv(file_path)
            column_name = 'Dirección'
            if column_name in df.columns:
                addresses = df[column_name].dropna().tolist()
            else:
                logging.error(f"La columna '{column_name}' no se encontró en el archivo CSV.")
                
        elif file_extension in ['.txt']:
            with open(file_path, 'r', encoding='utf-8') as f:
                addresses = [line.strip() for line in f if line.strip()]

        logging.info(f"Se encontraron {len(addresses)} direcciones en el archivo de datos.")
    except Exception as e:
        logging.error(f"Error al leer el archivo de datos: {e}")
        return []

    return addresses

# --- 3. CREACIÓN DE DIRECCIONES HOMÓNIMAS ---
def generate_homonyms(original_address: str) -> list:
    """Genera una lista de direcciones homónimas basadas en la dirección original."""
    replacements = {
        'carrera': ['kra', 'cra', 'karrera', 'carrera'],
        'calle': ['cll', 'c', 'calle'],
        'transversal': ['trv', 'transversal'],
        'numero': ['nro', 'num', '#', 'numero'],
        'avenida': ['av', 'avenida'],
        '-': ['-', ' '],
    }
    
    parts = re.split(r'(\s+|#|-)', original_address, flags=re.IGNORECASE)
    parts = [p.strip() for p in parts if p.strip()]

    homonyms = {original_address}
    
    temp_homonyms = [parts]
    for i, part in enumerate(parts):
        lower_part = part.lower()
        if lower_part in replacements:
            new_variants = []
            for h in temp_homonyms:
                for replacement in replacements[lower_part]:
                    new_h = list(h)
                    new_h[i] = replacement
                    new_variants.append(new_h)
            temp_homonyms.extend(new_variants)
    
    for h in temp_homonyms:
        homonyms.add(" ".join(h).strip())
        
    logging.info(f"Generadas {len(homonyms)} direcciones homónimas.")
    return list(homonyms)

# --- 4. COMPARACIÓN DE SIMILITUD Y ALMACENAMIENTO ---
def find_and_store_similar_addresses(original_address: str, homonym_list: list) -> list:
    """Compara direcciones y almacena las que tienen un 90% de similitud."""
    similar_addresses = []
    
    for homonym in homonym_list:
        similarity_score = fuzz.ratio(original_address.lower(), homonym.lower())
        
        if similarity_score >= 90:
            similar_addresses.append({
                "original": original_address,
                "homonima": homonym,
                "similitud": similarity_score
            })
    
    if similar_addresses:
        logging.info(f"Encontradas {len(similar_addresses)} direcciones con >90% de similitud.")
    else:
        logging.warning("No se encontraron direcciones homónimas con >90% de similitud.")
        
    return similar_addresses

# --- 5. OBTENCIÓN DE COORDENADAS ---
def get_coordinates_from_address(address: str) -> tuple:
    """Obtiene las coordenadas de una dirección usando la API de Google Geocoding, restringiendo la búsqueda a Colombia."""
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_API_KEY,
        "components": "country:CO" # Restringe la búsqueda a Colombia
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'OK' and data.get('results'):
            location = data['results'][0]['geometry']['location']
            logging.info(f"Coordenadas obtenidas para '{address}': ({location['lat']}, {location['lng']}).")
            return location['lat'], location['lng']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error en la petición a la API de Google: {e}")
    except KeyError:
        logging.error("Formato de respuesta de la API de Google inesperado.")
    
    return None, None

# --- 6. PRESENTACIÓN DEL MAPA ---
def create_map(locations: list):
    """Crea un mapa HTML con marcadores para cada ubicación, sobrescribiendo el anterior."""
    if not locations:
        logging.warning("No hay ubicaciones para generar el mapa.")
        return

    output_filename = "mapa_de_direcciones.html"

    m = folium.Map(location=[locations[0]['lat'], locations[0]['lng']], zoom_start=14)
    
    for loc in locations:
        folium.Marker(
            location=[loc['lat'], loc['lng']],
            tooltip=loc.get('original', 'Dirección'),
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
        
    m.save(output_filename)
    logging.info(f"Mapa interactivo guardado como '{output_filename}'.")

# --- FUNCIÓN PRINCIPAL Y MANEJO DE CONSOLA ---
def main():
    """Función principal para orquestar el flujo del programa."""
    parser = argparse.ArgumentParser(description="Automatiza el procesamiento de documentos para extraer y verificar direcciones.")
    parser.add_argument("document_path", nargs='+', help="Ruta de uno o más archivos de datos (ej. 'documento1.xlsx documento2.txt').")
    args = parser.parse_args()
    
    all_final_results = []
    
    for doc_path in args.document_path:
        logging.info(f"--- Procesando documento: {doc_path} ---")
        
        file_extension = os.path.splitext(doc_path)[1].lower()
        if file_extension in ['.xlsx', '.xls', '.csv', '.txt']:
            addresses_to_process = get_addresses_from_data_file(doc_path)
            if not addresses_to_process:
                logging.warning(f"No se encontraron direcciones en el archivo de datos '{doc_path}'.")
                continue
        else:
            logging.error(f"Formato de archivo no soportado: '{file_extension}'.")
            continue
            
        for original_address in addresses_to_process:
            if not original_address:
                continue
            
            logging.info(f"Intentando geocodificar la dirección: '{original_address}'")
            
            s3_url = upload_file_to_s3(doc_path, AWS_BUCKET_NAME)
            if not s3_url:
                continue
            
            homonyms = generate_homonyms(original_address)
            similar_addresses = find_and_store_similar_addresses(original_address, homonyms)
            
            for address_data in similar_addresses:
                lat, lng = get_coordinates_from_address(address_data['homonima'])
                if lat and lng:
                    address_data['lat'] = lat
                    address_data['lng'] = lng
                    all_final_results.append(address_data)
                else:
                    logging.warning(f"No se pudo obtener coordenadas para la dirección homónima: '{address_data['homonima']}'")
        
    if all_final_results:
        logging.info("\n--- Resultados Finales ---")
        for result in all_final_results:
            print(f"Original: {result['original']} | Coordenadas: ({result['lat']}, {result['lng']}) | Similitud: {result['similitud']}%")
        
        locations_for_map = [{'lat': r['lat'], 'lng': r['lng'], 'original': r['original']} for r in all_final_results]
        create_map(locations_for_map)
    else:
        logging.warning("\nNo se encontraron direcciones válidas para procesar. Esto puede deberse a un formato incorrecto en el archivo de datos.")

if __name__ == "__main__":
    main()