import os
import math
import numpy as np
from PIL import Image, ImageDraw

def generate_lofi_gamer_gif(image_path, output_gif_path, num_frames=36, fps=12):
    print(f"Loading image: {image_path}")
    base_img = Image.open(image_path).convert("RGBA")
    w, h = base_img.size
    print(f"Dimensions: {w}x{h}")

    base_arr = np.array(base_img, dtype=np.float32)

    # Bounding boxes
    # Monitor screen: X: 640..840, Y: 430..630
    eq_x1, eq_y1, eq_x2, eq_y2 = 660, 480, 820, 560

    # Cat: X: 240..450, Y: 520..640
    cat_box = (240, 520, 450, 640)

    # Desk lamp shade: X: 460..550, Y: 360..470
    lamp_box = (460, 360, 550, 470)

    # Lava lamp: X: 780..840, Y: 160..320
    lava_box = (780, 160, 840, 320)

    # Fairy lights string across wall: Y: 10..400
    fairy_mask = (base_arr[:, :, 0] > 220) & (base_arr[:, :, 1] > 180) & (base_arr[:, :, 2] < 140) & (np.arange(h)[:, None] < 420) & (np.arange(w)[None, :] > 400)

    # Window rain setup
    np.random.seed(99)
    window_rain = []
    for r_i in range(45):
        window_rain.append({
            "x": np.random.randint(20, 390),
            "y": np.random.randint(50, 580),
            "length": np.random.randint(8, 20),
            "speed": np.random.uniform(8, 18)
        })

    frames = []

    for frame_idx in range(num_frames):
        t = frame_idx / float(num_frames)
        angle = 2.0 * math.pi * t

        frame_arr = base_arr.copy()

        # A) Equalizer Spectrum Bars on Monitor Screen
        # Draw dynamic equalizer screen area
        screen_bg = np.array([14, 20, 30], dtype=np.float32)
        frame_arr[eq_y1:eq_y2, eq_x1:eq_x2, :3] = screen_bg

        num_bars = 14
        bar_w = 8
        gap = 3
        max_h = eq_y2 - eq_y1 - 6

        for i in range(num_bars):
            bx1 = eq_x1 + i * (bar_w + gap) + 4
            bx2 = bx1 + bar_w
            if bx2 > eq_x2 - 4:
                break
            
            phase = i * 0.65
            h_r = 0.2 + 0.75 * (0.5 + 0.5 * math.sin(angle * 4 + phase))
            if (frame_idx % 5) in [0, 1]:
                h_r = min(1.0, h_r * 1.25)

            bar_h = int(h_r * max_h)
            by2 = eq_y2 - 2
            by1 = max(eq_y1 + 2, by2 - bar_h)

            for py in range(by1, by2 + 1):
                prog = (by2 - py) / float(max_h)
                r = int(240 * (1 - prog) + 40 * prog)
                g = int(80 * (1 - prog) + 240 * prog)
                b = int(100 * (1 - prog) + 220 * prog)
                frame_arr[py, bx1:bx2, :3] = [r, g, b]

        # B) Cat Breathing Motion (1-px shift up/down)
        cx1, cy1, cx2, cy2 = cat_box
        breath_phase = math.sin(angle)
        cat_dy = -1 if breath_phase > 0.3 else 0

        if cat_dy != 0:
            cat_patch = base_arr[cy1:cy2, cx1:cx2, :3].copy()
            bg_bed = base_arr[cy1-1:cy1, cx1:cx2, :3]
            frame_arr[cy1:cy1+1, cx1:cx2, :3] = bg_bed
            frame_arr[cy1+cat_dy:cy2+cat_dy, cx1:cx2, :3] = cat_patch

        # C) Desk Lamp & Lava Lamp Glow Pulse
        lamp_pulse = 1.0 + 0.18 * math.sin(angle * 2)
        lx1, ly1, lx2, ly2 = lamp_box
        lamp_patch = frame_arr[ly1:ly2, lx1:lx2, :3]
        lamp_pixels = (lamp_patch[:, :, 0] > 200) & (lamp_patch[:, :, 1] > 160)
        lamp_patch[lamp_pixels] = np.clip(lamp_patch[lamp_pixels] * lamp_pulse, 0, 255)
        frame_arr[ly1:ly2, lx1:lx2, :3] = lamp_patch

        # Lava lamp glow
        lava_pulse = 1.0 + 0.25 * math.sin(angle * 3 + 1.0)
        lax1, lay1, lax2, lay2 = lava_box
        lava_patch = frame_arr[lay1:lay2, lax1:lax2, :3]
        lava_pixels = (lava_patch[:, :, 0] > 200) & (lava_patch[:, :, 1] > 100)
        lava_patch[lava_pixels] = np.clip(lava_patch[lava_pixels] * lava_pulse, 0, 255)
        frame_arr[lay1:lay2, lax1:lax2, :3] = lava_patch

        # Fairy lights
        fairy_pulse = 1.0 + 0.20 * math.sin(angle * 2.5)
        frame_arr[fairy_mask, :3] = np.clip(frame_arr[fairy_mask, :3] * fairy_pulse, 0, 255)

        # Draw Overlays (Window Rain, Coffee Steam, Cat Zzz)
        img_frame = Image.fromarray(np.uint8(frame_arr), mode="RGBA")
        draw = ImageDraw.Draw(img_frame)

        # Window Raindrops
        for rd in window_rain:
            rx = rd["x"]
            ry = int((rd["y"] + t * rd["speed"] * 20) % 550) + 40
            draw.line([rx, ry, rx, ry + rd["length"]], fill=(180, 210, 245, 120), width=1)

        # Coffee Steam Rising from Mug (X: 840, Y: 670)
        steam_y = 660
        for s_i in range(3):
            s_p = (t + s_i / 3.0) % 1.0
            sy = steam_y - int(s_p * 30)
            sx = 842 + int(5 * math.sin(s_p * math.pi * 3 + s_i))
            s_alpha = int(200 * math.sin(s_p * math.pi))
            if s_alpha > 15:
                draw.rectangle([sx, sy, sx+2, sy+3], fill=(245, 240, 255, s_alpha))

        # Cat Purring Zzz floating from Cat (X: 310, Y: 500)
        for z_i in range(2):
            z_p = (t + z_i * 0.5) % 1.0
            zy = 500 - int(z_p * 35)
            zx = 310 + int(10 * math.sin(z_p * math.pi * 2))
            z_alpha = int(230 * math.sin(z_p * math.pi))
            if z_alpha > 25:
                draw.text((zx, zy), "z" if z_i == 0 else "Z", fill=(255, 210, 150, z_alpha))

        frames.append(img_frame.convert("RGB"))

    print(f"Saving GIF to {output_gif_path}...")
    frames[0].save(
        output_gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True
    )
    print("Lofi Gamer Room GIF generation complete!")

if __name__ == "__main__":
    img_in = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\Lofi_Gamer_Room.png"
    gif_out = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\lofi_gamer_cat.gif"
    generate_lofi_gamer_gif(img_in, gif_out, num_frames=36, fps=12)
