from typing import List, Tuple, Optional, Dict
from backend.app.mvp.schemas import ParsedClues, RankedResult, PhotoRecord
from backend.app.mvp.photo_store import get_photo_store
from backend.app.mvp.ranking import rank_photos

def execute_retrieval(clues: ParsedClues, custom_weights: Optional[Dict[str, float]] = None) -> Tuple[List[RankedResult], str]:
    photo_store = get_photo_store()
    all_photos = photo_store.get_all_photos()
    
    if not all_photos:
        return [], "zero_matches"
        
    ranked_results = rank_photos(all_photos, clues, custom_weights=custom_weights)
    
    # Evaluate result status & filter out zero / non-meaningful matches
    meaningful_results = [r for r in ranked_results if r.score > 0.10]
    
    top_score = meaningful_results[0].score if meaningful_results else 0.0
    
    if top_score >= 0.55:
        status = "strong_matches"
        final_results = meaningful_results
    elif top_score >= 0.30:
        status = "weak_matches"
        final_results = meaningful_results
    else:
        status = "zero_matches"
        final_results = []
        
    return final_results, status
