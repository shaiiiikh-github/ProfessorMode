"""
src/semantic_similarity.py
Multi-granular semantic understanding using dense Transformer embeddings.
Evaluates global answer similarity, sentence-level proposition alignment,
and question relevance check.
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.stats import pearsonr, spearmanr
from model_loader import get_sentence_transformer, get_spacy_nlp
from preprocessing import clean_text

def compute_semantic_similarity(student_answer: str, reference_answer: str) -> dict:
    """
    Computes fine-grained semantic alignment:
    1. Global Embedding Cosine Similarity
    2. Propositional Cross-Sentence Alignment (coverage of reference propositions)
    3. Blended Composite Semantic Score (0 to 100)
    """
    if not student_answer or not reference_answer:
        return {
            "global_similarity": 0.0,
            "proposition_alignment": 0.0,
            "semantic_score": 0.0
        }
        
    model = get_sentence_transformer()
    nlp = get_spacy_nlp()
    
    # 1. Global Embedding Similarity
    embeddings = model.encode([reference_answer, student_answer], show_progress_bar=False)
    global_sim = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])
    global_sim = max(0.0, min(1.0, global_sim))
    
    # 2. Propositional / Sentence-Level Cross Alignment
    ref_doc = nlp(clean_text(reference_answer))
    ref_sents = [s.text.strip() for s in ref_doc.sents if s.text.strip()]
    
    stud_doc = nlp(clean_text(student_answer))
    stud_sents = [s.text.strip() for s in stud_doc.sents if s.text.strip()]
    
    if len(ref_sents) > 1 and len(stud_sents) >= 1:
        ref_embs = model.encode(ref_sents, show_progress_bar=False)
        stud_embs = model.encode(stud_sents, show_progress_bar=False)
        cross_sim = cosine_similarity(ref_embs, stud_embs)
        # Average of maximum match for each reference sentence
        prop_alignment = float(np.mean(np.max(cross_sim, axis=1)))
        prop_alignment = max(0.0, min(1.0, prop_alignment))
    else:
        prop_alignment = global_sim
        
    # Blended semantic score (70% global, 30% propositional alignment)
    blended_sim = 0.70 * global_sim + 0.30 * prop_alignment
    semantic_score = round(blended_sim * 100.0, 2)
    
    return {
        "global_similarity": round(global_sim, 4),
        "proposition_alignment": round(prop_alignment, 4),
        "semantic_score": semantic_score
    }

def compute_question_relevance(question: str, student_answer: str) -> float:
    """
    Computes semantic relevance of student answer to the original question.
    Prevents scoring high on answers that ignore the prompt.
    Returns relevance score (0.0 to 1.0).
    """
    if not question or not student_answer:
        return 0.0
    model = get_sentence_transformer()
    embs = model.encode([question, student_answer], show_progress_bar=False)
    sim = float(cosine_similarity([embs[0]], [embs[1]])[0][0])
    return round(max(0.0, min(1.0, sim)), 4)

def run_semantic_model(dataset_path: str):
    """
    Evaluates dataset against human ground-truth scores using semantic embeddings.
    """
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}.")
        return

    df = pd.read_csv(dataset_path)
    print("========================================")
    print("    PROFESSOR MODE — SEMANTIC MODEL     ")
    print("========================================")
    print(f"Loaded {len(df)} samples from {dataset_path}.")
    
    semantic_scores = []
    global_sims = []
    
    for _, row in df.iterrows():
        res = compute_semantic_similarity(str(row['student_answer']), str(row['reference_answer']))
        semantic_scores.append(res['semantic_score'])
        global_sims.append(res['global_similarity'])
        
    df['semantic_similarity'] = global_sims
    df['semantic_score_100'] = semantic_scores
    
    max_score = df['human_score'].max()
    normalized_human = df['human_score'] / max_score if max_score > 1 else df['human_score']
    
    p_corr, p_val = pearsonr(df['semantic_similarity'], normalized_human)
    s_corr, s_val = spearmanr(df['semantic_similarity'], normalized_human)
    
    print("\n--- SEMANTIC MODEL BENCHMARK RESULTS ---")
    print(f"Pearson Correlation (r):  {p_corr:.4f} (p-value: {p_val:.4e})")
    print(f"Spearman Correlation (ρ): {s_corr:.4f} (p-value: {s_val:.4e})")
    
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/semantic_results.csv", index=False)
    print("[SUCCESS] Semantic evaluation saved to 'results/semantic_results.csv'.")

if __name__ == "__main__":
    q = "What is asymmetric encryption?"
    ref = "Asymmetric encryption uses a public key to encrypt and a mathematically linked private key to decrypt."
    ans = "Public-key cryptography uses two distinct keys: a public key for encryption and a private key for decryption."
    print("Similarity test:", compute_semantic_similarity(ans, ref))
