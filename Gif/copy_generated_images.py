import os
import shutil

brain_dir = r"C:\Users\Krishna Kumar\.gemini\antigravity-ide\brain\aa51efbe-4df8-445b-a449-c085b5f26b02"
target_dir = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png"
os.makedirs(target_dir, exist_ok=True)

# Find generated files
files = os.listdir(brain_dir)

mapping = {}
for f in files:
    if f.startswith("cyberpunk_samurai_base"):
        mapping[f] = "Cyberpunk_Samurai.png"
    elif f.startswith("lofi_gamer_room_base"):
        mapping[f] = "Lofi_Gamer_Room.png"
    elif f.startswith("mystic_sorcerer_base"):
        mapping[f] = "Mystic_Sorcerer.png"

for src_name, dst_name in mapping.items():
    src_path = os.path.join(brain_dir, src_name)
    dst_path = os.path.join(target_dir, dst_name)
    shutil.copy(src_path, dst_path)
    print(f"Copied {src_name} -> {dst_path}")
