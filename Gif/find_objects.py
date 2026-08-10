import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size
arr = np.array(img)

# Let's search for the cat, board, and reflection by checking color dynamics and edge density.
# Let's divide into 8x8 grid (192x128 tiles) and measure details

print("=== 8x8 GRID DETAILED ANALYSIS ===")
for r in range(8):
    for c in range(8):
        y1, y2 = r * 128, (r + 1) * 128
        x1, x2 = c * 192, (c + 1) * 192
        tile = arr[y1:y2, x1:x2]
        
        # Color means
        r_mean, g_mean, b_mean = tile.mean(axis=(0,1))
        # Brightness max
        max_b = tile.max()
        # Saturation max
        std_rgb = tile.std(axis=2).mean()
        
        # Detect bright neon text (high brightness, high saturation, sharp edges)
        # Detect cat (warm fur colors, orange/black/white/grey, specific region)
        # Detect reflection (lower half y > 600, horizontal ripple patterns, mirrored colors of upper neon)
        
        desc = []
        if max_b > 240 and (r_mean > 50 or g_mean > 50 or b_mean > 50):
            desc.append("BRIGHT_NEON_LIGHT")
        if y1 >= 512 and max_b > 180:
            desc.append("REFLECTION_ZONE")
            
        if desc:
            print(f"Grid ({r},{c}) Box Y:[{y1:4d}-{y2:4d}], X:[{x1:4d}-{x2:4d}] | Mean RGB: ({r_mean:3.0f},{g_mean:3.0f},{b_mean:3.0f}) | Tags: {', '.join(desc)}")
