"""
src/quality_engine.py
Enterprise-grade explainable assessment engine for Professor Mode.
Combines semantic alignment, multi-tier concept coverage, structural health,
and redundancy penalties into a transparent weighted academic audit report.
"""

import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from semantic_similarity import compute_semantic_similarity, compute_question_relevance
from concept_extraction import analyze_concept_coverage
from structural_analysis import analyze_structure

# Default Explainable Indicator Weights
DEFAULT_WEIGHTS = {
    "semantic": 0.35,
    "concept": 0.30,
    "structure": 0.20,
    "redundancy": 0.15
}

def determine_letter_grade(score: float) -> tuple:
    """
    Maps 0-100 numerical score to standard academic letter grade and qualitative tier.
    """
    if score >= 90.0:
        return "A+", "Outstanding Mastery", "Comprehensive understanding with exemplary terminology and structure."
    elif score >= 80.0:
        return "A", "Excellent", "Strong conceptual grasp with solid explanations and minimal gaps."
    elif score >= 70.0:
        return "B", "Proficient", "Satisfactory technical coverage, though some supporting details or nuances are omitted."
    elif score >= 60.0:
        return "C", "Developing", "Basic comprehension demonstrated, but notable conceptual gaps or weak evidence present."
    elif score >= 50.0:
        return "D", "Marginal", "Fragmentary knowledge shown with missing core concepts or flawed explanations."
    else:
        return "F", "Inadequate", "Insufficient answer lacking primary technical concepts or off-topic."

def evaluate_answer_quality(question: str, student_answer: str, reference_answer: str, weights: dict = None) -> dict:
    """
    Performs multi-dimensional explainable analysis of student answer.
    Returns composite score, sub-scores, concept breakdown, letter grade, and pedagogical advice.
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
        
    # Check for empty or trivial submissions
    if not student_answer or not student_answer.strip():
        return {
            "final_score": 0.0,
            "letter_grade": "F",
            "tier_title": "Inadequate",
            "tier_description": "Inadequate (Blank Submission)",
            "semantic_alignment": 0.0,
            "concept_coverage": 0.0,
            "structural_quality": 0.0,
            "redundancy_control": 0.0,
            "redundancy_level": "N/A",
            "question_relevance": 0.0,
            "covered_concepts": [],
            "missing_concepts": [],
            "strengths": [],
            "weaknesses": ["Submission is blank or contains no valid text."],
            "suggestions": ["Provide a complete technical answer covering the prompt."],
            "diagnostics": {
                "word_count": 0,
                "sentence_count": 0,
                "lexical_diversity": 0.0,
                "flesch_reading_ease": 0.0,
                "reading_band": "N/A",
                "lexical_redundancy": 0.0,
                "semantic_redundancy": 0.0,
                "global_similarity": 0.0,
                "proposition_alignment": 0.0
            }
        }
        
    # 1. Semantic Similarity & Relevance
    sem_data = compute_semantic_similarity(student_answer, reference_answer)
    semantic_score = sem_data['semantic_score']
    q_relevance = compute_question_relevance(question, student_answer)
    
    # Question relevance safety guard: if completely off-topic, apply penalty
    if q_relevance < 0.25:
        relevance_penalty_factor = max(0.3, q_relevance / 0.25)
        semantic_score = round(semantic_score * relevance_penalty_factor, 2)
        
    # 2. Concept Coverage Analysis
    concept_data = analyze_concept_coverage(reference_answer, student_answer)
    concept_score = concept_data['concept_score']
    
    # 3. Structural & Linguistic Analysis
    struct_data = analyze_structure(student_answer, reference_answer)
    struct_score = struct_data['structural_score']
    
    # 4. Redundancy Control Score
    # Redundancy score ranges 0.0 to 1.0 (higher = worse repetition)
    raw_red = struct_data['redundancy']['redundancy_score']
    redundancy_control_score = round(max(0.0, 100.0 - (raw_red * 100.0)), 2)
    redundancy_level = struct_data['redundancy']['redundancy_level']
    
    # 5. Composite Final Score
    final_score = (
        weights['semantic'] * semantic_score +
        weights['concept'] * concept_score +
        weights['structure'] * struct_score +
        weights['redundancy'] * redundancy_control_score
    )
    final_score = round(max(0.0, min(100.0, final_score)), 2)
    
    # Letter Grade & Tier
    grade, tier_title, tier_desc = determine_letter_grade(final_score)
    
    # Generate Formative Feedback
    strengths = []
    weaknesses = []
    suggestions = []
    
    # Semantic feedback
    if semantic_score >= 80:
        strengths.append(f"High semantic alignment ({semantic_score}/100) with the model answer.")
    elif semantic_score >= 65:
        strengths.append("Adequate general alignment with core principles of the reference answer.")
    else:
        weaknesses.append(f"Low semantic correlation ({semantic_score}/100); statements diverge from the expected model answer.")
        suggestions.append("Re-anchor explanation on the foundational definitions outlined in the course materials.")
        
    # Concept feedback
    if concept_data['coverage_ratio'] >= 0.75:
        strengths.append(f"Exemplary concept coverage: identified {concept_data['covered_count']}/{concept_data['total_concepts']} expected technical concepts.")
    elif concept_data['coverage_ratio'] >= 0.50:
        strengths.append(f"Moderate concept coverage ({concept_data['covered_count']}/{concept_data['total_concepts']} concepts present).")
    else:
        weaknesses.append(f"Significant conceptual omissions ({len(concept_data['missing'])} key concepts missing).")
        
    if concept_data['missing']:
        missing_names = ", ".join([f"'{m['concept']}'" for m in concept_data['missing'][:3]])
        suggestions.append(f"Ensure to explicitly incorporate and define missing key concepts: {missing_names}.")
        
    # Structural & illustrative feedback
    if struct_data['has_examples']:
        strengths.append("Effectively uses illustrative examples or concrete use cases to substantiate technical points.")
    else:
        suggestions.append("Include a concrete example or practical application (e.g. using 'for example...') to elevate your response.")
        
    if struct_data['has_discourse_markers']:
        strengths.append("Well-connected sentences using formal academic transitions and discourse markers.")
        
    if struct_data['readability']['flesch_reading_ease'] < 30:
        weaknesses.append("Very high linguistic density; consider breaking complex compound sentences into clearer assertions.")
        
    if redundancy_level == "High":
        weaknesses.append(f"Elevated redundancy detected (Score: {raw_red}); repetitive sentences or filler phrases reduce conciseness.")
        suggestions.append("Eliminate redundant restatements to achieve higher technical conciseness.")
    elif redundancy_level == "Low":
        strengths.append("High information density with virtually zero filler or duplicate statements.")
        
    return {
        "final_score": final_score,
        "letter_grade": grade,
        "tier_title": tier_title,
        "tier_description": tier_desc,
        "semantic_alignment": semantic_score,
        "concept_coverage": concept_score,
        "structural_quality": struct_score,
        "redundancy_control": redundancy_control_score,
        "redundancy_level": redundancy_level,
        "question_relevance": q_relevance,
        "covered_concepts": concept_data['covered'],
        "missing_concepts": concept_data['missing'],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "diagnostics": {
            "word_count": struct_data['word_count'],
            "sentence_count": struct_data['sentence_count'],
            "lexical_diversity": struct_data['lexical_diversity'],
            "flesch_reading_ease": struct_data['readability']['flesch_reading_ease'],
            "reading_band": struct_data['readability']['reading_band'],
            "lexical_redundancy": struct_data['redundancy']['lexical_redundancy'],
            "semantic_redundancy": struct_data['redundancy']['semantic_redundancy'],
            "global_similarity": sem_data['global_similarity'],
            "proposition_alignment": sem_data['proposition_alignment']
        }
    }

def generate_html_report(question: str, student_answer: str, reference_answer: str, report: dict, output_path: str = "results/report.html"):
    """
    Generates a modern, standalone interactive HTML Quality Report card.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    covered_rows = ""
    for c in report['covered_concepts']:
        covered_rows += f"""
        <tr class="border-b border-gray-100 hover:bg-emerald-50/50">
            <td class="py-2.5 px-3 font-semibold text-emerald-800">{c['concept']}</td>
            <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-800">{c['match_type']}</span></td>
            <td class="py-2.5 px-3 text-xs text-gray-600 italic">"{c.get('evidence', '')}"</td>
        </tr>
        """
        
    missing_rows = ""
    for m in report['missing_concepts']:
        missing_rows += f"""
        <tr class="border-b border-gray-100 hover:bg-rose-50/50">
            <td class="py-2.5 px-3 font-semibold text-rose-800">{m['concept']}</td>
            <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-xs font-medium bg-rose-100 text-rose-800">Missing</span></td>
            <td class="py-2.5 px-3 text-xs text-gray-500">Closest detected match ({m.get('highest_similarity', 0)}): "{m.get('closest_match', 'None')}"</td>
        </tr>
        """
        
    empty_strengths = '<li class="text-xs text-gray-500">None recorded.</li>'
    empty_weaknesses = '<li class="text-xs text-gray-500">None identified.</li>'
    empty_suggestions = '<li class="text-xs text-gray-500">Maintain current quality standards.</li>'
    
    strengths_html = "".join([f"<li class='text-sm text-gray-700 flex items-start space-x-2'><span class='text-emerald-500 font-bold'>✓</span><span>{s}</span></li>" for s in report['strengths']]) or empty_strengths
    weaknesses_html = "".join([f"<li class='text-sm text-gray-700 flex items-start space-x-2'><span class='text-rose-500 font-bold'>✗</span><span>{w}</span></li>" for w in report['weaknesses']]) or empty_weaknesses
    suggestions_html = "".join([f"<li class='text-sm text-gray-700 flex items-start space-x-2'><span class='text-amber-500 font-bold'>→</span><span>{sg}</span></li>" for sg in report['suggestions']]) or empty_suggestions
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProfessorMode — Academic Assessment Audit</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}
        .mono {{ font-family: 'JetBrains Mono', monospace; }}
    </style>
</head>
<body class="bg-slate-50 min-h-screen text-slate-800 py-10 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto space-y-6">
        
        <!-- Header -->
        <div class="bg-white rounded-xl p-8 border border-slate-200 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
            <div>
                <div class="flex items-center space-x-2.5 mb-2">
                    <span class="px-2.5 py-0.5 bg-slate-900 text-white rounded text-xs font-mono font-bold tracking-wider">PM-AUDIT</span>
                    <span class="text-xs text-slate-400 font-mono">ID: {report.get('letter_grade', 'ASSESS')}-2026</span>
                </div>
                <h1 class="text-2xl font-bold tracking-tight text-slate-900">Academic Answer Quality Audit</h1>
                <p class="text-slate-500 text-xs mt-1">Multi-Dimensional Natural Language Processing Evaluation Report</p>
            </div>
            
            <div class="bg-slate-50 border border-slate-200 rounded-lg p-5 text-center min-w-[150px]">
                <div class="text-4xl font-extrabold text-slate-900 mono">{report['final_score']}</div>
                <div class="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mt-1">{report['letter_grade']} &bull; {report['tier_title']}</div>
            </div>
        </div>

        <!-- Prompts & Submission Card -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-slate-200 space-y-4">
            <div>
                <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Examination Prompt / Question</h3>
                <p class="text-slate-900 text-sm font-medium bg-slate-50 p-3 rounded-lg border border-slate-100">{question}</p>
            </div>
            <div class="grid md:grid-cols-2 gap-4">
                <div>
                    <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Student Submitted Response</h3>
                    <div class="text-xs text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-200 h-full leading-relaxed">{student_answer}</div>
                </div>
                <div>
                    <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">Instructor Benchmark Solution</h3>
                    <div class="text-xs text-slate-600 bg-slate-50 p-3 rounded-lg border border-slate-200 h-full leading-relaxed">{reference_answer}</div>
                </div>
            </div>
        </div>

        <!-- Indicator Metrics Grid -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div class="bg-white p-4 rounded-xl border border-slate-200">
                <span class="text-xs font-medium text-slate-500 uppercase">Semantic Alignment</span>
                <div class="text-xl font-bold text-slate-900 mono mt-1">{report['semantic_alignment']}%</div>
                <div class="w-full bg-slate-100 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div class="bg-slate-900 h-full rounded-full" style="width: {report['semantic_alignment']}%"></div>
                </div>
                <span class="text-[11px] text-slate-400 mt-1 block">Weight: 35%</span>
            </div>

            <div class="bg-white p-4 rounded-xl border border-slate-200">
                <span class="text-xs font-medium text-slate-500 uppercase">Concept Coverage</span>
                <div class="text-xl font-bold text-slate-900 mono mt-1">{report['concept_coverage']}%</div>
                <div class="w-full bg-slate-100 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div class="bg-slate-900 h-full rounded-full" style="width: {report['concept_coverage']}%"></div>
                </div>
                <span class="text-[11px] text-slate-400 mt-1 block">Weight: 30%</span>
            </div>

            <div class="bg-white p-4 rounded-xl border border-slate-200">
                <span class="text-xs font-medium text-slate-500 uppercase">Structural Health</span>
                <div class="text-xl font-bold text-slate-900 mono mt-1">{report['structural_quality']}%</div>
                <div class="w-full bg-slate-100 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div class="bg-slate-900 h-full rounded-full" style="width: {report['structural_quality']}%"></div>
                </div>
                <span class="text-[11px] text-slate-400 mt-1 block">Weight: 20%</span>
            </div>

            <div class="bg-white p-4 rounded-xl border border-slate-200">
                <span class="text-xs font-medium text-slate-500 uppercase">Conciseness</span>
                <div class="text-xl font-bold text-slate-900 mono mt-1">{report['redundancy_control']}%</div>
                <div class="w-full bg-slate-100 h-1.5 rounded-full mt-2 overflow-hidden">
                    <div class="bg-slate-900 h-full rounded-full" style="width: {report['redundancy_control']}%"></div>
                </div>
                <span class="text-[11px] text-slate-400 mt-1 block">Level: {report['redundancy_level']}</span>
            </div>
        </div>

        <!-- Concept Breakdown Table -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-slate-200 space-y-3">
            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-700">
                Academic Concept Verification Audit
            </h3>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse">
                    <thead>
                        <tr class="border-b border-slate-200 text-slate-400 uppercase font-semibold text-[11px]">
                            <th class="py-2.5 px-3">Target Concept</th>
                            <th class="py-2.5 px-3">Status</th>
                            <th class="py-2.5 px-3">Linguistic Evidence / Student Context</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100">
                        {covered_rows}
                        {missing_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Formative Feedback Cards -->
        <div class="grid md:grid-cols-3 gap-4">
            <div class="bg-white rounded-xl p-5 border border-slate-200 space-y-2">
                <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-800">
                    Demonstrated Competencies
                </h4>
                <ul class="space-y-1.5 text-xs text-slate-700">{strengths_html}</ul>
            </div>

            <div class="bg-white rounded-xl p-5 border border-slate-200 space-y-2">
                <h4 class="text-xs font-bold uppercase tracking-wider text-rose-800">
                    Identified Concept Gaps
                </h4>
                <ul class="space-y-1.5 text-xs text-slate-700">{weaknesses_html}</ul>
            </div>

            <div class="bg-white rounded-xl p-5 border border-slate-200 space-y-2">
                <h4 class="text-xs font-bold uppercase tracking-wider text-amber-800">
                    Actionable Next Steps
                </h4>
                <ul class="space-y-1.5 text-xs text-slate-700">{suggestions_html}</ul>
            </div>
        </div>

        <!-- Footer -->
        <div class="text-center text-xs text-slate-400 py-2">
            Generated by ProfessorMode Deterministic Academic NLP &bull; Words: {report['diagnostics'].get('word_count', 0)} &bull; Sentences: {report['diagnostics'].get('sentence_count', 0)} &bull; Flesch Index: {report['diagnostics'].get('flesch_reading_ease', 0)}
        </div>
    </div>
</body>
</html>"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
        
    return output_path

def print_report(question: str, student_answer: str, report: dict):
    """
    Prints a formatted, explainable Quality Report.
    Uses 'rich' library if available for vibrant terminal output, otherwise clean ASCII.
    """
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        
        console = Console()
        
        # Header Panel
        header_text = Text()
        header_text.append("PROFESSOR MODE — ACADEMIC ANSWER QUALITY REPORT\n", style="bold cyan")
        header_text.append(f"Grade: {report['letter_grade']} ({report['tier_title']})  |  Score: {report['final_score']} / 100", style="bold yellow")
        console.print(Panel(header_text, border_style="cyan", expand=False))
        
        # Sub-Indicators Table
        table = Table(title="Multi-Dimensional Evaluation Indicators", show_header=True, header_style="bold magenta")
        table.add_column("Dimension", style="dim", width=26)
        table.add_column("Score / Status", justify="right", width=18)
        table.add_column("Weight", justify="right", width=10)
        table.add_column("Pedagogical Interpretation", width=34)
        
        table.add_row("Semantic Alignment", f"{report['semantic_alignment']:.1f} / 100", "35%", "Similarity to reference answer")
        table.add_row("Concept Coverage", f"{report['concept_coverage']:.1f} / 100", "30%", f"{len(report['covered_concepts'])} covered / {len(report['missing_concepts'])} missing")
        table.add_row("Structural & Style Quality", f"{report['structural_quality']:.1f} / 100", "20%", f"{report['diagnostics']['word_count']} words | {report['diagnostics']['reading_band']}")
        table.add_row("Redundancy Control", f"{report['redundancy_control']:.1f} / 100", "15%", f"Level: {report['redundancy_level']}")
        console.print(table)
        
        # Concept Audit Table
        concept_table = Table(title="Detailed Academic Concept Audit", show_header=True, header_style="bold green")
        concept_table.add_column("Concept", style="bold", width=24)
        concept_table.add_column("Status", width=22)
        concept_table.add_column("Evidence in Student Text", style="italic", width=42)
        
        for c in report['covered_concepts']:
            concept_table.add_row(c['concept'], f"[green]✓ {c['match_type']}[/green]", f'"{c.get("evidence", "")[:40]}..."')
        for m in report['missing_concepts']:
            concept_table.add_row(m['concept'], "[red]✗ MISSING[/red]", f"Closest match: {m.get('highest_similarity', 0)}")
            
        console.print(concept_table)
        
        # Feedback Panel
        feedback_str = "\n[bold green]Key Strengths:[/bold green]\n" + "\n".join([f"  • {s}" for s in report['strengths']])
        if report['weaknesses']:
            feedback_str += "\n\n[bold red]Identified Gaps:[/bold red]\n" + "\n".join([f"  • {w}" for w in report['weaknesses']])
        if report['suggestions']:
            feedback_str += "\n\n[bold yellow]Suggestions for Improvement:[/bold yellow]\n" + "\n".join([f"  • {sg}" for sg in report['suggestions']])
            
        console.print(Panel(feedback_str, title="Formative Feedback & Diagnostic Insights", border_style="blue"))
        
    except ImportError:
        # Fallback to plain print
        print("\n" + "="*60)
        print("          PROFESSOR MODE — ANSWER QUALITY REPORT")
        print("="*60)
        print(f"Overall Score: {report['final_score']} / 100  [Grade: {report['letter_grade']} - {report['tier_title']}]")
        print("-" * 60)
        print(f" • Semantic Alignment:   {report['semantic_alignment']} / 100  (Weight: 35%)")
        print(f" • Concept Coverage:     {report['concept_coverage']} / 100  (Weight: 30%)")
        print(f" • Structural Quality:   {report['structural_quality']} / 100  (Weight: 20%)")
        print(f" • Redundancy Control:   {report['redundancy_control']} / 100  (Level: {report['redundancy_level']})")
        print("-" * 60)
        print("CONCEPTS COVERED:")
        for c in report['covered_concepts']:
            print(f"  ✓ {c['concept']} ({c['match_type']})")
        print("CONCEPTS MISSING:")
        for m in report['missing_concepts']:
            print(f"  ✗ {m['concept']}")
        print("-" * 60)
        print("STRENGTHS:")
        for s in report['strengths']:
            print(f"  • {s}")
        print("\nWEAKNESSES:")
        for w in report['weaknesses']:
            print(f"  • {w}")
        print("\nSUGGESTIONS:")
        for sg in report['suggestions']:
            print(f"  • {sg}")
        print("="*60)

if __name__ == "__main__":
    q = "Explain the working of RSA encryption."
    ref = "RSA is an asymmetric cryptographic algorithm that uses a public key for encryption and a private key for decryption. It relies on prime numbers."
    ans = "RSA is a public key encryption method using two keys: one for encrypting and another private key to decrypt messages. Prime factor calculation provides security."
    
    rep = evaluate_answer_quality(q, ans, ref)
    print_report(q, ans, rep)
    html_file = generate_html_report(q, ans, ref, rep)
    print(f"Saved interactive HTML report to: {html_file}")
