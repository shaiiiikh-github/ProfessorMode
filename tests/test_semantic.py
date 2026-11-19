"""
tests/test_semantic.py
Unit tests for dense semantic similarity and question relevance.
"""

import unittest
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, "src")
if src_dir not in sys.path:
    sys.path.append(src_dir)

from semantic_similarity import compute_semantic_similarity, compute_question_relevance

class TestSemanticSimilarity(unittest.TestCase):
    def test_identical_sentences(self):
        text = "RSA is an asymmetric cryptographic algorithm using public and private keys."
        res = compute_semantic_similarity(text, text)
        self.assertGreaterEqual(res["semantic_score"], 95.0)

    def test_paraphrase_similarity(self):
        ref = "RSA uses a public key for encryption and a private key for decryption."
        ans = "Public keys encrypt data in RSA while private keys are used for decrypting."
        res = compute_semantic_similarity(ans, ref)
        self.assertGreaterEqual(res["semantic_score"], 70.0)

    def test_irrelevant_similarity(self):
        ref = "Deadlock happens when processes wait circularly for allocated resources."
        ans = "The weather today is warm and sunny with scattered clouds."
        res = compute_semantic_similarity(ans, ref)
        self.assertLess(res["semantic_score"], 35.0)

    def test_question_relevance(self):
        q = "Explain database normalization."
        ans = "Normalization structures tables into normal forms to eliminate data duplication."
        rel = compute_question_relevance(q, ans)
        self.assertGreater(rel, 0.40)

if __name__ == "__main__":
    unittest.main()
