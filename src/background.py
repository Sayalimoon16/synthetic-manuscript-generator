from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import random


def generate_background(width=1600, height=1000, material="paper", seed=None):
    """Generate aged handmade-paper or palm-leaf-like background texture."""
    if material not in {"paper", "palm_leaf"}:
        raise ValueError("material must be 'paper' or 'palm_leaf'")

    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    base = np.array([220, 195, 145] if material == "paper" else [175, 155, 100], dtype=np.float32)

    # Low-frequency illumination variation plus fine grain.
    coarse_h = max(2, height // 45)
    coarse_w = max(2, width // 45)
    coarse = np_rng.normal(0, 5, (coarse_h, coarse_w)).astype(np.float32)
    coarse_img = Image.fromarray(np.uint8(np.clip(coarse + 128, 0, 255))).resize(
        (width, height), Image.Resampling.BICUBIC
    )
    coarse_noise = np.asarray(coarse_img, dtype=np.float32) - 128
    fine_noise = np_rng.normal(0, 5 if material == "paper" else 3, (height, width))
    noise = (coarse_noise * 0.8 + fine_noise)[..., None]
    arr = np.clip(base + noise, 0, 255).astype(np.uint8)

    image = Image.fromarray(arr, "RGB")
    draw = ImageDraw.Draw(image, "RGBA")

    stain_count = 260 if material == "paper" else 140
    for _ in range(stain_count):
        x, y = rng.randrange(width), rng.randrange(height)
        radius = rng.randint(2, 24 if material == "paper" else 15)
        alpha = rng.randint(8, 35)
        color = (95, 55, 25, alpha) if material == "paper" else (75, 55, 25, alpha)
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)

    if material == "paper":
        for _ in range(650):
            x, y = rng.randrange(width), rng.randrange(height)
            length = rng.randint(4, 32)
            draw.line((x, y, x + length, y + rng.randint(-3, 3)),
                      fill=(100, 75, 45, rng.randint(12, 32)), width=1)
        draw.rectangle((5, 5, width-6, height-6), outline=(75, 45, 20, 75), width=10)
    else:
        for y in range(12, height, 18):
            draw.line((0, y, width, y + rng.randint(-2, 2)),
                      fill=(85, 65, 25, 45), width=1)
        for _ in range(130):
            x, y = rng.randrange(width), rng.randrange(height)
            length = rng.randint(8, 45)
            draw.line((x, y, x + length, y), fill=(70, 50, 20, 45), width=1)

    return image.filter(ImageFilter.GaussianBlur(0.35))
