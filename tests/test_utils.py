import unittest
from utils import sanitize_filename

class TestUtils(unittest.TestCase):
    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename("user@domain.com"), "user_at_domain_dot_com")
        self.assertEqual(sanitize_filename("hello world"), "hello_world")
        self.assertEqual(sanitize_filename(""), "search")
        self.assertEqual(sanitize_filename(None), "search")

if __name__ == "__main__":
    unittest.main()
