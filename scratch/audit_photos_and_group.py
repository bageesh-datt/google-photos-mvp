import json
from backend.app.mvp.photo_store import get_photo_store
from backend.app.mvp.query_parser import parse_query, fallback_parse_query
from backend.app.mvp.ranking import rank_photos, calculate_people_semantic_score, calculate_visual_semantic_score, calculate_embedding_score

def audit():
    store = get_photo_store()
    photos = store.photos

    print(f"Total photos in store: {len(photos)}")
    
    group_photos = []
    for p in photos:
        v_sem = p.visual_semantics
        p_sem = v_sem.people if (v_sem and v_sem.people) else None
        if p_sem and p_sem.present:
            group_photos.append((p.photo_id, p.event, p.people, p_sem.count, p_sem.count_bucket, p_sem.group_type))

    print("\n--- PHOTOS WITH PEOPLE PRESENT ---")
    for g in group_photos:
        print(f"ID: {g[0]} | Event: {g[1]} | Count: {g[3]} | Bucket: {g[4]} | GroupType: {g[5]} | People: {g[2]}")

    print("\n--- TEST 'group of people together' RANKING ---")
    clues = parse_query("group of people together")
    print(f"Parsed Clues: {clues}")
    
    ranked = rank_photos(photos, clues)
    print("\nTOP 5 RANKED RESULTS FOR 'group of people together':")
    for r in ranked[:5]:
        print(f"ID: {r.photo_id} | Event: {r.event} | Score: {r.score} | SubScores: {r.sub_scores}")

if __name__ == "__main__":
    audit()
