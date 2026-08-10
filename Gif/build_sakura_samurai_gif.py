import os
import math
import numpy as np
from PIL import Image, ImageDraw

def generate_sakura_samurai_gif(image_path, output_gif_path, num_frames=36, fps=12):
    print(f"Loading base image: {image_path}")
    base_img = Image.open(image_path).convert("RGBA")
    w, h = base_img.size
    print(f"Image dimensions: {w}x{h}")

    base_arr = np.array(base_img, dtype=np.float32)

    # -------------------------------------------------------------------------
    # BOUNDING BOXES & FEATURE POSITIONS
    # -------------------------------------------------------------------------
    # Character boxes
    char_box = (250, 130, 580, 820)
    head_box = (320, 130, 480, 260)
    scarf_box = (290, 240, 460, 340)
    tail_box = (90, 390, 340, 630)
    sword_box = (450, 500, 570, 800)

    # Sakura canopy: X: 0..850, Y: 0..380
    sakura_tree_box = (0, 0, 850, 380)

    # Stone lanterns
    lantern1_box = (990, 710, 1070, 840)
    lantern2_box = (1250, 740, 1340, 920)

    # Village & Castle window mask detection
    # Yellow/orange glowing windows in background
    village_area = base_arr[350:950, 500:1536, :3]
    win_mask = (village_area[:, :, 0] > 180) & (village_area[:, :, 1] > 130) & (village_area[:, :, 2] < 110)
    wy, wx = np.where(win_mask)

    # Pick 40 distinct window seed points for independent blinking
    np.random.seed(101)
    if len(wx) > 0:
        indices = np.random.choice(len(wx), min(40, len(wx)), replace=False)
        windows = [(500 + wx[idx], 350 + wy[idx], i) for i, idx in enumerate(indices)]
    else:
        windows = []

    # Dynamic Falling Sakura Petals setup
    # 35 falling petals drifting across the wind
    petals = []
    for p_i in range(35):
        init_x = np.random.randint(-100, w)
        init_y = np.random.randint(-50, h)
        speed_x = np.random.uniform(1.2, 2.5)
        speed_y = np.random.uniform(0.8, 1.8)
        size = np.random.choice([2, 3, 4])
        wobble_freq = np.random.uniform(2.0, 4.0)
        petals.append({
            "x": init_x,
            "y": init_y,
            "sx": speed_x,
            "sy": speed_y,
            "size": size,
            "freq": wobble_freq,
            "phase": p_i * 0.3
        })

    frames = []

    for frame_idx in range(num_frames):
        t = frame_idx / float(num_frames) # 0.0 to 1.0
        angle = 2.0 * math.pi * t

        # Start from base image array
        frame_arr = base_arr.copy()

        # =====================================================================
        # FEATURE 1: FLOWER ANIMATION ("flower ka animation")
        # =====================================================================

        # Tree canopy animation removed as requested (tree stays static)
        # Ground flowers animation
        ground_patch = frame_arr[600:1024, 0:1400, :3]
        g_pink = (ground_patch[:, :, 0] > 140) & (ground_patch[:, :, 2] > 120) & (ground_patch[:, :, 1] < 130)
        g_glow = 1.0 + 0.25 * math.sin(angle * 3)
        ground_patch[g_pink] = np.clip(ground_patch[g_pink] * g_glow, 0, 255)
        frame_arr[600:1024, 0:1400, :3] = ground_patch

        # =====================================================================
        # FEATURE 2: HOUSE & LANTERN LIGHT ANIMATION ("ghar ka light ka bhi animation")
        # =====================================================================

        # A) Castle & Village Windows Blinking / Pulsing
        for wx_pos, wy_pos, w_offset in windows:
            w_pulse = 0.5 + 0.5 * math.sin(angle * 3 + w_offset)
            if w_pulse < 0.25:
                # Dim window pixel
                dim_color = np.array([45, 25, 35], dtype=np.float32)
                frame_arr[wy_pos-1:wy_pos+2, wx_pos-1:wx_pos+2, :3] = dim_color
            elif w_pulse > 0.8:
                # Bright golden glow
                bright_color = np.array([255, 210, 100], dtype=np.float32)
                frame_arr[wy_pos-1:wy_pos+2, wx_pos-1:wx_pos+2, :3] = bright_color

        # B) Stone Lantern 1 Flame Flickering
        l1x1, l1y1, l1x2, l1y2 = lantern1_box
        l1_patch = frame_arr[l1y1:l1y2, l1x1:l1x2, :3]
        l1_flame = (l1_patch[:, :, 0] > 180) & (l1_patch[:, :, 1] > 120)
        flicker1 = 1.0 + 0.30 * math.sin(angle * 5) + 0.12 * math.cos(angle * 11)
        l1_patch[l1_flame] = np.clip(l1_patch[l1_flame] * flicker1, 0, 255)
        frame_arr[l1y1:l1y2, l1x1:l1x2, :3] = l1_patch

        # C) Stone Lantern 2 Flame Flickering
        l2x1, l2y1, l2x2, l2y2 = lantern2_box
        l2_patch = frame_arr[l2y1:l2y2, l2x1:l2x2, :3]
        l2_flame = (l2_patch[:, :, 0] > 180) & (l2_patch[:, :, 1] > 120)
        flicker2 = 1.0 + 0.30 * math.sin(angle * 5 + 1.5) + 0.12 * math.cos(angle * 13)
        l2_patch[l2_flame] = np.clip(l2_patch[l2_flame] * flicker2, 0, 255)
        frame_arr[l2y1:l2y2, l2x1:l2x2, :3] = l2_patch

        # D) Full Moon Soft Aura Glow Pulse
        mcx, mcy = 1100, 160
        m_r = 90
        moon_pulse = 1.0 + 0.15 * math.sin(angle * 2)
        moon_patch = frame_arr[mcy-m_r:mcy+m_r, mcx-m_r:mcx+m_r, :3]
        moon_bright = (moon_patch[:, :, 0] > 180) & (moon_patch[:, :, 1] > 180)
        moon_patch[moon_bright] = np.clip(moon_patch[moon_bright] * moon_pulse, 0, 255)
        frame_arr[mcy-m_r:mcy+m_r, mcx-m_r:mcx+m_r, :3] = moon_patch

        # Character animation removed as requested (character stays static)

        # =====================================================================
        # FEATURE 4: DRIFTING FALLING SAKURA PETALS OVERLAY
        # =====================================================================
        img_frame = Image.fromarray(np.uint8(frame_arr), mode="RGBA")
        draw = ImageDraw.Draw(img_frame)

        for p in petals:
            # Update petal position over time
            px = int((p["x"] + t * p["sx"] * w * 0.4 + 15.0 * math.sin(angle * p["freq"] + p["phase"])) % w)
            py = int((p["y"] + t * p["sy"] * h * 0.5) % h)
            
            p_size = p["size"]
            petal_color = (255, 175, 210, 230)
            
            # Draw petal ellipse / polygon
            draw.ellipse([px, py, px+p_size, py+p_size+1], fill=petal_color)

        # Append RGB frame
        frames.append(img_frame.convert("RGB"))

    print(f"Saving animated GIF to: {output_gif_path}")
    frames[0].save(
        output_gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True
    )
    print("Sakura Samurai GIF generation complete!")

if __name__ == "__main__":
    img_input = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_46_13 PM.png"
    gif_output = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\ChatGPT_Image_Aug_10_2026_09_46_13_PM.gif"
    generate_sakura_samurai_gif(img_input, gif_output, num_frames=36, fps=12)
