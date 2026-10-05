import math
import logging
from typing import List, Optional, Dict
import numpy as np

logger = logging.getLogger(__name__)

_MODEL_INSTANCE = None
_QUERY_EMBEDDING_CACHE: Dict[str, List[float]] = {}

def get_embedding_model():
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SentenceTransformer 'all-MiniLM-L6-v2' model...")
            _MODEL_INSTANCE = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer: {e}")
            _MODEL_INSTANCE = False
    return _MODEL_INSTANCE

def encode_text(text: str) -> List[float]:
    """Encodes a text string into a 384-dimensional dense semantic vector."""
    if not text or not text.strip():
        return [0.0] * 384
        
    cleaned_text = text.strip().lower()
    if cleaned_text in _QUERY_EMBEDDING_CACHE:
        return _QUERY_EMBEDDING_CACHE[cleaned_text]
        
    model = get_embedding_model()
    if model:
        try:
            vec = model.encode(cleaned_text)
            vector_list = [float(x) for x in vec]
            _QUERY_EMBEDDING_CACHE[cleaned_text] = vector_list
            return vector_list
        except Exception as e:
            logger.warning(f"Error encoding text with SentenceTransformer: {e}")
            
    # Deterministic fallback embedding generation (384-dim normalized bag-of-character/word hash vector)
    vector = [0.0] * 384
    words = cleaned_text.split()
    for w in words:
        h = sum(ord(c) for c in w)
        idx = h % 384
        vector[idx] += 1.0
        
    norm = math.sqrt(sum(x * x for x in vector))
    if norm > 0:
        vector = [x / norm for x in vector]
    _QUERY_EMBEDDING_CACHE[cleaned_text] = vector
    return vector

def calculate_cosine_similarity(vec1: Optional[List[float]], vec2: Optional[List[float]]) -> float:
    """Calculates cosine similarity between two float vectors (0.0 to 1.0)."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
        
    arr1 = np.array(vec1, dtype=np.float32)
    arr2 = np.array(vec2, dtype=np.float32)
    
    norm1 = np.linalg.norm(arr1)
    norm2 = np.linalg.norm(arr2)
    
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
        
    dot = float(np.dot(arr1, arr2))
    sim = dot / (float(norm1) * float(norm2))
    return float(max(0.0, min(1.0, sim)))
