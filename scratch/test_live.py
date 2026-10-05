import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.app.mvp.retrieval import execute_retrieval
from backend.app.mvp.query_parser import parse_query

queries = [
    "lion",
    "dog",
    "beach",
    "2022",
    "Goa beach",
    "smg written hat",
    "birthday with Rohan"
]

for q in queries:
    clues = parse_query(q)
    results, status = execute_retrieval(clues)
    top = results[0] if results else None
    print(f"Query: '{q}' -> Status: {status}, Top Photo: {top.photo_id if top else None} ({top.filename if top else None}), Score: {top.score if top else 0:.3f}")
    if top and top.match_reasons:
        print(f"   Match reasons: {top.match_reasons[:3]}")
