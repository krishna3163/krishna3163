import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size
arr = np.array(img)

# Let's inspect the board lights:
# Find bright regions in top and middle
# Filter pixels with max(RGB) > 160
bright = (arr.max(axis=2) > 160)

# Let's check Y: 50..500
board_y, board_x = np.where(bright[:500, :])
print("Board lights Y range:", board_y.min(), board_y.max())
print("Board lights X range:", board_x.min(), board_x.max())

# Let's check reflection in Y: 500..1024
refl_y, refl_x = np.where(bright[500:, :])
refl_y += 500
print("Reflection Y range:", refl_y.min(), refl_y.max())
print("Reflection X range:", refl_x.min(), refl_x.max())

# Let's find local clusters for the board lights
# Check different color neon signs (Yellow, Red, Cyan, White)
yellow_sign = (arr[:,:,0] > 200) & (arr[:,:,1] > 150) & (arr[:,:,2] < 120) & (np.arange(h)[:, None] < 550)
red_sign = (arr[:,:,0] > 200) & (arr[:,:,1] < 120) & (arr[:,:,2] < 120) & (np.arange(h)[:, None] < 550)
cyan_sign = (arr[:,:,2] > 200) & (arr[:,:,1] > 150) & (arr[:,:,0] < 120) & (np.arange(h)[:, None] < 550)

if yellow_sign.sum() > 0:
    ys_y, ys_x = np.where(yellow_sign)
    print(f"Yellow Sign Box: Y [{ys_y.min()}-{ys_y.max()}], X [{ys_x.min()}-{ys_x.max()}]")

if red_sign.sum() > 0:
    rs_y, rs_x = np.where(red_sign)
    print(f"Red Sign Box: Y [{rs_y.min()}-{rs_y.max()}], X [{rs_x.min()}-{rs_x.max()}]")

if cyan_sign.sum() > 0:
    cs_y, cs_x = np.where(cyan_sign)
    print(f"Cyan Sign Box: Y [{cs_y.min()}-{cs_y.max()}], X [{cs_x.min()}-{cs_x.max()}]")

# Search for cat:
# Let's check for cat features across X: 0..1536 and Y: 300..750
# Check non-background objects (desk, shelf, window sill, bed, roof edge)
for x_start in range(0, 1400, 100):
    for y_start in range(300, 700, 100):
        patch = arr[y_start:y_start+100, x_start:x_start+100]
        # Check standard deviation to find detailed objects
        std_val = patch.std(axis=(0,1)).mean()
        if std_val > 35:
            # Check if this patch has orange/black/white/gray cat texture
            print(f"Detailed Object Patch at Y:[{y_start}-{y_start+100}], X:[{x_start}-{x_start+100}] | std={std_val:.1f} | Mean={patch.mean(axis=(0,1)).round(1)}")
