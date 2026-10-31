from PIL import Image, ImageDraw
import hashlib
import random

from src.text_renderer import load_font, wrap_text


def _text_bbox(draw, text, font, language=None):
    """Get a text bounding box with a fallback for older Pillow builds."""
    try:
        return draw.textbbox((0, 0), text, font=font, language=language)
    except (TypeError, ValueError):
        return draw.textbbox((0, 0), text, font=font)


def _text_width(draw, text, font, language=None):
    bbox = _text_bbox(draw, text, font, language)
    return max(0, bbox[2] - bbox[0])


def _wrap(draw, text, font, max_width, language=None):
    return wrap_text(text, font, max_width, draw, language)


def _draw_highlighted_line(
    draw, x, y, line, font, highlight_text="", language=None, rng=None
):
    """Draw one line and highlight the first matching occurrence."""
    rng = rng or random.Random()

    ink = (
        rng.randint(48, 68),
        rng.randint(27, 41),
        rng.randint(14, 25),
        rng.randint(218, 248),
    )

    if not highlight_text or highlight_text not in line:
        draw.text((x, y), line, font=font, fill=ink, language=language)
        return

    before, matched, after = line.partition(highlight_text)
    before_width = _text_width(draw, before, font, language)
    matched_width = _text_width(draw, matched, font, language)

    bbox = _text_bbox(draw, matched, font, language)
    highlight_box = (
        x + before_width + bbox[0] - 4,
        y + bbox[1] - 3,
        x + before_width + bbox[2] + 4,
        y + bbox[3] + 3,
    )

    draw.rounded_rectangle(
        highlight_box,
        radius=3,
        fill=(205, 151, 65, 105),
    )

    draw.text((x, y), before, font=font, fill=ink, language=language)
    draw.text(
        (x + before_width, y),
        matched,
        font=font,
        fill=(105, 54, 20, 255),
        language=language,
    )
    draw.text(
        (x + before_width + matched_width, y),
        after,
        font=font,
        fill=ink,
        language=language,
    )


def _render_rotated_line(
    image,
    x,
    y,
    line,
    font,
    highlight_text,
    language,
    rng,
    max_angle=1.0,
):
    """
    Render a complete shaped text line on its own transparent layer,
    then apply a very small rotation. Indic characters are never rotated
    individually, so vowel signs and conjuncts stay together.
    """
    measure = ImageDraw.Draw(image)
    bbox = _text_bbox(measure, line, font, language)

    text_width = max(1, bbox[2] - bbox[0])
    text_height = max(1, bbox[3] - bbox[1])
    padding = 14

    layer = Image.new(
        "RGBA",
        (text_width + padding * 2, text_height + padding * 2),
        (0, 0, 0, 0),
    )
    layer_draw = ImageDraw.Draw(layer, "RGBA")

    draw_x = padding - bbox[0]
    draw_y = padding - bbox[1]

    _draw_highlighted_line(
        draw=layer_draw,
        x=draw_x,
        y=draw_y,
        line=line,
        font=font,
        highlight_text=highlight_text,
        language=language,
        rng=rng,
    )

    angle = rng.uniform(-max_angle, max_angle)
    rotated = layer.rotate(
        angle,
        resample=Image.Resampling.BICUBIC,
        expand=True,
    )

    # Keep the rotated line centered near its original position.
    paste_x = int(x - (rotated.width - layer.width) / 2)
    paste_y = int(y - (rotated.height - layer.height) / 2)

    image.alpha_composite(rotated, (paste_x, paste_y))
    return image


def create_manuscript_layout(
    image,
    main_text,
    font_path,
    side_text="",
    heading="",
    highlight_text="",
    language=None,
):
    """
    Render a manuscript page with heading, main text and marginal notes.

    Adds subtle baseline/position irregularity, line-level rotation,
    variable spacing and ink variation while preserving Indic shaping.

    Returns:
        (RGB image, visible_lines)
    """
    if image is None:
        raise ValueError("image cannot be None")

    if not isinstance(main_text, str) or not main_text.strip():
        raise ValueError("main_text must contain non-empty text")

    image = image.convert("RGBA")
    width, height = image.size
    draw = ImageDraw.Draw(image, "RGBA")

    left_margin = max(55, int(width * 0.065))
    right_margin = max(55, int(width * 0.065))
    top_margin = max(55, int(height * 0.075))
    bottom_margin = max(55, int(height * 0.075))

    side_column_width = (
        min(190, max(125, int(width * 0.13))) if side_text else 0
    )
    column_gap = 28 if side_text else 0
    main_right = width - right_margin - side_column_width - column_gap
    main_width = main_right - left_margin

    if main_width < int(width * 0.45):
        raise ValueError(
            "Image is too narrow to fit the main and marginal text columns"
        )

    seed_text = f"{main_text}|{heading}|{side_text}|{width}|{height}"
    stable_seed = int(
        hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:8], 16
    )
    rng = random.Random(stable_seed)

    base_main_size = 37 if width >= 1400 else 30
    base_heading_size = 39 if width >= 1400 else 32
    base_side_size = 21 if width >= 1400 else 18
    min_main_size = 27 if width >= 1400 else 22

    chosen = None

    # Fit all text before drawing; do not silently discard overflowing lines.
    for main_size in range(base_main_size, min_main_size - 1, -2):
        scale = main_size / base_main_size
        heading_size = max(min_main_size, int(base_heading_size * scale))
        side_size = max(
            16 if width >= 1400 else 14,
            int(base_side_size * scale),
        )

        main_font = load_font(font_path, main_size)
        heading_font = load_font(font_path, heading_size)
        side_font = load_font(font_path, side_size)

        heading_lines = (
            _wrap(draw, heading, heading_font, main_width, language)
            if heading else []
        )
        if len(heading_lines) > 2:
            continue

        main_lines = _wrap(draw, main_text, main_font, main_width, language)
        side_lines = (
            _wrap(draw, side_text, side_font, side_column_width, language)
            if side_text else []
        )

        y = top_margin
        if heading_lines:
            for line in heading_lines:
                box = _text_bbox(draw, line, heading_font, language)
                y += (box[3] - box[1]) + 8
            y += 14

        # Reserve a little extra vertical room for rotated line edges.
        main_positions = []
        for line in main_lines:
            box = _text_bbox(draw, line, main_font, language)
            line_height = max(1, box[3] - box[1])
            main_positions.append((y, line_height))
            y += line_height + rng.randint(13, 21)

        main_fits = (
            not main_positions
            or main_positions[-1][0] + main_positions[-1][1] + 8
            <= height - bottom_margin
        )

        side_y = top_margin + max(0, int(height * 0.20))
        side_positions = []
        for line in side_lines:
            box = _text_bbox(draw, line, side_font, language)
            line_height = max(1, box[3] - box[1])
            side_positions.append((side_y, line_height))
            side_y += line_height + 7

        side_fits = (
            not side_positions
            or side_positions[-1][0] + side_positions[-1][1]
            <= height - bottom_margin
        )

        if main_fits and side_fits:
            chosen = (
                main_font, heading_font, side_font,
                heading_lines, main_lines, side_lines, main_positions,
            )
            break

    if chosen is None:
        raise ValueError(
            "Text does not fit inside the manuscript page even at the "
            "minimum font size. Shorten the input text or increase image size."
        )

    (
        main_font, heading_font, side_font,
        heading_lines, main_lines, side_lines, main_positions,
    ) = chosen

    visible_lines = []
    y = top_margin

    # Heading block with slight position irregularity.
    for line in heading_lines:
        box = _text_bbox(draw, line, heading_font, language)
        line_height = box[3] - box[1]
        x = left_margin + rng.randint(0, 3)
        draw.text(
            (x, y + rng.randint(-1, 1)),
            line,
            font=heading_font,
            fill=(78, 43, 23, rng.randint(225, 248)),
            language=language,
        )
        visible_lines.append(line)
        y += line_height + rng.randint(7, 10)

    if heading_lines:
        draw.line(
            (left_margin, y + 3, main_right, y + 3),
            fill=(105, 73, 40, 125),
            width=2,
        )

    # Main text: slight baseline changes and tiny whole-line rotations.
    for index, line in enumerate(main_lines):
        target_y, _ = main_positions[index]
        x = left_margin + rng.randint(-2, 4)
        baseline_shift = rng.randint(-2, 2)

        image = _render_rotated_line(
            image=image,
            x=x,
            y=target_y + baseline_shift,
            line=line,
            font=main_font,
            highlight_text=highlight_text,
            language=language,
            rng=rng,
            max_angle=1.0,
        )
        visible_lines.append(line)

    # Marginal annotation column.
    if side_lines:
        side_x = main_right + column_gap
        side_y = top_margin + max(0, int(height * 0.20))

        draw = ImageDraw.Draw(image, "RGBA")
        draw.line(
            (
                main_right + 10,
                top_margin,
                main_right + 10,
                height - bottom_margin,
            ),
            fill=(120, 87, 50, 85),
            width=1,
        )

        for line in side_lines:
            box = _text_bbox(draw, line, side_font, language)
            line_height = box[3] - box[1]
            draw.text(
                (side_x + rng.randint(-1, 2), side_y + rng.randint(-1, 1)),
                line,
                font=side_font,
                fill=(105, 48, 27, rng.randint(175, 220)),
                language=language,
            )
            visible_lines.append(line)
            side_y += line_height + rng.randint(6, 9)

    # Folio marker.
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse(
        (width - 92, 55, width - 68, 79),
        outline=(105, 72, 38, 155),
        width=2,
    )

    return image.convert("RGB"), visible_lines
