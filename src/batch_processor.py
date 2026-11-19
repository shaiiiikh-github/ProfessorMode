"""
src/batch_processor.py
Batch evaluation engine for grading full sets of student submissions.
Calculates cohort analytics, grade distributions, and identifies common misconceptions.
"""

import os
import sys
import pandas as pd
from collections import Counter

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from quality_engine import evaluate_answer_quality

def process_batch(input_csv_path: str, output_csv_path: str = "results/batch_evaluation_results.csv") -> dict:
    """
    Grades an entire CSV of student submissions.
    Expected CSV columns: question, reference_answer, student_answer (optional: student_id, question_id, human_score)
    """
    if not os.path.exists(input_csv_path):
        raise FileNotFoundError(f"Input file not found at: {input_csv_path}")
        
    df = pd.read_csv(input_csv_path)
    required_cols = ['question', 'reference_answer', 'student_answer']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Input CSV missing required column: '{col}'")
            
    total_records = len(df)
    print(f"\nProcessing batch evaluation of {total_records} student submissions...")
    
    final_scores = []
    letter_grades = []
    semantic_scores = []
    concept_scores = []
    structural_scores = []
    redundancy_scores = []
    all_missing_concepts = []
    
    for idx, row in df.iterrows():
        res = evaluate_answer_quality(str(row['question']), str(row['student_answer']), str(row['reference_answer']))
        
        final_scores.append(res['final_score'])
        letter_grades.append(res['letter_grade'])
        semantic_scores.append(res['semantic_alignment'])
        concept_scores.append(res['concept_coverage'])
        structural_scores.append(res['structural_quality'])
        redundancy_scores.append(res['redundancy_control'])
        
        for m in res['missing_concepts']:
            all_missing_concepts.append(m['concept'])
            
    df['evaluated_score'] = final_scores
    df['letter_grade'] = letter_grades
    df['semantic_alignment'] = semantic_scores
    df['concept_coverage'] = concept_scores
    df['structural_quality'] = structural_scores
    df['redundancy_control'] = redundancy_scores
    
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    df.to_csv(output_csv_path, index=False)
    
    # Cohort summary statistics
    mean_score = round(float(df['evaluated_score'].mean()), 2)
    std_score = round(float(df['evaluated_score'].std()), 2) if len(df) > 1 else 0.0
    grade_distribution = dict(df['letter_grade'].value_counts())
    
    top_missing = [item[0] for item in Counter(all_missing_concepts).most_common(5)]
    
    summary = {
        "total_submissions": total_records,
        "mean_score": mean_score,
        "std_dev": std_score,
        "grade_distribution": grade_distribution,
        "top_missed_concepts": top_missing,
        "average_dimensions": {
            "semantic_alignment": round(float(df['semantic_alignment'].mean()), 2),
            "concept_coverage": round(float(df['concept_coverage'].mean()), 2),
            "structural_quality": round(float(df['structural_quality'].mean()), 2),
            "redundancy_control": round(float(df['redundancy_control'].mean()), 2)
        },
        "output_path": output_csv_path
    }
    
    return summary

if __name__ == "__main__":
    test_csv = "dataset/student_answers.csv"
    if os.path.exists(test_csv):
        res = process_batch(test_csv)
        print("\nBatch Processing Summary:")
        print(f"Total graded: {res['total_submissions']}")
        print(f"Mean Score: {res['mean_score']} ± {res['std_dev']}")
        print(f"Grade Distribution: {res['grade_distribution']}")
        print(f"Top Missed Concepts across class: {res['top_missed_concepts']}")
