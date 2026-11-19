"""
tests/test_quality_engine.py
Unit tests for end-to-end answer quality evaluation and grading logic.
"""

import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, "src")
if src_dir not in sys.path:
    sys.path.append(current_dir)

from quality_engine import evaluate_answer_quality, determine_letter_grade

class TestQualityEngine(unittest.TestCase):
    def test_determine_letter_grade(self):
        self.assertEqual(determine_letter_grade(95.0)[0], "A+")
        self.assertEqual(determine_letter_grade(85.0)[0], "A")
        self.assertEqual(determine_letter_grade(75.0)[0], "B")
        self.assertEqual(determine_letter_grade(65.0)[0], "C")
        self.assertEqual(determine_letter_grade(55.0)[0], "D")
        self.assertEqual(determine_letter_grade(30.0)[0], "F")

    def test_evaluate_answer_quality_high_grade(self):
        q = "Explain the working of RSA encryption."
        ref = "RSA is an asymmetric cryptographic algorithm that uses a public key for encryption and a private key for decryption. It relies on the mathematical difficulty of factoring the product of two large prime numbers."
        ans = "RSA is a public key encryption technique where two keys are used. One key encrypts the data and the private key decrypts it. It is based on prime numbers."
        
        rep = evaluate_answer_quality(q, ans, ref)
        self.assertGreaterEqual(rep["final_score"], 70.0)
        self.assertIn(rep["letter_grade"], ["A+", "A", "B"])
        self.assertGreaterEqual(len(rep["strengths"]), 1)

    def test_evaluate_blank_submission(self):
        rep = evaluate_answer_quality("What is a deadlock?", "", "Deadlock is circular wait.")
        self.assertEqual(rep["final_score"], 0.0)
        self.assertEqual(rep["letter_grade"], "F")

if __name__ == "__main__":
    unittest.main()
