"""
src/model_loader.py
Centralized model loader and singleton manager for Professor Mode.
Ensures SentenceTransformer and spaCy models are loaded once into memory
and reused across all pipeline modules. Auto-detects project venv packages.
"""

import os
import sys
import logging

# Auto-detect and inject local venv site-packages if running under global Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
venv_site = os.path.join(project_root, "venv", "Lib", "site-packages")
if os.path.exists(venv_site) and venv_site not in sys.path:
    sys.path.insert(0, venv_site)

# Ensure offline huggingface loading succeeds quickly from local cache
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ProfessorMode.ModelLoader")

_SENTENCE_MODEL = None
_SPACY_NLP = None

def get_sentence_transformer(model_name: str = "all-MiniLM-L6-v2"):
    """
    Returns the singleton SentenceTransformer instance.
    Loads from cache on first call, then reuses existing instance.
    """
    global _SENTENCE_MODEL
    if _SENTENCE_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            import torch
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading SentenceTransformer '{model_name}' on device '{device}'...")
            
            try:
                _SENTENCE_MODEL = SentenceTransformer(model_name, device=device)
            except Exception as e:
                # If offline loading failed, allow online retry
                logger.warning(f"Offline load failed ({e}), attempting online fetch...")
                os.environ["HF_HUB_OFFLINE"] = "0"
                os.environ["TRANSFORMERS_OFFLINE"] = "0"
                _SENTENCE_MODEL = SentenceTransformer(model_name, device=device)
                
            logger.info("SentenceTransformer loaded successfully.")
        except Exception as err:
            logger.error(f"Fatal error loading SentenceTransformer: {err}")
            raise err
            
    return _SENTENCE_MODEL

def get_spacy_nlp(model_name: str = "en_core_web_sm"):
    """
    Returns the singleton spaCy Language instance.
    Safely locates spaCy and models across global and virtual environments.
    """
    global _SPACY_NLP
    if _SPACY_NLP is None:
        try:
            import spacy
        except ModuleNotFoundError:
            # Fallback: check project venv
            if os.path.exists(venv_site) and venv_site not in sys.path:
                sys.path.insert(0, venv_site)
                import spacy
            else:
                logger.error("spaCy not found. Run: pip install -r requirements.txt")
                raise ModuleNotFoundError("No module named 'spacy'. Please install requirements or activate venv.")
                
        try:
            _SPACY_NLP = spacy.load(model_name)
        except OSError:
            logger.info(f"spaCy model '{model_name}' not found locally. Downloading...")
            import subprocess
            subprocess.run([sys.executable, "-m", "spacy", "download", model_name], check=True)
            _SPACY_NLP = spacy.load(model_name)
            
        logger.info(f"spaCy model '{model_name}' loaded successfully.")
        
    return _SPACY_NLP

if __name__ == "__main__":
    nlp = get_spacy_nlp()
    st = get_sentence_transformer()
    print("Model Loader check: All models initialized successfully.")
