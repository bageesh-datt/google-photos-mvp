import json
from backend.app.mvp.query_parser import parse_query, fallback_parse_query
from backend.app.mvp.retrieval import execute_retrieval

clues = parse_query("charity")
results, status = execute_retrieval(clues)

print(f"Status: {status}")
print(f"Total Results: {len(results)}\n")

for idx, r in enumerate(results[:5]):
    print(f"[{idx}] Photo ID: {r.photo_id} | Filename: {r.filename} | Event: '{r.event}' | Score: {r.score}")
    print(f"    Image URL: {r.image_url}")
    print(f"    Description: {r.description}")
    print("-" * 60)
