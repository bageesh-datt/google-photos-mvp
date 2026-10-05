import os
import hashlib
from PIL import Image

p006_path = "frontend/public/photos/P006.jpg"
p007_path = "frontend/public/photos/P007.jpg"

print(f"P006.jpg exists: {os.path.exists(p006_path)}")
print(f"P007.jpg exists: {os.path.exists(p007_path)}")

with open(p006_path, "rb") as f:
    h006 = hashlib.md5(f.read()).hexdigest()

with open(p007_path, "rb") as f:
    h007 = hashlib.md5(f.read()).hexdigest()

print(f"P006 MD5: {h006}")
print(f"P007 MD5: {h007}")

with Image.open(p006_path) as img:
    print(f"P006.jpg size: {img.size}, format: {img.format}")

with Image.open(p007_path) as img:
    print(f"P007.jpg size: {img.size}, format: {img.format}")
