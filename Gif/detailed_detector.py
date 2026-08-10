import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size
arr = np.array(img)

# Let's inspect where orange fur / cat ears / cat silhouette or sleeping cat is located.
# Typical cat colors in pixel art / digital art:
# Orange cat: R: 160-240, G: 90-160, B: 30-100
# Calico/Black cat: Dark silhouette R<50, G<50, B<50 surrounded by brighter background or bed/couch/desk.
# White/Grey cat: R,G,B close to each other (120-200)

print("--- Searching for Cat Color Candidates ---")
# 1) Orange cat candidate:
orange_cat = (arr[:,:,0] > 170) & (arr[:,:,1] > 100) & (arr[:,:,1] < 160) & (arr[:,:,2] < 90)
# exclude bright neon yellow/orange in upper board (y < 300 x > 400)
cy, cx = np.where(orange_cat)
for i in range(0, len(cy), len(cy)//20 if len(cy)>20 else 1):
    print(f"Orange pixel at Y={cy[i]}, X={cx[i]}")

# Let's inspect region around Y: 400..700 across X: 0..1536
print("\n--- Inspecting Y:400-700 for cat & key objects ---")
for y_start in range(400, 700, 50):
    for x_start in range(0, 1500, 200):
        patch = arr[y_start:y_start+50, x_start:x_start+200]
        r_m, g_m, b_m = patch.mean(axis=(0,1))
        # Print non-dark non-water patches
        if r_m > 30 or g_m > 30 or b_m > 30:
            print(f"Box Y:[{y_start}-{y_start+50}], X:[{x_start}-{x_start+200}] -> RGB: ({r_m:.1f}, {g_m:.1f}, {b_m:.1f})")
