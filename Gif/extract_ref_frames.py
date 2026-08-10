import os
from PIL import Image

gif_paths = [
    r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\d1p0kr2-931c991a-906c-44de-9ffa-0f654bc310f6.gif",
    r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\ddwqjut-79060fc2-c6be-4e80-ab44-3c405523e4fd.gif",
    r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\demij6b-7cea31ba-524e-440b-8567-5249198385d5.gif",
]

out_dir = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\ref_frames"
os.makedirs(out_dir, exist_ok=True)

for idx, path in enumerate(gif_paths):
    img = Image.open(path)
    img.seek(0)
    out_path = os.path.join(out_dir, f"ref_gif_{idx+1}.png")
    img.convert("RGB").save(out_path)
    print(f"Saved {out_path}")
