from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np
import random


def add_folds(image, count=4, rng=None):
    """Add subtle crease shading to the manuscript page."""
    rng = rng or random.Random()
    base = image.convert("RGB")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = base.size

    for _ in range(count):
        x = rng.randint(60, max(60, width - 60))
        offset = rng.randint(-18, 18)

        # Dark crease edge and a lighter edge create shallow fold shading.
        draw.line(
            (x, 0, x + offset, height),
            fill=(70, 45, 20, 16),
            width=rng.randint(1, 3)
        )
        draw.line(
            (x + 3, 0, x + offset + 3, height),
            fill=(255, 240, 205, 22),
            width=1
        )

    return Image.alpha_composite(
        base.convert("RGBA"), overlay
    ).convert("RGB")


def add_waviness(image, amplitude=2, rng=None):
    """Apply subtle horizontal displacement without wrap-around seams."""
    rng = rng or random.Random()
    arr = np.asarray(image.convert("RGB"))
    height, width, _ = arr.shape
    result = np.empty_like(arr)
    phase = rng.uniform(0, 6.283)

    for y in range(height):
        shift = int(amplitude * np.sin(y / 55.0 + phase))
        result[y] = np.roll(arr[y], shift, axis=0)

        # Replicate edge pixels rather than wrapping the opposite edge.
        if shift > 0:
            result[y, :shift] = arr[y, 0]
        elif shift < 0:
            result[y, shift:] = arr[y, -1]

    return Image.fromarray(result)


def add_ink_fading(image, strength=0.08, rng=None):
    """Add sparse, soft fading patches without washing out the whole page."""
    rng = rng or random.Random()
    base = image.convert("RGB")
    overlay = Image.new("RGB", base.size, (218, 202, 170))
    mask = Image.new("L", base.size, 0)
    draw = ImageDraw.Draw(mask)
    width, height = base.size

    for _ in range(18):
        x = rng.randrange(width)
        y = rng.randrange(height)
        radius = rng.randint(8, 28)
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=rng.randint(8, 28)
        )

    mask = mask.filter(ImageFilter.GaussianBlur(10))
    scale = max(0.0, min(1.0, strength / 0.12))
    mask = mask.point(lambda pixel: int(pixel * scale))

    return Image.composite(overlay, base, mask)


def add_ink_smudges(image, count=18, rng=None):
    """Add small, low-opacity ink smudges."""
    rng = rng or random.Random()
    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = base.size

    for _ in range(count):
        x = rng.randrange(width)
        y = rng.randrange(height)
        radius_x = rng.randint(2, 7)
        radius_y = rng.randint(1, 4)

        draw.ellipse(
            (
                x - radius_x,
                y - radius_y,
                x + radius_x,
                y + radius_y
            ),
            fill=(55, 30, 15, rng.randint(5, 18))
        )

    overlay = overlay.filter(ImageFilter.GaussianBlur(1.5))

    return Image.alpha_composite(base, overlay).convert("RGB")


def add_ink_bleeding(image, radius=1):
    """
    Create slight ink spread around dark strokes.

    MinFilter takes the minimum (darker) value in a neighborhood, which
    gently expands dark strokes. The effect is blended only near detected
    ink pixels so most of the paper background remains unchanged.
    """
    base = image.convert("RGB")
    arr = np.asarray(base)

    luminance = arr.mean(axis=2)
    ink_mask = luminance < 125

    if not ink_mask.any():
        return base

    # Use a small odd filter size. Keep this subtle to avoid thick lettering.
    filter_size = 3 if radius <= 1 else 5
    dilated = base.filter(ImageFilter.MinFilter(filter_size))
    dilated_arr = np.asarray(dilated)

    near_ink = Image.fromarray(
        (ink_mask.astype(np.uint8) * 255)
    ).filter(ImageFilter.MaxFilter(5))

    mask = np.asarray(near_ink) > 0
    output = arr.copy()

    output[mask] = (
        0.75 * output[mask] + 0.25 * dilated_arr[mask]
    ).astype(np.uint8)

    return Image.fromarray(output)


def apply_distortions(image, seed=None):
    """Apply reproducible manuscript aging and surface distortions."""
    rng = random.Random(seed)

    image = add_folds(image, rng=rng)
    image = add_waviness(image, rng=rng)
    image = add_ink_fading(image, rng=rng)
    image = add_ink_smudges(image, rng=rng)
    image = add_ink_bleeding(image)

    contrast = ImageEnhance.Contrast(image)
    return contrast.enhance(rng.uniform(0.96, 1.04))
