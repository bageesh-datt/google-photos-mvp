import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/mvp/search"

queries = [
    "charity",
    "lion",
    "SMG",
    "many people together",
    "beach",
    "2022",
    "Goa beach 2022",
    "birthday with Rohan",
    "group of people",
    "crowd",
    "dog",
    "hat",
    "document",
    "people sitting together",
    "random query"
]

def run_sequential_tests():
    print(f"Executing {len(queries)} sequential search requests...")
    for idx, q in enumerate(queries, 1):
        resp = requests.post(BASE_URL, json={"query": q})
        assert resp.status_code == 200, f"Query '{q}' failed with status {resp.status_code}"
        data = resp.json()
        assert "results" in data, f"Query '{q}' response missing 'results'"
        results = data["results"]
        top_photo = (results[0].get("event") or results[0].get("filename")) if results else "No Match"
        top_score = results[0]["score"] if results else 0.0
        print(f"[{idx:02d}/{len(queries)}] Query: '{q}' -> Top Result: '{top_photo}' (Score: {top_score:.1%})")

if __name__ == "__main__":
    run_sequential_tests()
