import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size

# Save 6 strategic crops to locate cat
crops = {
    "cat_candidate_left": (100, 400, 400, 700),
    "cat_candidate_midleft": (400, 300, 750, 600),
    "cat_candidate_center": (500, 300, 900, 650),
    "cat_candidate_right": (900, 300, 1300, 650),
    "cat_candidate_farright": (1200, 300, 1500, 650),
}

out_dir = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search"
os.makedirs(out_dir, exist_ok=True)

for name, box in crops.items():
    crop = img.crop(box)
    crop.save(os.path.join(out_dir, f"{name}.png"))

print("Saved strategic crops for cat location check.")
