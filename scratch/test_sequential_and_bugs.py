import sys
from backend.app.mvp.query_parser import parse_query, fallback_parse_query
from backend.app.mvp.retrieval import execute_retrieval
from backend.app.mvp.photo_store import get_photo_store

def run_tests():
    store = get_photo_store()
    print(f"Loaded {len(store.photos)} photos from store.")

    test_queries = [
        "charity",
        "lion",
        "SMG",
        "group of people together",
        "beach",
        "2022",
        "Goa beach 2022",
        "birthday with Rohan",
        "many people together",
        "flower spring tour"
    ]

    print("\n--- SEQUENTIAL SEARCH VERIFICATION ---")
    for idx, q in enumerate(test_queries, 1):
        clues = parse_query(q)
        results, status = execute_retrieval(clues)
        top = results[0] if results else None
        top_info = f"{top.photo_id} | {top.event} | Score: {top.score}" if top else "NO RESULTS"
        print(f"[{idx}] Query: '{q}' -> Status: {status} | Top Match: {top_info}")
        if q == "group of people together" or q == "many people together":
            print(f"    Parsed clues: ocr={clues.ocr_text}, count_bucket={clues.people_count_bucket}, people={clues.people}")
            if top:
                print(f"    Top photo people present={top.visual_semantics.people.present if top.visual_semantics else False}, count_bucket={top.visual_semantics.people.count_bucket if top.visual_semantics else None}")
        elif q == "charity":
            print(f"    Parsed clues: ocr={clues.ocr_text}, objects={clues.objects}, visual_concepts={clues.visual_concepts}")

if __name__ == "__main__":
    run_tests()
