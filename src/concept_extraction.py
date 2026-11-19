"""
src/concept_extraction.py
Advanced academic concept extraction and explainable coverage verification.
Combines syntactic chunking, entity recognition, and multi-tier semantic matching.
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from model_loader import get_spacy_nlp, get_sentence_transformer
from preprocessing import clean_text

def extract_key_concepts(text: str) -> list:
    """
    Extracts key academic and technical concepts from text using:
    1. Multi-word noun chunks with stop-word filtering
    2. Named entities (products, algorithms, methods)
    3. Part-of-speech patterns (Compound nouns, Adjective + Noun pairs)
    Returns a deduplicated list of clean concept strings.
    """
    if not isinstance(text, str) or not text.strip():
        return []
        
    nlp = get_spacy_nlp()
    doc = nlp(clean_text(text))
    
    concepts = []
    seen = set()
    
    # 1. Noun chunks
    for chunk in doc.noun_chunks:
        # Strip leading determiners/pronouns/punctuations
        tokens = [t.text.strip() for t in chunk if not t.is_stop and not t.is_punct and len(t.text.strip()) > 1]
        if tokens:
            concept_str = " ".join(tokens).lower()
            if len(concept_str) > 2 and concept_str not in seen:
                seen.add(concept_str)
                concepts.append(concept_str)
                
    # 2. Named Entities
    for ent in doc.ents:
        ent_str = clean_text(ent.text, keep_punctuation=False).lower()
        if len(ent_str) > 2 and ent_str not in seen:
            seen.add(ent_str)
            concepts.append(ent_str)
            
    # 3. Compound nouns / Technical adjectives fallback
    for token in doc:
        if token.pos_ in ("NOUN", "PROPN") and not token.is_stop and len(token.text) > 2:
            single_concept = token.text.lower()
            if single_concept not in seen and not any(single_concept in c for c in concepts):
                seen.add(single_concept)
                concepts.append(single_concept)
                
    return concepts

def analyze_concept_coverage(reference_text: str, student_answer: str, semantic_threshold: float = 0.55) -> dict:
    """
    Multi-tier verification of reference concepts in student answers:
    - Tier 1: Exact Substring / Lemma Match (score = 1.0)
    - Tier 2: Token Overlap / Partial Match (score = 0.85)
    - Tier 3: Dense Semantic Embedding Cosine Match against sentences & phrases
    
    Returns explainable diagnostic data with concrete student evidence snippets.
    """
    if not reference_text or not student_answer:
        return {
            "total_concepts": 0,
            "covered_count": 0,
            "coverage_ratio": 0.0,
            "concept_score": 0.0,
            "covered": [],
            "missing": []
        }
        
    reference_concepts = extract_key_concepts(reference_text)
    if not reference_concepts:
        return {
            "total_concepts": 0,
            "covered_count": 0,
            "coverage_ratio": 1.0,
            "concept_score": 100.0,
            "covered": [],
            "missing": []
        }
        
    nlp = get_spacy_nlp()
    model = get_sentence_transformer()
    
    stud_doc = nlp(clean_text(student_answer))
    student_sentences = [sent.text.strip() for sent in stud_doc.sents if sent.text.strip()]
    if not student_sentences:
        student_sentences = [student_answer.strip()]
        
    student_chunks = [c.text.lower() for c in stud_doc.noun_chunks if len(c.text.strip()) > 2]
    candidate_targets = list(set(student_chunks + student_sentences))
    
    # Pre-encode candidate targets and reference concepts
    ref_embeddings = model.encode(reference_concepts, show_progress_bar=False)
    cand_embeddings = model.encode(candidate_targets, show_progress_bar=False) if candidate_targets else None
    
    student_lower = student_answer.lower()
    student_tokens = set([t.lemma_.lower() for t in stud_doc if not t.is_stop and not t.is_punct])
    
    covered = []
    missing = []
    
    for idx, concept in enumerate(reference_concepts):
        concept_tokens = set(concept.lower().split())
        
        # Tier 1: Exact Substring Match
        if concept in student_lower:
            # Find evidence sentence
            evidence = next((s for s in student_sentences if concept in s.lower()), student_sentences[0])
            covered.append({
                "concept": concept,
                "match_type": "Exact Match",
                "similarity": 1.0,
                "evidence": evidence
            })
            continue
            
        # Tier 2: High Token Overlap (at least 75% for multi-word concept)
        if len(concept_tokens) > 1 and len(concept_tokens & student_tokens) / len(concept_tokens) >= 0.75:
            overlap_words = list(concept_tokens & student_tokens)
            evidence = next((s for s in student_sentences if any(w in s.lower() for w in overlap_words)), student_sentences[0])
            covered.append({
                "concept": concept,
                "match_type": "Partial Keyword Match",
                "similarity": 0.85,
                "evidence": evidence
            })
            continue
            
        # Tier 3: Semantic Embedding Match
        best_sim = 0.0
        best_target = ""
        if cand_embeddings is not None and len(cand_embeddings) > 0:
            c_emb = ref_embeddings[idx]
            sims = cosine_similarity([c_emb], cand_embeddings)[0]
            best_idx = int(np.argmax(sims))
            best_sim = float(sims[best_idx])
            best_target = candidate_targets[best_idx]
            
        if best_sim >= semantic_threshold:
            covered.append({
                "concept": concept,
                "match_type": "Semantic Paraphrase",
                "similarity": round(best_sim, 2),
                "evidence": best_target
            })
        else:
            missing.append({
                "concept": concept,
                "highest_similarity": round(best_sim, 2),
                "closest_match": best_target if best_target else "None"
            })
            
    total = len(reference_concepts)
    covered_count = len(covered)
    coverage_ratio = round(covered_count / total, 4) if total > 0 else 0.0
    concept_score = round(coverage_ratio * 100.0, 2)
    
    return {
        "total_concepts": total,
        "covered_count": covered_count,
        "coverage_ratio": coverage_ratio,
        "concept_score": concept_score,
        "covered": covered,
        "missing": missing
    }

if __name__ == "__main__":
    ref = "RSA is an asymmetric cryptographic algorithm that uses a public key for encryption and a private key for decryption. It relies on prime numbers."
    ans = "RSA is a public key encryption method using two keys: one for encrypting and another private key to decrypt messages. Prime factor calculation provides security."
    
    print("Testing Concept Extraction & Coverage...")
    res = analyze_concept_coverage(ref, ans)
    print(f"Coverage: {res['covered_count']}/{res['total_concepts']} ({res['concept_score']}%)")
    for c in res['covered']:
        print(f"  + [{c['match_type']}] '{c['concept']}' -> Evidence: \"{c['evidence']}\"")
    for m in res['missing']:
        print(f"  - [MISSING] '{m['concept']}' (closest: \"{m['closest_match']}\" @ {m['highest_similarity']})")
