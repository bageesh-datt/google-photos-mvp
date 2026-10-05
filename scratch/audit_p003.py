import json
import os
from PIL import Image

METADATA_PATH = "backend/app/data/photo_metadata.json"
PHOTOS_DIR = "frontend/public/photos"

with open(METADATA_PATH, "r") as f:
    photos = json.load(f)

p003_meta = None
for p in photos:
    if p["photo_id"] == "P003":
        p003_meta = p
        break

print("=== P003 METADATA RECORD ===")
print(json.dumps(p003_meta, indent=2))

# Find physical image file for P003
image_url = p003_meta.get("image_url", "")
filename = p003_meta.get("filename", "")
print("\nImage URL:", image_url)
print("Filename:", filename)

# Check files in frontend/public/photos
if os.path.exists(PHOTOS_DIR):
    files = os.listdir(PHOTOS_DIR)
    p003_files = [f for f in files if "P003" in f or "p003" in f or "Monsoon" in f or "monsoon" in f or "lion" in f]
    print("\nMatching image files in public/photos:", p003_files)
    
    for fname in p003_files:
        fpath = os.path.join(PHOTOS_DIR, fname)
        try:
            with Image.open(fpath) as img:
                print(f"File '{fname}': Format={img.format}, Size={img.size}, Mode={img.mode}")
        except Exception as e:
            print(f"File '{fname}': Could not open - {e}")
