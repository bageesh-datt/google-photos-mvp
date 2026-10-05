import json
import os

METADATA_PATH = "backend/app/data/photo_metadata.json"
PHOTOS_DIR = "frontend/public/photos"

with open(METADATA_PATH, "r") as f:
    photos = json.load(f)

print(f"Total photos in metadata: {len(photos)}")
assert len(photos) == 50, f"Expected 50 photos, found {len(photos)}"

problematic_ids = ["P001", "P003", "P007", "P009", "P028", "P043"]
audit_log = []

for p in photos:
    pid = p["photo_id"]
    fname = p["filename"]
    fpath = os.path.join(PHOTOS_DIR, fname)
    exists = os.path.exists(fpath)
    
    vs = p.get("visual_semantics", {})
    p_meta = vs.get("people", {})
    ocr = p.get("ocr_text", "")
    event = p.get("event", "")
    desc = p.get("description", "")
    
    if not exists:
        print(f"ERROR: Image file missing for {pid}: {fname}")
        
    if pid in problematic_ids:
        audit_log.append({
            "photo_id": pid,
            "filename": fname,
            "event": event,
            "description": desc,
            "people_present": p_meta.get("present"),
            "people_count": p_meta.get("count"),
            "count_bucket": p_meta.get("count_bucket"),
            "ocr_text": ocr
        })

print("\n=== PROBLEMATIC PHOTOS AUDIT LOG ===")
print(json.dumps(audit_log, indent=2))
