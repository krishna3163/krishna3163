import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size
arr = np.array(img)

print(f"Image Size: {w}x{h}")

# Let's save 16 crop tiles to inspect visually or programmatically find features
crop_dir = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\crops"
os.makedirs(crop_dir, exist_ok=True)

# Scan grid 4x4
tile_w, tile_h = w // 4, h // 4
for r in range(4):
    for c in range(4):
        x1, y1 = c * tile_w, r * tile_h
        x2, y2 = x1 + tile_w, y1 + tile_h
        crop = img.crop((x1, y1, x2, y2))
        crop.save(os.path.join(crop_dir, f"crop_r{r}_c{c}_{x1}_{y1}.png"))

print("Saved 16 crop tiles for region analysis.")
