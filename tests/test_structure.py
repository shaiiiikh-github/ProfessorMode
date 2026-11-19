"""
tests/test_structure.py
Unit tests for readability metrics, lexical diversity, and redundancy.
"""

import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, "src")
if src_dir not in sys.path:
    sys.path.append(current_dir)

from structural_analysis import count_syllables, compute_readability_metrics, analyze_redundancy, analyze_structure

class TestStructuralAnalysis(unittest.TestCase):
    def test_count_syllables(self):
        self.assertEqual(count_syllables("cat"), 1)
        self.assertGreaterEqual(count_syllables("algorithm"), 3)
        self.assertGreaterEqual(count_syllables("cryptography"), 4)

    def test_readability_metrics(self):
        words = ["this", "is", "a", "simple", "test", "sentence"]
        sentences = ["This is a simple test sentence."]
        res = compute_readability_metrics("This is a simple test sentence.", words, sentences)
        self.assertGreater(res["flesch_reading_ease"], 60.0)

    def test_example_detection(self):
        ans_with_example = "Polymorphism allows code flexibility, for example overriding methods in child classes."
        ans_without_example = "Polymorphism allows code flexibility."
        self.assertTrue(analyze_structure(ans_with_example)["has_examples"])
        self.assertFalse(analyze_structure(ans_without_example)["has_examples"])

    def test_redundancy_detection(self):
        repetitive = [
            "RSA uses keys to encrypt data.",
            "RSA uses keys to encrypt data.",
            "RSA uses keys to encrypt data."
        ]
        res = analyze_redundancy(repetitive, "RSA uses keys to encrypt data RSA uses keys to encrypt data".split())
        self.assertGreaterEqual(res["redundancy_score"], 0.50)

if __name__ == "__main__":
    unittest.main()
