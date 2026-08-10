import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_46_13 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size
arr = np.array(img)

print(f"Image loaded: {w}x{h}")

# Save cropped test regions to verify exact bounding boxes

# 1. Character crop: X: 80..580, Y: 130..820
char_crop = img.crop((80, 130, 580, 820))
char_crop.save(r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search\samurai_char.png")

# 2. Castle & Village Lights crop: X: 520..1536, Y: 380..950
village_crop = img.crop((520, 380, 1536, 950))
village_crop.save(r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search\village_lights.png")

# 3. Sakura canopy crop: X: 0..850, Y: 0..380
sakura_crop = img.crop((0, 0, 850, 380))
sakura_crop.save(r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search\sakura_canopy.png")

# 4. Stone Lantern crop: X: 980..1350, Y: 700..920
lantern_crop = img.crop((980, 700, 1350, 920))
lantern_crop.save(r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search\lanterns.png")

print("Saved inspection crops successfully!")
