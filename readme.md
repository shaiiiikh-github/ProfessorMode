# Professor Mode — Explainable Academic Answer Quality Analyzer & Feedback Framework

> An enterprise-grade, explainable Natural Language Processing (NLP) framework designed to analyze student assignment answers and evaluate academic quality across multiple linguistic, semantic, and conceptual dimensions—providing transparent, actionable indicators rather than an opaque black-box score.

---

## 📋 Table of Contents
1. [Project Overview & Problem Statement](#-1-project-overview--problem-statement)
2. [Proposed Novelty & Contribution](#-2-proposed-novelty--contribution)
3. [System Architecture & Pipeline Flow](#-3-system-architecture--pipeline-flow)
4. [Dataset Specifications & Schema](#-4-dataset-specifications--schema)
5. [Tech Stack, Models & Mathematical Foundations](#-5-tech-stack-models--mathematical-foundations)
6. [Complete Project File Directory Structure](#-6-complete-project-file-directory-structure)
7. [Installation & Setup Guide (Windows PowerShell)](#-7-installation--setup-guide-windows-powershell)
8. [Execution Instructions & Module Breakdown](#-8-execution-instructions--module-breakdown)
9. [Quantitative Evaluation Metrics & Benchmark](#-9-quantitative-evaluation-metrics--benchmark)
10. [Viva Defense & FAQ Guide](#-10-viva-defense--faq-guide)
11. [Academic Limitations & Disclaimer](#-11-academic-limitations--disclaimer)

---

## 🚀 1. Project Overview & Problem Statement
Automated assessment of student short answers and assignments traditionally suffers from two extreme limitations:
* **Rigid Lexical Systems:** Traditional keyword-matching and TF-IDF tools fail completely when students use synonyms or paraphrase correct concepts.
* **Opaque Black-Box LLMs:** Large Language Model APIs output arbitrary grades without verifiable reasoning, leaving instructors and students unable to audit *why* a score was given.

**Professor Mode** solves this by building an explainable, deterministic NLP feature extraction pipeline. Instead of a single score, it delivers a comprehensive audit report detailing **semantic alignment, concept coverage gaps, structural health, and redundancy levels**.

---

## 💡 2. Proposed Novelty & Contribution
> **“A Multi-Dimensional Explainable Academic Answer Quality Framework combining semantic relevance, concept coverage, structural quality, readability, and redundancy into a single transparent feedback system rather than an opaque black-box score.”**

### Why this stands out for a college project:
* Treats short-answer assessment as a **multi-feature analytical and regression problem**.
* Explicitly separates **measurable NLP evidence** from **estimated scoring**.
* Provides automated formative feedback (missing technical concepts with exact student evidence, structural suggestions, letter grades) rather than just a grade.
* Features both an interactive **Rich Terminal CLI** and a modern **Web Studio Dashboard** with standalone HTML audit report generation.

---

## 🏗️ 3. System Architecture & Pipeline Flow

```text
[ Input: Question, Student Answer, Reference Answer ]
                       │
                       ▼
         [ Preprocessing & Normalization ]
         (spaCy Tokenization, Contractions Handling, Lemmatization)
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
[ Lexical Analysis ]        [ Semantic Transformers ]
(TF-IDF Vectorizer)         (Sentence Transformers: all-MiniLM-L6-v2)
       │                               │
       └───────────────┬───────────────┘
                       ▼
         [ Multi-Feature Extraction Engine ]
         ├─ Semantic Alignment Scoring (35% weight)
         ├─ Multi-Tier Concept Coverage & Gap Detection (30% weight)
         ├─ Structural, Readability & Linguistic Profiling (20% weight)
         └─ Internal Redundancy & Repetition Check (15% weight)
                       │
                       ▼
           [ Transparent Scoring Engine ]
           (Weighted Formula + Letter Grade + Strengths & Gap Diagnosis)
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
[ Rich Terminal CLI ]       [ Interactive Web Studio & HTML Cards ]
```

---

## 📊 4. Dataset Specifications & Schema
The project includes a curated academic benchmark dataset (`dataset/student_answers.csv`) inspired by the **Mohler Short Answer Grading (ASAG)** standard, covering 30 diverse computer science and software engineering problems (RSA, Deadlocks, MVC, Normalization, ACID, TCP/UDP, Virtual Memory, B-Trees, etc.) across 5 human ground-truth score bands:

| Column Name | Data Type | Description |
|---|---|---|
| `question_id` | Integer | Unique identifier for the question prompt |
| `question` | String | Academic question or exam prompt |
| `reference_answer`| String | Ideal instructor model answer |
| `student_answer` | String | Student's submitted response |
| `human_score` | Float | Expert human score (0.0 to 5.0 scale) |

---

## 🧮 5. Tech Stack, Models & Mathematical Foundations

### 5.1 Models Employed
1. **Sentence Transformers (`all-MiniLM-L6-v2`)**:
   - Encodes text into 384-dimensional dense vectors.
   - Captures contextual semantic similarity and paraphrasing robustness.
2. **spaCy (`en_core_web_sm`)**:
   - Handles sentence boundary detection, tokenization, lemmatization, POS tagging, and noun chunk parsing.
3. **Scikit-Learn (`TfidfVectorizer`)**:
   - Powers lexical baseline and internal sentence-to-sentence redundancy analysis.

### 5.2 Mathematical Formulations

#### 1. Dense Semantic Cosine Similarity
$$\text{Cosine Similarity}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|} = \frac{\sum_{i=1}^{n} u_i v_i}{\sqrt{\sum_{i=1}^{n} u_i^2} \sqrt{\sum_{i=1}^{n} v_i^2}}$$

#### 2. Composite Semantic Alignment
Combines global document embedding similarity $S_{\text{global}}$ with proposition-level cross-sentence alignment $S_{\text{prop}}$:
$$S_{\text{semantic}} = 0.70 \cdot S_{\text{global}} + 0.30 \cdot S_{\text{prop}}$$

#### 3. Concept Coverage Ratio
$$C_{\text{coverage}} = \frac{\sum_{i=1}^{K} w_i \cdot \mathbb{I}(\text{concept}_i \text{ is covered})}{K} \times 100$$
where $\mathbb{I}$ matches via exact substring, token overlap, or semantic embedding threshold ($\tau \ge 0.55$).

#### 4. Readability Benchmarks
* **Flesch Reading Ease (FRE):**
$$\text{FRE} = 206.835 - 1.015 \left(\frac{\text{Total Words}}{\text{Total Sentences}}\right) - 84.6 \left(\frac{\text{Total Syllables}}{\text{Total Words}}\right)$$
* **Flesch-Kincaid Grade Level (FKGL):**
$$\text{FKGL} = 0.39 \left(\frac{\text{Total Words}}{\text{Total Sentences}}\right) + 11.8 \left(\frac{\text{Total Syllables}}{\text{Total Words}}\right) - 15.59$$

#### 5. Unified Redundancy Penalty
Evaluates maximum pairwise sentence similarity (TF-IDF and Semantic embeddings) plus repeated trigram density:
$$R_{\text{score}} = 0.40 \cdot R_{\text{lexical}} + 0.40 \cdot R_{\text{semantic}} + 0.20 \cdot R_{\text{ngram}}$$
$$\text{Score}_{\text{redundancy}} = \max(0, 100 - (R_{\text{score}} \times 100))$$

#### 6. Final Explainable Weighted Score
$$\text{Final Score} = 0.35 \cdot S_{\text{semantic}} + 0.30 \cdot C_{\text{coverage}} + 0.20 \cdot S_{\text{structure}} + 0.15 \cdot \text{Score}_{\text{redundancy}}$$

---

## 📁 6. Complete Project File Directory Structure

```text
ProfessorMode/
│
├── dataset/
│   ├── student_answers.csv               # 30 curated multi-domain academic test samples
│   └── annotations-00001.parquet         # Mohler SemEval alignment dataset
│
├── models/                               # Local model storage directory
│
├── results/                              # Evaluation outputs & visual figures
│   ├── model_comparison_metrics.csv      # Benchmarking data (Pearson, Spearman, MAE, RMSE)
│   ├── baseline_results.csv              # TF-IDF baseline predictions
│   ├── semantic_results.csv              # Semantic transformer predictions
│   ├── report.html                       # Standalone interactive audit report card
│   ├── score_distribution.png            # Score histogram & KDE
│   ├── length_vs_score.png               # Word count regression trendline
│   ├── model_benchmark_comparison.png    # Comparative bar chart
│   └── dimension_correlation_heatmap.png # Correlation matrix
│
├── src/                                  # Core NLP & Analytics Modules
│   ├── __init__.py
│   ├── model_loader.py                   # Centralized singleton model manager & cache handler
│   ├── preprocessing.py                  # Text cleaning, contractions, lemmatization
│   ├── concept_extraction.py             # Noun chunking, entities, multi-tier concept coverage
│   ├── structural_analysis.py            # Flesch readability, diversity, evidence, redundancy
│   ├── semantic_similarity.py            # Transformer embeddings, global & sentence alignment
│   ├── quality_engine.py                 # Multi-dimensional explainable rubric, HTML report
│   ├── batch_processor.py                # Grader for entire student cohort CSV files
│   ├── baseline.py                       # Lexical TF-IDF baseline evaluation
│   ├── evaluation.py                     # Statistical comparison (Pearson, Spearman, MAE, R²)
│   └── eda.py                            # Diagnostic visualizations generator
│
├── tests/                                # Automated Unit Test Suite (19 tests)
│   ├── __init__.py
│   ├── test_preprocessing.py
│   ├── test_semantic.py
│   ├── test_concept.py
│   ├── test_structure.py
│   └── test_quality_engine.py
│
├── demo.txt                              # Demonstration test cases and verification guide
├── main.py                               # Rich-powered interactive CLI application
├── web_app.py                            # Interactive local Web Studio Dashboard
├── requirements.txt                      # Complete pinned dependencies
└── readme.md                             # Comprehensive project documentation
```

---

## 💻 7. Installation & Setup Guide (Windows PowerShell)

### Prerequisites
- Python 3.10+ installed
- Windows PowerShell or Command Prompt

### Step-by-Step Setup
```powershell
# 1. Clone or navigate to the project directory
cd D:\PROJECTS\ProfessorMode

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Verify installed packages
pip list
```

---

## ⚡ 8. Execution Instructions & Module Breakdown

### Option A: Launch Interactive Rich CLI
```powershell
python main.py
```
*Provides an interactive menu for single answer evaluation, batch cohort grading, benchmark runs, and test suites.*

### Option B: Launch Interactive Web Studio Dashboard
```powershell
python web_app.py
```
*Open your browser and navigate to `http://localhost:8000`. Features one-click demo presets, interactive score meters, concept pills, and instant PDF/HTML report exports.*

### Option C: Run Model Benchmark & Comparative Evaluation
```powershell
python src/evaluation.py
```

### Option D: Generate Publication-Quality Visualizations
```powershell
python src/eda.py
```

### Option E: Run Full Automated Unit Test Suite
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📈 9. Quantitative Evaluation Metrics & Benchmark

Benchmarked on 30 curated academic question-answer pairs against expert human ground truth (normalized to 0–100 scale):

| Framework / Model | Pearson ($r$) ↑ | Spearman ($\rho$) ↑ | MAE ↓ | RMSE ↓ | $R^2$ Score ↑ |
|---|---|---|---|---|---|
| **TF-IDF Lexical Baseline** | 0.4137 | 0.4134 | 48.51 | 55.22 | -2.0442 |
| **Semantic Embeddings (MiniLM)** | 0.4170 | 0.5408 | 24.98 | 30.22 | 0.0883 |
| **Professor Mode (Multi-Dim)** | **0.6714** | **0.7439** | **22.27** | **25.40** | **0.3557** |

### Key Findings for Research & Defense:
1. **Strong Correlation Improvement:** Professor Mode improves Pearson correlation by **+61.8%** and Spearman rank correlation to **0.7439** compared to lexical TF-IDF.
2. **Error Minimization:** Reduces Mean Absolute Error (MAE) from 48.51 down to **22.27**.
3. **Multi-Feature Superiority:** Pure semantic embeddings capture phrasing but miss technical omissions and keyword stuffing; Professor Mode's concept coverage and structural indicators bridge the gap.

---

## 🎓 10. Viva Defense & FAQ Guide

### Q1: Why not just ask ChatGPT or an LLM to grade the answer?
**Answer:** LLMs suffer from severe limitations in high-stakes academic grading:
1. **Hallucination & Inconsistency:** The same answer can receive different scores on repeated API calls due to non-zero sampling temperatures.
2. **Black-Box Opacity:** LLMs cannot produce deterministic mathematical audits linking sub-scores to specific linguistic indicators.
3. **Cost & Privacy:** Sending student exam papers to third-party commercial APIs violates student privacy regulations (FERPA/GDPR) and incurs recurring API costs. Professor Mode runs **100% locally and deterministically**.

### Q2: How does Professor Mode solve the synonym problem?
**Answer:** Pure lexical matchers (TF-IDF) only match identical word stems. Professor Mode employs **Dense Sentence Transformers (`all-MiniLM-L6-v2`)** to map student answers and reference concepts into a 384-dimensional continuous vector space. If a student writes *"asymmetric cryptographic algorithm"* and the model answer states *"public key encryption"*, their vector dot product yields high cosine similarity ($\ge 0.75$), correctly rewarding semantic understanding.

### Q3: How do you extract key technical concepts?
**Answer:** We use spaCy's dependency parser and Part-of-Speech tagger to extract:
1. Non-stopword **noun chunks** (e.g. *"private key"*, *"circular wait"*).
2. **Named entities** and technical acronyms (e.g. *"RSA"*, *"MVC"*, *"ACID"*).
3. **Compound nouns** and technical adjective-noun pairs.
We then perform multi-tier verification (exact match, token overlap, and sentence-level semantic cosine matching).

### Q4: How does the system prevent keyword stuffing?
**Answer:** In keyword-stuffing attacks, a student submits a list of technical buzzwords without coherent grammar. Professor Mode defends against this through:
1. **Propositional Sentence Alignment:** Checks whether full assertions match reference propositions.
2. **Structural & Readability Profiling:** Analyzes sentence length, clause variety, and discourse transitions.
3. **Question Relevance Check:** Ensures the answer semantically aligns with the prompt.

### Q5: What is the significance of the Redundancy Level indicator?
**Answer:** Students frequently attempt to artificially lengthen short answers by repeating the same argument in different words. Professor Mode computes pairwise TF-IDF similarity, sentence-level transformer cosine similarity, and repeated n-gram frequencies across sentences. If redundancy exceeds threshold ($\ge 0.60$), a penalty is applied, training students to write concise, academically rigorous answers.

---

## ⚠️ 11. Academic Limitations & Disclaimer
* **Subject-Specific Reference Answer Requirement:** Professor Mode evaluates student submissions by contrasting them against instructor-provided reference answers. It is intended for formative feedback and short-answer exam auditing, not unguided grading of open-ended creative essays.
* **Domain Tuning:** While `all-MiniLM-L6-v2` excels across general STEM, computer science, and engineering contexts, highly specialized fields (e.g. organic chemistry or legal statutes) would benefit from domain-fine-tuned transformer checkpoints.
