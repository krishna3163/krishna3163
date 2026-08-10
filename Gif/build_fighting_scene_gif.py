import os
import math
import numpy as np
from PIL import Image, ImageDraw

def generate_fighting_scene_gif(image_path, output_gif_path, num_frames=36, fps=12):
    print(f"Loading image: {image_path}")
    base_img = Image.open(image_path).convert("RGBA")
    w, h = base_img.size
    print(f"Image dimensions: {w}x{h}")

    base_arr = np.array(base_img, dtype=np.float32)

    # -------------------------------------------------------------------------
    # BOUNDING BOXES & FEATURE DEFINITIONS
    # -------------------------------------------------------------------------
    # Blade clash center: X: 440..600, Y: 360..540
    clash_box = (440, 360, 600, 540)
    clash_center = (510, 450)

    # Red Samurai (Left): X: 200..480, Y: 320..700
    red_samurai_box = (200, 320, 480, 700)
    red_cape_box = (200, 440, 360, 580)

    # Blue Samurai (Right): X: 520..800, Y: 380..720
    blue_samurai_box = (520, 380, 800, 720)
    blue_cape_box = (680, 460, 850, 580)

    # Lightning strike area: X: 100..380, Y: 30..350
    lightning_box = (100, 30, 380, 350)

    # Moon box: X: 380..620, Y: 50..290
    moon_box = (380, 50, 620, 290)

    # Bonfire box: X: 740..880, Y: 720..860
    bonfire_box = (740, 720, 880, 860)

    # Setup floating clash sparks particle system
    # 40 sparks radiating outwards from clash center (510, 450)
    np.random.seed(3163)
    sparks = []
    for s_i in range(45):
        angle_rad = np.random.uniform(0, 2.0 * math.pi)
        speed = np.random.uniform(2.5, 7.5)
        spark_type = np.random.choice(["gold", "cyan", "red", "white"])
        size = np.random.choice([2, 3, 4])
        sparks.append({
            "angle": angle_rad,
            "speed": speed,
            "type": spark_type,
            "size": size,
            "life_offset": s_i * 0.2
        })

    frames = []

    for frame_idx in range(num_frames):
        # t goes smoothly from 0.0 to 1.0
        # Smooth continuous loop angle: 2 * pi * t
        # Crucial for seamless loop: f(0.0) == f(1.0)!
        t = frame_idx / float(num_frames)
        angle = 2.0 * math.pi * t

        frame_arr = base_arr.copy()

        # =====================================================================
        # FEATURE 1: SWORD CLASH SPARKS & ENERGY EXPLOSION
        # =====================================================================
        # Periodic clash energy wave pulse (2 full cycles during 36 frames)
        clash_pulse = 1.0 + 0.40 * math.sin(angle * 2)
        
        # High impact flash on frames 9..11 and 27..29
        if frame_idx in [9, 10, 11]:
            clash_pulse *= 1.45
        elif frame_idx in [27, 28, 29]:
            clash_pulse *= 1.35

        cx1, cy1, cx2, cy2 = clash_box
        clash_patch = frame_arr[cy1:cy2, cx1:cx2, :3]
        bright_clash = (clash_patch[:, :, 0] > 180) | (clash_patch[:, :, 1] > 180) | (clash_patch[:, :, 2] > 180)
        clash_patch[bright_clash] = np.clip(clash_patch[bright_clash] * clash_pulse, 0, 255)
        frame_arr[cy1:cy2, cx1:cx2, :3] = clash_patch

        # =====================================================================
        # FEATURE 2: RED & BLUE SAMURAI COMBAT AURA & CAPE FLUTTER
        # =====================================================================
        # Red Samurai Aura Pulse
        rx1, ry1, rx2, ry2 = red_samurai_box
        red_patch = frame_arr[ry1:ry2, rx1:rx2, :3]
        red_aura = (red_patch[:, :, 0] > 180) & (red_patch[:, :, 1] < 120)
        red_pulse = 1.0 + 0.28 * math.sin(angle * 2 + 0.5)
        red_patch[red_aura] = np.clip(red_patch[red_aura] * red_pulse, 0, 255)
        frame_arr[ry1:ry2, rx1:rx2, :3] = red_patch

        # Blue Samurai Aura Pulse
        bx1, by1, bx2, by2 = blue_samurai_box
        blue_patch = frame_arr[by1:by2, bx1:bx2, :3]
        blue_aura = (blue_patch[:, :, 2] > 180) & (blue_patch[:, :, 1] > 140)
        blue_pulse = 1.0 + 0.28 * math.sin(angle * 2 + 2.0)
        blue_patch[blue_aura] = np.clip(blue_patch[blue_aura] * blue_pulse, 0, 255)
        frame_arr[by1:by2, bx1:bx2, :3] = blue_patch

        # Cape wind flutter wave displacement
        rcx1, rcy1, rcx2, rcy2 = red_cape_box
        cape_shift = int(2.0 * math.sin(angle * 3))
        if cape_shift != 0:
            cape_patch = base_arr[rcy1:rcy2, rcx1:rcx2, :3].copy()
            frame_arr[rcy1:rcy2, rcx1+cape_shift:rcx2+cape_shift, :3] = cape_patch

        # =====================================================================
        # FEATURE 3: SKY LIGHTNING FLASHES & MOON AURA
        # =====================================================================
        # Lightning strikes on frames 4..6 and 22..24
        lx1, ly1, lx2, ly2 = lightning_box
        if frame_idx in [4, 5, 6, 22, 23, 24]:
            light_patch = frame_arr[ly1:ly2, lx1:lx2, :3]
            light_pixels = (light_patch[:, :, 0] > 160) | (light_patch[:, :, 1] > 160)
            light_mult = 1.6 if frame_idx in [5, 23] else 1.3
            light_patch[light_pixels] = np.clip(light_patch[light_pixels] * light_mult, 0, 255)
            frame_arr[ly1:ly2, lx1:lx2, :3] = light_patch

        # Moon Aura Glow
        mx1, my1, mx2, my2 = moon_box
        moon_patch = frame_arr[my1:my2, mx1:mx2, :3]
        moon_pixels = (moon_patch[:, :, 0] > 180) & (moon_patch[:, :, 1] > 180)
        moon_pulse = 1.0 + 0.15 * math.sin(angle * 2)
        moon_patch[moon_pixels] = np.clip(moon_patch[moon_pixels] * moon_pulse, 0, 255)
        frame_arr[my1:my2, mx1:mx2, :3] = moon_patch

        # =====================================================================
        # FEATURE 4: BONFIRE FLAME FLICKERING BELOW
        # =====================================================================
        fx1, fy1, fx2, fy2 = bonfire_box
        fire_patch = frame_arr[fy1:fy2, fx1:fx2, :3]
        fire_pixels = (fire_patch[:, :, 0] > 180) & (fire_patch[:, :, 1] > 120)
        flicker = 1.0 + 0.35 * math.sin(angle * 6) + 0.15 * math.cos(angle * 14)
        fire_patch[fire_pixels] = np.clip(fire_patch[fire_pixels] * flicker, 0, 255)
        frame_arr[fy1:fy2, fx1:fx2, :3] = fire_patch

        # =====================================================================
        # DRAW OVERLAY (Radiating Blade Clash Sparks & Energy Slash Lines)
        # =====================================================================
        img_frame = Image.fromarray(np.uint8(frame_arr), mode="RGBA")
        draw = ImageDraw.Draw(img_frame)

        ccx, ccy = clash_center
        for s in sparks:
            # Distance from clash center loops smoothly with time t
            dist = ((t * 80.0 * s["speed"] + s["life_offset"] * 50.0) % 90.0)
            sx = int(ccx + dist * math.cos(s["angle"]))
            sy = int(ccy + dist * math.sin(s["angle"]))

            # Spark alpha fades out near edge of radius
            alpha = int(255 * (1.0 - dist / 90.0))
            if alpha > 20 and 0 <= sx < w and 0 <= sy < h:
                if s["type"] == "gold":
                    scol = (255, 220, 100, alpha)
                elif s["type"] == "cyan":
                    scol = (100, 230, 255, alpha)
                elif s["type"] == "red":
                    scol = (255, 90, 90, alpha)
                else:
                    scol = (255, 255, 240, alpha)

                sp_size = s["size"]
                draw.ellipse([sx, sy, sx+sp_size, sy+sp_size], fill=scol)

        # Dynamic Energy Slash Impact Lines on high clash frames
        if frame_idx in [9, 10, 11, 27, 28, 29]:
            slash_alpha = 220 if frame_idx in [10, 28] else 140
            draw.line([ccx-60, ccy-40, ccx+60, ccy+40], fill=(255, 255, 230, slash_alpha), width=3)
            draw.line([ccx-50, ccy+50, ccx+50, ccy-50], fill=(120, 240, 255, slash_alpha), width=2)

        # Append final RGB frame
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
    print("Seamless Loop Fighting Scene GIF generation complete!")

if __name__ == "__main__":
    img_in = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\png\Fighting_Scene.png"
    gif_out = r"c:\Users\Krishna Kumar\Desktop\Github\krishna3163\Gif\fighting_scene.gif"
    generate_fighting_scene_gif(img_in, gif_out, num_frames=36, fps=12)
