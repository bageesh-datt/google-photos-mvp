import json

METADATA_PATH = "backend/app/data/photo_metadata.json"

with open(METADATA_PATH, "r") as f:
    photos = json.load(f)

for p in photos:
    if p["photo_id"] == "P003":
        print("Fixing P003 metadata...")
        p["people"] = []
        p["people_relationships"] = []
        p["objects"] = ["asiatic lion", "lion", "greenery", "grass", "animal", "wildlife"]
        p["visual_concepts"] = ["lion", "asiatic lion", "wildlife", "animal", "nature", "monsoon trek", "outdoors"]
        if "visual_semantics" in p:
            vs = p["visual_semantics"]
            vs["objects"] = p["objects"]
            vs["visual_concepts"] = p["visual_concepts"]
            vs["people"] = {
                "present": False,
                "count": 0,
                "count_bucket": "none",
                "group_type": "none",
                "people_context": "No people present, animal subject",
                "relationships": []
            }
            vs["people_context"] = "No people present, animal subject"

with open(METADATA_PATH, "w") as f:
    json.dump(photos, f, indent=2)

print("P003 metadata successfully corrected!")
