"""
src/load_data.py
Unpacks the nested parquet structure from the Mohler ASAG dataset
and converts it into the project's standardized CSV format.
"""

import os
import pandas as pd
import ast

def convert_parquet_to_csv(parquet_path: str, output_csv_path: str):
    if not os.path.exists(parquet_path):
        print(f"Error: Parquet file not found at {parquet_path}.")
        return
    
    print(f"Loading parquet file from {parquet_path}...")
    df = pd.read_parquet(parquet_path)
    
    print("\n--- RAW PARQUET COLUMNS FOUND ---")
    print(df.columns.tolist())
    print("\nInspecting first row annotations:")
    print(df['annotations'].iloc[0])
    
    extracted_rows = []
    
    for idx, row in df.iterrows():
        q_id = row['id']
        annotations = row['annotations']
        
        # Handle if annotations is stored as a stringified list or native list/dict
        if isinstance(annotations, str):
            try:
                annotations = ast.literal_eval(annotations)
            except Exception:
                pass
                
        if isinstance(annotations, list):
            for item in annotations:
                if isinstance(item, dict):
                    # Extract fields matching Mohler ASAG schema inside annotations
                    question = item.get('question', item.get('prompt', ''))
                    ref_answer = item.get('instructor_answer', item.get('reference_answer', item.get('ideal_answer', '')))
                    student_ans = item.get('student_answer', item.get('answer', ''))
                    score = item.get('score', item.get('grade', item.get('score_avg', 0.0)))
                    
                    extracted_rows.append({
                        'question_id': q_id,
                        'question': question,
                        'reference_answer': ref_answer,
                        'student_answer': student_ans,
                        'human_score': score
                    })
        elif isinstance(annotations, dict):
            question = annotations.get('question', '')
            ref_answer = annotations.get('instructor_answer', '')
            student_ans = annotations.get('student_answer', '')
            score = annotations.get('score', 0.0)
            
            extracted_rows.append({
                'question_id': q_id,
                'question': question,
                'reference_answer': ref_answer,
                'student_answer': student_ans,
                'human_score': score
            })
            
    processed_df = pd.DataFrame(extracted_rows)
    
    # Fallback if fields weren't directly keyed as expected, let's inspect keys dynamically
    if processed_df.empty or 'student_answer' not in processed_df.columns or processed_df['student_answer'].dropna().empty:
        print("\nNotice: Standard keys not matched directly. Let's inspect raw item keys from the first annotation element.")
        sample_item = annotations[0] if isinstance(annotations, list) and len(annotations) > 0 else annotations
        print("Sample annotation dictionary keys:", sample_item.keys() if isinstance(sample_item, dict) else type(sample_item))
        return

    # Clean up missing data
    processed_df.dropna(subset=['student_answer', 'question'], inplace=True)
    
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    processed_df.to_csv(output_csv_path, index=False)
    print(f"\nSuccessfully unpacked and saved standardized dataset to: {output_csv_path}")
    print(f"Total rows extracted: {len(processed_df)}")
    print("\nSample processed rows:")
    print(processed_df.head(2))

if __name__ == "__main__":
    parquet_file = "dataset/annotations-00001.parquet"
    output_file = "dataset/student_answers.csv"
    convert_parquet_to_csv(parquet_file, output_file)