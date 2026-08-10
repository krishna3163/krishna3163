import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size
arr = np.array(img)

# Let's crop vertical strips or subregions and inspect where cat fur / cat body is.
# Cat fur can be orange/ginger (R>140, G:60..140, B<80) or dark silhouette or white/gray.
# Let's scan all 200x200 blocks across the image and save crops with high detail in middle area (Y: 200 to 700).

out_dir = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search"
os.makedirs(out_dir, exist_ok=True)

count = 0
for y in range(150, 700, 100):
    for x in range(100, 1400, 150):
        crop = img.crop((x, y, x+200, y+200))
        crop.save(os.path.join(out_dir, f"crop_y{y}_x{x}.png"))
        count += 1

print(f"Saved {count} crops to {out_dir}")
