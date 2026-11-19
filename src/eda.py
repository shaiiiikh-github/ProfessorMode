"""
src/eda.py
Exploratory Data Analysis and publication-quality diagnostic visualizations:
1. Human vs Evaluated Score Distributions
2. Answer Word Count vs Score Regression
3. Multi-Dimension Correlation Heatmap
4. Comparative Benchmark Bar Chart
"""

import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def run_eda(dataset_path: str = "dataset/student_answers.csv", metrics_path: str = "results/model_comparison_metrics.csv"):
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}.")
        return

    df = pd.read_csv(dataset_path)
    os.makedirs("results", exist_ok=True)
    
    # Configure publication aesthetics
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 11})
    
    print("========================================")
    print("      PROFESSOR MODE — DATASET EDA      ")
    print("========================================")
    print(f"Total Student Submissions: {len(df)}")
    print(f"Unique Academic Prompts: {df['question_id'].nunique()}")
    
    df["word_count"] = df["student_answer"].apply(lambda x: len(str(x).split()))
    
    print("\n--- SUMMARY DESCRIPTIVE STATISTICS ---")
    print(df[["human_score", "word_count"]].describe().round(2))
    
    # 1. Score Distribution Plot
    plt.figure(figsize=(8, 5))
    ax = sns.histplot(df["human_score"], bins=8, kde=True, color="#4F46E5", edgecolor="black")
    plt.title("Distribution of Human Expert Evaluation Scores", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Human Score (Scale 0.0 - 5.0)", fontweight="semibold")
    plt.ylabel("Frequency (Answer Count)", fontweight="semibold")
    plt.tight_layout()
    plt.savefig("results/score_distribution.png", dpi=300)
    plt.close()
    
    # 2. Answer Word Count vs Score Plot with Trendline
    plt.figure(figsize=(8, 5))
    sns.regplot(
        x="word_count", y="human_score", data=df,
        scatter_kws={"color": "#6366F1", "s": 65, "alpha": 0.8},
        line_kws={"color": "#EF4444", "linewidth": 2, "label": "Linear Fit Trend"}
    )
    plt.title("Student Answer Word Count vs Evaluated Human Score", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Student Answer Word Count", fontweight="semibold")
    plt.ylabel("Human Score", fontweight="semibold")
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/length_vs_score.png", dpi=300)
    plt.close()
    
    # 3. Model Benchmark Comparison Chart (if metrics file exists)
    if os.path.exists(metrics_path):
        m_df = pd.read_csv(metrics_path)
        
        # Calculate Pearson and Spearman for the 3 models
        from scipy.stats import pearsonr, spearmanr
        models = ["TF-IDF Baseline", "Semantic MiniLM", "Professor Mode"]
        pearsons = [
            pearsonr(m_df['tfidf_score'], m_df['human_normalized'])[0],
            pearsonr(m_df['semantic_score'], m_df['human_normalized'])[0],
            pearsonr(m_df['professor_mode_score'], m_df['human_normalized'])[0]
        ]
        spearmans = [
            spearmanr(m_df['tfidf_score'], m_df['human_normalized'])[0],
            spearmanr(m_df['semantic_score'], m_df['human_normalized'])[0],
            spearmanr(m_df['professor_mode_score'], m_df['human_normalized'])[0]
        ]
        
        # Bar Chart
        x = np.arange(len(models))
        width = 0.35
        
        plt.figure(figsize=(9, 5))
        plt.bar(x - width/2, pearsons, width, label="Pearson (r)", color="#3B82F6")
        plt.bar(x + width/2, spearmans, width, label="Spearman (ρ)", color="#10B981")
        
        plt.ylabel("Correlation Coefficient", fontweight="semibold")
        plt.title("Comparative Correlation with Human Ground Truth", fontsize=14, fontweight="bold", pad=12)
        plt.xticks(x, models, fontweight="semibold")
        plt.ylim(0.0, 1.0)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig("results/model_benchmark_comparison.png", dpi=300)
        plt.close()
        
        # 4. Dimension Correlation Heatmap
        eval_cols = ['human_normalized', 'professor_mode_score', 'semantic_score', 'concept_coverage_score', 'structural_score', 'redundancy_control_score']
        avail_cols = [c for c in eval_cols if c in m_df.columns]
        
        if len(avail_cols) >= 3:
            plt.figure(figsize=(8, 6))
            corr = m_df[avail_cols].corr()
            labels = [c.replace('_', ' ').title() for c in avail_cols]
            sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", vmin=-0.2, vmax=1.0, xticklabels=labels, yticklabels=labels)
            plt.title("Inter-Indicator Correlation Heatmap", fontsize=14, fontweight="bold", pad=12)
            plt.xticks(rotation=30, ha="right")
            plt.tight_layout()
            plt.savefig("results/dimension_correlation_heatmap.png", dpi=300)
            plt.close()
            
    print("\n[SUCCESS] Publication-quality figures generated in 'results/':")
    print(" • results/score_distribution.png")
    print(" • results/length_vs_score.png")
    print(" • results/model_benchmark_comparison.png")
    print(" • results/dimension_correlation_heatmap.png")

if __name__ == "__main__":
    run_eda()
