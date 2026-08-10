import os
import math
import numpy as np
from PIL import Image, ImageDraw

def generate_rooftop_gif(image_path, output_gif_path, num_frames=30, fps=12):
    print(f"Loading image: {image_path}")
    base_img = Image.open(image_path).convert("RGBA")
    w, h = base_img.size
    print(f"Image size: {w}x{h}")
    
    base_arr = np.array(base_img, dtype=np.float32)
    frames = []

    # 1. Neon sign board box: X: 850..980, Y: 120..530
    neon_box = (850, 120, 980, 530)

    # 2. Lantern flame box: X: 755..800, Y: 460..540
    lantern_box = (755, 460, 800, 540)

    # 3. Sun box: X: 360..430, Y: 350..410
    sun_center = (396, 378)


    # 5. Character Head & Body: X: 420..610, Y: 280..630
    char_box = (420, 280, 610, 540)

    # 6. Coffee mug steam position: X: 745, Y: 605

    # 7. City windows positions (find bright orange/yellow window pixels in buildings)
    # Buildings area: Y: 420..580, X: 0..850
    np.random.seed(123)
    bldg_area = base_arr[420:580, 0:850]
    win_mask = (bldg_area[:, :, 0] > 180) & (bldg_area[:, :, 1] > 120) & (bldg_area[:, :, 2] < 100)
    wy, wx = np.where(win_mask)
    # Pick 25 distinct window pixels
    indices = np.random.choice(len(wx), min(25, len(wx)), replace=False)
    windows = [(0 + wx[idx], 420 + wy[idx], i) for i, idx in enumerate(indices)]

    # 8. Night Sky Stars
    stars = [
        (75, 80, 0),
        (135, 45, 1),
        (300, 70, 2),
        (410, 110, 3),
        (520, 50, 4),
        (650, 90, 5),
        (780, 60, 6),
        (880, 100, 7),
        (220, 140, 8),
        (940, 40, 9),
    ]

    for frame_idx in range(num_frames):
        t = frame_idx / float(num_frames) # 0.0 to 1.0
        angle_rad = 2 * math.pi * t
        
        # Copy base array for frame editing
        frame_arr = base_arr.copy()

        # -------------------------------------------------------------
        # FEATURE 1: Japanese Neon Sign Board Glow & Flicker
        # -------------------------------------------------------------
        nx1, ny1, nx2, ny2 = neon_box
        neon_patch = frame_arr[ny1:ny2, nx1:nx2, :3]
        # Bright neon orange/red pixels
        neon_pixels = (neon_patch[:, :, 0] > 170) & (neon_patch[:, :, 1] > 70)
        pulse_neon = 1.0 + 0.20 * math.sin(angle_rad * 2)
        # Micro flicker on 2 frames
        if frame_idx in [6, 21]:
            pulse_neon *= 0.75
        elif frame_idx in [7, 22]:
            pulse_neon *= 1.25
            
        neon_patch[neon_pixels] = np.clip(neon_patch[neon_pixels] * pulse_neon, 0, 255)
        frame_arr[ny1:ny2, nx1:nx2, :3] = neon_patch

        # -------------------------------------------------------------
        # FEATURE 2: Lantern Flame & Light Pulse
        # -------------------------------------------------------------
        lx1, ly1, lx2, ly2 = lantern_box
        lantern_patch = frame_arr[ly1:ly2, lx1:lx2, :3]
        flame_pixels = (lantern_patch[:, :, 0] > 180) & (lantern_patch[:, :, 1] > 120)
        # Randomized flame flicker
        flicker_val = 1.0 + 0.25 * math.sin(angle_rad * 5) + 0.10 * math.cos(angle_rad * 11)
        lantern_patch[flame_pixels] = np.clip(lantern_patch[flame_pixels] * flicker_val, 0, 255)
        frame_arr[ly1:ly2, lx1:lx2, :3] = lantern_patch

        # -------------------------------------------------------------
        # FEATURE 3: Sun Glow & Rays Horizon Pulse
        # -------------------------------------------------------------
        scx, scy = sun_center
        # Create subtle radial glow around sun
        sun_r = 45
        y_indices, x_indices = np.ogrid[scy-sun_r:scy+sun_r, scx-sun_r:scx+sun_r]
        dist_from_center = np.sqrt((x_indices - scx)**2 + (y_indices - scy)**2)
        glow_mask = dist_from_center <= sun_r
        glow_factor = (1.0 - dist_from_center / float(sun_r)) * glow_mask
        glow_pulse = 0.15 * math.sin(angle_rad * 2) + 0.15
        
        sun_region = frame_arr[scy-sun_r:scy+sun_r, scx-sun_r:scx+sun_r, :3]
        for c in range(2): # Red and Green channels
            sun_region[:, :, c] += glow_factor * glow_pulse * 80
        frame_arr[scy-sun_r:scy+sun_r, scx-sun_r:scx+sun_r, :3] = np.clip(sun_region, 0, 255)

        # -------------------------------------------------------------
        # FEATURE 4: City Windows Blinking
        # -------------------------------------------------------------
        for wx_pos, wy_pos, w_offset in windows:
            w_blink = 0.5 + 0.5 * math.sin(angle_rad * 3 + w_offset)
            if w_blink < 0.3:
                # Dim window
                frame_arr[wy_pos:wy_pos+2, wx_pos:wx_pos+2, :3] = [35, 25, 40]

        # -------------------------------------------------------------
        # FEATURE 6: Twinkling Night Stars & Moon Aura
        # -------------------------------------------------------------
        for sx, sy, offset in stars:
            twinkle = 0.5 + 0.5 * math.sin(angle_rad * 3.5 + offset)
            star_color = [int(180 * twinkle + 75), int(190 * twinkle + 65), 255]
            frame_arr[sy:sy+2, sx:sx+2, :3] = star_color

        # -------------------------------------------------------------
        # FEATURE 7: Character Breathing & Hair Sway
        # -------------------------------------------------------------
        cx1, cy1, cx2, cy2 = char_box
        # Gentle 1-pixel breathing shift up/down
        breath_cycle = frame_idx % 10
        char_dy = -1 if breath_cycle in [0, 1, 2, 3] else 0

        if char_dy != 0:
            char_patch = base_arr[cy1:cy2, cx1:cx2, :3].copy()
            # Shift character upper body up 1 pixel
            sky_bg = base_arr[cy1-1, cx1:cx2, :3]
            frame_arr[cy2-1:cy2, cx1:cx2, :3] = base_arr[cy2, cx1:cx2, :3]
            frame_arr[cy1+char_dy:cy2+char_dy, cx1:cx2, :3] = char_patch

        # Convert array back to PIL image for drawing overlay elements (Coffee Steam)
        img_frame = Image.fromarray(np.uint8(frame_arr), mode="RGBA")
        draw = ImageDraw.Draw(img_frame)

        # -------------------------------------------------------------
        # FEATURE 8: Rising Steam from Coffee Cup on Balcony Table
        # -------------------------------------------------------------
        # Mug position: X: 745, Y: 605
        steam_y_start = 605
        for s_idx in range(3):
            s_t = (t + s_idx / 3.0) % 1.0
            sy = steam_y_start - int(s_t * 30)
            sx = 745 + int(5 * math.sin(s_t * math.pi * 3 + s_idx))
            alpha = int(200 * math.sin(s_t * math.pi))
            if alpha > 10:
                draw.rectangle([sx, sy, sx+1, sy+2], fill=(255, 220, 200, alpha))

        # Append final frame
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
    print("Rooftop GIF generation complete!")

if __name__ == "__main__":
    img_in = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\rooftop_sunset.jpg"
    gif_out = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\rooftop_sunset_animated.gif"
    generate_rooftop_gif(img_in, gif_out, num_frames=30, fps=12)
