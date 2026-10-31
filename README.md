# Synthetic Manuscript Generator

A Python-based project for generating synthetic Indic manuscript folio
images with synchronized Markdown annotations. The generator supports
**Devanagari, Modi, and Sharada** scripts and two manuscript material
styles: **aged handmade paper** and **palm leaf**.

The project is designed to create a small, organized dataset for
experimentation with manuscript-image processing, OCR, script
recognition, and related computer-vision tasks. The generated samples
are synthetic and should not be treated as historically authenticated
manuscripts.

------------------------------------------------------------------------

## 1. Project Objectives

-   Generate manuscript-style folio images using three Indic scripts:
    -   Devanagari
    -   Modi
    -   Sharada
-   Render text in two material styles:
    -   Aged handmade paper
    -   Palm leaf
-   Add visual variation such as natural texture, stains, folds,
    waviness, faded ink, smudges, and ink bleeding.
-   Arrange text using manuscript-inspired layouts, including headings,
    main text, highlights, marginal notes, and folio markers where
    configured.
-   Save a Markdown annotation alongside every generated image.
-   Organize the dataset into training, validation, and test splits.

## 2. Supported Scripts

Each script has its own input-text file and font file. The generator
selects the corresponding script configuration when creating samples.

  -----------------------------------------------------------------------------------------------
  Script                  Input text                    Font file
  ----------------------- ----------------------------- -----------------------------------------
  Devanagari              `input_text/devanagari.txt`   `fonts/NotoSerifDevanagari-Regular.ttf`

  Modi                    `input_text/modi.txt`         `fonts/NotoSansModi-Regular.ttf` or the
                                                        configured Modi font file

Sharada:              `input_text/sharada.txt`        `fonts/NotoSansSharada-Regular.ttf` 
-----------------------------------------------------------------------------------------------

**Important:** Modi and Sharada samples must contain text in their
respective Unicode scripts. Changing only the script label or font name
does not convert Devanagari text into Modi or Sharada. Review the input
files and rendered images to confirm that the intended characters are
present and render correctly.

The text is used for synthetic dataset generation. Unless separately
checked against reliable manuscript sources, it should not be described
as historically verified transcription.

## 3. Supported Manuscript Materials

The generator supports two material types:

### Aged handmade paper

-   Warm, aged paper-like base colour.
-   Paper texture and fibre-like details.
-   Stains and surface variation.
-   Border and ageing effects.

### Palm leaf

-   Darker, earthy base colour.
-   Palm-leaf-style horizontal surface lines.
-   Fibre-like texture and stains.
-   Material-specific visual variation.

The material is selected for each generated sample from the configured
material options. Check the saved annotation metadata to identify the
material used for a particular image.

## 4. Image Appearance and Layout

The project combines background generation, text layout, and image
distortions to create varied folio-like samples.

### Background and texture

-   Generates a separate background appearance for paper and palm leaf.
-   Adds texture, fibres, stains, and borders.

### Text layout

Depending on the configured layout and available text, a folio may
contain: - A heading or opening text. - Main manuscript text. -
Highlighted text. - A marginal or side annotation. - A folio marker.

The layout code reserves space for side annotations when they are used
and adjusts text sizing to help keep content within the image. If the
content cannot fit at the configured minimum font size, the layout can
raise an error rather than silently treating omitted text as a complete
transcription.

### Visual distortions

The distortion module can apply effects such as: - Folds. - Waviness. -
Ink fading. - Ink smudges. - Ink bleeding.

These effects are intended to add visual variation. They do not
establish that an image reproduces the appearance of a particular
historical manuscript.

## 5. Dataset Size and Split

The configured dataset contains **100 images per script**, distributed
as follows:

  Split                    Images per script
  ---------------------- -------------------
  Train                                   85
  Validation                              10
  Test                                     5
  **Total per script**               **100**

  Script                Train   Validation     Test     Total
  ----------------- --------- ------------ -------- ---------
  Devanagari               85           10        5       100
  Modi                     85           10        5       100
  Sharada                  85           10        5       100
  **All scripts**     **255**       **30**   **15**   **300**

The dataset was previously checked for this 300-image distribution and
matching Markdown annotation files. If you regenerate the dataset or
change the configuration, run the count checks again before publishing.

## 6. Project Structure

``` text
Synthetic Manuscript Generator/
│
├── generate.py
├── config.py
├── requirements.txt
├── README.md
│
├── fonts/
│   ├── NotoSerifDevanagari-Regular.ttf
│   ├── NotoSansModi-Regular.ttf
│   └── NotoSansSharada-Regular.ttf
│
├── input_text/
│   ├── devanagari.txt
│   ├── modi.txt
│   └── sharada.txt
│
├── src/
│   ├── background.py
│   ├── text_renderer.py
│   ├── layout.py
│   ├── distortions.py
│   └── annotations.py
│
└── data/
    ├── devanagari/
    │   ├── train/
    │   ├── validation/
    │   └── test/
    │
    ├── modi/
    │   ├── train/
    │   ├── validation/
    │   └── test/
    │
    └── sharada/
        ├── train/
        ├── validation/
        └── test/
```

Each script folder contains its own split folders. Generated image files
and their corresponding `.md` annotation files are saved in the relevant
split folder.

## 7. Main Modules

  -----------------------------------------------------------------------
  File                                Responsibility
  ----------------------------------- -----------------------------------
  `generate.py`                       Coordinates dataset generation for
                                      the configured scripts and splits.

  `config.py`                         Stores configuration such as image
                                      dimensions, scripts, materials,
                                      fonts, and split counts.

  `src/background.py`                 Creates paper and palm-leaf
                                      backgrounds and their textures.

  `src/text_renderer.py`              Loads fonts, measures text, wraps
                                      text, and renders text.

  `src/layout.py`                     Places headings, main text,
                                      highlights, and side annotations on
                                      the folio.

  `src/distortions.py`                Applies folds, waviness, fading,
                                      smudges, and ink bleeding.

  `src/annotations.py`                Creates and saves Markdown metadata
                                      and transcription files.
  -----------------------------------------------------------------------

## 8. Requirements

The project uses Python and the following Python packages:

``` text
Pillow
numpy
opencv-python
matplotlib
fonttools
```

Install the dependencies:

``` bash
pip install -r requirements.txt
```

`fonttools` is useful for font inspection and checking. If it is not
imported by the generator or its test scripts, it may not be required
for the core generation command.

## 9. Setup

### Windows PowerShell

Open the project folder in VS Code or PowerShell:

``` powershell
cd "C:\Users\HP\Downloads\Synthetic Manuscript Generator"
```

Create a virtual environment:

``` powershell
python -m venv venv
```

Activate it:

``` powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

``` powershell
pip install -r requirements.txt
```

Make sure the font files and all three input-text files are present in
their respective folders before generating the dataset.

## 10. Generate the Dataset

Run the generator from the project root:

``` bash
python generate.py
```

The script uses the settings in `config.py` and the text and font
resources for each configured script. Generated images and annotations
are written under the corresponding `data/<script>/<split>/` directory.

Do not run generation again if you only want to inspect or publish the
already generated dataset. Running it may create or replace files
depending on the implementation and configuration.

## 11. Run the Smoke Test

If the project includes `smoke_test.py`, run:

``` bash
python smoke_test.py
```

The smoke test is intended to check that the generation pipeline can
produce a sample for each supported script. Test files created with
special sample IDs (for example, ID `999`) are extra test artifacts;
remove them before publishing if the dataset is required to contain
exactly 100 samples per script.

## 12. Annotation Format

Every generated image should have a matching Markdown file with the same
base filename.

Example:

``` text
devanagari_001.png
devanagari_001.md
```

An annotation records information such as: - Image filename. - Script. -
Material. - Dataset split. - Image width and height. - Rendered/visible
text transcription.

Example structure:

``` markdown
# devanagari_001.png

- **Script:** devanagari
- **Material:** paper
- **Split:** train
- **Image Width:** 1600
- **Image Height:** 1000

## Transcription

Text visible in the generated image.
```

The transcription should correspond to the text rendered in the image.
If a layout adds headings, side notes, or other text, make sure the
annotation accurately represents the visible content and its ordering.

## 13. Verify Dataset Counts

From the project root, you can use PowerShell to count PNG images and
Markdown annotations in each split:

``` powershell
$scriptNames = @("devanagari", "modi", "sharada")

foreach ($script in $scriptNames) {
    Write-Host "`n$script"
    foreach ($split in @("train", "validation", "test")) {
        $folder = "data/$script/$split"
        $images = (Get-ChildItem $folder -Filter "*.png" -ErrorAction SilentlyContinue).Count
        $annotations = (Get-ChildItem $folder -Filter "*.md" -ErrorAction SilentlyContinue).Count
        Write-Host "$split : images=$images annotations=$annotations"
    }
}
```

Expected counts, excluding temporary smoke-test files:

-   Each script: 85 train, 10 validation, 5 test.
-   All scripts: 300 images.
-   Each image: one matching Markdown annotation.
-   No missing annotation files.

Also inspect samples from all three scripts and both material types. A
successful file count alone does not confirm correct script shaping,
readable glyphs, or historical authenticity.

## 14. Quality Checks Before Publishing

Before uploading to GitHub or Hugging Face:

1.  Confirm that each script uses its intended input text and font.
2.  Open sample images from Devanagari, Modi, and Sharada.
3.  Check that characters render correctly and are not replaced by empty
    boxes or missing-glyph symbols.
4.  Inspect both paper and palm-leaf examples.
5.  Check that text, headings, and marginal notes are not clipped or
    unintentionally overlapping.
6.  Confirm that each image has a matching annotation and that the
    transcription matches the visible text.
7.  Remove temporary smoke-test images and annotations.
8.  Recount the final dataset to confirm the intended 100 samples per
    script.

## 15. Hugging Face Dataset Organization

The intended public dataset repository should contain three script
subsets, each with train, validation, and test splits:

``` text
dataset/
├── devanagari/
│   ├── train/
│   ├── validation/
│   └── test/
├── modi/
│   ├── train/
│   ├── validation/
│   └── test/
└── sharada/
    ├── train/
    ├── validation/
    └── test/
```

Keep each image and its `.md` annotation together, or preserve an
unambiguous filename-based relationship if the Hugging Face repository
uses a different layout. In the dataset card, describe the scripts,
materials, split counts, annotation format, generation process, and
known limitations.

## 16. GitHub Repository

The GitHub repository should include: - Python source code. -
`config.py` and `generate.py`. - `requirements.txt`. - The three
input-text files. - Font files only when their licenses permit
redistribution; otherwise document where to obtain them. - README and
usage instructions. - Optional tests and a small number of sample
images.

For a large dataset, link to the Hugging Face dataset repository rather
than duplicating all generated images in the GitHub source repository.

## 17. Limitations

-   The images are procedurally generated synthetic samples, not scans
    of original manuscripts.
-   Visual texture effects are approximations and may not capture the
    full physical characteristics of historical palm leaves or handmade
    paper.
-   Text accuracy depends on the input text, font coverage, and
    text-shaping support.
-   A font rendering successfully does not prove that the text is
    historically accurate or that every glyph form is correct for a
    particular manuscript period.
-   Modi and Sharada input content should be checked by a reader
    familiar with those scripts before making linguistic or historical
    claims.
-   OCR performance or similarity to real manuscripts must be evaluated
    separately; this project does not guarantee a particular accuracy or
    parity score.

## 18. Future Improvements

-   Add more verified source transcriptions for each script.
-   Expand the font collection and validate script-specific shaping.
-   Add richer physical effects such as edge damage, cracks, curling,
    and perspective warping.
-   Add automated checks for missing glyphs, clipping, duplicate files,
    and annotation mismatches.
-   Evaluate generated samples against real manuscript images using
    suitable image-quality and OCR metrics.

------------------------------------------------------------------------

## Project Summary

  -----------------------------------------------------------------------
  Item                                Details
  ----------------------------------- -----------------------------------
  Project                             Synthetic Manuscript Generator

  Language                            Python

  Scripts                             Devanagari, Modi, Sharada

  Materials                           Aged handmade paper, palm leaf

  Images                              100 per script; 300 total in the
                                      configured dataset

  Split                               85 train, 10 validation, 5 test per
                                      script

  Annotations                         Markdown file paired with each
                                      image

  Main use                            Synthetic manuscript-image dataset
                                      generation and experimentation
  -----------------------------------------------------------------------
