"""
tests/test_preprocessing.py
Unit tests for text cleaning, contraction expansion, and tokenization.
"""

import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from preprocessing import clean_text, expand_contractions, preprocess_text, extract_sentences

class TestPreprocessing(unittest.TestCase):
    def test_expand_contractions(self):
        text = "It's obvious that you can't and won't fail."
        expanded = expand_contractions(text)
        self.assertIn("it is", expanded.lower())
        self.assertIn("cannot", expanded.lower())
        self.assertIn("will not", expanded.lower())

    def test_clean_text_removes_html(self):
        raw = "<p>This is a <b>bold</b> test.</p>"
        cleaned = clean_text(raw)
        self.assertEqual(cleaned, "This is a bold test.")

    def test_preprocess_text_lemmatization(self):
        text = "Encryption algorithms are running efficiently."
        processed = preprocess_text(text, remove_stopwords=True, lemmatize=True)
        # "running" should lemmatize to "run", "algorithms" to "algorithm"
        self.assertIn("run", processed)
        self.assertIn("algorithm", processed)

    def test_extract_sentences(self):
        text = "First sentence here. Second sentence follows! Is this the third?"
        sents = extract_sentences(text)
        self.assertEqual(len(sents), 3)

    def test_empty_input(self):
        self.assertEqual(clean_text(""), "")
        self.assertEqual(preprocess_text(""), "")
        self.assertEqual(extract_sentences(""), [])

if __name__ == "__main__":
    unittest.main()
