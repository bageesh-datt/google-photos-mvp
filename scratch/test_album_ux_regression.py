import requests

BASE_URL = "http://127.0.0.1:8000/api/mvp/photos"

def test_album_data_derivation():
    print("Fetching all 50 photos to verify album UX grouping...")
    resp = requests.get(BASE_URL)
    assert resp.status_code == 200
    photos = resp.json()
    assert len(photos) == 50, f"Expected 50 photos, got {len(photos)}"
    
    albums = {}
    for p in photos:
        aname = p.get("album", "Miscellaneous")
        if aname not in albums:
            albums[aname] = []
        albums[aname].append(p)
        
    print(f"Verified {len(albums)} dynamic albums from metadata.")
    
    # Test specific key albums
    fam_fest = albums.get("Family Festivities", [])
    assert len(fam_fest) == 4, f"Expected 4 photos in 'Family Festivities', got {len(fam_fest)}"
    fam_fest_ids = [p["photo_id"] for p in fam_fest]
    assert fam_fest_ids == ["P001", "P002", "P007", "P010"], f"Unexpected photo IDs for Family Festivities: {fam_fest_ids}"
    print("[OK] Family Festivities album dynamically derives exactly 4 photos (P001, P002, P007, P010)")
    
    docs = albums.get("Important Documents", [])
    assert len(docs) == 5, f"Expected 5 photos in 'Important Documents', got {len(docs)}"
    print("[OK] Important Documents album dynamically derives exactly 5 photos")
    
    foodie = albums.get("Foodie Diaries", [])
    assert len(foodie) == 4, f"Expected 4 photos in 'Foodie Diaries', got {len(foodie)}"
    print("[OK] Foodie Diaries album dynamically derives exactly 4 photos")
    
    for aname, plist in albums.items():
        assert len(plist) > 0, f"Album '{aname}' should have at least 1 photo"
        
    print("All album grouping data assertions passed cleanly!")

if __name__ == "__main__":
    test_album_data_derivation()
