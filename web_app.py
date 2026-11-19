"""
web_app.py
Principal Engineer Quality Academic Assessment Studio for Professor Mode.
Built with enterprise-grade UX (inspired by Linear, Stripe, and Gradescope).
Features animated SVG radial score meters, interactive inline text annotations,
multi-axis dimension telemetry, smooth skeleton loading, and instant markdown export.
"""

import os
import sys
import json
import logging
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

# Ensure src and venv site-packages are in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
venv_site = os.path.join(current_dir, "venv", "Lib", "site-packages")

if os.path.exists(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from quality_engine import evaluate_answer_quality, generate_html_report
from batch_processor import process_batch

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ProfessorMode.WebStudio")

SAMPLE_PRESETS = [
    {
        "id": "rsa-accurate",
        "tag": "Cryptography",
        "title": "RSA Encryption (Exemplary)",
        "question": "Explain the working of RSA encryption.",
        "reference": "RSA is an asymmetric cryptographic algorithm that uses a public key for encryption and a private key for decryption. It relies on the mathematical difficulty of factoring the product of two large prime numbers.",
        "student": "RSA is a public key encryption technique where two distinct keys are used. One key encrypts the data and the private key decrypts it. The mathematical security is fundamentally based on the difficulty of factoring large prime numbers."
    },
    {
        "id": "rsa-weak",
        "tag": "Cryptography",
        "title": "RSA Encryption (Concept Gaps)",
        "question": "Explain the working of RSA encryption.",
        "reference": "RSA is an asymmetric cryptographic algorithm that uses a public key for encryption and a private key for decryption. It relies on the mathematical difficulty of factoring the product of two large prime numbers.",
        "student": "RSA uses keys to make data secure on web servers and computers."
    },
    {
        "id": "os-deadlock",
        "tag": "Operating Systems",
        "title": "Deadlock Characterization",
        "question": "What is a deadlock in operating systems?",
        "reference": "Deadlock is a situation where a set of processes are blocked because each process is holding a resource and waiting for another resource acquired by some other process in the set, leading to a circular wait condition.",
        "student": "Deadlock happens when two or more processes are permanently blocked waiting for resources held by each other, producing a circular wait state where execution cannot advance."
    },
    {
        "id": "arch-mvc",
        "tag": "Software Engineering",
        "title": "MVC Architecture",
        "question": "Describe the Model-View-Controller (MVC) architecture.",
        "reference": "MVC is a software architectural pattern consisting of three parts: Model (manages data and business logic), View (handles UI display), and Controller (acts as an interface between Model and View).",
        "student": "MVC divides an application into three distinct components: the Model encapsulates business logic and data structures, the View handles user interface presentation, and the Controller receives incoming input and updates the model and view accordingly."
    },
    {
        "id": "dbms-norm",
        "tag": "Database Systems",
        "title": "Database Normalization",
        "question": "What is database normalization and why is it used?",
        "reference": "Normalization is the process of structuring a relational database to reduce data redundancy and improve data integrity by organizing tables and columns into normal forms.",
        "student": "Normalization organizes database relations to eliminate repetitive data and guard against insertion or deletion anomalies, preserving relational integrity across tables."
    }
]

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProfessorMode &mdash; Academic Quality Audit Studio</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
        }
        body {
            font-family: var(--font-sans);
            background-color: #0b0f19;
            color: #f1f5f9;
        }
        .mono { font-family: var(--font-mono); }
        .score-dial-circle {
            transition: stroke-dashoffset 1.4s cubic-bezier(0.16, 1, 0.3, 1);
            transform: rotate(-90deg);
            transform-origin: 50% 50%;
        }
        .animate-fade-in {
            animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .tab-btn.active {
            color: #38bdf8;
            border-bottom: 2px solid #38bdf8;
            font-weight: 600;
        }
        .tab-btn {
            color: #64748b;
            border-bottom: 2px solid transparent;
        }
        .scenario-pill.active {
            background-color: #1e293b;
            color: #38bdf8;
            border-color: #38bdf8;
            box-shadow: 0 0 15px -3px rgba(56, 189, 248, 0.2);
        }
        .highlight-matched {
            background-color: rgba(16, 185, 129, 0.15);
            border-bottom: 2px solid #10b981;
            padding: 2px 4px;
            border-radius: 4px;
            font-weight: 500;
            color: #34d399;
        }
        .custom-scrollbar::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: #0f172a;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: #334155;
            border-radius: 4px;
        }
    </style>
</head>
<body class="min-h-screen antialiased flex flex-col selection:bg-sky-500 selection:text-white">

    <!-- Top Navigation Bar -->
    <header class="bg-slate-900/80 backdrop-blur-md border-b border-slate-800/80 sticky top-0 z-40">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-4">
                <div class="flex items-center space-x-3">
                    <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center text-white font-extrabold text-sm shadow-lg shadow-sky-500/20">
                        PM
                    </div>
                    <div>
                        <div class="flex items-center space-x-2">
                            <span class="font-extrabold text-slate-100 text-sm tracking-tight">ProfessorMode</span>
                            <span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">Studio v2.5</span>
                        </div>
                        <span class="text-[11px] text-slate-400 block -mt-0.5">Explainable Academic Assessment Framework</span>
                    </div>
                </div>
            </div>

            <!-- Action Controls -->
            <div class="flex items-center space-x-3">
                <button type="button" onclick="copyMarkdownSummary()" id="copySummaryBtn" disabled class="hidden sm:inline-flex items-center space-x-1.5 px-3 py-1.5 border border-slate-700 hover:border-slate-600 rounded-lg text-xs font-semibold text-slate-300 hover:text-white bg-slate-800/60 hover:bg-slate-800 transition disabled:opacity-30 disabled:cursor-not-allowed">
                    <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                    </svg>
                    <span>Copy Summary</span>
                </button>

                <button type="button" onclick="exportReport()" id="exportHeaderBtn" disabled class="inline-flex items-center space-x-1.5 px-3.5 py-1.5 border border-sky-500/30 hover:border-sky-500/60 rounded-lg text-xs font-semibold text-sky-300 hover:text-white bg-sky-500/10 hover:bg-sky-500/20 transition disabled:opacity-30 disabled:cursor-not-allowed">
                    <svg class="w-3.5 h-3.5 text-sky-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                    </svg>
                    <span>Export Audit Dossier</span>
                </button>

                <div class="hidden lg:inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-mono text-slate-400 bg-slate-800/40 border border-slate-700/50">
                    Ctrl + Enter
                </div>
            </div>
        </div>
    </header>

    <!-- Scenario Switcher Bar -->
    <div class="bg-slate-900/40 border-b border-slate-800/60 py-2.5">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4">
            <div class="flex items-center space-x-2 text-xs font-semibold text-slate-400 shrink-0">
                <span class="inline-block w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse"></span>
                <span class="uppercase tracking-wider text-[11px]">Benchmark Presets:</span>
            </div>
            <div class="flex items-center space-x-2 overflow-x-auto py-0.5 custom-scrollbar" id="presetPillContainer"></div>
        </div>
    </div>

    <!-- Main Workspace -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

            <!-- Left Panel: Assignment Input & Live Text Inspector (5 cols) -->
            <section class="lg:col-span-5 space-y-5">
                <div class="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm space-y-5">
                    
                    <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                        <div class="flex items-center space-x-2">
                            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Submission Editor</span>
                        </div>
                        <div class="flex items-center space-x-1 bg-slate-800/80 p-0.5 rounded-lg border border-slate-700/60 text-xs">
                            <button type="button" onclick="setViewMode('editor')" id="viewModeEditorBtn" class="px-2.5 py-1 rounded-md font-semibold text-slate-200 bg-slate-700/80 transition">Editor</button>
                            <button type="button" onclick="setViewMode('annotated')" id="viewModeAnnotatedBtn" class="px-2.5 py-1 rounded-md font-semibold text-slate-400 hover:text-slate-200 transition">Annotated</button>
                        </div>
                    </div>

                    <!-- Question Input -->
                    <div>
                        <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5" for="questionInput">
                            Academic Prompt / Examination Question
                        </label>
                        <textarea id="questionInput" rows="2" class="w-full text-xs sm:text-sm p-3 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-500 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 focus:outline-none transition leading-relaxed resize-y custom-scrollbar" placeholder="Enter problem statement..."></textarea>
                    </div>

                    <!-- Reference Answer Input -->
                    <div>
                        <div class="flex items-center justify-between mb-1.5">
                            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400" for="refInput">
                                Instructor Reference Solution (Ground Truth)
                            </label>
                            <span class="text-[11px] text-slate-500 mono" id="refWordCount">0 words</span>
                        </div>
                        <textarea id="refInput" rows="3" class="w-full text-xs sm:text-sm p-3 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-200 placeholder-slate-500 focus:border-sky-500 focus:ring-1 focus:ring-sky-500 focus:outline-none transition leading-relaxed resize-y custom-scrollbar" placeholder="Enter ideal reference answer..."></textarea>
                    </div>

                    <!-- Student Answer Editor vs Annotated View -->
                    <div>
                        <div class="flex items-center justify-between mb-1.5">
                            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-300" for="studInput">
                                Student Submitted Response
                            </label>
                            <span class="text-[11px] text-slate-500 mono" id="studWordCount">0 words</span>
                        </div>

                        <!-- Raw Textarea View -->
                        <div id="editorViewWrapper">
                            <textarea id="studInput" rows="6" class="w-full text-xs sm:text-sm p-3.5 bg-slate-950 border border-slate-700/80 rounded-xl text-slate-100 placeholder-slate-500 focus:border-sky-400 focus:ring-1 focus:ring-sky-400 focus:outline-none transition leading-relaxed resize-y custom-scrollbar shadow-inner" placeholder="Paste or type student submission here..."></textarea>
                        </div>

                        <!-- Live Highlighted Annotated View -->
                        <div id="annotatedViewWrapper" class="hidden p-4 bg-slate-950/80 border border-slate-800 rounded-xl text-xs sm:text-sm leading-relaxed text-slate-300 min-h-[140px] max-h-[300px] overflow-y-auto custom-scrollbar">
                            <div id="annotatedContent" class="leading-relaxed"></div>
                        </div>
                    </div>

                    <!-- Action Button -->
                    <button id="analyzeBtn" type="button" onclick="runAnalysis()" class="w-full py-3.5 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white rounded-xl text-xs sm:text-sm font-bold tracking-wide transition shadow-lg shadow-sky-500/20 flex items-center justify-center space-x-2 cursor-pointer active:scale-[0.99]">
                        <span id="btnText">Audit & Evaluate Answer</span>
                        <span id="spinner" class="hidden flex items-center space-x-2">
                            <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span class="mono text-xs">Computing Multi-Dimension Rubric...</span>
                        </span>
                    </button>

                    <!-- Alert message -->
                    <div id="errorAlert" class="hidden p-3.5 bg-rose-500/10 border border-rose-500/30 rounded-xl text-xs text-rose-300 leading-normal"></div>
                </div>
            </section>

            <!-- Right Panel: Executive Audit Dossier (7 cols) -->
            <section class="lg:col-span-7 space-y-6">

                <!-- Placeholder Empty State -->
                <div id="emptyState" class="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-16 text-center shadow-lg">
                    <div class="w-16 h-16 rounded-2xl bg-slate-800/50 border border-slate-700/60 mx-auto flex items-center justify-center text-slate-400 mb-4 shadow-inner">
                        <svg class="w-8 h-8 text-sky-400/80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                        </svg>
                    </div>
                    <h3 class="text-base font-bold text-slate-200">Awaiting Evaluation Input</h3>
                    <p class="text-xs text-slate-400 max-w-sm mx-auto mt-1.5 leading-relaxed">
                        Select a benchmark scenario from the top bar or enter custom answers, then click "Audit & Evaluate Answer".
                    </p>
                </div>

                <!-- Live Evaluated Results Container -->
                <div id="resultsContainer" class="hidden space-y-6 animate-fade-in">

                    <!-- Radial Dial & Grade Banner -->
                    <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
                        <div class="flex flex-col sm:flex-row items-center justify-between gap-6 pb-6 border-b border-slate-800/80">
                            
                            <!-- Left: Radial Dial & Score Counter -->
                            <div class="flex items-center space-x-6">
                                <div class="relative w-28 h-28 flex items-center justify-center shrink-0">
                                    <svg class="w-28 h-28" viewBox="0 0 100 100">
                                        <!-- Background Track -->
                                        <circle cx="50" cy="50" r="45" fill="none" stroke="#1e293b" stroke-width="8"></circle>
                                        <!-- Active Gauge Ring -->
                                        <circle id="scoreDialCircle" class="score-dial-circle" cx="50" cy="50" r="45" fill="none" stroke="#38bdf8" stroke-width="8" stroke-linecap="round" stroke-dasharray="282.7" stroke-dashoffset="282.7"></circle>
                                    </svg>
                                    <div class="absolute inset-0 flex flex-col items-center justify-center text-center">
                                        <span id="finalScoreCounter" class="text-2xl font-extrabold mono text-white tracking-tight">0.0</span>
                                        <span class="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">/ 100</span>
                                    </div>
                                </div>

                                <div class="space-y-1">
                                    <div class="flex items-center space-x-2">
                                        <span id="gradeBadge" class="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-extrabold mono bg-sky-500/10 text-sky-400 border border-sky-500/30">
                                            GRADE A
                                        </span>
                                        <span class="text-xs text-slate-400 mono" id="evalAuditId">ID: AUDIT-2026</span>
                                    </div>
                                    <h3 id="tierTitle" class="text-base font-bold text-slate-100">Exemplary Mastery</h3>
                                    <p id="tierDescription" class="text-xs text-slate-400 leading-relaxed max-w-sm">
                                        Comprehensive understanding with rigorous technical terminology and structural clarity.
                                    </p>
                                </div>
                            </div>

                            <!-- Right: Meta Tags -->
                            <div class="sm:text-right border-t sm:border-t-0 pt-4 sm:pt-0 border-slate-800 w-full sm:w-auto flex sm:flex-col justify-between items-center sm:items-end">
                                <div>
                                    <span class="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">Redundancy Status</span>
                                    <div id="redundancyBadge" class="text-sm font-bold mono text-emerald-400 mt-0.5">Low Level (0.08)</div>
                                </div>
                                <div class="mt-2 text-right">
                                    <span class="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block">Prompt Relevance</span>
                                    <div id="questionRelevanceBadge" class="text-sm font-bold mono text-sky-400 mt-0.5">100% Aligned</div>
                                </div>
                            </div>

                        </div>

                        <!-- 4 Dimension Indicator Bars -->
                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6">
                            
                            <div class="bg-slate-950/40 p-3.5 rounded-xl border border-slate-800/60">
                                <div class="flex items-center justify-between text-xs">
                                    <span class="font-medium text-slate-400">Semantic</span>
                                    <span id="scoreSemantic" class="font-bold text-sky-400 mono">0%</span>
                                </div>
                                <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2.5 overflow-hidden">
                                    <div id="barSemantic" class="score-bar bg-sky-400 h-full rounded-full" style="width: 0%"></div>
                                </div>
                                <span class="text-[10px] text-slate-500 font-mono mt-1.5 block">Weight 35%</span>
                            </div>

                            <div class="bg-slate-950/40 p-3.5 rounded-xl border border-slate-800/60">
                                <div class="flex items-center justify-between text-xs">
                                    <span class="font-medium text-slate-400">Concepts</span>
                                    <span id="scoreConcept" class="font-bold text-emerald-400 mono">0%</span>
                                </div>
                                <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2.5 overflow-hidden">
                                    <div id="barConcept" class="score-bar bg-emerald-400 h-full rounded-full" style="width: 0%"></div>
                                </div>
                                <span class="text-[10px] text-slate-500 font-mono mt-1.5 block">Weight 30%</span>
                            </div>

                            <div class="bg-slate-950/40 p-3.5 rounded-xl border border-slate-800/60">
                                <div class="flex items-center justify-between text-xs">
                                    <span class="font-medium text-slate-400">Structure</span>
                                    <span id="scoreStructure" class="font-bold text-indigo-400 mono">0%</span>
                                </div>
                                <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2.5 overflow-hidden">
                                    <div id="barStructure" class="score-bar bg-indigo-400 h-full rounded-full" style="width: 0%"></div>
                                </div>
                                <span class="text-[10px] text-slate-500 font-mono mt-1.5 block">Weight 20%</span>
                            </div>

                            <div class="bg-slate-950/40 p-3.5 rounded-xl border border-slate-800/60">
                                <div class="flex items-center justify-between text-xs">
                                    <span class="font-medium text-slate-400">Conciseness</span>
                                    <span id="scoreRedundancy" class="font-bold text-amber-400 mono">0%</span>
                                </div>
                                <div class="w-full bg-slate-800 h-1.5 rounded-full mt-2.5 overflow-hidden">
                                    <div id="barRedundancy" class="score-bar bg-amber-400 h-full rounded-full" style="width: 0%"></div>
                                </div>
                                <span class="text-[10px] text-slate-500 font-mono mt-1.5 block">Weight 15%</span>
                            </div>

                        </div>
                    </div>

                    <!-- Concept Verification Matrix -->
                    <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm space-y-4">
                        <div class="flex items-center justify-between border-b border-slate-800 pb-3.5">
                            <div>
                                <h3 class="text-xs font-bold uppercase tracking-wider text-slate-200">
                                    Academic Concept Verification Matrix
                                </h3>
                                <p class="text-[11px] text-slate-400 mt-0.5">Click any row to pinpoint and highlight the evidence in the student answer.</p>
                            </div>
                            <span class="text-xs font-mono font-semibold text-sky-400 px-2.5 py-1 bg-sky-500/10 rounded-lg border border-sky-500/20" id="conceptRatioText">
                                0 / 0 Verified
                            </span>
                        </div>

                        <div class="overflow-x-auto custom-scrollbar">
                            <table class="w-full text-left text-xs border-collapse">
                                <thead>
                                    <tr class="border-b border-slate-800 text-slate-400 uppercase font-semibold text-[10px] tracking-wider">
                                        <th class="py-2.5 px-3">Target Academic Concept</th>
                                        <th class="py-2.5 px-3">Verification Status</th>
                                        <th class="py-2.5 px-3">Extracted Student Evidence Quote</th>
                                    </tr>
                                </thead>
                                <tbody id="conceptTableBody" class="divide-y divide-slate-800/60 text-slate-300"></tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Tabbed Diagnostic Inspection -->
                    <div class="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
                        <!-- Navigation Tabs -->
                        <div class="flex items-center space-x-6 border-b border-slate-800 mb-5">
                            <button type="button" onclick="switchTab('feedback')" id="tab-btn-feedback" class="tab-btn active pb-3 text-xs font-semibold tracking-wide transition cursor-pointer">
                                Formative Feedback
                            </button>
                            <button type="button" onclick="switchTab('metrics')" id="tab-btn-metrics" class="tab-btn pb-3 text-xs font-semibold tracking-wide transition cursor-pointer">
                                Linguistic &amp; Readability Benchmarks
                            </button>
                            <button type="button" onclick="switchTab('raw')" id="tab-btn-raw" class="tab-btn pb-3 text-xs font-semibold tracking-wide transition cursor-pointer">
                                Raw JSON Telemetry
                            </button>
                        </div>

                        <!-- Tab 1: Formative Feedback -->
                        <div id="tab-panel-feedback" class="space-y-4">
                            <div class="bg-slate-950/40 p-4 rounded-xl border border-emerald-500/20">
                                <h4 class="text-xs font-bold uppercase text-emerald-400 tracking-wider mb-2 flex items-center space-x-2">
                                    <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                                    </svg>
                                    <span>Demonstrated Competencies &amp; Strengths</span>
                                </h4>
                                <ul id="strengthsList" class="space-y-1.5 text-xs text-slate-300 pl-1"></ul>
                            </div>

                            <div class="bg-slate-950/40 p-4 rounded-xl border border-rose-500/20">
                                <h4 class="text-xs font-bold uppercase text-rose-400 tracking-wider mb-2 flex items-center space-x-2">
                                    <svg class="w-4 h-4 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                                    </svg>
                                    <span>Identified Concept Gaps &amp; Deficiencies</span>
                                </h4>
                                <ul id="weaknessesList" class="space-y-1.5 text-xs text-slate-300 pl-1"></ul>
                            </div>

                            <div class="bg-slate-950/40 p-4 rounded-xl border border-amber-500/20">
                                <h4 class="text-xs font-bold uppercase text-amber-400 tracking-wider mb-2 flex items-center space-x-2">
                                    <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
                                    </svg>
                                    <span>Actionable Recommendations for Revision</span>
                                </h4>
                                <ul id="suggestionsList" class="space-y-1.5 text-xs text-slate-300 pl-1"></ul>
                            </div>
                        </div>

                        <!-- Tab 2: Linguistic Metrics -->
                        <div id="tab-panel-metrics" class="hidden space-y-4">
                            <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                                <div class="p-3.5 bg-slate-950/40 border border-slate-800 rounded-xl">
                                    <span class="text-slate-400 block mb-1">Flesch Reading Ease</span>
                                    <span id="metricFRE" class="text-base font-bold mono text-sky-400">-</span>
                                    <span id="metricBand" class="text-[11px] text-slate-500 block mt-0.5">-</span>
                                </div>

                                <div class="p-3.5 bg-slate-950/40 border border-slate-800 rounded-xl">
                                    <span class="text-slate-400 block mb-1">Lexical Diversity (TTR)</span>
                                    <span id="metricTTR" class="text-base font-bold mono text-sky-400">-</span>
                                    <span class="text-[11px] text-slate-500 block mt-0.5">Unique Lemmas / Words</span>
                                </div>

                                <div class="p-3.5 bg-slate-950/40 border border-slate-800 rounded-xl">
                                    <span class="text-slate-400 block mb-1">Word &amp; Sentence Count</span>
                                    <span id="metricCounts" class="text-base font-bold mono text-sky-400">-</span>
                                    <span id="metricAvgSent" class="text-[11px] text-slate-500 block mt-0.5">Avg words/sent</span>
                                </div>

                                <div class="p-3.5 bg-slate-950/40 border border-slate-800 rounded-xl">
                                    <span class="text-slate-400 block mb-1">Lexical Redundancy (TF-IDF)</span>
                                    <span id="metricLexRed" class="text-base font-bold mono text-amber-400">-</span>
                                    <span class="text-[11px] text-slate-500 block mt-0.5">Max Pairwise Cosine</span>
                                </div>

                                <div class="p-3.5 bg-slate-950/40 border border-slate-800 rounded-xl">
                                    <span class="text-slate-400 block mb-1">Semantic Redundancy</span>
                                    <span id="metricSemRed" class="text-base font-bold mono text-amber-400">-</span>
                                    <span class="text-[11px] text-slate-500 block mt-0.5">Transformer Embeddings</span>
                                </div>

                                <div class="p-3.5 bg-slate-950/40 border border-slate-800 rounded-xl">
                                    <span class="text-slate-400 block mb-1">Proposition Alignment</span>
                                    <span id="metricPropAlign" class="text-base font-bold mono text-emerald-400">-</span>
                                    <span class="text-[11px] text-slate-500 block mt-0.5">Cross-Sentence Score</span>
                                </div>
                            </div>
                        </div>

                        <!-- Tab 3: Raw JSON Output -->
                        <div id="tab-panel-raw" class="hidden">
                            <pre id="rawJsonBlock" class="p-4 bg-slate-950 text-slate-200 rounded-xl text-xs mono overflow-x-auto max-h-96 border border-slate-800/80 custom-scrollbar"></pre>
                        </div>
                    </div>

                </div>

            </section>
        </div>
    </main>

    <!-- Floating Toast Notification -->
    <div id="toastNotification" class="fixed bottom-6 right-6 z-50 transform translate-y-12 opacity-0 transition duration-300 pointer-events-none flex items-center space-x-2 px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl text-xs font-semibold text-slate-100">
        <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
        </svg>
        <span id="toastMessage">Success</span>
    </div>

    <footer class="border-t border-slate-800/80 bg-slate-950/60 py-4 text-center text-xs text-slate-500">
        ProfessorMode &bull; Deterministic &amp; Transparent Academic NLP Framework &bull; MIT License
    </footer>

    <script>
        const PRESETS = """ + json.dumps(SAMPLE_PRESETS) + """;
        let activePresetId = PRESETS[0].id;
        let lastReport = null;

        // Render preset scenario pills
        function renderPresetPills() {
            const container = document.getElementById('presetPillContainer');
            container.innerHTML = '';
            PRESETS.forEach(p => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = `scenario-pill px-3 py-1.5 rounded-lg border text-xs font-semibold whitespace-nowrap transition cursor-pointer ${p.id === activePresetId ? 'active' : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'}`;
                btn.innerHTML = `<span class="text-[10px] text-slate-500 mr-1.5 font-mono uppercase">${p.tag}</span>${p.title}`;
                btn.onclick = () => selectPreset(p.id);
                container.appendChild(btn);
            });
        }

        function selectPreset(id) {
            activePresetId = id;
            renderPresetPills();
            const p = PRESETS.find(x => x.id === id);
            if (!p) return;

            document.getElementById('questionInput').value = p.question;
            document.getElementById('refInput').value = p.reference;
            document.getElementById('studInput').value = p.student;
            updateCounters();
            document.getElementById('errorAlert').classList.add('hidden');
        }

        function updateCounters() {
            const refText = document.getElementById('refInput').value.trim();
            const studText = document.getElementById('studInput').value.trim();
            document.getElementById('refWordCount').innerText = (refText ? refText.split(/\\s+/).length : 0) + ' words';
            document.getElementById('studWordCount').innerText = (studText ? studText.split(/\\s+/).length : 0) + ' words';
        }

        document.getElementById('refInput').addEventListener('input', updateCounters);
        document.getElementById('studInput').addEventListener('input', updateCounters);

        // View mode: Editor vs Annotated
        function setViewMode(mode) {
            const editWrapper = document.getElementById('editorViewWrapper');
            const annotWrapper = document.getElementById('annotatedViewWrapper');
            const btnEdit = document.getElementById('viewModeEditorBtn');
            const btnAnnot = document.getElementById('viewModeAnnotatedBtn');

            if (mode === 'editor') {
                editWrapper.classList.remove('hidden');
                annotWrapper.classList.add('hidden');
                btnEdit.className = "px-2.5 py-1 rounded-md font-semibold text-slate-200 bg-slate-700/80 transition";
                btnAnnot.className = "px-2.5 py-1 rounded-md font-semibold text-slate-400 hover:text-slate-200 transition";
            } else {
                renderAnnotatedText();
                editWrapper.classList.add('hidden');
                annotWrapper.classList.remove('hidden');
                btnAnnot.className = "px-2.5 py-1 rounded-md font-semibold text-slate-200 bg-slate-700/80 transition";
                btnEdit.className = "px-2.5 py-1 rounded-md font-semibold text-slate-400 hover:text-slate-200 transition";
            }
        }

        function renderAnnotatedText(highlightTarget = null) {
            const rawText = document.getElementById('studInput').value;
            const container = document.getElementById('annotatedContent');
            if (!rawText.trim()) {
                container.innerHTML = '<span class="text-slate-500 italic">No text provided.</span>';
                return;
            }

            if (!lastReport || !lastReport.report || !lastReport.report.covered_concepts) {
                container.innerText = rawText;
                return;
            }

            let annotatedHtml = rawText;
            const covered = lastReport.report.covered_concepts || [];
            covered.forEach(c => {
                const term = c.concept;
                if (!term) return;
                const regex = new RegExp(`\\\\b(${term})\\\\b`, 'gi');
                const isTarget = highlightTarget && highlightTarget.toLowerCase() === term.toLowerCase();
                const hlClass = isTarget ? 'bg-sky-500/30 text-sky-200 border-b-2 border-sky-400 ring-2 ring-sky-400' : 'highlight-matched';
                annotatedHtml = annotatedHtml.replace(regex, `<span class="${hlClass}" title="Matched: ${c.match_type}">$1</span>`);
            });

            container.innerHTML = annotatedHtml;
        }

        function highlightConceptInEditor(conceptTerm) {
            setViewMode('annotated');
            renderAnnotatedText(conceptTerm);
        }

        // Keyboard shortcut: Ctrl+Enter
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                runAnalysis();
            }
        });

        // Toast feedback
        function showToast(message) {
            const toast = document.getElementById('toastNotification');
            const msgSpan = document.getElementById('toastMessage');
            msgSpan.innerText = message;
            toast.classList.remove('translate-y-12', 'opacity-0');
            toast.classList.add('translate-y-0', 'opacity-100');
            setTimeout(() => {
                toast.classList.remove('translate-y-0', 'opacity-100');
                toast.classList.add('translate-y-12', 'opacity-0');
            }, 3000);
        }

        async function runAnalysis() {
            const q = document.getElementById('questionInput').value.trim();
            const ref = document.getElementById('refInput').value.trim();
            const stud = document.getElementById('studInput').value.trim();

            const errDiv = document.getElementById('errorAlert');
            errDiv.classList.add('hidden');

            if (!q || !ref || !stud) {
                errDiv.innerText = "Please provide Question, Reference Benchmark, and Student Answer.";
                errDiv.classList.remove('hidden');
                return;
            }

            const btn = document.getElementById('analyzeBtn');
            const btnText = document.getElementById('btnText');
            const spinner = document.getElementById('spinner');

            btn.disabled = true;
            btnText.classList.add('hidden');
            spinner.classList.remove('hidden');

            try {
                const res = await fetch('/api/evaluate', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ question: q, reference_answer: ref, student_answer: stud })
                });

                if (!res.ok) {
                    const errorJson = await res.json().catch(() => ({ error: 'HTTP ' + res.status }));
                    throw new Error(errorJson.error || ('Server returned HTTP ' + res.status));
                }

                const data = await res.json();
                lastReport = { question: q, reference_answer: ref, student_answer: stud, report: data };
                displayReport(data);
                document.getElementById('exportHeaderBtn').disabled = false;
                document.getElementById('copySummaryBtn').disabled = false;
            } catch (err) {
                errDiv.innerText = "Evaluation Error: " + err.message;
                errDiv.classList.remove('hidden');
            } finally {
                btn.disabled = false;
                btnText.classList.remove('hidden');
                spinner.classList.add('hidden');
            }
        }

        // Animate counter from 0 to target
        function animateScoreCounter(target) {
            const elem = document.getElementById('finalScoreCounter');
            let start = 0;
            const duration = 1200;
            const startTime = performance.now();

            function update(now) {
                const elapsed = now - startTime;
                const progress = Math.min(1, elapsed / duration);
                // Ease out cubic
                const ease = 1 - Math.pow(1 - progress, 3);
                const current = start + (target - start) * ease;
                elem.innerText = current.toFixed(1);
                if (progress < 1) {
                    requestAnimationFrame(update);
                }
            }
            requestAnimationFrame(update);
        }

        function displayReport(data) {
            document.getElementById('emptyState').classList.add('hidden');
            document.getElementById('resultsContainer').classList.remove('hidden');

            const score = typeof data.final_score === 'number' ? data.final_score : 0;
            animateScoreCounter(score);

            // Animate SVG circle gauge (circumference 282.7)
            const circumference = 282.7;
            const offset = circumference - (score / 100) * circumference;
            const dial = document.getElementById('scoreDialCircle');
            dial.style.strokeDashoffset = offset;

            // Set color of dial based on score
            if (score >= 80) {
                dial.setAttribute('stroke', '#34d399'); // Emerald
            } else if (score >= 65) {
                dial.setAttribute('stroke', '#38bdf8'); // Sky
            } else if (score >= 50) {
                dial.setAttribute('stroke', '#fbbf24'); // Amber
            } else {
                dial.setAttribute('stroke', '#f87171'); // Rose
            }

            document.getElementById('gradeBadge').innerText = (data.letter_grade || 'N/A').toUpperCase();
            document.getElementById('tierTitle').innerText = data.tier_title || 'Assessed Answer';
            document.getElementById('tierDescription').innerText = data.tier_description || '';

            // Redundancy & Relevance
            const redScore = (data.diagnostics && typeof data.diagnostics.lexical_redundancy === 'number') ? data.diagnostics.lexical_redundancy : 0.0;
            document.getElementById('redundancyBadge').innerText = `${data.redundancy_level || 'Low'} (${redScore.toFixed(2)})`;
            
            const qRel = typeof data.question_relevance === 'number' ? Math.round(data.question_relevance * 100) : 100;
            document.getElementById('questionRelevanceBadge').innerText = `${qRel}% Aligned`;

            // Dimension indicators
            const sem = typeof data.semantic_alignment === 'number' ? data.semantic_alignment : 0;
            document.getElementById('scoreSemantic').innerText = sem.toFixed(0) + '%';
            document.getElementById('barSemantic').style.width = sem + '%';

            const cov = typeof data.concept_coverage === 'number' ? data.concept_coverage : 0;
            document.getElementById('scoreConcept').innerText = cov.toFixed(0) + '%';
            document.getElementById('barConcept').style.width = cov + '%';

            const str = typeof data.structural_quality === 'number' ? data.structural_quality : 0;
            document.getElementById('scoreStructure').innerText = str.toFixed(0) + '%';
            document.getElementById('barStructure').style.width = str + '%';

            const red = typeof data.redundancy_control === 'number' ? data.redundancy_control : 0;
            document.getElementById('scoreRedundancy').innerText = red.toFixed(0) + '%';
            document.getElementById('barRedundancy').style.width = red + '%';

            // Concept table
            const tbody = document.getElementById('conceptTableBody');
            tbody.innerHTML = '';

            const covered = data.covered_concepts || [];
            const missing = data.missing_concepts || [];
            const total = covered.length + missing.length;
            document.getElementById('conceptRatioText').innerText = `${covered.length} / ${total} Verified`;

            covered.forEach(c => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-800/50 transition cursor-pointer';
                tr.onclick = () => highlightConceptInEditor(c.concept);
                const tagClass = c.match_type === 'Exact Match' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-sky-500/10 text-sky-400 border-sky-500/30';
                tr.innerHTML = `
                    <td class="py-3 px-3 font-semibold text-slate-200">
                        <span class="hover:underline">${c.concept || c}</span>
                    </td>
                    <td class="py-3 px-3">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-mono font-medium border ${tagClass}">
                            ${c.match_type || 'Verified'}
                        </span>
                    </td>
                    <td class="py-3 px-3 font-mono text-[11px] text-slate-400">
                        <span class="text-slate-300">"${c.evidence || '-'}"</span>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            missing.forEach(m => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-rose-500/10 transition';
                tr.innerHTML = `
                    <td class="py-3 px-3 font-semibold text-rose-300">${m.concept || m}</td>
                    <td class="py-3 px-3">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-mono font-medium border bg-rose-500/10 text-rose-400 border-rose-500/30">
                            Omitted Gap
                        </span>
                    </td>
                    <td class="py-3 px-3 text-[11px] text-slate-500 italic">Closest semantic target: "${m.closest_match || 'None'}" (${m.highest_similarity || 0})</td>
                `;
                tbody.appendChild(tr);
            });

            if (total === 0) {
                tbody.innerHTML = '<tr><td colspan="3" class="py-4 text-center text-slate-500 italic">No technical concepts detected.</td></tr>';
            }

            // Strengths / Weaknesses / Suggestions
            const sList = document.getElementById('strengthsList');
            sList.innerHTML = '';
            (data.strengths || []).forEach(s => {
                const li = document.createElement('li');
                li.className = 'flex items-start space-x-2 text-slate-300';
                li.innerHTML = `<span class="text-emerald-400 font-bold">&bull;</span><span>${s}</span>`;
                sList.appendChild(li);
            });
            if ((data.strengths || []).length === 0) sList.innerHTML = '<li class="text-slate-500 italic">None recorded.</li>';

            const wList = document.getElementById('weaknessesList');
            wList.innerHTML = '';
            (data.weaknesses || []).forEach(w => {
                const li = document.createElement('li');
                li.className = 'flex items-start space-x-2 text-slate-300';
                li.innerHTML = `<span class="text-rose-400 font-bold">&bull;</span><span>${w}</span>`;
                wList.appendChild(li);
            });
            if ((data.weaknesses || []).length === 0) wList.innerHTML = '<li class="text-slate-500 italic">No critical omissions flagged.</li>';

            const sgList = document.getElementById('suggestionsList');
            sgList.innerHTML = '';
            (data.suggestions || []).forEach(sg => {
                const li = document.createElement('li');
                li.className = 'flex items-start space-x-2 text-slate-300';
                li.innerHTML = `<span class="text-amber-400 font-bold">&rarr;</span><span>${sg}</span>`;
                sgList.appendChild(li);
            });
            if ((data.suggestions || []).length === 0) sgList.innerHTML = '<li class="text-slate-500 italic">Maintain current answer standard.</li>';

            // Tab 2: Metrics
            const diag = data.diagnostics || {};
            document.getElementById('metricFRE').innerText = typeof diag.flesch_reading_ease === 'number' ? diag.flesch_reading_ease.toFixed(1) : '-';
            document.getElementById('metricBand').innerText = diag.reading_band || 'Standard';
            document.getElementById('metricTTR').innerText = typeof diag.lexical_diversity === 'number' ? diag.lexical_diversity.toFixed(2) : '-';
            document.getElementById('metricCounts').innerText = `${diag.word_count || 0} w / ${diag.sentence_count || 0} s`;
            const avgSentLen = diag.sentence_count ? (diag.word_count / diag.sentence_count).toFixed(1) : 0;
            document.getElementById('metricAvgSent').innerText = `${avgSentLen} words per sentence`;

            document.getElementById('metricLexRed').innerText = typeof diag.lexical_redundancy === 'number' ? diag.lexical_redundancy.toFixed(2) : '-';
            document.getElementById('metricSemRed').innerText = typeof diag.semantic_redundancy === 'number' ? diag.semantic_redundancy.toFixed(2) : '-';
            document.getElementById('metricPropAlign').innerText = typeof diag.proposition_alignment === 'number' ? (diag.proposition_alignment * 100).toFixed(1) + '%' : '-';

            // Tab 3: Raw JSON
            document.getElementById('rawJsonBlock').innerText = JSON.stringify(data, null, 2);
        }

        function switchTab(tab) {
            ['feedback', 'metrics', 'raw'].forEach(t => {
                document.getElementById(`tab-panel-${t}`).classList.add('hidden');
                document.getElementById(`tab-btn-${t}`).classList.remove('active');
            });
            document.getElementById(`tab-panel-${tab}`).classList.remove('hidden');
            document.getElementById(`tab-btn-${tab}`).classList.add('active');
        }

        function copyMarkdownSummary() {
            if (!lastReport || !lastReport.report) return;
            const r = lastReport.report;
            const md = `### ProfessorMode Assessment Summary\\n- **Score:** ${r.final_score} / 100 (${r.letter_grade})\\n- **Semantic Alignment:** ${r.semantic_alignment}%\\n- **Concept Coverage:** ${r.concept_coverage}%\\n- **Structural Quality:** ${r.structural_quality}%\\n- **Redundancy Control:** ${r.redundancy_control}%\\n\\n**Strengths:**\\n${(r.strengths || []).map(s => '- ' + s).join('\\n')}\\n\\n**Key Gaps:**\\n${(r.missing_concepts || []).map(m => '- ' + (m.concept || m)).join('\\n')}`;
            navigator.clipboard.writeText(md).then(() => {
                showToast("Markdown evaluation summary copied to clipboard.");
            });
        }

        async function exportReport() {
            if (!lastReport) return;
            try {
                const res = await fetch('/api/export_html', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(lastReport)
                });
                if (res.ok) {
                    window.open('/results/report.html', '_blank');
                    showToast("Audit Dossier generated successfully.");
                }
            } catch (e) {
                alert("Failed to export report: " + e.message);
            }
        }

        // Initialize with first preset
        selectPreset(PRESETS[0].id);
    </script>
</body>
</html>
"""

def safe_json_dumps(obj) -> str:
    """Serializes objects to JSON, converting numpy scalars/arrays to native Python types."""
    def default_serializer(o):
        if hasattr(o, 'item'):
            return o.item()
        if hasattr(o, 'tolist'):
            return o.tolist()
        return str(o)
    return json.dumps(obj, default=default_serializer)

class RequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        """Clean terminal logging without clutter."""
        logger.info(f"{self.address_string()} - {format % args}")

    def send_cors_headers(self):
        """Attaches complete Cross-Origin Resource Sharing headers."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept, Authorization")

    def do_OPTIONS(self):
        """Handles browser CORS preflight requests."""
        self.send_response(200, "OK")
        self.send_cors_headers()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # Favicon optimization to avoid 404 terminal logs
        if path == "/favicon.ico":
            self.send_response(204)
            self.send_cors_headers()
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
            
        if path == "/" or path == "/index.html":
            body = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_cors_headers()
            self.end_headers()
            try:
                self.wfile.write(body)
            except (ConnectionResetError, BrokenPipeError):
                pass
        elif path == "/results/report.html":
            file_path = os.path.join(current_dir, "results", "report.html")
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.send_cors_headers()
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (ConnectionResetError, BrokenPipeError):
                    pass
            else:
                self.send_error(404, "Report not yet generated.")
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(length) if length > 0 else b""
        
        try:
            req_json = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception as err:
            logger.warning(f"Malformed JSON payload: {err}")
            req_json = {}
            
        if path == "/api/evaluate":
            q = req_json.get("question", "")
            ans = req_json.get("student_answer", "")
            ref = req_json.get("reference_answer", "")
            
            try:
                res = evaluate_answer_quality(q, ans, ref)
                resp_str = safe_json_dumps(res)
                resp_bytes = resp_str.encode("utf-8")
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(resp_bytes)
            except Exception as e:
                logger.error(f"Error during evaluation: {e}", exc_info=True)
                err_bytes = safe_json_dumps({"error": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(err_bytes)))
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(err_bytes)
                
        elif path == "/api/export_html":
            q = req_json.get("question", "")
            ans = req_json.get("student_answer", "")
            ref = req_json.get("reference_answer", "")
            rep = req_json.get("report", {})
            
            try:
                out_file = generate_html_report(q, ans, ref, rep)
                resp_bytes = safe_json_dumps({"status": "success", "file": out_file}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(resp_bytes)
            except Exception as e:
                logger.error(f"Error exporting HTML report: {e}", exc_info=True)
                err_bytes = safe_json_dumps({"error": str(e)}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(err_bytes)))
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(err_bytes)
        else:
            self.send_error(404, "Unknown API endpoint")

def run_server(port: int = 8000):
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, RequestHandler)
    print("=" * 65)
    print("      PROFESSOR MODE — ACADEMIC ASSESSMENT STUDIO v2.5")
    print(f"      Server running at:")
    print(f"        -> http://localhost:{port}")
    print(f"        -> http://127.0.0.1:{port}")
    print("      Press Ctrl+C in this terminal to stop the server.")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Stopping Professor Mode web server. Goodbye!")

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port)
