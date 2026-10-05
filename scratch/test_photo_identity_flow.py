import requests
import json
import os

BASE_URL = "http://127.0.0.1:8000/api/mvp/search"
PHOTOS_DIR = "frontend/public/photos"

test_queries = [
    ("charity", "P007", "Christmas Charity Drive", "P007.jpg"),
    ("lion", "P038", "Gir Lion Wildlife Safari", "P038.jpg"),
    ("SMG", "P001", "Diwali Celebration", "P001.jpg"),
    ("beach", "P023", "Goa Summer Vacation", "P023.jpg"),
    ("birthday with Rohan", "P022", "Rohan 11th Birthday", "P022.jpg")
]

def test_photo_identity_flow():
    print("=== STEP 6 & 10: VERIFY SEARCH RESULT PHOTO IDENTITY FLOW ===")
    
    for q, expected_id, expected_title, expected_filename in test_queries:
        resp = requests.post(BASE_URL, json={"query": q})
        assert resp.status_code == 200, f"Query '{q}' failed with HTTP {resp.status_code}"
        data = resp.json()
        results = data.get("results", [])
        assert len(results) > 0, f"Query '{q}' returned zero results"
        
        top = results[0]
        top_id = top["photo_id"]
        top_file = top["filename"]
        top_url = top["image_url"]
        
        print(f"\nQuery: '{q}'")
        print(f"  Top Result photo_id : '{top_id}' (Expected: '{expected_id}')")
        print(f"  Filename            : '{top_file}' (Expected: '{expected_filename}')")
        print(f"  Image URL           : '{top_url}'")
        
        assert top_id == expected_id, f"Photo ID mismatch for '{q}': got {top_id}, expected {expected_id}"
        assert top_file == expected_filename, f"Filename mismatch for '{q}': got {top_file}, expected {expected_filename}"
        assert top_url == f"/photos/{expected_filename}", f"URL mismatch for '{q}': got {top_url}"
        
        # Verify physical image asset exists on disk
        physical_file = os.path.join(PHOTOS_DIR, top_file)
        assert os.path.exists(physical_file), f"Physical photo file missing on disk: {physical_file}"
        
        print(f"  [OK] Identity preserved: Card photo_id '{top_id}' == Viewer image '{top_url}'")

    print("\nAll photo identity flow tests passed 100% cleanly!")

if __name__ == "__main__":
    test_photo_identity_flow()
