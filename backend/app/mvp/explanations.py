from typing import List, Dict
from backend.app.mvp.schemas import PhotoRecord, ParsedClues

def generate_match_reasons(photo: PhotoRecord, clues: ParsedClues, sub_scores: Dict[str, float]) -> List[str]:
    reasons: List[str] = []
    
    # 1. Visual Semantic reason (ACTUAL visual photo content match)
    if sub_scores.get("visual", 0.0) >= 0.3:
        v_semantics = photo.visual_semantics
        v_objs = [o.lower() for o in (v_semantics.objects if v_semantics else photo.objects)]
        v_concepts = [c.lower() for c in (v_semantics.visual_concepts if v_semantics else photo.visual_concepts)]
        
        matched_concepts = []
        for q_concept in clues.objects + clues.visual_concepts:
            qc = q_concept.lower()
            if any(qc in vo or vo in qc for vo in v_objs + v_concepts):
                matched_concepts.append(q_concept)
                
        if matched_concepts:
            reasons.append(f"✓ Visual concept '{matched_concepts[0]}' matches actual photo content")
        elif v_semantics and v_semantics.scene:
            reasons.append(f"✓ Photo visual scene '{v_semantics.scene}' matches query")
        else:
            reasons.append(f"✓ Photo visual semantics match query")
            
    # 2. Date reason
    if sub_scores.get("date", 0.0) >= 0.8:
        if clues.approximate_date:
            reasons.append(f"✓ Year {photo.year} matches '{clues.approximate_date}'")
        else:
            reasons.append(f"✓ Photo date {photo.date} falls in target timeframe")
    elif sub_scores.get("date", 0.0) >= 0.4 and (clues.approximate_date or clues.date_range):
        reasons.append(f"✓ Year {photo.year} is close to requested timeframe")
        
    # 3. Location reason
    if sub_scores.get("location", 0.0) >= 0.3 and clues.location:
        loc_matches = [l for l in clues.location if l.lower() in photo.location.city.lower() or l.lower() in (photo.location.landmark or "").lower()]
        if loc_matches:
            reasons.append(f"✓ Location '{loc_matches[0].title()}' matches {photo.location.city}")
        else:
            reasons.append(f"✓ Matched place context ({photo.location.city})")
            
    # 4. People & Group Context reason
    if sub_scores.get("people", 0.0) >= 0.3:
        v_semantics = photo.visual_semantics
        p_meta = v_semantics.people if (v_semantics and v_semantics.people) else None
        
        # Check specific parsed count bucket match
        if clues.people_count_bucket and p_meta:
            if clues.people_count_bucket in ["large_group", "crowd"] and p_meta.count_bucket in ["large_group", "crowd"]:
                reasons.append(f"✓ Large group detected ({p_meta.count} people)")
            elif clues.people_count_bucket == "two" and p_meta.count_bucket == "two":
                reasons.append("✓ Two people detected")
            elif clues.people_count_bucket == "one" and p_meta.count_bucket == "one":
                reasons.append("✓ One person detected")
            elif clues.people_count_bucket == "small_group" and p_meta.count_bucket == "small_group":
                reasons.append(f"✓ Small group detected ({p_meta.count} people)")
            elif p_meta.people_context:
                reasons.append(f"✓ {p_meta.people_context.capitalize()}")
            else:
                reasons.append(f"✓ People present ({p_meta.count} people)")
        elif p_meta:
            if p_meta.people_context:
                reasons.append(f"✓ {p_meta.people_context.capitalize()}")
            elif p_meta.count_bucket in ["large_group", "crowd"]:
                reasons.append(f"✓ Large group detected ({p_meta.count} people)")
            elif p_meta.present:
                reasons.append("✓ People present")
        elif clues.people:
            people_found = [p for p in clues.people if any(p.lower() in m.lower() for m in photo.people + photo.people_relationships)]
            if people_found:
                reasons.append(f"✓ People clue '{', '.join(people_found)}' matches photo group")
            else:
                reasons.append(f"✓ Context matches people ({', '.join(photo.people[:2])})")
        else:
            reasons.append(f"✓ Group context matches query ({len(photo.people)} people)")

    # 4b. Vector Embedding Semantic similarity reason
    if sub_scores.get("embedding", 0.0) >= 0.3:
        reasons.append(f"✓ Semantic visual similarity matches query")

    # 5. Event reason
    if sub_scores.get("event", 0.0) >= 0.3 and clues.event:
        reasons.append(f"✓ Event context '{photo.event}' matches search clue")
        
    # 6. OCR Text reason
    if sub_scores.get("ocr", 0.0) >= 0.3 and photo.ocr_text and clues.ocr_text:
        matched_ocr = [t for t in clues.ocr_text if t.lower() in photo.ocr_text.lower()]
        if matched_ocr:
            reasons.append(f"✓ Visible text '{', '.join(matched_ocr)}' matches photo content")
        else:
            reasons.append(f"✓ Visible OCR text matches query signal")
        
    # 7. Text Metadata reason (Title / Filename / Description text match ONLY)
    if sub_scores.get("text", 0.0) >= 0.2 and not reasons:
        q_raw = clues.raw_query.lower()
        if q_raw in photo.filename.lower():
            reasons.append(f"✓ Filename contains '{clues.raw_query}'")
        elif q_raw in photo.event.lower() or q_raw in photo.album.lower():
            reasons.append(f"✓ Title text contains '{clues.raw_query}'")
        else:
            reasons.append(f"✓ Textual metadata matches '{clues.raw_query}'")
            
    if not reasons:
        max_sub = max(sub_scores.values()) if sub_scores else 0.0
        if max_sub > 0.1:
            reasons.append(f"✓ Contextually matches '{photo.album}' album")
        else:
            reasons.append("Low overall signal match")
            
    return reasons
