import os
import math
import numpy as np
from PIL import Image, ImageDraw

def generate_cyberpunk_samurai_gif(image_path, output_gif_path, num_frames=36, fps=12):
    print(f"Loading image: {image_path}")
    base_img = Image.open(image_path).convert("RGBA")
    w, h = base_img.size
    print(f"Dimensions: {w}x{h}")

    base_arr = np.array(base_img, dtype=np.float32)

    # 1. Katana blade mask: X: 300..750, Y: 530..720
    # Cyan blade pixels
    blade_patch = base_arr[530:720, 300:750, :3]
    cyan_mask = (blade_patch[:, :, 1] > 180) & (blade_patch[:, :, 2] > 200)

    # 2. Visor eyes: X: 590..660, Y: 210..260
    visor_patch = base_arr[210:260, 590:660, :3]
    visor_mask = (visor_patch[:, :, 1] > 180) & (visor_patch[:, :, 2] > 200)

    # 3. Neon signs regions (top-left magenta/cyan signs, right side RAMEN/16-BIT signs)
    # Magenta signs
    mag_mask = (base_arr[:, :, 0] > 180) & (base_arr[:, :, 2] > 180) & (base_arr[:, :, 1] < 120)
    # Cyan signs
    cy_mask = (base_arr[:, :, 2] > 200) & (base_arr[:, :, 1] > 160) & (base_arr[:, :, 0] < 120) & (np.arange(h)[:, None] < 700)

    # Setup rain drops
    np.random.seed(42)
    raindrops = []
    for r_i in range(60):
        raindrops.append({
            "x": np.random.randint(0, w),
            "y": np.random.randint(0, h),
            "length": np.random.randint(12, 25),
            "speed": np.random.uniform(25, 40)
        })

    # Setup floating neon particles
    particles = []
    for p_i in range(25):
        particles.append({
            "x": np.random.randint(200, 900),
            "y": np.random.randint(500, 950),
            "speed_y": np.random.uniform(1.5, 3.5),
            "wobble": np.random.uniform(2.0, 5.0),
            "size": np.random.choice([2, 3])
        })

    frames = []

    for frame_idx in range(num_frames):
        t = frame_idx / float(num_frames)
        angle = 2.0 * math.pi * t

        frame_arr = base_arr.copy()

        # A) Katana Blade Energy Pulse & Spark Stream
        b_pulse = 1.0 + 0.35 * math.sin(angle * 3)
        if frame_idx in [6, 20]:
            b_pulse *= 1.3
        elif frame_idx in [7, 21]:
            b_pulse *= 0.8
        
        b_sub = frame_arr[530:720, 300:750, :3]
        b_sub[cyan_mask] = np.clip(b_sub[cyan_mask] * b_pulse, 0, 255)
        frame_arr[530:720, 300:750, :3] = b_sub

        # B) Visor Eye Glint
        v_pulse = 1.0 + 0.30 * math.sin(angle * 2)
        v_sub = frame_arr[210:260, 590:660, :3]
        v_sub[visor_mask] = np.clip(v_sub[visor_mask] * v_pulse, 0, 255)
        frame_arr[210:260, 590:660, :3] = v_sub

        # C) Neon City Signs Pulse & Micro-Flicker
        mag_pulse = 1.0 + 0.25 * math.sin(angle * 2)
        cy_pulse = 1.0 + 0.25 * math.sin(angle * 2.5 + 1.0)
        if frame_idx in [12, 30]:
            mag_pulse *= 0.75
        
        frame_arr[mag_mask, :3] = np.clip(frame_arr[mag_mask, :3] * mag_pulse, 0, 255)
        frame_arr[cy_mask, :3] = np.clip(frame_arr[cy_mask, :3] * cy_pulse, 0, 255)

        # Draw Overlay (Rain Streaks & Floating Neon Sparks)
        img_frame = Image.fromarray(np.uint8(frame_arr), mode="RGBA")
        draw = ImageDraw.Draw(img_frame)

        # Cyber Rain Streaks
        for rd in raindrops:
            rx1 = int((rd["x"] - t * rd["speed"] * 5) % w)
            ry1 = int((rd["y"] + t * rd["speed"] * 15) % h)
            rx2 = rx1 - int(rd["length"] * 0.3)
            ry2 = ry1 + rd["length"]
            draw.line([rx1, ry1, rx2, ry2], fill=(160, 230, 255, 140), width=1)

        # Floating Neon Sparks
        for p in particles:
            px = int((p["x"] + 8.0 * math.sin(angle * p["wobble"])) % w)
            py = int((p["y"] - t * p["speed_y"] * h * 0.4) % h)
            p_color = (0, 240, 255, 220) if (px % 2 == 0) else (255, 80, 220, 220)
            draw.ellipse([px, py, px+p["size"], py+p["size"]], fill=p_color)

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
    print("Cyberpunk Samurai GIF generation complete!")

if __name__ == "__main__":
    img_in = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\Cyberpunk_Samurai.png"
    gif_out = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\cyberpunk_samurai.gif"
    generate_cyberpunk_samurai_gif(img_in, gif_out, num_frames=36, fps=12)
