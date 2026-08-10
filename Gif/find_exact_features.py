import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size
arr = np.array(img)

# Let's save crops for different regions to pinpoint cat, board light, reflection

# 1. Check top half Y: 0..550 for Neon / Board Lights
# Let's find all bright regions
bright_map = arr.max(axis=2) > 140

# Save crop of board lights region
board_crop = img.crop((0, 0, w, 550))
board_crop.save(r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search\board_lights.png")

# Save crop of reflection region Y: 550..1024
refl_crop = img.crop((0, 550, w, h))
refl_crop.save(r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search\reflection.png")

# Search for cat:
# Let's inspect where cat body is located by checking variance, color, shapes across the middle region (Y: 200..750)
print("Scanning for Cat...")
# Let's check non-dark areas in mid-left, mid-center, mid-right
for y in range(200, 750, 50):
    for x in range(0, w - 150, 100):
        patch = arr[y:y+100, x:x+150]
        # Calculate color variance
        var = patch.var(axis=(0,1)).sum()
        mean_rgb = patch.mean(axis=(0,1))
        # Cat usually has distinct fur texture or silhouette
        if 500 < var < 8000 and mean_rgb[0] > 20: # interesting object
            print(f"Object at Y:[{y}-{y+100}], X:[{x}-{x+150}]: Var={var:.0f}, Mean RGB={list(mean_rgb.astype(int))}")
