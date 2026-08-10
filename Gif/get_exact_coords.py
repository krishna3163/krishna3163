import os
from PIL import Image
import numpy as np

img_path = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
img = Image.open(img_path).convert("RGB")
w, h = img.size
arr = np.array(img)

print("Image size:", w, h)

# Let's crop and save key element boxes to confirm coordinates:
# 1. Cat box: X: 350..560, Y: 620..810
# 2. PIXEL MART sign box: X: 470..950, Y: 130..240
# 3. OPEN sign box: X: 820..950, Y: 360..440
# 4. MENU BOARD sign box: X: 1140..1480, Y: 200..600

cat_crop = img.crop((350, 620, 560, 810))
cat_crop.save(r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search\cat_exact.png")

pm_crop = img.crop((470, 130, 950, 240))
pm_crop.save(r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search\pixel_mart.png")

open_crop = img.crop((820, 360, 950, 440))
open_crop.save(r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search\open_sign.png")

menu_crop = img.crop((1140, 200, 1480, 600))
menu_crop.save(r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search\menu_board.png")

refl_crop = img.crop((0, 680, 1536, 1024))
refl_crop.save(r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cat_search\street_reflection.png")

print("Saved exact element crops successfully!")
