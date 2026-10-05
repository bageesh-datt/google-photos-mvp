import json

METADATA_PATH = "backend/app/data/photo_metadata.json"

with open(METADATA_PATH, "r") as f:
    photos = json.load(f)

albums = {}
for p in photos:
    aname = p.get("album", "Miscellaneous")
    if aname not in albums:
        albums[aname] = []
    albums[aname].append(p)

print(f"Total Albums found: {len(albums)}\n")
for aname, plist in sorted(albums.items()):
    pids = [p["photo_id"] for p in plist]
    print(f"Album: '{aname}' | Count: {len(plist)} photos | Photo IDs: {pids}")
