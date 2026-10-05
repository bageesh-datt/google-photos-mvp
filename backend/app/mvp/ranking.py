import re
import math
from typing import List, Dict, Tuple, Any, Optional
from backend.app.config import settings
from backend.app.mvp.schemas import PhotoRecord, ParsedClues, RankedResult
from backend.app.mvp.explanations import generate_match_reasons

STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "from", "to", "of", "for", "with", "by", "about", "around",
    "photo", "photos", "pic", "pics", "picture", "pictures", "image", "images", "some", "my",
    "me", "show", "find", "get", "look", "looking", "search", "see", "taken", "shot", "view",
    "where", "is", "are", "was", "were", "this", "that", "these", "those"
}

def is_word_match(query_term: str, target_text: str) -> bool:
    """Checks if query_term appears as a whole word or token in target_text (or vice-versa for multi-word phrases)."""
    if not query_term or not target_text:
        return False
    q = query_term.lower().strip()
    t = target_text.lower().strip()
    pattern_q = r'\b' + re.escape(q) + r'\b'
    if re.search(pattern_q, t):
        return True
    pattern_t = r'\b' + re.escape(t) + r'\b'
    if re.search(pattern_t, q):
        return True
    return False

def calculate_visual_semantic_score(photo: PhotoRecord, clues: ParsedClues) -> float:
    """Calculates match score against actual visual photo content / semantics (objects, animals, clothing, colors, scene, activities, environment)."""
    # 1. Gather all query visual terms
    query_terms = set()
    for attr in ['objects', 'visual_concepts', 'animals', 'clothing', 'colors', 'activities', 'spatial_relations']:
        term_list = getattr(clues, attr, []) or []
        for item in term_list:
            if item and item.strip():
                query_terms.add(item.lower().strip())
                
    if clues.environment:
        query_terms.add(clues.environment.lower().strip())

    group_modifiers = {
        "many", "people", "together", "group", "crowd", "lots", "large", "several", "persons", "person",
        "group shot", "people gathering", "group of people", "gathering", "people standing", "lots of people", "large group",
        "group photo", "standing together", "gathering together"
    }
    if clues.people_count_bucket or clues.people_present is not None:
        query_terms = {t for t in query_terms if t not in group_modifiers and not any(g in t for g in ["group of people", "people together", "group shot", "people gathering"])}
        
    if not query_terms:
        tokens = [t.lower() for t in re.findall(r'\b[a-z0-9]+\b', clues.raw_query) if t.lower() not in STOP_WORDS]
        if clues.people_count_bucket or clues.people_present is not None:
            tokens = [t for t in tokens if t not in group_modifiers]
        query_terms = set(tokens)
        
    if not query_terms:
        if clues.people_count_bucket and photo.visual_semantics and photo.visual_semantics.people:
            if photo.visual_semantics.people.count_bucket == clues.people_count_bucket:
                return 1.0
            elif clues.people_count_bucket in ["large_group", "crowd"] and photo.visual_semantics.people.count_bucket in ["large_group", "crowd", "medium_group"]:
                return 0.85
            elif photo.visual_semantics.people.present:
                return 0.5
            else:
                return 0.0
        return 0.0

    # 2. Gather target photo visual elements
    v_semantics = photo.visual_semantics
    primary_terms = set()
    secondary_text = ""
    
    if v_semantics:
        for item in (v_semantics.objects + v_semantics.visual_concepts + (v_semantics.animals or []) + (v_semantics.clothing or []) + (v_semantics.colors or [])):
            if item:
                primary_terms.add(item.lower().strip())
        secondary_text = f"{v_semantics.scene or ''} {' '.join(v_semantics.activities or [])} {v_semantics.generated_description or ''} {v_semantics.environment or ''} {photo.event or ''} {photo.description or ''}".lower()
    else:
        for item in (photo.objects + photo.visual_concepts):
            if item:
                primary_terms.add(item.lower().strip())
        secondary_text = f"{photo.event or ''} {photo.description or ''}".lower()
        
    matches = 0.0
    for q_term in query_terms:
        if any(is_word_match(q_term, pt) for pt in primary_terms):
            matches += 1.0
        elif is_word_match(q_term, secondary_text):
            matches += 0.75
        elif any(q_term in pt or pt in q_term for pt in primary_terms):
            matches += 0.50
            
    return min(1.0, matches / len(query_terms))

def calculate_text_metadata_score(photo: PhotoRecord, clues: ParsedClues) -> float:
    """Calculates match score against textual metadata (filename, title, event name, album).
    Capped at 0.35 max so text/filename match ALONE can NEVER dominate over visual concept mismatch."""
    raw_q = clues.raw_query.lower()
    tokens = [t for t in re.findall(r'\b[a-z0-9]+\b', raw_q) if len(t) >= 2 and t not in STOP_WORDS]
    if not tokens:
        return 0.0
        
    filename = photo.filename.lower()
    event_title = photo.event.lower()
    album = photo.album.lower()
    desc = photo.description.lower()
    
    matches = 0.0
    for t in tokens:
        if is_word_match(t, filename) or is_word_match(t, event_title) or is_word_match(t, album):
            matches += 0.35
        elif is_word_match(t, desc):
            matches += 0.20
            
    return min(0.35, matches / len(tokens))

def calculate_ocr_score(photo: PhotoRecord, clues: ParsedClues) -> float:
    if not clues.ocr_text:
        return 0.0
        
    photo_ocr = photo.ocr_text.lower() if photo.ocr_text else ""
    if not photo_ocr:
        return 0.0
        
    matches = sum(1.0 for token in clues.ocr_text if token.lower() in photo_ocr)
    if len(clues.ocr_text) == 0:
        return 0.0
    return min(1.0, matches / len(clues.ocr_text))

def calculate_date_score(photo: PhotoRecord, clues: ParsedClues) -> float:
    if not clues.approximate_date and not clues.date_range:
        return 0.0
        
    photo_year = photo.year
    target_year = None
    
    if clues.approximate_date:
        match = re.search(r'\b(20\d{2}|19\d{2})\b', clues.approximate_date)
        if match:
            target_year = int(match.group(1))
            
    if not target_year and clues.date_range and clues.date_range.start:
        try:
            target_year = int(clues.date_range.start.split("-")[0])
        except Exception:
            pass
            
    if target_year:
        diff = abs(photo_year - target_year)
        if diff == 0:
            return 1.0
        elif diff == 1:
            return 0.5
        elif diff == 2:
            return 0.25
        else:
            return 0.0
            
    return 0.0

def calculate_location_score(photo: PhotoRecord, clues: ParsedClues) -> float:
    if not clues.location:
        return 0.0
        
    p_loc = f"{photo.location.city} {photo.location.state} {photo.location.country} {photo.location.landmark or ''}".lower()
    matches = sum(1.0 for loc_token in clues.location if loc_token.lower() in p_loc)
    if len(clues.location) == 0:
        return 0.0
    return min(1.0, matches / len(clues.location))

def calculate_people_score(photo: PhotoRecord, clues: ParsedClues) -> float:
    if not clues.people:
        return 0.0
        
    photo_people_set = {p.lower() for p in photo.people + photo.people_relationships}
    matches = sum(1.0 for p_token in clues.people if any(p_token.lower() in member for member in photo_people_set))
    if len(clues.people) == 0:
        return 0.0
    return min(1.0, matches / len(clues.people))

def calculate_event_score(photo: PhotoRecord, clues: ParsedClues) -> float:
    if not clues.event:
        return 0.0
        
    photo_event = f"{photo.event} {photo.album}".lower()
    matches = sum(1.0 for ev in clues.event if ev.lower() in photo_event)
    if len(clues.event) == 0:
        return 0.0
    return min(1.0, matches / len(clues.event))

from backend.app.mvp.embedding_service import encode_text, calculate_cosine_similarity

def calculate_embedding_score(photo: PhotoRecord, clues: ParsedClues) -> float:
    query_text = clues.semantic_query or clues.raw_query
    if not query_text or not query_text.strip():
        return 0.0
        
    query_vec = encode_text(query_text)
    
    # 1. Use pre-computed visual_embedding if available
    v_sem = photo.visual_semantics
    photo_vec = v_sem.visual_embedding if (v_sem and v_sem.visual_embedding) else None
    
    # 2. Encode rich text description for additional semantic match
    photo_desc_parts = [
        photo.event,
        photo.album,
        photo.description,
        v_sem.generated_description if v_sem else "",
        " ".join(v_sem.objects if v_sem else photo.objects),
        " ".join(v_sem.animals if (v_sem and v_sem.animals) else []),
        " ".join(v_sem.visual_concepts if v_sem else photo.visual_concepts),
        " ".join(v_sem.activities if (v_sem and v_sem.activities) else []),
        " ".join(v_sem.clothing if (v_sem and v_sem.clothing) else []),
        " ".join(v_sem.colors if (v_sem and v_sem.colors) else []),
        v_sem.scene if v_sem else "",
        v_sem.environment if v_sem else "",
        v_sem.people_context if v_sem else "",
        photo.ocr_text or ""
    ]
    full_photo_text = " ".join([p for p in photo_desc_parts if p]).strip()
    text_vec = encode_text(full_photo_text)
    
    sim_text = calculate_cosine_similarity(query_vec, text_vec)
    sim_vis = calculate_cosine_similarity(query_vec, photo_vec) if photo_vec else sim_text
    
    sim = max(sim_text, sim_vis)
    if sim <= 0.15:
        return 0.0
    scaled = (sim - 0.15) / 0.70
    return float(min(1.0, max(0.0, scaled)))

BUCKET_COMPATIBILITY_MATRIX = {
    "crowd": {
        "crowd": 1.0, "large_group": 0.95, "medium_group": 0.60, "small_group": 0.30, "two": 0.10, "one": 0.0, "none": 0.0
    },
    "large_group": {
        "crowd": 0.95, "large_group": 1.0, "medium_group": 0.70, "small_group": 0.35, "two": 0.10, "one": 0.0, "none": 0.0
    },
    "medium_group": {
        "crowd": 0.70, "large_group": 0.85, "medium_group": 1.0, "small_group": 0.70, "two": 0.25, "one": 0.05, "none": 0.0
    },
    "small_group": {
        "crowd": 0.30, "large_group": 0.45, "medium_group": 0.75, "small_group": 1.0, "two": 0.60, "one": 0.15, "none": 0.0
    },
    "two": {
        "crowd": 0.0, "large_group": 0.0, "medium_group": 0.10, "small_group": 0.35, "two": 1.0, "one": 0.25, "none": 0.0
    },
    "one": {
        "crowd": 0.0, "large_group": 0.0, "medium_group": 0.0, "small_group": 0.05, "two": 0.25, "one": 1.0, "none": 0.0
    },
    "none": {
        "crowd": 0.0, "large_group": 0.0, "medium_group": 0.0, "small_group": 0.0, "two": 0.0, "one": 0.0, "none": 1.0
    }
}

def calculate_people_semantic_score(photo: PhotoRecord, clues: ParsedClues) -> float:
    """Calculates generic people compatibility score based on count bucket, group type, spatial relations, presence, and named people."""
    v_sem = photo.visual_semantics
    p_sem = v_sem.people if (v_sem and v_sem.people) else None
    p_present = p_sem.present if p_sem else bool(photo.people)
    p_bucket = p_sem.count_bucket if p_sem else ("small_group" if photo.people else "none")
    p_group_type = p_sem.group_type if p_sem else "none"

    # Presence veto
    if clues.people_present is True and not p_present:
        return 0.0
        
    base_score = 0.5 if p_present else 0.0

    # 1. Generic count bucket compatibility
    if clues.people_count_bucket:
        q_b = clues.people_count_bucket
        if q_b in BUCKET_COMPATIBILITY_MATRIX:
            base_score = BUCKET_COMPATIBILITY_MATRIX[q_b].get(p_bucket, 0.0)

    # 2. Group type compatibility bonus
    if clues.group_type and p_group_type and clues.group_type == p_group_type:
        base_score = min(1.0, base_score + 0.05)

    # 3. Explicit named people match
    if clues.people:
        s_names = calculate_people_score(photo, clues)
        if s_names > 0:
            base_score = min(1.0, max(base_score, s_names))

    # 4. Spatial relations match ("sitting", "standing", "together")
    if clues.spatial_relations and p_present:
        photo_spatial = set(v_sem.spatial_relations if (v_sem and v_sem.spatial_relations) else [])
        photo_ctx = f"{p_sem.people_context if p_sem else ''} {photo.description}".lower()
        
        matches = 0
        for sr in clues.spatial_relations:
            if sr in photo_spatial or sr in photo_ctx:
                matches += 1
        if matches > 0:
            base_score = min(1.0, base_score + 0.10 * (matches / len(clues.spatial_relations)))

    return round(base_score, 3)

def rank_photos(photos: List[PhotoRecord], clues: ParsedClues, custom_weights: Optional[Dict[str, float]] = None) -> List[RankedResult]:
    has_people_intent = bool(clues.people or clues.people_count_bucket or clues.people_present is not None or clues.group_type)
    has_ocr_intent = bool(clues.ocr_text)
    
    active_signals = {
        "embedding": bool(clues.raw_query and len(clues.raw_query.strip()) >= 3),
        "visual": bool(clues.objects or clues.visual_concepts or clues.animals or clues.clothing or clues.colors or clues.raw_query.strip()),
        "people": has_people_intent,
        "ocr": has_ocr_intent,
        "date": bool(clues.approximate_date or clues.date_range),
        "location": bool(clues.location),
        "event": bool(clues.event),
        "text": True
    }
    
    if has_ocr_intent and not has_people_intent:
        base_weights = {
            "ocr": 0.85,
            "visual": 0.65,
            "embedding": 0.50,
            "people": 0.20,
            "date": 0.20,
            "location": 0.20,
            "event": 0.20,
            "text": 0.15
        }
    elif has_people_intent:
        base_weights = {
            "people": 0.85,
            "visual": 0.35,
            "embedding": 0.30,
            "text": 0.05,
            "event": 0.0,
            "ocr": 0.0,
            "date": 0.10,
            "location": 0.10
        }
    else:
        base_weights = {
            "embedding": 0.50,
            "visual": 0.65,
            "people": 0.60,
            "ocr": 0.50,
            "date": 0.30,
            "location": 0.30,
            "event": 0.30,
            "text": 0.15
        }
        
    if custom_weights:
        base_weights.update(custom_weights)
        
    raw_weights = {sig: (base_weights[sig] if active_signals[sig] else 0.0) for sig in base_weights}
    total_raw = sum(raw_weights.values())
    
    if total_raw > 0:
        norm_weights = {sig: raw_weights[sig] / total_raw for sig in raw_weights}
    else:
        norm_weights = {sig: (1.0 if sig == "visual" else 0.0) for sig in base_weights}
        
    ranked_results: List[RankedResult] = []
    
    for photo in photos:
        s_emb = calculate_embedding_score(photo, clues) if active_signals["embedding"] else 0.0
        s_visual = calculate_visual_semantic_score(photo, clues)
        s_text = calculate_text_metadata_score(photo, clues)
        s_ocr = calculate_ocr_score(photo, clues)
        s_date = calculate_date_score(photo, clues)
        s_loc = calculate_location_score(photo, clues)
        s_people = calculate_people_semantic_score(photo, clues) if active_signals["people"] else 0.0
        s_event = calculate_event_score(photo, clues)
        
        # Contradiction Veto: If explicit people query, zero-person photo cannot rank high
        if has_people_intent and photo.visual_semantics and photo.visual_semantics.people and not photo.visual_semantics.people.present:
            if clues.people_present is True or clues.people_count_bucket is not None or clues.group_type is not None:
                s_people = 0.0
                s_emb = 0.0
                s_visual = 0.0
                s_text = 0.0
        
        final_score = (
            norm_weights["embedding"] * s_emb +
            norm_weights["visual"] * s_visual +
            norm_weights["people"] * s_people +
            norm_weights["text"] * s_text +
            norm_weights["ocr"] * s_ocr +
            norm_weights["date"] * s_date +
            norm_weights["location"] * s_loc +
            norm_weights["event"] * s_event
        )
        
        # Capping for contradiction
        if has_people_intent and photo.visual_semantics and photo.visual_semantics.people and not photo.visual_semantics.people.present:
            final_score = 0.0

        # Visual mismatch penalty: If query specifies explicit visual objects/clothing/animals/activities,
        # and photo has ZERO match on visual semantics and low embedding similarity, penalize false positives.
        has_explicit_visual_intent = bool(clues.objects or clues.clothing or clues.animals or clues.activities)
        if has_explicit_visual_intent and s_visual == 0.0 and s_emb < 0.45:
            final_score = final_score * 0.30

        sub_scores = {
            "embedding": round(s_emb, 2),
            "visual": round(s_visual, 2),
            "people": round(s_people, 2),
            "text": round(s_text, 2),
            "ocr": round(s_ocr, 2),
            "date": round(s_date, 2),
            "location": round(s_loc, 2),
            "event": round(s_event, 2),
            "objects": round(s_visual, 2),
            "semantic": round(max(s_visual, s_emb), 2)
        }
        
        match_reasons = generate_match_reasons(photo, clues, sub_scores)
        
        location_str = f"{photo.location.city}, {photo.location.country}"
        if photo.location.landmark:
            location_str = f"{photo.location.landmark}, {photo.location.city}"
            
        ranked_results.append(RankedResult(
            photo_id=photo.photo_id,
            filename=photo.filename,
            image_url=photo.image_url,
            date=photo.date,
            year=photo.year,
            location=location_str,
            event=photo.event,
            album=photo.album,
            score=round(final_score, 3),
            sub_scores=sub_scores,
            match_reasons=match_reasons,
            is_favorite=photo.is_favorite,
            description=photo.description,
            people=photo.people,
            objects=photo.objects,
            visual_semantics=photo.visual_semantics,
            ocr_text=photo.ocr_text or ""
        ))
        
    ranked_results.sort(key=lambda r: r.score, reverse=True)
    return ranked_results
