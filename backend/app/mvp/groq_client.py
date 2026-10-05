import json
import time
import logging
from typing import Optional, Dict, Any, List
from backend.app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI Memory Parsing Engine for a photo search app.
Extract structured search clues from the user prompt into JSON:
- semantic_query: The full normalized natural description of what the user remembers (e.g., "a man wearing a black cap working on a computer")
- approximate_date: Approximate year/season (e.g. "2022", "around 2021", null)
- date_range: {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"} or null
- people: Array of named persons or relationships (e.g. ["Rohan"], ["friends"])
- location: Array of cities, landmarks, or place types (e.g. ["Goa"], ["beach"])
- event: Array of occasions, trips, or activities (e.g. ["birthday"], ["vacation"])
- objects: Array of physical objects remembered (e.g. ["computer", "cake", "hat", "table"])
- animals: Array of animals (e.g. ["lion", "dog"])
- clothing: Array of clothing/accessories (e.g. ["cap", "black cap", "shirt"])
- colors: Array of colors mentioned (e.g. ["black", "green", "red"])
- activities: Array of actions/activities (e.g. ["working", "celebrating", "running", "standing"])
- environment: Setting ("indoor", "outdoor", or null)
- visual_concepts: Array of visual settings/concepts (e.g. ["office", "sunset", "party"])
- ocr_text: Array of visible written text keywords explicitly mentioned as being written/printed/labeled (e.g. ["charity"], ["smg"]). CRITICAL: Do NOT put connector/generic words like "photo", "written", "with", "on", "it", "standing", "room", "in", "a", "the" into ocr_text. Ocr_text MUST BE empty unless the user explicitly refers to text written on an item or an acronym.
- confidence: {"date": "high|medium|low", "location": "...", "people": "...", "event": "...", "objects": "..."}

Respond STRICTLY with a valid JSON object matching this schema. Do not output markdown code blocks or conversational text.
"""

def get_configured_models() -> List[str]:
    """Dynamically build candidate model list from environment/configuration only."""
    models: List[str] = []
    
    if settings.GROQ_MODEL and settings.GROQ_MODEL.strip():
        models.append(settings.GROQ_MODEL.strip())
        
    if settings.GROQ_FALLBACK_MODEL and settings.GROQ_FALLBACK_MODEL.strip():
        fallback = settings.GROQ_FALLBACK_MODEL.strip()
        if fallback not in models:
            models.append(fallback)
            
    if hasattr(settings, "GROQ_FALLBACK_MODELS") and settings.GROQ_FALLBACK_MODELS:
        extra_fallbacks = [m.strip() for m in settings.GROQ_FALLBACK_MODELS.split(",") if m.strip()]
        for m in extra_fallbacks:
            if m not in models:
                models.append(m)
                
    return models

def extract_clues_llm(raw_query: str) -> Optional[Dict[str, Any]]:
    if not settings.GROQ_API_KEY:
        logger.info("GROQ_API_KEY is unconfigured. Using fallback parser.")
        return None
        
    models = get_configured_models()
    if not models:
        logger.info("No Groq models configured. Using fallback parser.")
        return None
        
    try:
        from groq import Groq, RateLimitError, APIError
    except ImportError:
        logger.warning("Groq library not installed. Using fallback parser.")
        return None

    try:
        client = Groq(api_key=settings.GROQ_API_KEY, timeout=3.0)
    except Exception as init_err:
        logger.warning("Groq client initialization failed. Using fallback parser.")
        return None
        
    for idx, model_name in enumerate(models):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Extract memory clues from query: '{raw_query}' into JSON."}
                ],
                response_format={"type": "json_object"},
                temperature=0.1,
                max_tokens=500
            )

            
            content = response.choices[0].message.content
            if content:
                parsed = json.loads(content)
                return parsed
        except RateLimitError:
            has_next = (idx + 1 < len(models))
            if has_next:
                logger.warning(f"Groq rate limit reached (HTTP 429) for model '{model_name}'. Trying configured fallback model '{models[idx+1]}'.")
                time.sleep(1.0)
            else:
                logger.warning(f"Groq rate limit reached (HTTP 429) for model '{model_name}'. Defaulting to deterministic fallback parser.")
        except Exception as model_err:
            err_msg = str(model_err)
            has_next = (idx + 1 < len(models))
            if has_next:
                logger.warning(f"Groq API error on model '{model_name}': {err_msg}. Trying configured fallback model '{models[idx+1]}'.")
            else:
                logger.warning(f"Groq model '{model_name}' failed: {err_msg}. Defaulting to deterministic fallback parser.")
                
    return None


