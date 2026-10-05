import json

def audit_dataset():
    with open("backend/app/data/photo_metadata.json", "r", encoding="utf-8") as f:
        photos = json.load(f)

    print(f"Total photos: {len(photos)}")
    
    print("\n--- ALL 50 PHOTOS & PEOPLE METADATA ---")
    for p in photos:
        p_id = p.get("photo_id")
        filename = p.get("filename")
        event = p.get("event")
        people_named = p.get("people", [])
        v_sem = p.get("visual_semantics", {})
        p_sem = v_sem.get("people", {}) if isinstance(v_sem, dict) else {}
        
        present = p_sem.get("present", False)
        count = p_sem.get("count", 0)
        bucket = p_sem.get("count_bucket", "none")
        g_type = p_sem.get("group_type", "none")
        ctx = p_sem.get("people_context", "")
        spatial = v_sem.get("spatial_relations", []) if isinstance(v_sem, dict) else []

        print(f"[{p_id}] {filename} | {event}")
        print(f"     Named: {people_named}")
        print(f"     PeopleSemantics: present={present}, count={count}, bucket={bucket}, group_type={g_type}")
        print(f"     Context: '{ctx}' | Spatial: {spatial}")

if __name__ == "__main__":
    audit_dataset()
