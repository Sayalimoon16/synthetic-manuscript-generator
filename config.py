from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input_text"
DATA_DIR = BASE_DIR / "data"
FONT_DIR = BASE_DIR / "fonts"

SCRIPTS = ["devanagari", "modi", "sharada"]
FONT_PATHS = {
    "devanagari": FONT_DIR / "NotoSerifDevanagari-Regular.ttf",
    "modi": FONT_DIR / "NotoSansModi-Regular.otf",
    "sharada": FONT_DIR / "NotoSansSharada-Regular.ttf",
}
SPLITS = {"train": 85, "validation": 10, "test": 5}
IMAGE_WIDTH = 1600
IMAGE_HEIGHT = 1000
IMAGES_PER_SCRIPT = 100
RANDOM_SEED = 42

# Visual generation settings
FONT_SIZE_RANGE = (42, 50)
MARGIN_RANGE = (100, 130)
LINE_SPACING_RANGE = (18, 28)
INK_COLORS = [
    (55, 30, 20),
    (65, 38, 22),
    (75, 40, 25),
    (60, 35, 28),
    (85, 48, 30),
]
MATERIALS = ["paper", "palm_leaf"]
