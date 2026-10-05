import json

def update_metadata():
    path = "backend/app/data/photo_metadata.json"
    with open(path, "r", encoding="utf-8") as f:
        photos = json.load(f)

    updated_count = 0
    for p in photos:
        if p.get("photo_id") == "P009":
            v_sem = p.get("visual_semantics", {})
            p_sem = v_sem.get("people", {})
            p_sem["count"] = 3
            p_sem["count_bucket"] = "small_group"
            p_sem["group_type"] = "group_of_people"
            p_sem["people_context"] = "small group of friends taking an evening stroll"
            v_sem["people"] = p_sem
            p["visual_semantics"] = v_sem
            updated_count += 1
            print("Updated P009 metadata to small_group (count=3).")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(photos, f, indent=2)
    print(f"Saved {path}. Updated {updated_count} record(s).")

if __name__ == "__main__":
    update_metadata()
