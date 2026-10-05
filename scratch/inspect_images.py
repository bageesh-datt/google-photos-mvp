import os
from PIL import Image

for pid in ["P001", "P002", "P003", "P007", "P011", "P038", "P043"]:
    p_path = f"backend/app/data/photos/{pid}.jpg"
    if os.path.exists(p_path):
        with Image.open(p_path) as img:
            print(f"{pid}.jpg: size={img.size}, mode={img.mode}")
