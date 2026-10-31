
from pathlib import Path


def create_annotation(
    image_name,
    script,
    material,
    split,
    original_text,
    rendered_text=None,
    image_width=1600,
    image_height=1000,
):
    """Create a Markdown annotation synchronized with the image."""

    if rendered_text is None:
        visible_text = str(original_text)
    elif isinstance(rendered_text, (list, tuple)):
        visible_text = "\n".join(
            str(line) for line in rendered_text
        )
    else:
        visible_text = str(rendered_text)

    annotation = f"""# {image_name}

- **Script:** {script}
- **Material:** {material}
- **Split:** {split}
- **Image Width:** {image_width}
- **Image Height:** {image_height}

## Transcription

{visible_text}
"""
    return annotation


def save_annotation(
    output_path,
    image_name,
    script,
    material,
    split,
    original_text,
    rendered_text=None,
    image_width=1600,
    image_height=1000,
):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    content = create_annotation(
        image_name=image_name,
        script=script,
        material=material,
        split=split,
        original_text=original_text,
        rendered_text=rendered_text,
        image_width=image_width,
        image_height=image_height,
    )

    output_path.write_text(content, encoding="utf-8")
    return output_path
