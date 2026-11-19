"""
src/evaluation.py
Rigorous quantitative benchmark and comparative evaluation across:
1. TF-IDF Lexical Baseline
2. Dense Semantic Embeddings (Sentence Transformers)
3. Professor Mode Multi-Dimensional Framework
Measures Pearson correlation, Spearman rank correlation, MAE, RMSE, and R².
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
from model_loader import get_sentence_transformer
from quality_engine import evaluate_answer_quality
from preprocessing import clean_text

def run_evaluation(dataset_path: str = "dataset/student_answers.csv"):
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}.")
        return

    df = pd.read_csv(dataset_path)
    print("========================================")
    print("   PROFESSOR MODE — MODEL COMPARISON    ")
    print("========================================")
    print(f"Benchmarking models on {len(df)} curated academic test samples...\n")
    
    # Ground truth normalized to 0-100 scale
    max_human = df['human_score'].max()
    human_100 = (df['human_score'] / max_human) * 100.0
    df['human_normalized'] = human_100
    
    # 1. TF-IDF Baseline
    print("1/3 Evaluating TF-IDF Lexical Baseline...")
    vectorizer = TfidfVectorizer()
    tfidf_scores = []
    for _, row in df.iterrows():
        try:
            m = vectorizer.fit_transform([clean_text(str(row['reference_answer'])), clean_text(str(row['student_answer']))])
            sim = cosine_similarity(m[0:1], m[1:2])[0][0]
            tfidf_scores.append(float(sim) * 100.0)
        except Exception:
            tfidf_scores.append(0.0)
    df['tfidf_score'] = tfidf_scores
    
    # 2. Dense Semantic Embeddings
    print("2/3 Evaluating Dense Semantic Transformer Embeddings...")
    model = get_sentence_transformer()
    ref_embs = model.encode(df['reference_answer'].tolist(), show_progress_bar=False)
    stud_embs = model.encode(df['student_answer'].tolist(), show_progress_bar=False)
    
    semantic_scores = []
    for r_emb, s_emb in zip(ref_embs, stud_embs):
        sim = cosine_similarity([r_emb], [s_emb])[0][0]
        semantic_scores.append(float(max(0.0, sim)) * 100.0)
    df['semantic_score'] = semantic_scores
    
    # 3. Professor Mode Multi-Dimensional Quality Engine
    print("3/3 Evaluating Professor Mode Explainable Quality Engine...")
    pm_scores = []
    concept_scores = []
    structural_scores = []
    redundancy_scores = []
    letter_grades = []
    
    for _, row in df.iterrows():
        rep = evaluate_answer_quality(str(row['question']), str(row['student_answer']), str(row['reference_answer']))
        pm_scores.append(rep['final_score'])
        concept_scores.append(rep['concept_coverage'])
        structural_scores.append(rep['structural_quality'])
        redundancy_scores.append(rep['redundancy_control'])
        letter_grades.append(rep['letter_grade'])
        
    df['professor_mode_score'] = pm_scores
    df['concept_coverage_score'] = concept_scores
    df['structural_score'] = structural_scores
    df['redundancy_control_score'] = redundancy_scores
    df['letter_grade'] = letter_grades
    
    def compute_all_metrics(preds, actuals):
        p_r, p_p = pearsonr(preds, actuals)
        s_r, s_p = spearmanr(preds, actuals)
        mae = mean_absolute_error(actuals, preds)
        rmse = root_mean_squared_error(actuals, preds)
        r2 = r2_score(actuals, preds)
        return {
            "pearson": p_r,
            "pearson_p": p_p,
            "spearman": s_r,
            "spearman_p": s_p,
            "mae": mae,
            "rmse": rmse,
            "r2": r2
        }
        
    m_tfidf = compute_all_metrics(df['tfidf_score'], human_100)
    m_sem = compute_all_metrics(df['semantic_score'], human_100)
    m_pm = compute_all_metrics(df['professor_mode_score'], human_100)
    
    try:
        from rich.console import Console
        from rich.table import Table
        console = Console()
        
        table = Table(title="Quantitative Evaluation & Benchmark Results", header_style="bold cyan")
        table.add_column("Framework / Model", style="bold", width=28)
        table.add_column("Pearson (r) ↑", justify="right", width=14)
        table.add_column("Spearman (ρ) ↑", justify="right", width=14)
        table.add_column("MAE ↓", justify="right", width=10)
        table.add_column("RMSE ↓", justify="right", width=10)
        table.add_column("R² Score ↑", justify="right", width=12)
        
        table.add_row(
            "TF-IDF Lexical Baseline",
            f"{m_tfidf['pearson']:.4f}",
            f"{m_tfidf['spearman']:.4f}",
            f"{m_tfidf['mae']:.2f}",
            f"{m_tfidf['rmse']:.2f}",
            f"{m_tfidf['r2']:.4f}"
        )
        table.add_row(
            "Semantic Embeddings (MiniLM)",
            f"{m_sem['pearson']:.4f}",
            f"{m_sem['spearman']:.4f}",
            f"{m_sem['mae']:.2f}",
            f"{m_sem['rmse']:.2f}",
            f"{m_sem['r2']:.4f}"
        )
        table.add_row(
            "[bold green]Professor Mode (Multi-Dim)[/bold green]",
            f"[bold green]{m_pm['pearson']:.4f}[/bold green]",
            f"[bold green]{m_pm['spearman']:.4f}[/bold green]",
            f"[bold green]{m_pm['mae']:.2f}[/bold green]",
            f"[bold green]{m_pm['rmse']:.2f}[/bold green]",
            f"[bold green]{m_pm['r2']:.4f}[/bold green]"
        )
        console.print(table)
    except ImportError:
        print("\n" + "="*80)
        print(f"{'Framework / Model':<28} | {'Pearson (r)':<12} | {'Spearman (ρ)':<12} | {'MAE':<8} | {'RMSE':<8} | {'R²':<8}")
        print("-" * 80)
        print(f"{'TF-IDF Baseline':<28} | {m_tfidf['pearson']:<12.4f} | {m_tfidf['spearman']:<12.4f} | {m_tfidf['mae']:<8.2f} | {m_tfidf['rmse']:<8.2f} | {m_tfidf['r2']:<8.4f}")
        print(f"{'Semantic Model (MiniLM)':<28} | {m_sem['pearson']:<12.4f} | {m_sem['spearman']:<12.4f} | {m_sem['mae']:<8.2f} | {m_sem['rmse']:<8.2f} | {m_sem['r2']:<8.4f}")
        print(f"{'Professor Mode (Multi-Dim)':<28} | {m_pm['pearson']:<12.4f} | {m_pm['spearman']:<12.4f} | {m_pm['mae']:<8.2f} | {m_pm['rmse']:<8.2f} | {m_pm['r2']:<8.4f}")
        print("="*80)
        
    os.makedirs("results", exist_ok=True)
    df.to_csv("results/model_comparison_metrics.csv", index=False)
    print("\n[SUCCESS] Detailed benchmark results saved to 'results/model_comparison_metrics.csv'.")
    
    return {
        "tfidf": m_tfidf,
        "semantic": m_sem,
        "professor_mode": m_pm
    }

if __name__ == "__main__":
    run_evaluation()
