"""
src/structural_analysis.py
Comprehensive linguistic, structural, readability, and redundancy analyzer.
Computes Flesch Reading Ease, Grade Level, Lexical Diversity (TTR),
Syntactic Complexity, Evidence Markers, and Semantic/Lexical Redundancy.
"""

import os
import re
import sys
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from model_loader import get_spacy_nlp, get_sentence_transformer
from preprocessing import clean_text

def count_syllables(word: str) -> int:
    """
    Estimates syllable count of an English word using phonetic regex heuristics.
    """
    word = word.lower().strip()
    if not word or not word.isalpha():
        return 1
    if len(word) <= 3:
        return 1
    # Remove trailing silent e / es / ed
    word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
    word = re.sub(r'^y', '', word)
    syllables = len(re.findall(r'[aeiouy]{1,2}', word))
    return max(1, syllables)

def compute_readability_metrics(text: str, words: list, sentences: list) -> dict:
    """
    Computes standard academic readability benchmarks:
    - Flesch Reading Ease (FRE)
    - Flesch-Kincaid Grade Level (FKGL)
    - Automated Readability Index (ARI)
    """
    word_count = len(words)
    sentence_count = max(1, len(sentences))
    
    if word_count == 0:
        return {
            "flesch_reading_ease": 0.0,
            "flesch_grade_level": 0.0,
            "automated_readability_index": 0.0,
            "reading_band": "N/A"
        }
        
    total_syllables = sum(count_syllables(w) for w in words)
    total_chars = sum(len(w) for w in words)
    
    asl = word_count / sentence_count  # Average Sentence Length
    asw = total_syllables / word_count # Average Syllables per Word
    cpw = total_chars / word_count     # Characters per Word
    
    # Flesch Reading Ease formula
    fre = 206.835 - (1.015 * asl) - (84.6 * asw)
    fre = round(max(0.0, min(100.0, fre)), 2)
    
    # Flesch-Kincaid Grade Level formula
    fkgl = (0.39 * asl) + (11.8 * asw) - 15.59
    fkgl = round(max(1.0, fkgl), 2)
    
    # Automated Readability Index (ARI) formula
    ari = (4.71 * cpw) + (0.5 * asl) - 21.43
    ari = round(max(1.0, ari), 2)
    
    if fre >= 70:
        band = "Standard / Accessible"
    elif fre >= 50:
        band = "College / Academic"
    elif fre >= 30:
        band = "Advanced College / Technical"
    else:
        band = "Graduate / Highly Complex"
        
    return {
        "flesch_reading_ease": fre,
        "flesch_grade_level": fkgl,
        "automated_readability_index": ari,
        "reading_band": band
    }

def analyze_redundancy(sentences: list, words: list) -> dict:
    """
    Evaluates both Lexical and Semantic Redundancy:
    1. Maximum Pairwise TF-IDF Cosine Similarity
    2. Maximum Pairwise Semantic Transformer Cosine Similarity
    3. Repeated N-gram frequency (phrasal padding)
    """
    if len(sentences) <= 1:
        return {
            "redundancy_score": 0.0,
            "lexical_redundancy": 0.0,
            "semantic_redundancy": 0.0,
            "repeated_ngrams": [],
            "redundancy_level": "Low"
        }
        
    # 1. Lexical Redundancy (TF-IDF)
    lexical_max = 0.0
    try:
        tfidf = TfidfVectorizer().fit_transform(sentences)
        tfidf_sim = cosine_similarity(tfidf, tfidf)
        np.fill_diagonal(tfidf_sim, 0.0)
        lexical_max = float(np.max(tfidf_sim))
    except Exception:
        lexical_max = 0.0
        
    # 2. Semantic Redundancy (Sentence Embeddings)
    semantic_max = 0.0
    try:
        model = get_sentence_transformer()
        embs = model.encode(sentences, show_progress_bar=False)
        sem_sim = cosine_similarity(embs, embs)
        np.fill_diagonal(sem_sim, 0.0)
        semantic_max = float(np.max(sem_sim))
    except Exception:
        semantic_max = 0.0
        
    # 3. N-gram Repetition (Trigrams)
    repeated_ngrams = []
    if len(words) >= 6:
        trigrams = [tuple(words[i:i+3]) for i in range(len(words)-2)]
        from collections import Counter
        counts = Counter(trigrams)
        repeated_ngrams = [" ".join(tg) for tg, c in counts.items() if c > 1]
        
    # Unified redundancy index (weighted average)
    ngram_factor = min(1.0, len(repeated_ngrams) * 0.2)
    unified_score = round(0.4 * lexical_max + 0.4 * max(0.0, semantic_max) + 0.2 * ngram_factor, 2)
    
    if unified_score > 0.60:
        level = "High"
    elif unified_score > 0.35:
        level = "Moderate"
    else:
        level = "Low"
        
    return {
        "redundancy_score": unified_score,
        "lexical_redundancy": round(lexical_max, 2),
        "semantic_redundancy": round(semantic_max, 2),
        "repeated_ngrams": repeated_ngrams[:3],
        "redundancy_level": level
    }

def analyze_structure(student_answer: str, reference_answer: str = "") -> dict:
    """
    Full structural, stylistic, and linguistic analysis of student answer.
    """
    if not isinstance(student_answer, str) or not student_answer.strip():
        return {
            "sentence_count": 0,
            "word_count": 0,
            "avg_sentence_length": 0.0,
            "lexical_diversity": 0.0,
            "hapax_ratio": 0.0,
            "has_examples": False,
            "has_discourse_markers": False,
            "readability": compute_readability_metrics("", [], []),
            "redundancy": analyze_redundancy([], []),
            "structural_score": 0.0
        }
        
    nlp = get_spacy_nlp()
    doc = nlp(clean_text(student_answer))
    
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    sentence_count = len(sentences)
    
    words = [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
    word_count = len(words)
    
    avg_sentence_len = round(word_count / sentence_count, 2) if sentence_count > 0 else 0.0
    
    # Lexical Diversity: Type-Token Ratio (TTR)
    unique_lemmas = set(token.lemma_.lower() for token in doc if not token.is_punct and not token.is_space)
    lexical_diversity = round(len(unique_lemmas) / word_count, 2) if word_count > 0 else 0.0
    
    # Hapax Legomena Ratio (words appearing exactly once)
    from collections import Counter
    lemma_counts = Counter(token.lemma_.lower() for token in doc if not token.is_punct and not token.is_space)
    hapax_count = sum(1 for c in lemma_counts.values() if c == 1)
    hapax_ratio = round(hapax_count / len(unique_lemmas), 2) if unique_lemmas else 0.0
    
    # Example & Evidence Markers
    example_patterns = [
        r'\bfor\s+example\b', r'\bfor\s+instance\b', r'\be\.?g\.?\b',
        r'\bsuch\s+as\b', r'\bspecifically\b', r'\billustrate\b',
        r'\bin\s+case\s+of\b', r'\bdemonstrated\s+by\b'
    ]
    has_examples = any(re.search(pat, student_answer, re.IGNORECASE) for pat in example_patterns)
    
    # Academic Discourse & Transition Markers
    discourse_markers = [
        "furthermore", "moreover", "consequently", "therefore",
        "however", "in contrast", "specifically", "in addition",
        "as a result", "whereas", "alternatively", "hence"
    ]
    has_discourse = any(dm in student_answer.lower() for dm in discourse_markers)
    
    # Readability
    readability = compute_readability_metrics(student_answer, words, sentences)
    
    # Redundancy
    redundancy = analyze_redundancy(sentences, words)
    
    # Balanced Structural Score Calculation (0 to 100)
    # Evaluates length adequacy, discourse connectivity, vocabulary richness, and readability
    ref_word_count = len(reference_answer.split()) if reference_answer else 30
    length_ratio = min(1.2, word_count / max(10, ref_word_count))
    
    # Base length score (max 50 pts)
    length_pts = min(50.0, length_ratio * 45.0)
    if word_count >= 15:
        length_pts = max(30.0, length_pts)
        
    # Diversity & vocabulary pts (max 25 pts)
    vocab_pts = min(25.0, lexical_diversity * 35.0)
    
    # Discourse & evidence bonus (max 15 pts)
    evidence_pts = 0.0
    if has_examples:
        evidence_pts += 8.0
    if has_discourse:
        evidence_pts += 7.0
        
    # Readability health (max 10 pts)
    readability_pts = 10.0 if (40 <= readability['flesch_reading_ease'] <= 85) else 5.0
    
    structural_score = round(min(100.0, length_pts + vocab_pts + evidence_pts + readability_pts), 2)
    
    return {
        "sentence_count": sentence_count,
        "word_count": word_count,
        "avg_sentence_length": avg_sentence_len,
        "lexical_diversity": lexical_diversity,
        "hapax_ratio": hapax_ratio,
        "has_examples": has_examples,
        "has_discourse_markers": has_discourse,
        "readability": readability,
        "redundancy": redundancy,
        "structural_score": structural_score
    }

if __name__ == "__main__":
    test_ans = (
        "RSA is an asymmetric cryptographic algorithm. For example, it secures HTTPS web traffic. "
        "Consequently, the public key encrypts data while the private key performs decryption."
    )
    res = analyze_structure(test_ans, reference_answer="RSA is asymmetric encryption using public and private keys.")
    print("Structural Analysis Result:")
    print(f"Words: {res['word_count']}, Sentences: {res['sentence_count']}, FRE: {res['readability']['flesch_reading_ease']}")
    print(f"Structural Score: {res['structural_score']} / 100, Redundancy: {res['redundancy']['redundancy_level']}")
