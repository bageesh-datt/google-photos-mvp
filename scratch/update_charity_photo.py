import json
from backend.app.mvp.embedding_service import encode_text

def update_charity_photo():
    filepath = "backend/app/data/photo_metadata.json"
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for photo in data:
        if photo["photo_id"] == "P007":
            photo["event"] = "Christmas Charity Drive"
            photo["ocr_text"] = "Merry Christmas 2021 CHARITY Drive"
            photo["description"] = "Kids opening gift boxes under the glowing Christmas tree with Mom during community CHARITY drive."
            
            if not photo.get("visual_concepts"):
                photo["visual_concepts"] = []
            if "charity" not in photo["visual_concepts"]:
                photo["visual_concepts"].extend(["charity", "charity drive", "donation"])
                
            if photo.get("visual_semantics"):
                v = photo["visual_semantics"]
                v["ocr_text"] = "Merry Christmas 2021 CHARITY Drive"
                v["generated_description"] = "Kids opening gift boxes under the glowing Christmas tree with Mom during community CHARITY drive."
                if "charity" not in v["visual_concepts"]:
                    v["visual_concepts"].extend(["charity", "charity drive", "donation"])
                if "charity box" not in v["objects"]:
                    v["objects"].append("charity box")
                    
                # Recompute embedding vector
                emb_text = f"{photo['event']} {photo['description']} {' '.join(v['visual_concepts'])} {v['ocr_text']}"
                v["visual_embedding"] = encode_text(emb_text)
                
            print("Successfully updated P007 as CHARITY drive photo.")
            break
            
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    update_charity_photo()
