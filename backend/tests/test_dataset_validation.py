import os
import json
import pytest

METADATA_PATH = "backend/app/data/photo_metadata.json"
PHOTOS_DIR_BACKEND = "backend/app/data/photos"
PHOTOS_DIR_FRONTEND = "frontend/public/photos"

def test_dataset_count_and_integrity():
    assert os.path.exists(METADATA_PATH), f"Metadata file missing at {METADATA_PATH}"
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    # 1. Exactly 50 records
    assert len(metadata) == 50, f"Expected exactly 50 photo metadata records, found {len(metadata)}"
    
    # 2. Check Photo IDs P001 to P050
    expected_ids = [f"P{i:03d}" for i in range(1, 51)]
    actual_ids = [p["photo_id"] for p in metadata]
    assert actual_ids == expected_ids, "Photo IDs do not match exact sequence P001..P050"
    
    # 3. Check for duplicates
    assert len(set(actual_ids)) == 50, "Duplicate photo IDs found"
    
    # 4. Check files exist in both backend and frontend directories
    for p in metadata:
        pid = p["photo_id"]
        filename = f"{pid}.jpg"
        backend_img = os.path.join(PHOTOS_DIR_BACKEND, filename)
        frontend_img = os.path.join(PHOTOS_DIR_FRONTEND, filename)
        
        assert os.path.exists(backend_img), f"Backend image missing for {pid}: {backend_img}"
        assert os.path.exists(frontend_img), f"Frontend image missing for {pid}: {frontend_img}"
        
        # Required fields check
        required_fields = ["photo_id", "filename", "date", "year", "location", "people", "event", "objects", "visual_concepts", "album"]
        for field in required_fields:
            assert field in p, f"Field '{field}' missing in photo record {pid}"
            
        assert isinstance(p["location"], dict), f"Location must be dict for {pid}"
        assert "city" in p["location"], f"Location.city missing for {pid}"
        assert "country" in p["location"], f"Location.country missing for {pid}"
