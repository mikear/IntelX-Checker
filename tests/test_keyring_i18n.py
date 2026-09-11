import unittest
from unittest.mock import patch, MagicMock
from keyring_storage import get_api_key, set_api_key
from i18n import t, LANGUAGES

class TestKeyringAndI18n(unittest.TestCase):
    def test_i18n_t(self):
        self.assertEqual(t("Buscar", "es"), "Buscar")
        self.assertEqual(t("Buscar", "en"), "Search")

    @patch("keyring_storage.set_key")
    @patch("keyring.delete_password")
    @patch("keyring.set_password")
    @patch("keyring.get_password")
    def test_keyring_storage_functions(self, mock_get_pw, mock_set_pw, mock_del_pw, mock_set_key):
        mock_get_pw.return_value = "mock_secret_key"
        self.assertTrue(set_api_key("mock_secret_key"))
        mock_set_pw.assert_called_with("IntelX_Checker", "INTELX_API_KEY", "mock_secret_key")
        self.assertEqual(get_api_key(), "mock_secret_key")

if __name__ == "__main__":
    unittest.main()
