import json

with open('backend/app/data/photo_metadata.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for p in data:
    pid = p.get('photo_id')
    ocr = p.get('ocr_text', '')
    objs = p.get('objects', [])
    desc = p.get('description', '')
    if any(k in str(p).lower() for k in ['smg', 'hat', 'cap', 'p007']):
        print(f"{pid}: filename={p.get('filename')} | event={p.get('event')}")
        print(f"   ocr_text: '{ocr}'")
        print(f"   objects: {objs}")
        print(f"   desc: {desc}")
        print("-" * 50)
