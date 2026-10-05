import json

with open("backend/app/data/photo_metadata.json", "r") as f:
    photos = json.load(f)

for p in photos:
    objs = [o.lower() for o in p.get("objects", [])]
    concepts = [c.lower() for c in p.get("visual_concepts", [])]
    desc = p.get("description", "").lower()
    gen_desc = p.get("visual_semantics", {}).get("generated_description", "").lower()
    if "lion" in desc or "lion" in gen_desc or "lion" in objs or "lion" in concepts:
        print(f"Photo ID: {p['photo_id']} | Filename: {p['filename']} | Title: {p.get('event')}")
        print("  Description:", p.get("description"))
        print("  Generated Description:", p.get("visual_semantics", {}).get("generated_description"))
        print("  People Semantics:", p.get("visual_semantics", {}).get("people"))
        print("-" * 60)
