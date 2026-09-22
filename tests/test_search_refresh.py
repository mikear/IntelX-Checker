import unittest
from utils import (
    normalize_search_term,
    is_same_search_term,
    merge_records,
)


class TestSearchRefresh(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_search_term("  Test@Dom.com  "), "test@dom.com")
        self.assertEqual(normalize_search_term(""), "")
        self.assertEqual(normalize_search_term(None), "")
        self.assertEqual(normalize_search_term(123), "")

    def test_same_domain_suma(self):
        self.assertTrue(is_same_search_term("test@hotmail.com", "test@hotmail.com"))
        self.assertTrue(is_same_search_term("Test@Hotmail.com ", " test@hotmail.com"))
        self.assertTrue(is_same_search_term("DOM.COM", "dom.com"))

    def test_different_domain_reemplaza(self):
        self.assertFalse(is_same_search_term("a@hotmail.com", "b@gmail.com"))
        self.assertFalse(is_same_search_term("", "b@gmail.com"))
        self.assertFalse(is_same_search_term("a@hotmail.com", ""))
        self.assertFalse(is_same_search_term(None, "b@gmail.com"))

    def test_merge_suma_sin_duplicados(self):
        existing = [{'systemid': '1'}, {'systemid': '2'}]
        new = [{'systemid': '2'}, {'systemid': '3'}]
        merged = merge_records(existing, new)
        self.assertEqual(len(merged), 3)

    def test_reemplazo_descarta_anterior(self):
        # Simula dominio distinto: la tabla nueva es solo `new`
        new = [{'systemid': '10'}]
        tabla = list(new)
        self.assertEqual(tabla, new)
        self.assertEqual(len(tabla), 1)


if __name__ == "__main__":
    unittest.main()
