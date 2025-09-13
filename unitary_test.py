import unittest
import os
import tempfile
import json
from unittest import mock
from unittest.mock import patch, MagicMock

# Importa todas las funciones de tu script principal
# Asume que el archivo principal se llama main.py
from main import (
    get_addresses_from_data_file,
    generate_homonyms,
    find_and_store_similar_addresses,
    get_coordinates_from_address,
    create_map,
    upload_file_to_s3
)

# Creamos una clase para agrupar todas las pruebas
class TestGeocodingScript(unittest.TestCase):
    
    # --- PRUEBAS PARA LA LECTURA DE ARCHIVOS ---
    def test_get_addresses_from_data_file_txt(self):
        """Prueba que la función lee correctamente un archivo .txt."""
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
            tmp.write("Carrera 12 # 34-56\n")
            tmp.write("Calle 56 # 78-90\n")
            tmp_path = tmp.name
        
        addresses = get_addresses_from_data_file(tmp_path)
        self.assertEqual(addresses, ["Carrera 12 # 34-56", "Calle 56 # 78-90"])
        os.remove(tmp_path)

    # --- PRUEBAS PARA LA GENERACIÓN DE HOMÓNIMOS ---
    def test_generate_homonyms(self):
        """Prueba que la función genera correctamente direcciones homónimas."""
        original_address = "Carrera 10 # 20-30"
        homonyms = generate_homonyms(original_address)
        self.assertIn("kra 10 # 20-30", homonyms)
        self.assertIn("carrera 10 # 20-30", homonyms)
        self.assertIn("Carrera 10 numero 20-30", homonyms)
        self.assertGreaterEqual(len(homonyms), 3)

    # --- PRUEBAS PARA LA BÚSQUEDA DE SIMILITUD ---
    def test_find_and_store_similar_addresses(self):
        """Prueba que la función filtra las direcciones por similitud."""
        original = "Calle 50 # 50-50"
        homonyms = ["Cl 50 # 50-50", "Calle 50-50", "Carrera 10-20"]
        similar = find_and_store_similar_addresses(original, homonyms)
        
        self.assertEqual(len(similar), 1)
        self.assertEqual(similar[0]['homonima'], "Cl 50 # 50-50")
        self.assertGreaterEqual(similar[0]['similitud'], 90)

    # --- PRUEBAS CON MOCKING PARA LA API DE GOOGLE MAPS ---
    @patch('requests.get')
    def test_get_coordinates_from_address_success(self, mock_get):
        """Prueba que se obtienen las coordenadas correctamente."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"geometry": {"location": {"lat": 4.5, "lng": -74.0}}}],
            "status": "OK"
        }
        mock_get.return_value = mock_response
        
        lat, lng = get_coordinates_from_address("Carrera 10 # 20-30")
        self.assertEqual(lat, 4.5)
        self.assertEqual(lng, -74.0)

    @patch('requests.get')
    def test_get_coordinates_from_address_failure(self, mock_get):
        """Prueba que la función maneja fallos de la API."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response
        
        lat, lng = get_coordinates_from_address("Dirección inválida")
        self.assertIsNone(lat)
        self.assertIsNone(lng)

    # --- PRUEBAS CON MOCKING PARA AWS S3 ---
    @patch('boto3.client')
    def test_upload_file_to_s3(self, mock_boto_client):
        """Prueba que el archivo se sube a S3 con los parámetros correctos."""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        file_path = "documento.txt"
        bucket_name = "test-bucket"
        
        upload_file_to_s3(file_path, bucket_name)
        
        # Verifica que el método upload_file fue llamado exactamente una vez
        mock_s3.upload_file.assert_called_once_with(file_path, bucket_name, "documento.txt")

    # --- PRUEBAS PARA LA CREACIÓN DEL MAPA ---
    def test_create_map(self):
        """Prueba que se crea el archivo HTML con el mapa."""
        locations = [{"lat": 4.5, "lng": -74.0, "original": "Dirección de prueba"}]
        output_filename = "test_mapa.html"
        
        create_map(locations, output_filename)
        
        self.assertTrue(os.path.exists(output_filename))
        
        with open(output_filename, 'r') as f:
            content = f.read()
            self.assertIn("folium.Map", content)
            self.assertIn("4.5", content)
            self.assertIn("-74.0", content)
            
        os.remove(output_filename)

if __name__ == '__main__':
    unittest.main()