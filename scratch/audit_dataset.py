import json

with open('backend/app/data/photo_metadata.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total photos: {len(data)}")
for p in data:
    vs = p.get('visual_semantics', {})
    objs = vs.get('objects', p.get('objects', []))
    concepts = vs.get('visual_concepts', p.get('visual_concepts', []))
    desc = vs.get('generated_description', p.get('description', ''))
    print(f"{p['photo_id']} | fn={p['filename']} | event={p['event']} | album={p['album']}")
    print(f"   objects: {objs}")
    print(f"   concepts: {concepts}")
    print(f"   desc: {desc}")
    print("-" * 60)
