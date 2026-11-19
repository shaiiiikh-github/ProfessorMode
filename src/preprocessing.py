"""
src/preprocessing.py
Comprehensive text cleaning, tokenization, contractions handling, 
lemmatization, and linguistic normalization for academic text.
"""

import os
import re
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from model_loader import get_spacy_nlp

# Common English Contractions Map
CONTRACTIONS = {
    "can't": "cannot",
    "won't": "will not",
    "n't": " not",
    "i'm": "i am",
    "'re": " are",
    "'d": " would",
    "'ll": " will",
    "'ve": " have",
    "it's": "it is",
    "that's": "that is",
    "there's": "there is",
    "what's": "what is",
    "let's": "let us"
}

def expand_contractions(text: str) -> str:
    """Expands common English contractions in the text."""
    if not isinstance(text, str):
        return ""
    # Specific irregular contractions first
    irregular = {
        r"\bwon't\b": "will not",
        r"\bcan't\b": "cannot",
        r"\bshan't\b": "shall not",
        r"\bi'm\b": "i am",
        r"\blet's\b": "let us"
    }
    for pat, rep in irregular.items():
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)
        
    # General contraction rules
    text = re.sub(r"(\w+)n't\b", r"\1 not", text, flags=re.IGNORECASE)
    text = re.sub(r"(\w+)'re\b", r"\1 are", text, flags=re.IGNORECASE)
    text = re.sub(r"(\w+)'s\b", r"\1 is", text, flags=re.IGNORECASE)
    text = re.sub(r"(\w+)'d\b", r"\1 would", text, flags=re.IGNORECASE)
    text = re.sub(r"(\w+)'ll\b", r"\1 will", text, flags=re.IGNORECASE)
    text = re.sub(r"(\w+)'ve\b", r"\1 have", text, flags=re.IGNORECASE)
    return text

def clean_text(text: str, keep_punctuation: bool = True) -> str:
    """
    Cleans raw academic text:
    - Removes HTML tags and stray markup
    - Normalizes Unicode spaces and quotes
    - Expands contractions
    - Optionally retains grammatical sentence punctuation for downstream parsing
    """
    if not isinstance(text, str):
        return ""
        
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normalize unicode quotation marks & hyphens
    text = text.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
    text = text.replace('—', '-').replace('–', '-')
    
    text = expand_contractions(text)
    
    if keep_punctuation:
        # Keep letters, numbers, spaces, and essential sentence punctuation (. , ? ! ; : -)
        text = re.sub(r'[^a-zA-Z0-9\s\.\,\?\!\;\:\-\(\)]', ' ', text)
    else:
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
    # Collapse multiple whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_text(text: str, remove_stopwords: bool = True, lemmatize: bool = True) -> str:
    """
    Full preprocessing pipeline:
    - Cleans and normalizes text
    - Tokenizes and lemmatizes using spaCy
    - Filters stopwords and punctuation
    Returns a normalized, space-separated string of tokens.
    """
    if not text or not isinstance(text, str):
        return ""
        
    nlp = get_spacy_nlp()
    cleaned = clean_text(text, keep_punctuation=False).lower()
    doc = nlp(cleaned)
    
    tokens = []
    for token in doc:
        if remove_stopwords and token.is_stop:
            continue
        if token.is_punct or token.is_space or len(token.text.strip()) == 0:
            continue
        
        token_val = token.lemma_.strip() if lemmatize else token.text.strip()
        if token_val and token_val != "-PRON-":
            tokens.append(token_val)
            
    return " ".join(tokens)

def extract_sentences(text: str) -> list:
    """Extracts clean sentence strings from text using spaCy sentence boundary detector."""
    if not isinstance(text, str) or not text.strip():
        return []
    nlp = get_spacy_nlp()
    doc = nlp(clean_text(text))
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]

def extract_tokens(text: str, remove_stopwords: bool = True) -> list:
    """Extracts non-empty word tokens list."""
    preprocessed = preprocess_text(text, remove_stopwords=remove_stopwords, lemmatize=False)
    return preprocessed.split() if preprocessed else []

if __name__ == "__main__":
    sample = "Don't forget! The MVC architecture's controller manages the user's input, e.g. clicking a button."
    print("Original:", sample)
    print("Cleaned:", clean_text(sample))
    print("Preprocessed (No stopwords):", preprocess_text(sample))
    print("Sentences:", extract_sentences(sample))
