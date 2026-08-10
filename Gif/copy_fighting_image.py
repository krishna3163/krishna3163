import os
import shutil

brain_dir = r"C:\Users\Krishna Kumar\.gemini\antigravity-ide\brain\aa51efbe-4df8-445b-a449-c085b5f26b02"
target_dir = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png"
os.makedirs(target_dir, exist_ok=True)

for f in os.listdir(brain_dir):
    if f.startswith("fighting_scene_base"):
        src = os.path.join(brain_dir, f)
        dst = os.path.join(target_dir, "Fighting_Scene.png")
        shutil.copy(src, dst)
        print(f"Copied {f} -> {dst}")
