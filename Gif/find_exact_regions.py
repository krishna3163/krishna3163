import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size
arr = np.array(img)

# Let's inspect bright neon colors in the top 60% vs bottom 40%
# Bright red/yellow/pink/cyan neon text/signs in top half
# Reflections in bottom half (y > 550)

# Let's save small crops of interest to analyze where the cat is located.
# Let's check non-dark pixels in middle rows (Y: 300 to 700) to find character/cat features.

# Let's scan Y in steps of 50
print("--- Scan Y slices ---")
for y in range(0, h, 50):
    row_slice = arr[y:y+50, :]
    # count pixels by color category
    red_neon = ((row_slice[:,:,0] > 180) & (row_slice[:,:,1] < 120) & (row_slice[:,:,2] < 120)).sum()
    yellow_neon = ((row_slice[:,:,0] > 180) & (row_slice[:,:,1] > 140) & (row_slice[:,:,2] < 100)).sum()
    cyan_neon = ((row_slice[:,:,2] > 180) & (row_slice[:,:,1] > 140) & (row_slice[:,:,0] < 100)).sum()
    white_bright = (row_slice.mean(axis=2) > 200).sum()
    
    print(f"Y [{y:4d}-{y+50:4d}]: Red={red_neon:5d}, Yellow={yellow_neon:5d}, Cyan={cyan_neon:5d}, White={white_bright:5d}")
