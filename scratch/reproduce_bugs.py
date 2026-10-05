from backend.app.mvp.query_parser import parse_query, fallback_parse_query
from backend.app.mvp.retrieval import execute_retrieval

def reproduce():
    print("=" * 60)
    print("REPRODUCING ISSUE 2: 'charity'")
    print("=" * 60)
    clues_c = fallback_parse_query("charity")
    results_c, status_c = execute_retrieval(clues_c)
    print(f"Fallback parsed clues for 'charity': {clues_c}")
    print(f"Top result: {results_c[0].photo_id} ({results_c[0].filename} - {results_c[0].event}), Score: {results_c[0].score}")
    print(f"Top 3 results: {[(r.photo_id, r.event, r.score) for r in results_c[:3]]}")
    
    print("\n" + "=" * 60)
    print("REPRODUCING ISSUE 3: 'group of people together'")
    print("=" * 60)
    clues_g = fallback_parse_query("group of people together")
    results_g, status_g = execute_retrieval(clues_g)
    print(f"Fallback parsed clues for 'group of people together': {clues_g}")
    print(f"Top result: {results_g[0].photo_id} ({results_g[0].filename} - {results_g[0].event}), Score: {results_g[0].score}")
    print(f"Top 5 results: {[(r.photo_id, r.event, r.score) for r in results_g[:5]]}")

if __name__ == "__main__":
    reproduce()
