"""
main.py
Interactive CLI Application for Professor Mode: Explainable Academic Quality Framework.
Features rich interactive menu, preset test cases, batch processing, benchmarking, and web studio launcher.
"""

import os
import sys
import subprocess

# Ensure src and venv site-packages are in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
venv_site = os.path.join(current_dir, "venv", "Lib", "site-packages")

if os.path.exists(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from quality_engine import evaluate_answer_quality, print_report, generate_html_report
from batch_processor import process_batch
from evaluation import run_evaluation
from eda import run_eda

DEMO_PRESETS = [
    {
        "title": "RSA Encryption — High Quality Answer",
        "question": "Explain the working of RSA encryption.",
        "reference": "RSA is an asymmetric cryptographic algorithm that uses a public key for encryption and a private key for decryption. It relies on the mathematical difficulty of factoring the product of two large prime numbers.",
        "student": "RSA is a public key encryption technique where two keys are used. One key encrypts the data and the private key decrypts it. It is based on prime numbers."
    },
    {
        "title": "RSA Encryption — Weak Answer (Missing Concepts)",
        "question": "Explain the working of RSA encryption.",
        "reference": "RSA is an asymmetric cryptographic algorithm that uses a public key for encryption and a private key for decryption. It relies on the mathematical difficulty of factoring the product of two large prime numbers.",
        "student": "RSA uses keys to make things secure."
    },
    {
        "title": "Operating Systems — Deadlock Explanation",
        "question": "What is a deadlock in operating systems?",
        "reference": "Deadlock is a situation where a set of processes are blocked because each process is holding a resource and waiting for another resource acquired by some other process in the set, leading to a circular wait condition.",
        "student": "Deadlock happens when two or more processes are stuck waiting for each other to release resources, so none of them can finish execution."
    },
    {
        "title": "Software Architecture — Model-View-Controller (MVC)",
        "question": "Describe the Model-View-Controller (MVC) architecture.",
        "reference": "MVC is a software architectural pattern consisting of three parts: Model (manages data and business logic), View (handles UI display), and Controller (acts as an interface between Model and View).",
        "student": "MVC separates an application into three components: the model for data, the view for the user interface, and the controller that handles user input and logic."
    }
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def interactive_single_evaluation():
    print("\n" + "="*50)
    print("      SINGLE ANSWER INTERACTIVE EVALUATION        ")
    print("="*50)
    print("Select an option:")
    print("  [1] Choose from Demo Test Cases (Instant)")
    print("  [2] Enter Custom Question & Answers")
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    question, reference_answer, student_answer = "", "", ""
    
    if choice == "1":
        print("\nAvailable Demo Test Cases:")
        for idx, p in enumerate(DEMO_PRESETS, start=1):
            print(f"  [{idx}] {p['title']}")
        sub_choice = input(f"\nSelect case (1-{len(DEMO_PRESETS)}): ").strip()
        try:
            sel_idx = int(sub_choice) - 1
            if 0 <= sel_idx < len(DEMO_PRESETS):
                sel = DEMO_PRESETS[sel_idx]
                question = sel["question"]
                reference_answer = sel["reference"]
                student_answer = sel["student"]
            else:
                print("Invalid selection, returning to menu.")
                return
        except ValueError:
            print("Invalid input, returning to menu.")
            return
    else:
        print("\nEnter custom assignment details:")
        question = input("Question / Prompt: ").strip()
        reference_answer = input("Reference / Ideal Answer: ").strip()
        student_answer = input("Student Answer: ").strip()
        
    if not question or not reference_answer or not student_answer:
        print("[Error] All fields (Question, Reference Answer, Student Answer) are required.")
        return
        
    print("\nAnalyzing answer across multiple explainable NLP dimensions...")
    report = evaluate_answer_quality(question, student_answer, reference_answer)
    print_report(question, student_answer, report)
    
    save_html = input("\nGenerate and export standalone HTML audit report? (y/n): ").strip().lower()
    if save_html == 'y':
        out_path = generate_html_report(question, student_answer, reference_answer, report)
        print(f"[SUCCESS] Interactive HTML report generated at: {out_path}")

def interactive_batch_evaluation():
    print("\n" + "="*50)
    print("         COHORT BATCH EVALUATION ENGINE           ")
    print("="*50)
    default_csv = "dataset/student_answers.csv"
    csv_path = input(f"Enter CSV file path (press Enter for default '{default_csv}'): ").strip()
    if not csv_path:
        csv_path = default_csv
        
    if not os.path.exists(csv_path):
        print(f"[Error] File not found: {csv_path}")
        return
        
    summary = process_batch(csv_path)
    print("\n" + "-"*50)
    print("COHORT ASSESSMENT SUMMARY:")
    print(f" • Total Submissions Graded: {summary['total_submissions']}")
    print(f" • Cohort Mean Score:        {summary['mean_score']} ± {summary['std_dev']}")
    print(f" • Letter Grade Breakdown:   {summary['grade_distribution']}")
    print(f" • Most Missed Concepts:     {', '.join(summary['top_missed_concepts'])}")
    print(f" • Results exported to:      {summary['output_path']}")
    print("-"*50)

def main():
    while True:
        print("\n" + "="*60)
        print("          PROFESSOR MODE — CLI ANALYZER v2.0          ")
        print("    Explainable Academic Answer Quality Framework     ")
        print("="*60)
        print("  [1] Single Answer Interactive Evaluation")
        print("  [2] Batch Cohort Evaluation (Grade entire CSV)")
        print("  [3] Benchmark Models (TF-IDF vs Semantic vs Professor Mode)")
        print("  [4] Exploratory Data Analysis & Diagnostic Plots")
        print("  [5] Launch Interactive Web Studio Dashboard")
        print("  [6] Run Unit Test Suite")
        print("  [7] Exit")
        print("="*60)
        
        choice = input("Enter option (1-7): ").strip()
        
        if choice == "1":
            interactive_single_evaluation()
        elif choice == "2":
            interactive_batch_evaluation()
        elif choice == "3":
            run_evaluation()
        elif choice == "4":
            run_eda()
        elif choice == "5":
            print("\nStarting local Web Studio server...")
            print("Open your browser and navigate to: http://localhost:8000")
            from web_app import run_server
            run_server(8000)
        elif choice == "6":
            print("\nRunning automated unit test suite...")
            subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"])
        elif choice == "7":
            print("\nExiting Professor Mode. Best of luck with your academic evaluation and viva!")
            break
        else:
            print("[Warning] Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()
