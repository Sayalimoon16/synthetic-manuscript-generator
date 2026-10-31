from PIL import Image, ImageDraw, ImageFont, features
import random


def load_font(font_path, font_size):
    """
    Load a TrueType/OpenType font with RAQM shaping.
    RAQM is important for correct Indic-script rendering.
    """
    if not features.check("raqm"):
        raise RuntimeError(
            "Pillow was built without RAQM support. "
            "Indic script shaping may be incorrect. "
            "Install a Pillow build with libraqm support."
        )

    try:
        return ImageFont.truetype(
            str(font_path),
            font_size,
            layout_engine=ImageFont.Layout.RAQM,
        )
    except OSError as exc:
        raise FileNotFoundError(
            f"Could not load font: {font_path}"
        ) from exc


def _text_bbox(draw, text, font, language=None):
    """Get a text bounding box, with a fallback for Pillow variations."""
    try:
        return draw.textbbox(
            (0, 0),
            text,
            font=font,
            language=language,
        )
    except (TypeError, ValueError):
        return draw.textbbox((0, 0), text, font=font)


def _text_width(draw, text, font, language=None):
    box = _text_bbox(draw, text, font, language)
    return max(0, box[2] - box[0])


def wrap_text(text, font, max_width, draw, language=None):
    """
    Wrap paragraphs without intentionally dropping characters.
    Long words/tokens are split only when they exceed the available width.
    """
    if max_width <= 0:
        raise ValueError("max_width must be greater than zero")

    lines = []

    for paragraph in str(text).splitlines():
        if not paragraph.strip():
            lines.append("")
            continue

        words = paragraph.split()
        current = ""

        for word in words:
            candidate = f"{current} {word}".strip()

            if _text_width(draw, candidate, font, language) <= max_width:
                current = candidate
                continue

            if current:
                lines.append(current)
                current = ""

            # Handle a single token wider than the available line width.
            piece = ""

            for char in word:
                candidate_piece = piece + char

                if (
                    piece
                    and _text_width(
                        draw, candidate_piece, font, language
                    ) > max_width
                ):
                    lines.append(piece)
                    piece = char
                else:
                    piece = candidate_piece

            current = piece

        if current:
            lines.append(current)

    return lines


def render_text(
    image,
    text,
    font_path,
    font_size=42,
    margin=110,
    ink_color=(60, 35, 22),
    line_spacing=22,
    language=None,
    rng=None,
):
    """
    Render text directly onto an image.

    Returns:
        image, rendered_lines

    This function is retained for compatibility with the earlier
    generate.py. The newer layout.py can use load_font() and wrap_text().
    """
    rng = rng or random.Random()

    if image.mode != "RGB":
        image = image.convert("RGB")

    draw = ImageDraw.Draw(image)
    width, height = image.size

    if margin < 0 or margin * 2 >= width:
        raise ValueError(
            "margin must be non-negative and less than half the image width"
        )

    font = load_font(font_path, font_size)
    max_width = width - 2 * margin

    lines = wrap_text(
        text=text,
        font=font,
        max_width=max_width,
        draw=draw,
        language=language,
    )

    y = margin
    rendered_lines = []

    for line in lines:
        if not line:
            y += line_spacing
            continue

        bbox = _text_bbox(draw, line, font, language)
        line_height = max(1, bbox[3] - bbox[1])

        if y + line_height > height - margin:
            break

        # Small baseline and position changes imitate hand-set writing.
        x = margin + rng.randint(-2, 3)
        baseline_y = y - bbox[1]

        actual_box = draw.textbbox(
            (x, baseline_y),
            line,
            font=font,
            language=language,
        )

        if actual_box[0] < 0:
            x += -actual_box[0]

        if actual_box[2] > width:
            x -= actual_box[2] - width

        # Slight ink variation, kept subtle for legibility.
        variation = rng.randint(-5, 5)
        color = tuple(
            max(0, min(255, channel + variation))
            for channel in ink_color
        )

        draw.text(
            (x, baseline_y),
            line,
            font=font,
            fill=color,
            language=language,
        )

        rendered_lines.append(line)
        y += line_height + rng.randint(
            max(1, line_spacing - 3),
            line_spacing + 4,
        )

    return image, rendered_lines
