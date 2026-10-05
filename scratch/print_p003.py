import json

with open("backend/app/data/photo_metadata.json", "r") as f:
    photos = json.load(f)

for p in photos:
    if p["photo_id"] == "P003":
        p_copy = dict(p)
        if "visual_semantics" in p_copy and "visual_embedding" in p_copy["visual_semantics"]:
            p_copy["visual_semantics"] = dict(p_copy["visual_semantics"])
            p_copy["visual_semantics"]["visual_embedding"] = f"[{len(p_copy['visual_semantics']['visual_embedding'])} floats]"
        print(json.dumps(p_copy, indent=2))
