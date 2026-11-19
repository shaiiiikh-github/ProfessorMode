"""
tests/test_concept.py
Unit tests for concept extraction and multi-tier coverage analysis.
"""

import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from concept_extraction import extract_key_concepts, analyze_concept_coverage

class TestConceptExtraction(unittest.TestCase):
    def test_extract_key_concepts(self):
        ref = "RSA is an asymmetric cryptographic algorithm that uses prime numbers."
        concepts = extract_key_concepts(ref)
        self.assertGreater(len(concepts), 0)
        # Check that meaningful technical phrases or words were captured
        joined = " ".join(concepts).lower()
        self.assertTrue("rsa" in joined or "cryptographic" in joined or "prime" in joined)

    def test_concept_coverage_full(self):
        ref = "RSA is an asymmetric algorithm using public keys and private keys."
        ans = "RSA is an asymmetric algorithm where public keys encrypt and private keys decrypt."
        res = analyze_concept_coverage(ref, ans)
        self.assertGreaterEqual(res["coverage_ratio"], 0.70)
        self.assertEqual(len(res["missing"]), 0)

    def test_concept_coverage_missing(self):
        ref = "Deadlock requires mutual exclusion, hold and wait, no preemption, and circular wait."
        ans = "Deadlock happens when processes freeze."
        res = analyze_concept_coverage(ref, ans)
        self.assertGreater(len(res["missing"]), 0)

if __name__ == "__main__":
    unittest.main()
