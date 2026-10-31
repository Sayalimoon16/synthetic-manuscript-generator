
from pathlib import Path
import random
import sys
import traceback

from config import (
    BASE_DIR,
    INPUT_DIR,
    DATA_DIR,
    SCRIPTS,
    SPLITS,
    FONT_PATHS,
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
    IMAGES_PER_SCRIPT,
    RANDOM_SEED,
    MATERIALS,
)

from src.background import generate_background
from src.layout import create_manuscript_layout
from src.distortions import apply_distortions
from src.annotations import save_annotation


# --------------------------------------------------
# LOAD INPUT TEXT
# --------------------------------------------------

def load_input_text(script_name):

    input_path = INPUT_DIR / f"{script_name}.txt"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    text = input_path.read_text(
        encoding="utf-8"
    ).strip()

    # Split text using blank lines.
    # Multiple lines inside one paragraph are joined.

    paragraphs = [
        " ".join(
            line.strip()
            for line in paragraph.splitlines()
            if line.strip()
        )
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    if not paragraphs:
        raise ValueError(
            f"No text found in: {input_path}"
        )

    return paragraphs


# --------------------------------------------------
# VALIDATE PROJECT
# --------------------------------------------------

def validate_project():

    if sum(SPLITS.values()) != IMAGES_PER_SCRIPT:
        raise ValueError(
            f"SPLITS total is {sum(SPLITS.values())}, "
            f"but IMAGES_PER_SCRIPT is {IMAGES_PER_SCRIPT}"
        )

    required_splits = {
        "train",
        "validation",
        "test"
    }

    if set(SPLITS.keys()) != required_splits:
        raise ValueError(
            "SPLITS must contain train, validation and test."
        )

    if not MATERIALS:
        raise ValueError(
            "MATERIALS cannot be empty."
        )

    for script in SCRIPTS:

        if script not in FONT_PATHS:
            raise KeyError(
                f"Font not configured for {script}"
            )

        font_path = Path(FONT_PATHS[script])
        input_path = INPUT_DIR / f"{script}.txt"

        if not font_path.exists():
            raise FileNotFoundError(
                f"Font not found: {font_path}"
            )

        if not input_path.exists():
            raise FileNotFoundError(
                f"Input text not found: {input_path}"
            )

        load_input_text(script)


# --------------------------------------------------
# PREPARE MAIN TEXT
# --------------------------------------------------

def prepare_text(paragraphs, rng):

    count = min(
        len(paragraphs),
        rng.randint(2, 4)
    )

    selected = rng.sample(
        paragraphs,
        count
    )

    return " ".join(selected)


# --------------------------------------------------
# CREATE HEADING
# --------------------------------------------------

def make_heading(script_name):

    paragraphs = load_input_text(script_name)

    first_line = paragraphs[0]
    words = first_line.split()

    if len(words) >= 3:
        return " ".join(words[:3])

    return first_line[:35]


# --------------------------------------------------
# CREATE SIDE ANNOTATION
# --------------------------------------------------

def make_side_text(source_text):

    words = source_text.split()

    if not words:
        return ""

    return " ".join(words[:4])


# --------------------------------------------------
# CREATE HIGHLIGHT TEXT
# --------------------------------------------------

def make_highlight_text(source_text):

    words = source_text.split()

    if not words:
        return ""

    return words[len(words) // 2]


# --------------------------------------------------
# GENERATE ONE IMAGE
# --------------------------------------------------

def generate_one_image(
    script_name,
    split_name,
    image_number,
    rng
):

    font_path = FONT_PATHS[script_name]

    paragraphs = load_input_text(
        script_name
    )

    source_text = prepare_text(
        paragraphs,
        rng
    )

    heading = make_heading(
        script_name
    )

    side_text = make_side_text(
        source_text
    )

    highlight_text = make_highlight_text(
        source_text
    )

    # Select exactly one material per image.

    material = rng.choice(
        MATERIALS
    )

    seed = (
        RANDOM_SEED
        + SCRIPTS.index(script_name) * 100_000
        + image_number
    )

    # Generate background.

    image = generate_background(
        width=IMAGE_WIDTH,
        height=IMAGE_HEIGHT,
        material=material,
        seed=seed
    )

    # Generate manuscript layout.

    image, rendered_lines = create_manuscript_layout(
        image=image,
        main_text=source_text,
        font_path=font_path,
        side_text=side_text,
        heading=heading,
        highlight_text=highlight_text,
        language=None
    )

    # Apply manuscript distortions.

    image = apply_distortions(
        image,
        seed=seed
    )

    # Create output directories.

    output_dir = (
        DATA_DIR
        / script_name
        / split_name
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    image_name = (
        f"{script_name}_{image_number:03d}.png"
    )

    image_path = output_dir / image_name

    annotation_path = (
        output_dir
        / f"{script_name}_{image_number:03d}.md"
    )

    # Save image.

    image.save(
        image_path,
        format="PNG"
    )

    # Save synchronized Markdown annotation.

    save_annotation(
        output_path=annotation_path,
        image_name=image_name,
        script=script_name,
        material=material,
        split=split_name,
        original_text=source_text,
        rendered_text=rendered_lines,
        image_width=IMAGE_WIDTH,
        image_height=IMAGE_HEIGHT
    )

    return image_path, annotation_path


# --------------------------------------------------
# GENERATE COMPLETE DATASET
# --------------------------------------------------

def generate_dataset():

    validate_project()

    print("=" * 65)
    print("SYNTHETIC MANUSCRIPT DATASET GENERATOR")
    print("=" * 65)

    print(f"Project folder : {BASE_DIR}")
    print(f"Scripts        : {', '.join(SCRIPTS)}")
    print(f"Images/script  : {IMAGES_PER_SCRIPT}")
    print(f"Split counts   : {SPLITS}")

    print("=" * 65)

    total_images = 0
    total_errors = 0

    for script_index, script_name in enumerate(SCRIPTS):

        print(
            f"\nGenerating script: {script_name.upper()}"
        )

        image_number = 1

        for split_name, split_count in SPLITS.items():

            print(
                f"\nSplit: {split_name} "
                f"({split_count} images)"
            )

            for _ in range(split_count):

                seed = (
                    RANDOM_SEED
                    + script_index * 100_000
                    + image_number
                )

                rng = random.Random(seed)

                try:

                    image_path, annotation_path = generate_one_image(
                        script_name=script_name,
                        split_name=split_name,
                        image_number=image_number,
                        rng=rng
                    )

                    total_images += 1

                    print(
                        f"[{image_number:03d}/{IMAGES_PER_SCRIPT}] "
                        f"Saved: {image_path.name}"
                    )

                except Exception as error:

                    total_errors += 1

                    print(
                        f"ERROR: {script_name} "
                        f"image {image_number}: {error}"
                    )

                    traceback.print_exc()

                image_number += 1

    # Final summary.

    print("\n" + "=" * 65)
    print("DATASET GENERATION FINISHED")

    print(
        f"Successfully generated: {total_images}"
    )

    print(
        f"Errors: {total_errors}"
    )

    print(
        f"Output directory: {DATA_DIR}"
    )

    print("=" * 65)

    if total_errors:
        print(
            "\nSome images could not be generated. "
            "Check the errors above."
        )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    try:
        generate_dataset()

    except Exception as error:

        print(
            f"\nFATAL ERROR: {error}"
        )

        sys.exit(1)
