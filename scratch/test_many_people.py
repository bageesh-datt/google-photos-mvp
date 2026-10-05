import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.app.mvp.query_parser import parse_query
from backend.app.mvp.retrieval import execute_retrieval

queries = [
    "many people together",
    "large group of people",
    "people sitting together",
    "red shirt",
    "lion",
    "SMG",
    "hat with SMG written on it"
]

for q in queries:
    clues = parse_query(q)
    results, status = execute_retrieval(clues)
    top = results[0] if results else None
    print(f"Query: '{q}'")
    print(f"   Parsed clues: people_bucket={clues.people_count_bucket}, objects={clues.objects}, ocr={clues.ocr_text}")
    print(f"   Status: {status} | Top Photo: {top.photo_id if top else None} ({top.filename if top else None} - {top.event if top else ''}), Score: {top.score if top else 0:.3f}")
    if top and top.match_reasons:
        print(f"   Reasons: {top.match_reasons[:2]}")
    print("-" * 60)
