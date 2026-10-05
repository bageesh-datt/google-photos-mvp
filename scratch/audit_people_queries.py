import json
from backend.app.mvp.photo_store import get_photo_store
from backend.app.mvp.query_parser import parse_query, fallback_parse_query
from backend.app.mvp.ranking import rank_photos, calculate_people_semantic_score, calculate_visual_semantic_score, calculate_embedding_score

def audit_runtime():
    store = get_photo_store()
    photos = store.photos

    test_queries = [
        "many people together",
        "group of people",
        "large group",
        "crowd",
        "people together",
        "two people",
        "one person",
        "people sitting together",
        "people standing together"
    ]

    print("==================================================")
    print("STEP 1: AUDIT RUNTIME VALUES FOR PEOPLE QUERIES")
    print("==================================================")

    for q in test_queries:
        print(f"\nQUERY: '{q}'")
        clues = parse_query(q)
        print(f"  Parsed Clues: raw='{clues.raw_query}' | present={clues.people_present} | bucket={clues.people_count_bucket} | type={clues.group_type} | people={clues.people} | ocr={clues.ocr_text}")
        
        ranked = rank_photos(photos, clues)
        print("  Top 5 Ranked Results:")
        for idx, r in enumerate(ranked[:5], 1):
            p_obj = store.get_photo_by_id(r.photo_id)
            v_sem = p_obj.visual_semantics if p_obj else None
            p_sem = v_sem.people if (v_sem and v_sem.people) else None
            p_present = p_sem.present if p_sem else False
            p_count = p_sem.count if p_sem else 0
            p_bucket = p_sem.count_bucket if p_sem else "none"
            p_type = p_sem.group_type if p_sem else "none"

            print(f"    [{idx}] {r.photo_id} | {r.event} | Score: {r.score} | SubScores: {r.sub_scores}")
            print(f"        Meta: present={p_present}, count={p_count}, bucket={p_bucket}, type={p_type}")

if __name__ == "__main__":
    audit_runtime()
