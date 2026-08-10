import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def generate_pixel_mart_gif(image_path, output_gif_path, num_frames=36, fps=12):
    print(f"Loading base image: {image_path}")
    base_img = Image.open(image_path).convert("RGBA")
    w, h = base_img.size
    print(f"Image dimensions: {w}x{h}")

    base_arr = np.array(base_img, dtype=np.float32)

    # -------------------------------------------------------------------------
    # BOUNDING BOXES & FEATURE DEFINITIONS
    # -------------------------------------------------------------------------
    # Cat box: X: 350..560, Y: 620..810
    cat_box = (350, 620, 560, 810)
    cat_head_box = (450, 615, 550, 715)
    cat_tail_box = (350, 700, 410, 790)

    # Main "PIXEL MART" neon sign: X: 470..950, Y: 130..240
    pm_box = (470, 130, 950, 240)

    # "OPEN" neon sign: X: 820..950, Y: 360..440
    open_box = (820, 360, 950, 440)

    # MENU BOARD lines: X: 1140..1480, Y: 200..600
    menu_box = (1140, 200, 1480, 600)
    menu_lines = [
        {"name": "COFFEE", "y1": 200, "y2": 290},
        {"name": "RAMEN",  "y1": 290, "y2": 390},
        {"name": "CODE",   "y1": 390, "y2": 490},
        {"name": "REPEAT", "y1": 490, "y2": 590},
    ]

    # Hanging lamps: X: 300..420, Y: 150..230
    lamps_box = (300, 150, 420, 230)

    # Vending Machine LED box: X: 880..1060, Y: 450..710
    vending_box = (880, 450, 1060, 710)

    # Reflection zone: Y: 680..1024, X: 0..1536
    refl_y_start = 680

    frames = []
    np.random.seed(42)

    for frame_idx in range(num_frames):
        t = frame_idx / float(num_frames) # 0.0 to 1.0
        angle = 2.0 * math.pi * t

        # Start from base image array
        frame_arr = base_arr.copy()

        # =====================================================================
        # FEATURE 1: LIGHT OF BOARD ANIMATION ("light of board animate")
        # =====================================================================

        # A) PIXEL MART Main Sign Pulse & Micro-Flicker
        pm_x1, pm_y1, pm_x2, pm_y2 = pm_box
        pm_patch = frame_arr[pm_y1:pm_y2, pm_x1:pm_x2, :3]
        # Bright yellow/orange letters mask
        pm_letters = (pm_patch[:, :, 0] > 160) & (pm_patch[:, :, 1] > 100)
        
        pm_pulse = 1.0 + 0.28 * math.sin(angle * 2)
        if frame_idx in [9, 27]:
            pm_pulse *= 0.70  # micro-flicker dim
        elif frame_idx in [10, 28]:
            pm_pulse *= 1.25  # micro-flicker boost

        pm_patch[pm_letters] = np.clip(pm_patch[pm_letters] * pm_pulse, 0, 255)
        frame_arr[pm_y1:pm_y2, pm_x1:pm_x2, :3] = pm_patch

        # B) OPEN Neon Sign Blink & Glow Pulse
        op_x1, op_y1, op_x2, op_y2 = open_box
        op_patch = frame_arr[op_y1:op_y2, op_x1:op_x2, :3]
        op_magenta = (op_patch[:, :, 0] > 150) & (op_patch[:, :, 2] > 120)
        op_pulse = 1.0 + 0.35 * math.sin(angle * 3 + 1.0)
        if frame_idx in [15, 33]:
            op_pulse *= 0.60
        op_patch[op_magenta] = np.clip(op_patch[op_magenta] * op_pulse, 0, 255)
        frame_arr[op_y1:op_y2, op_x1:op_x2, :3] = op_patch

        # C) MENU BOARD Line Highlight Cycle (COFFEE -> RAMEN -> CODE -> REPEAT)
        active_line_idx = int(t * 4) % 4
        mb_x1, mb_x2 = 1140, 1480
        for idx, line in enumerate(menu_lines):
            ly1, ly2 = line["y1"], line["y2"]
            line_patch = frame_arr[ly1:ly2, mb_x1:mb_x2, :3]
            bright_p = (line_patch[:, :, 0] > 110) | (line_patch[:, :, 1] > 110) | (line_patch[:, :, 2] > 110)
            
            if idx == active_line_idx:
                l_mult = 1.40 + 0.15 * math.sin(angle * 4)
            else:
                l_mult = 0.85 + 0.10 * math.sin(angle * 2)
            
            line_patch[bright_p] = np.clip(line_patch[bright_p] * l_mult, 0, 255)
            frame_arr[ly1:ly2, mb_x1:mb_x2, :3] = line_patch

        # D) Vending Machine RGB Pulse
        vx1, vy1, vx2, vy2 = vending_box
        vend_patch = frame_arr[vy1:vy2, vx1:vx2, :3]
        vend_lights = (vend_patch[:, :, 0] > 100) | (vend_patch[:, :, 1] > 100) | (vend_patch[:, :, 2] > 120)
        v_shift = 0.85 + 0.30 * math.sin(angle * 2 + 2.0)
        vend_patch[vend_lights] = np.clip(vend_patch[vend_lights] * v_shift, 0, 255)
        frame_arr[vy1:vy2, vx1:vx2, :3] = vend_patch

        # E) Hanging Lamps Warm Pulse
        lx1, ly1, lx2, ly2 = lamps_box
        lamp_patch = frame_arr[ly1:ly2, lx1:lx2, :3]
        lamp_bright = (lamp_patch[:, :, 0] > 180) & (lamp_patch[:, :, 1] > 140)
        lamp_pulse = 1.0 + 0.20 * math.sin(angle * 2.5)
        lamp_patch[lamp_bright] = np.clip(lamp_patch[lamp_bright] * lamp_pulse, 0, 255)
        frame_arr[ly1:ly2, lx1:lx2, :3] = lamp_patch

        # =====================================================================
        # FEATURE 2: CAT ANIMATION ("cat ko animate karo")
        # =====================================================================
        # A) Breathing Motion: 1-2 px subtle head & chest shift up/down
        breath_phase = math.sin(angle)
        breath_dy = -1 if breath_phase > 0.3 else (1 if breath_phase < -0.3 else 0)

        # Apply breathing displacement to cat head & upper chest
        hx1, hy1, hx2, hy2 = cat_head_box
        if breath_dy != 0:
            head_patch = base_arr[hy1:hy2, hx1:hx2, :3].copy()
            bg_wall = base_arr[hy1-1:hy1, hx1:hx2, :3]
            frame_arr[hy1:hy1+1, hx1:hx2, :3] = bg_wall
            frame_arr[hy1+breath_dy:hy2+breath_dy, hx1:hx2, :3] = head_patch

        # B) Tail Wagging / Wave effect
        tx1, ty1, tx2, ty2 = cat_tail_box
        tail_shift = int(2.0 * math.sin(angle * 2))
        if tail_shift != 0:
            tail_patch = base_arr[ty1:ty2, tx1:tx2, :3].copy()
            # horizontal shift
            if tail_shift > 0:
                frame_arr[ty1:ty2, tx1+tail_shift:tx2+tail_shift, :3] = tail_patch
            else:
                frame_arr[ty1:ty2, tx1+tail_shift:tx2+tail_shift, :3] = tail_patch

        # C) Eyes blinking (close eyes on frames 12..14)
        if frame_idx in [12, 13, 14]:
            # Cat eye region: X: 470..530, Y: 645..660
            eye_bg = np.array([140, 130, 160], dtype=np.float32)
            frame_arr[648:656, 475:490, :3] = eye_bg
            frame_arr[648:656, 510:525, :3] = eye_bg

        # Ground reflection is kept static as requested (reflection animation removed)

        # =====================================================================
        # PIL OVERLAY DRAWING (Floating Steam / Zzz / Purring effects)
        # =====================================================================
        img_frame = Image.fromarray(np.uint8(frame_arr), mode="RGBA")
        draw = ImageDraw.Draw(img_frame)

        # 1. Coffee Steam Rising from Menu Board Coffee Cup (X: 1195, Y: 220)
        steam_y_start = 220
        for s_i in range(3):
            s_progress = (t + s_i / 3.0) % 1.0
            sy = steam_y_start - int(s_progress * 25)
            sx = 1195 + int(4 * math.sin(s_progress * math.pi * 3 + s_i))
            alpha = int(210 * math.sin(s_progress * math.pi))
            if alpha > 15:
                draw.rectangle([sx, sy, sx+2, sy+3], fill=(240, 230, 255, alpha))

        # 2. Cat Purring / Heart / Zzz floating aura (X: 470..500, Y: 600)
        for z_i in range(2):
            z_p = (t + z_i * 0.5) % 1.0
            zy = 615 - int(z_p * 35)
            zx = 475 + int(12 * math.sin(z_p * math.pi * 2))
            z_alpha = int(220 * math.sin(z_p * math.pi))
            if z_alpha > 25:
                draw.text((zx, zy), "♪" if z_i == 0 else "z", fill=(255, 220, 180, z_alpha))

        # Append converted RGB frame
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
    print("GIF generation completed successfully!")

if __name__ == "__main__":
    img_input = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\ChatGPT Image Aug 10, 2026, 09_43_27 PM.png"
    gif_output = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\ChatGPT_Image_Aug_10_2026_09_43_27_PM.gif"
    generate_pixel_mart_gif(img_input, gif_output, num_frames=36, fps=12)
