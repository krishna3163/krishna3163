import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size
arr = np.array(img)

print("Image Size:", w, h)

# Let's check coordinates from build_gif_43_27.py
# kc_box = (520, 60, 700, 220)
kc_patch = arr[60:220, 520:700]
print("KC Box mean RGB:", kc_patch.mean(axis=(0,1)))

# eat_lines box: X: 1180..1430, Y: 35..240
eat_patch = arr[35:240, 1180:1430]
print("EAT Lines mean RGB:", eat_patch.mean(axis=(0,1)))

# pc_win box: Y: 780..950, X: 1040..1200
pc_patch = arr[780:950, 1040:1200]
print("PC Case mean RGB:", pc_patch.mean(axis=(0,1)))

# Sleeping Cat area: X: 150..350, Y: 550..700
cat_patch = arr[550:700, 150:350]
print("Cat Bed Area mean RGB:", cat_patch.mean(axis=(0,1)))
