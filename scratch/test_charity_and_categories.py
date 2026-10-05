import os
import sys
from backend.app.mvp.query_parser import fallback_parse_query
from backend.app.mvp.retrieval import execute_retrieval

def run_test_suite():
    queries = [
        "charity",
        "CHARITY",
        "charity event",
        "SMG",
        "passport text",
        "birthday",
        "welcome",
        "many people together",
        "lion",
        "Goa beach 2022"
    ]
    
    print("=" * 70)
    print("UNIVERSAL RETRIEVAL & QUERY INTENT TEST SUITE")
    print("=" * 70)
    
    for q in queries:
        clues = fallback_parse_query(q)
        results, status = execute_retrieval(clues)
        top = results[0]
        
        safe_reasons = [r.encode('ascii', 'replace').decode('ascii') for r in top.match_reasons]
        
        print(f"Query: '{q}'")
        print(f"  Parsed Intent: ocr={clues.ocr_text}, people_bucket={clues.people_count_bucket}, objects={clues.objects}")
        print(f"  Status: {status} | Top Result: {top.photo_id} ({top.filename} - {top.event}), Score: {top.score:.3f}")
        print(f"  Reasons: {safe_reasons}")
        print("-" * 70)

if __name__ == "__main__":
    run_test_suite()
