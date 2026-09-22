import unittest
from unittest.mock import patch, MagicMock
import threading
from api import (
    check_intelx, retrieve_intelx_results, get_api_credits,
    terminate_intelx_search, get_last_search_id, MEDIA_TYPE_MAP,
)

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

    def test_check_intelx_cancellation(self):
        cancel_evt = threading.Event()
        cancel_evt.set()
        success, err, sid = check_intelx("domain.com", "valid_key", cancel_event=cancel_evt)
        self.assertFalse(success)
        self.assertIn("cancelada", err.lower())

    @patch("api.requests.post")
    def test_terminate_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp
        self.assertTrue(terminate_intelx_search("sid-123", "key-abc"))
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs.get("json"), {"id": "sid-123"})

    def test_terminate_invalid_input(self):
        self.assertFalse(terminate_intelx_search("", "key-abc"))
        self.assertFalse(terminate_intelx_search("sid-123", ""))
        self.assertFalse(terminate_intelx_search(None, None))

    @patch("api.requests.post")
    def test_terminate_server_error(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("down")
        self.assertFalse(terminate_intelx_search("sid-123", "key-abc"))

    @patch("api.requests.post")
    def test_check_intelx_tracks_last_search_id(self, mock_post):
        mock_resp_search = MagicMock()
        mock_resp_search.status_code = 200
        mock_resp_search.json.return_value = {"id": "tracked-id", "status": 0}
        mock_post.return_value = mock_resp_search
        with patch("api.retrieve_intelx_results") as mock_retrieve:
            mock_retrieve.return_value = (True, {"records": []})
            check_intelx("domain.com", "valid_key")
            self.assertEqual(get_last_search_id(), "tracked-id")

if __name__ == "__main__":
    unittest.main()
