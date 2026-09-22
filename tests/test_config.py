import unittest
from unittest.mock import patch, MagicMock
from config import get_text, get_stored_api_key, save_stored_api_key

class TestConfig(unittest.TestCase):
    def test_get_text_translations(self):
        self.assertEqual(get_text("Buscar", "es"), "🔍 Buscar")
        self.assertEqual(get_text("Buscar", "en"), "🔍 Search")
        self.assertEqual(get_text("non_existent_key", "es"), "non_existent_key")

    @patch("keyring.get_password")
    def test_get_stored_api_key_from_keyring(self, mock_get_password):
        mock_get_password.return_value = "keyring_secret_123"
        key = get_stored_api_key()
        self.assertEqual(key, "keyring_secret_123")

if __name__ == "__main__":
    unittest.main()
