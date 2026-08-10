import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size
arr = np.array(img)

# Let's write an analysis script to locate:
# 1. Cat: check where cat shape/eyes/tail/fur is.
# Let's inspect non-black objects on balcony / rooftop / window / street / desk / bed.
# Let's save 9 main quadrant crops and print pixel intensity distributions.

quads = {
    "top_left": (0, 0, 512, 341),
    "top_center": (512, 0, 1024, 341),
    "top_right": (1024, 0, 1536, 341),
    "mid_left": (0, 341, 512, 682),
    "mid_center": (512, 341, 1024, 682),
    "mid_right": (1024, 341, 1536, 682),
    "bot_left": (0, 682, 512, 1024),
    "bot_center": (512, 682, 1024, 1024),
    "bot_right": (1024, 682, 1536, 1024),
}

for name, box in quads.items():
    x1, y1, x2, y2 = box
    sub = arr[y1:y2, x1:x2]
    bright = (sub.max(axis=2) > 200).sum()
    mean_rgb = sub.mean(axis=(0,1)).astype(int)
    print(f"Quadrant {name:10s} [X:{x1:4d}-{x2:4d}, Y:{y1:4d}-{y2:4d}]: Bright={bright:6d}, Mean RGB={list(mean_rgb)}")
