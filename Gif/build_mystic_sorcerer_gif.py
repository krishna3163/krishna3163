import os
import math
import numpy as np
from PIL import Image, ImageDraw

def generate_mystic_sorcerer_gif(image_path, output_gif_path, num_frames=36, fps=12):
    print(f"Loading image: {image_path}")
    base_img = Image.open(image_path).convert("RGBA")
    w, h = img_w, img_h = base_img.size
    print(f"Dimensions: {w}x{h}")

    base_arr = np.array(base_img, dtype=np.float32)

    # Magic orb center: X: 375, Y: 320, radius ~70
    orb_center = (375, 320)
    orb_box = (300, 240, 450, 400)

    # Staff tip: X: 640, Y: 330, radius ~35
    staff_box = (610, 300, 670, 360)

    # Crescent Moon center: X: 730, Y: 200, radius ~150
    moon_box = (580, 50, 880, 350)

    # Cosmic stars & swirling particles setup
    np.random.seed(77)
    magic_particles = []
    for p_i in range(40):
        magic_particles.append({
            "radius": np.random.uniform(25, 90),
            "speed": np.random.uniform(1.5, 3.5),
            "angle_offset": p_i * (2.0 * math.pi / 40.0),
            "size": np.random.choice([2, 3, 4]),
            "color_type": np.random.choice(["purple", "cyan", "gold"])
        })

    sky_stars = []
    for s_i in range(30):
        sky_stars.append({
            "x": np.random.randint(20, w-20),
            "y": np.random.randint(20, 350),
            "twinkle_speed": np.random.uniform(2.0, 5.0),
            "phase": s_i * 0.4
        })

    frames = []

    for frame_idx in range(num_frames):
        t = frame_idx / float(num_frames)
        angle = 2.0 * math.pi * t

        frame_arr = base_arr.copy()

        # A) Magic Orb Swirling Energy & Pulsing Glow
        orb_pulse = 1.0 + 0.35 * math.sin(angle * 2)
        if frame_idx in [8, 24]:
            orb_pulse *= 1.25
        
        ox1, oy1, ox2, oy2 = orb_box
        orb_patch = frame_arr[oy1:oy2, ox1:ox2, :3]
        orb_pixels = (orb_patch[:, :, 0] > 140) | (orb_patch[:, :, 2] > 160)
        orb_patch[orb_pixels] = np.clip(orb_patch[orb_pixels] * orb_pulse, 0, 255)
        frame_arr[oy1:oy2, ox1:ox2, :3] = orb_patch

        # B) Staff Crystal Arcane Pulse
        sx1, sy1, sx2, sy2 = staff_box
        staff_patch = frame_arr[sy1:sy2, sx1:sx2, :3]
        staff_pixels = (staff_patch[:, :, 0] > 160) & (staff_patch[:, :, 2] > 180)
        st_pulse = 1.0 + 0.30 * math.sin(angle * 3 + 1.0)
        staff_patch[staff_pixels] = np.clip(staff_patch[staff_pixels] * st_pulse, 0, 255)
        frame_arr[sy1:sy2, sx1:sx2, :3] = staff_patch

        # C) Crescent Moon Aura & Cosmic Nebula Shimmer
        mx1, my1, mx2, my2 = moon_box
        moon_patch = frame_arr[my1:my2, mx1:mx2, :3]
        moon_pixels = (moon_patch[:, :, 0] > 140) & (moon_patch[:, :, 2] > 160)
        m_pulse = 1.0 + 0.18 * math.sin(angle * 2)
        moon_patch[moon_pixels] = np.clip(moon_patch[moon_pixels] * m_pulse, 0, 255)
        frame_arr[my1:my2, mx1:mx2, :3] = moon_patch

        # D) Twinkling Sky Stars
        for st in sky_stars:
            tw = 0.5 + 0.5 * math.sin(angle * st["twinkle_speed"] + st["phase"])
            s_color = np.array([int(180 * tw + 75), int(160 * tw + 95), 255], dtype=np.float32)
            frame_arr[st["y"]:st["y"]+2, st["x"]:st["x"]+2, :3] = s_color

        # Draw Overlays (Swirling Magic Energy Particles around Orb)
        img_frame = Image.fromarray(np.uint8(frame_arr), mode="RGBA")
        draw = ImageDraw.Draw(img_frame)

        ocx, ocy = orb_center
        for mp in magic_particles:
            cur_angle = angle * mp["speed"] + mp["angle_offset"]
            px = int(ocx + mp["radius"] * math.cos(cur_angle))
            py = int(ocy + (mp["radius"] * 0.6) * math.sin(cur_angle))
            
            p_size = mp["size"]
            if mp["color_type"] == "purple":
                p_col = (230, 140, 255, 230)
            elif mp["color_type"] == "cyan":
                p_col = (120, 240, 255, 230)
            else:
                p_col = (255, 220, 150, 230)

            draw.ellipse([px, py, px+p_size, py+p_size], fill=p_col)

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
    print("Mystic Sorcerer GIF generation complete!")

if __name__ == "__main__":
    img_in = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\Mystic_Sorcerer.png"
    gif_out = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\mystic_sorcerer.gif"
    generate_mystic_sorcerer_gif(img_in, gif_out, num_frames=36, fps=12)
