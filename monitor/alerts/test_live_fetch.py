from unittest.mock import patch
from django.test import SimpleTestCase
from .live_fetch import fetch_category, CollectionError

class LiveFetchTests(SimpleTestCase):
    @patch("alerts.live_fetch.socket.getaddrinfo")
    def test_unapproved_url_never_resolves(self, resolve):
        with patch.dict("os.environ", {"APPROVED_CATEGORY_URLS": ""}):
            with self.assertRaises(CollectionError):
                fetch_category("https://example.com/category")
        resolve.assert_not_called()

    @patch("alerts.live_fetch.socket.getaddrinfo")
    def test_private_resolution_rejected(self, resolve):
        url = "https://example.com/category"
        resolve.return_value = [(2, 1, 6, "", ("127.0.0.1", 443))]
        with patch.dict("os.environ", {"APPROVED_CATEGORY_URLS": url}):
            with self.assertRaises(CollectionError):
                fetch_category(url)
