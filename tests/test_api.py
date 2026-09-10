import unittest
from unittest.mock import patch, MagicMock
import threading
from api import check_intelx, retrieve_intelx_results, get_api_credits, MEDIA_TYPE_MAP

class TestAPI(unittest.TestCase):
    def test_media_type_map(self):
        self.assertEqual(MEDIA_TYPE_MAP.get(1), "Paste Document")
        self.assertEqual(MEDIA_TYPE_MAP.get(15), "PDF Document")
        self.assertEqual(MEDIA_TYPE_MAP.get(999, "Unknown"), "Unknown")

    def test_check_intelx_invalid_input(self):
        success, err, sid = check_intelx("", "fake_key")
        self.assertFalse(success)
        self.assertIn("término", err)
        self.assertIsNone(sid)

        success, err, sid = check_intelx("test@example.com", "")
        self.assertFalse(success)
        self.assertIn("clave API", err)
        self.assertIsNone(sid)

    @patch("api.requests.post")
    def test_check_intelx_success(self, mock_post):
        mock_resp_search = MagicMock()
        mock_resp_search.status_code = 200
        mock_resp_search.json.return_value = {"id": "test-search-id", "status": 0}
        mock_post.return_value = mock_resp_search

        with patch("api.retrieve_intelx_results") as mock_retrieve:
            mock_retrieve.return_value = (True, {"records": []})
            success, data, sid = check_intelx("domain.com", "valid_key")
            self.assertTrue(success)
            self.assertEqual(sid, "test-search-id")

    @patch("api.requests.get")
    def test_get_api_credits(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "paths": {
                "/intelligent/search": {
                    "Credit": 150
                }
            }
        }
        mock_get.return_value = mock_resp

        success, credits = get_api_credits("fake_key")
        self.assertTrue(success)
        self.assertEqual(credits, 150)

if __name__ == "__main__":
    unittest.main()
