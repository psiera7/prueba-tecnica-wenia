import unittest
import os
import tempfile
import json
from unittest import mock
from unittest.mock import patch, MagicMock

# Importa todas las funciones de tu script principal
import document_processor

# Crea una clase para agrupar todas las pruebas
class TestDocumentProcessorScript(unittest.TestCase):
    
    # --- PRUEBAS PARA LA SUBIDA A S3 ---
    @patch('boto3.client')
    def test_upload_file_to_s3_success(self, mock_boto_client):
        """Prueba que un archivo se subió a S3 con parámetros correctos."""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        file_path = "documento.txt"
        bucket_name = "test-bucket"
        
        # Llama a la función que se está probando
        result = document_processor.upload_file_to_s3(file_path, bucket_name)
        
        # Verifica que el método upload_file fue llamado exactamente una vez
        mock_s3.upload_file.assert_called_once_with(file_path, bucket_name, os.path.basename(file_path))
        self.assertIn(bucket_name, result)
        self.assertIn(os.path.basename(file_path), result)

    @patch('boto3.client')
    def test_upload_file_to_s3_failure(self, mock_boto_client):
        """Prueba que la función maneja fallos de subida correctamente."""
        mock_s3 = MagicMock()
        mock_s3.upload_file.side_effect = Exception("AWS Error")
        mock_boto_client.return_value = mock_s3
        
        result = document_processor.upload_file_to_s3("non_existent_file.txt", "test-bucket")
        
        self.assertEqual(result, "")

    # --- PRUEBAS PARA LA LECTURA DE ARCHIVOS ---
    @patch('pandas.read_excel')
    def test_get_addresses_from_excel(self, mock_read_excel):
        """Prueba que las direcciones son leídas correctamente de un archivo de Excel."""
        mock_df = MagicMock()
        mock_df.columns = ['Dirección', 'OtrosDatos']
        mock_df.__getitem__.return_value.dropna.return_value.tolist.return_value = ["Calle 10 # 20-30", "Carrera 40 # 50-60"]
        mock_read_excel.return_value = mock_df
        
        addresses = document_processor.get_addresses_from_data_file("test.xlsx")
        self.assertEqual(len(addresses), 2)
        self.assertIn("Calle 10 # 20-30", addresses)
        
    def test_get_addresses_from_txt(self):
        """Prueba que las direcciones fueron leídas correctamente de un archivo TXT."""
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as tmp:
            tmp.write("Carrera 12 # 34-56\n")
            tmp.write("Calle 56 # 78-90\n")
            tmp_path = tmp.name
        
        addresses = document_processor.get_addresses_from_data_file(tmp_path)
        self.assertEqual(addresses, ["Carrera 12 # 34-56", "Calle 56 # 78-90"])
        os.remove(tmp_path)

    # --- PRUEBAS PARA LA GENERACIÓN DE HOMÓNIMOS ---
    def test_generate_homonyms_basic(self):
        """Prueba que la función genera correctamente homónimos básicos con la normalización."""
        original_address = "Carrera 10 # 20-30"
        homonyms = document_processor.generate_homonyms(original_address)
        
        # Prueba que se crean y normalizan homónimos específicos
        self.assertIn("kra 10 numero 20 30", homonyms)
        self.assertIn("carrera 10 num 20-30", homonyms)
        self.assertIn("carrera 10 # 20-30", homonyms)
        self.assertGreaterEqual(len(homonyms), 4)

    def test_generate_homonyms_handles_spaces_and_hyphens(self):
        """Prueba que la función maneja variaciones en espaciado y puntuación correctamente."""
        original_address = "Cl 10-20"
        homonyms = document_processor.generate_homonyms(original_address)
        
        self.assertIn("calle 10-20", homonyms)
        self.assertIn("cl-10-20", homonyms)
        self.assertIn("cl 10 20", homonyms)
        
    # --- PRUEBAS PARA LA SIMILITUD DE DIRECCIONES ---
    def test_find_and_store_similar_addresses(self):
        """Prueba que la función identifica correctamente direcciones similares."""
        original = "Calle 50 # 50-50"
        # Se ajusta la lista de homónimos para que dos de ellos tengan similitud >= 90
        # Estos valores tienen un alto grado de similitud con "Calle 50 # 50-50"
        homonyms = ["cll 50 # 50-50", "calle 50 num 50-50"]
        
        similar = document_processor.find_and_store_similar_addresses(original, homonyms)
        
        self.assertEqual(len(similar), 1)
        self.assertGreaterEqual(similar[0]['similitud'], 90)
        
    # --- PRUEBAS PARA LLAMADAS A LA API DE COORDENADAS ---
    @patch('requests.get')
    def test_get_coordinates_success(self, mock_get):
        """Prueba que las coordenadas son obtenidas correctamente de la API de Google."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 'OK',
            'results': [{'geometry': {'location': {'lat': 4.5, 'lng': -74.0}}}]
        }
        mock_get.return_value = mock_response
        
        lat, lng = document_processor.get_coordinates_from_address("Carrera 10 # 20-30")
        
        self.assertEqual(lat, 4.5)
        self.assertEqual(lng, -74.0)
        
    @patch('requests.get')
    def test_get_coordinates_failure(self, mock_get):
        """Prueba que la función maneja fallos de API correctamente."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response
        
        lat, lng = document_processor.get_coordinates_from_address("Invalid Address")
        
        self.assertIsNone(lat)
        self.assertIsNone(lng)

    # --- PRUEBAS PARA LA CREACIÓN DEL MAPA ---
    @patch('folium.Map')
    def test_create_map(self, mock_folium_map):
        """Prueba que la función de creación del mapa trabaja como es esperado."""
        mock_map_instance = MagicMock()
        mock_folium_map.return_value = mock_map_instance
        
        locations = [{'lat': 4.5, 'lng': -74.0, 'original': 'Test Address'}]
        
        document_processor.create_map(locations)
        
        mock_folium_map.assert_called_once()
        mock_map_instance.save.assert_called_once()

if __name__ == '__main__':
    unittest.main()