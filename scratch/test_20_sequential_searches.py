import requests

BASE_URL = "http://127.0.0.1:8000/api/mvp/search"

queries = [
    "charity",
    "lion",
    "SMG",
    "hat with SMG written on it",
    "many people together",
    "group of people",
    "large group",
    "crowd",
    "two people",
    "one person",
    "beach",
    "2022",
    "Goa beach 2022",
    "birthday with Rohan",
    "dog",
    "hat",
    "document",
    "people sitting together",
    "people standing together",
    "random query xyz123"
]

def run_20_sequential_tests():
    print(f"Executing {len(queries)} sequential search requests...")
    for idx, q in enumerate(queries, 1):
        resp = requests.post(BASE_URL, json={"query": q})
        assert resp.status_code == 200, f"Query '{q}' failed with status {resp.status_code}"
        data = resp.json()
        assert "results" in data, f"Query '{q}' response missing 'results'"
        results = data["results"]
        status = data.get("result_status", "unknown")
        
        top_photo = (results[0].get("event") or results[0].get("filename")) if results else "No Match"
        top_score = results[0]["score"] if results else 0.0
        print(f"[{idx:02d}/{len(queries)}] Query: '{q:28s}' -> Status: {status:14s} | Top Result: '{top_photo}' ({top_score:.1%})")

if __name__ == "__main__":
    run_20_sequential_tests()
