import json

with open("backend/app/data/photo_metadata.json", "r") as f:
    photos = json.load(f)

for p in photos:
    if p["photo_id"] in ["P006", "P007"]:
        print(f"Photo ID: {p['photo_id']}")
        print(f"  Filename: {p['filename']}")
        print(f"  Image URL: {p['image_url']}")
        print(f"  Event: {p['event']}")
        print(f"  Description: {p['description']}")
        print("-" * 50)
