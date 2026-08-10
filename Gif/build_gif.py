import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def generate_pixel_gif(image_path, output_gif_path, num_frames=30, fps=12):
    print(f"Loading image: {image_path}")
    base_img = Image.open(image_path).convert("RGBA")
    w, h = base_img.size
    print(f"Image size: {w}x{h}")
    
    base_arr = np.array(base_img, dtype=np.float32)
    frames = []

    # Let's pre-calculate mask coordinates for efficiency

    # 1. KEEP CODING sign bounds (X: 520..700, Y: 60..220)
    kc_box = (520, 60, 700, 220)

    # 2. EAT SLEEP CODE REPEAT Y-ranges inside X: 1180..1430, Y: 30..250
    eat_lines = [
        {"name": "EAT", "y1": 35, "y2": 85, "color": (255, 200, 50)},
        {"name": "SLEEP", "y1": 85, "y2": 135, "color": (50, 200, 255)},
        {"name": "CODE", "y1": 135, "y2": 185, "color": (220, 80, 255)},
        {"name": "REPEAT", "y1": 185, "y2": 240, "color": (80, 255, 120)}
    ]
    eat_x = (1180, 1430)

    # 3. Monitor 2 Equalizer region (X: 1065..1228, Y: 572..609)
    eq_x1, eq_y1, eq_x2, eq_y2 = 1065, 572, 1228, 609
    
    # 4. Clock Colon region (X: 1150..1156, Y: 648..672)
    clock_colon_box = (1150, 648, 1156, 672)
    # Background color near clock colon to replace when dark
    bg_clock_color = base_arr[660, 1145, :3].copy()

    # 5. PC Fan / RGB area (X: 1060..1150, Y: 800..870)
    pc_fan_center = (1100, 835)

    # 6. Coffee mug steam start (X: 975..995, Y: 615)
    
    # 7. Sleeping Cat Zzz start (X: 200, Y: 600)

    # Star twinkle positions (sky in window: X: 30..320, Y: 50..250)
    np.random.seed(42)
    stars = [
        (80, 120, 0),
        (140, 70, 1),
        (220, 180, 2),
        (290, 90, 3),
        (110, 210, 4),
        (260, 150, 5),
    ]

    for frame_idx in range(num_frames):
        t = frame_idx / float(num_frames) # 0.0 to 1.0
        angle_rad = 2 * math.pi * t
        
        # Copy base array for frame editing
        frame_arr = base_arr.copy()

        # -------------------------------------------------------------
        # FEATURE A: Keep Coding Neon Pulse
        # -------------------------------------------------------------
        kc_x1, kc_y1, kc_x2, kc_y2 = kc_box
        kc_patch = frame_arr[kc_y1:kc_y2, kc_x1:kc_x2, :3]
        # Bright neon magenta/purple pixels filter
        magenta_mask = (kc_patch[:, :, 0] > 140) & (kc_patch[:, :, 2] > 140)
        pulse_val = 1.0 + 0.25 * math.sin(angle_rad * 2)
        # Random occasional micro flicker on 2 frames
        if frame_idx in [7, 21]:
            pulse_val *= 0.8
        elif frame_idx in [8, 22]:
            pulse_val *= 1.2
            
        kc_patch[magenta_mask] = np.clip(kc_patch[magenta_mask] * pulse_val, 0, 255)
        frame_arr[kc_y1:kc_y2, kc_x1:kc_x2, :3] = kc_patch

        # -------------------------------------------------------------
        # FEATURE B: EAT SLEEP CODE REPEAT Highlight Cycle
        # -------------------------------------------------------------
        active_line_idx = int(t * 4) % 4
        for idx, line in enumerate(eat_lines):
            ly1, ly2 = line["y1"], line["y2"]
            lx1, lx2 = eat_x
            line_patch = frame_arr[ly1:ly2, lx1:lx2, :3]
            bright_pixels = (line_patch[:, :, 0] > 100) | (line_patch[:, :, 1] > 100) | (line_patch[:, :, 2] > 100)
            
            if idx == active_line_idx:
                mult = 1.35 + 0.15 * math.sin(angle_rad * 4)
            else:
                mult = 0.85
            line_patch[bright_pixels] = np.clip(line_patch[bright_pixels] * mult, 0, 255)
            frame_arr[ly1:ly2, lx1:lx2, :3] = line_patch

        # -------------------------------------------------------------
        # FEATURE C: Equalizer Bars on Monitor 2
        # -------------------------------------------------------------
        # Clear existing equalizer area with dark screen background color
        screen_bg = np.array([12, 10, 24], dtype=np.float32)
        frame_arr[eq_y1:eq_y2, eq_x1:eq_x2, :3] = screen_bg

        num_bars = 16
        bar_width = 7
        gap = 3
        max_bar_h = eq_y2 - eq_y1 - 2

        for i in range(num_bars):
            bx1 = eq_x1 + i * (bar_width + gap) + 4
            bx2 = bx1 + bar_width
            if bx2 > eq_x2:
                break
            
            # Dynamic height curve per bar
            phase = i * 0.7
            h_ratio = 0.25 + 0.7 * (0.5 + 0.5 * math.sin(angle_rad * 3 + phase))
            # Add beat pulse on certain frames
            if (frame_idx % 6) in [0, 1]:
                h_ratio = min(1.0, h_ratio * 1.3)
                
            bar_h = int(h_ratio * max_bar_h)
            by2 = eq_y2 - 1
            by1 = max(eq_y1 + 1, by2 - bar_h)

            # Gradient color from magenta (bottom) to cyan/green (top)
            for py in range(by1, by2 + 1):
                prog = (by2 - py) / float(max_bar_h)
                r = int(220 * (1 - prog) + 30 * prog)
                g = int(50 * (1 - prog) + 240 * prog)
                b = int(240 * (1 - prog) + 220 * prog)
                frame_arr[py, bx1:bx2, :3] = [r, g, b]

        # -------------------------------------------------------------
        # FEATURE D: Digital Clock Colon Blinking
        # -------------------------------------------------------------
        cx1, cy1, cx2, cy2 = clock_colon_box
        if frame_idx >= (num_frames // 2):
            # Colon off (fill with clock screen dark purple background)
            clock_bg = np.array([20, 15, 35], dtype=np.float32)
            frame_arr[cy1:cy2, cx1:cx2, :3] = clock_bg

        # -------------------------------------------------------------
        # FEATURE E: PC Case RGB Light & Fan Rotation
        # -------------------------------------------------------------
        # RGB strip glow (PC case window right side: X: 1040..1200, Y: 780..950)
        pc_win = frame_arr[780:950, 1040:1200, :3]
        purple_parts = (pc_win[:, :, 0] > 100) & (pc_win[:, :, 2] > 120)
        # Shift color hue smoothly
        hue_shift = 0.5 + 0.5 * math.sin(angle_rad)
        r_mult = 0.8 + 0.4 * hue_shift
        b_mult = 1.2 - 0.4 * hue_shift
        pc_win[purple_parts, 0] = np.clip(pc_win[purple_parts, 0] * r_mult, 0, 255)
        pc_win[purple_parts, 2] = np.clip(pc_win[purple_parts, 2] * b_mult, 0, 255)
        frame_arr[780:950, 1040:1200, :3] = pc_win

        # -------------------------------------------------------------
        # FEATURE F: Window Stars Twinkling
        # -------------------------------------------------------------
        for sx, sy, offset in stars:
            twinkle = 0.5 + 0.5 * math.sin(angle_rad * 4 + offset)
            star_color = [int(200 * twinkle + 55), int(220 * twinkle + 35), int(255)]
            frame_arr[sy:sy+2, sx:sx+2, :3] = star_color

        # -------------------------------------------------------------
        # FEATURE I: Head Bobbing (Head & Headphones)
        # -------------------------------------------------------------
        # Head box: X: 470..710, Y: 370..560
        head_x1, head_y1, head_x2, head_y2 = 470, 370, 710, 560
        bob_cycle = frame_idx % 8
        if bob_cycle in [0, 1]:
            head_dy = 1
        elif bob_cycle in [2, 3]:
            head_dy = 2
        elif bob_cycle in [4, 5]:
            head_dy = 1
        else:
            head_dy = 0

        if head_dy > 0:
            head_patch = base_arr[head_y1:head_y2, head_x1:head_x2, :3].copy()
            wall_bg = base_arr[head_y1-1, head_x1:head_x2, :3]
            frame_arr[head_y1:head_y1+head_dy, head_x1:head_x2, :3] = wall_bg
            frame_arr[head_y1+head_dy:head_y2+head_dy, head_x1:head_x2, :3] = head_patch

        # -------------------------------------------------------------
        # FEATURE J: Typing Hands Movement
        # -------------------------------------------------------------
        # Left hand: X: 745..775, Y: 670..705
        # Right hand: X: 776..810, Y: 670..705
        hand_y1, hand_y2 = 670, 705
        lh_x1, lh_x2 = 745, 775
        rh_x1, rh_x2 = 776, 810

        typing_state = frame_idx % 4
        lh_dy = -1 if typing_state in [0, 1] else 0
        rh_dy = -1 if typing_state in [2, 3] else 0

        if lh_dy != 0:
            lh_patch = base_arr[hand_y1:hand_y2, lh_x1:lh_x2, :3].copy()
            kb_bg = base_arr[hand_y2, lh_x1:lh_x2, :3]
            frame_arr[hand_y2-1:hand_y2, lh_x1:lh_x2, :3] = kb_bg
            frame_arr[hand_y1+lh_dy:hand_y2+lh_dy, lh_x1:lh_x2, :3] = lh_patch

        if rh_dy != 0:
            rh_patch = base_arr[hand_y1:hand_y2, rh_x1:rh_x2, :3].copy()
            kb_bg = base_arr[hand_y2, rh_x1:rh_x2, :3]
            frame_arr[hand_y2-1:hand_y2, rh_x1:rh_x2, :3] = kb_bg
            frame_arr[hand_y1+rh_dy:hand_y2+rh_dy, rh_x1:rh_x2, :3] = rh_patch

        # Convert array back to PIL image for drawing overlay elements (Steam, Zzz)
        img_frame = Image.fromarray(np.uint8(frame_arr), mode="RGBA")
        draw = ImageDraw.Draw(img_frame)

        # -------------------------------------------------------------
        # FEATURE G: Rising Coffee Steam
        # -------------------------------------------------------------
        steam_y_start = 625
        for s_idx in range(3):
            s_t = (t + s_idx / 3.0) % 1.0
            sy = steam_y_start - int(s_t * 35)
            sx = 985 + int(6 * math.sin(s_t * math.pi * 3 + s_idx))
            alpha = int(220 * math.sin(s_t * math.pi))
            if alpha > 10:
                draw.rectangle([sx, sy, sx+1, sy+2], fill=(230, 230, 255, alpha))

        # -------------------------------------------------------------
        # FEATURE H: Sleeping Cat "Zzz"
        # -------------------------------------------------------------
        for z_i in range(2):
            z_progress = (t + z_i * 0.5) % 1.0
            zy = 590 - int(z_progress * 40)
            zx = 210 + int(z_progress * 25) + int(4 * math.sin(z_progress * math.pi * 2))
            z_alpha = int(255 * math.sin(z_progress * math.pi))
            z_size = "z" if z_i == 0 else "Z"
            if z_alpha > 20:
                draw.text((zx, zy), z_size, fill=(180, 220, 255, z_alpha))

        # Append final frame
        frames.append(img_frame.convert("RGB"))

    print(f"Saving animated GIF to: {output_gif_path}")
    # Optimize palette for pixel art GIF
    frames[0].save(
        output_gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True
    )
    print("GIF generation complete!")

if __name__ == "__main__":
    img_in = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\ChatGPT Image Aug 10, 2026, 09_35_55 PM.png"
    gif_out = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\coder_workspace_animated.gif"
    generate_pixel_gif(img_in, gif_out, num_frames=30, fps=12)
