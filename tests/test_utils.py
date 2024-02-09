import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.append('/src/RagTime/src/app')
from src.app import utils

class UtilsTest(unittest.TestCase):
    @patch('RagTime.src.app.utils.Chroma')
    @patch('RagTime.src.app.utils.os')
    @patch('RagTime.src.app.utils.json')
    @patch('RagTime.src.app.utils._log')
    def setUp(self, mock_log, mock_json, mock_os, mock_chroma):
        self.mock_log = mock_log
        self.mock_json = mock_json
        self.mock_os = mock_os
        self.mock_chroma = mock_chroma

    def test_update_params(self):
        collection_name = 'test_collection'
        utils.update_params(collection_name)
        # TODO: Add assertions here to verify the behavior of update_params

    def test_create_new_vector_store(self):
        db_name = 'test_db'
        utils.create_new_vector_store(db_name)
        # TODO: Add assertions here to verify the behavior of create_new_vector_store

if __name__ == '__main__':
    unittest.main()
