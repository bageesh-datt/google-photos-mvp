import json

with open('backend/app/data/photo_metadata.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("ALL PHOTO OCR TEXTS:")
for p in data:
    pid = p.get('photo_id')
    fn = p.get('filename')
    ocr = p.get('ocr_text', '')
    objs = p.get('objects', [])
    print(f"{pid} ({fn}): ocr='{ocr}' | objs={objs[:3]}")
