
"""
src/baseline.py
Traditional TF-IDF lexical similarity baseline for student answers.
Demonstrates the limitations of rigid keyword matching compared to semantic models.
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from scipy.stats import pearsonr, spearmanr
from preprocessing import preprocess_text

def run_baseline(dataset_path: str = "dataset/student_answers.csv"):
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}.")
        return

    df = pd.read_csv(dataset_path)
    print("========================================")
    print("      PROFESSOR MODE — NLP BASELINE     ")
    print("========================================")
    print(f"Evaluating {len(df)} samples using Lexical TF-IDF...")
    
    # Preprocess text pairs
    df['clean_ref'] = df['reference_answer'].apply(lambda x: preprocess_text(str(x)))
    df['clean_student'] = df['student_answer'].apply(lambda x: preprocess_text(str(x)))
    
    vectorizer = TfidfVectorizer()
    similarities = []
    
    for _, row in df.iterrows():
        texts = [row['clean_ref'], row['clean_student']]
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            similarities.append(float(sim))
        except Exception:
            similarities.append(0.0)
            
    df['tfidf_similarity'] = similarities
    df['tfidf_score_100'] = [s * 100.0 for s in similarities]
    
    max_human = df['human_score'].max()
    normalized_human = (df['human_score'] / max_human) * 100.0
    
    p_corr, p_val = pearsonr(df['tfidf_score_100'], normalized_human)
    s_corr, s_val = spearmanr(df['tfidf_score_100'], normalized_human)
    mae = mean_absolute_error(normalized_human, df['tfidf_score_100'])
    rmse = root_mean_squared_error(normalized_human, df['tfidf_score_100'])
    r2 = r2_score(normalized_human, df['tfidf_score_100'])
    
    print("\n--- BASELINE TF-IDF EVALUATION METRICS ---")
    print(f"Pearson Correlation (r):  {p_corr:.4f} (p-value: {p_val:.4e})")
    print(f"Spearman Correlation (ρ): {s_corr:.4f} (p-value: {s_val:.4e})")
    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
    print(f"R-squared (R²): {r2:.4f}")
    
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/baseline_results.csv", index=False)
    print("\n[SUCCESS] Baseline results saved to 'results/baseline_results.csv'.")
    
    return {
        "pearson": p_corr,
        "spearman": s_corr,
        "mae": mae,
        "rmse": rmse,
        "r2": r2
    }

if __name__ == "__main__":
    run_baseline()
