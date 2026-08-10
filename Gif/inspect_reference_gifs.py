import os
from PIL import Image

gif_paths = [
    r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\d1p0kr2-931c991a-906c-44de-9ffa-0f654bc310f6.gif",
    r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\ddwqjut-79060fc2-c6be-4e80-ab44-3c405523e4fd.gif",
    r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\demij6b-7cea31ba-524e-440b-8567-5249198385d5.gif",
]

for idx, path in enumerate(gif_paths):
    if os.path.exists(path):
        img = Image.open(path)
        frames = 0
        try:
            while True:
                frames += 1
                img.seek(img.tell() + 1)
        except EOFError:
            pass
        print(f"GIF #{idx+1} ({os.path.basename(path)}): Size={img.size}, Frames={frames}, Mode={img.mode}")
    else:
        print(f"GIF #{idx+1} not found at {path}")
