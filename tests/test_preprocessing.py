import unittest

from preprocessing import case_folding, preprocess, remove_stopwords, tokenize


class TestPreprocessing(unittest.TestCase):
    def test_case_folding(self):
        self.assertEqual(case_folding("Machine Learning"), "machine learning")

    def test_tokenization(self):
        self.assertEqual(tokenize("Data, Mining 2026!"), ["data", "mining", "2026"])

    def test_stopword_removal(self):
        self.assertEqual(remove_stopwords(["data", "dan", "mining"]), ["data", "mining"])

    def test_full_preprocess(self):
        result = preprocess("Sistem ini melakukan pencarian dokumen dengan cosine similarity")
        self.assertIn("pencarian", result)
        self.assertIn("dokumen", result)
        self.assertNotIn(" ini ", f" {result} ")


if __name__ == "__main__":
    unittest.main()
