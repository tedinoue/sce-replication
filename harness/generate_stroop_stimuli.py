#!/usr/bin/env python3
"""
Generate Stroop T6 images at arbitrary load levels.

The first 12 positions match the existing verified answer key
(docs/STROOP_RESULTS.md). Positions 13+ extend the sequence
with continued incongruent word/ink pairs.

Canvas: 1200 x 900 RGB on white. Four columns, rows grow as needed.
Fonts: DejaVuSans-Bold (matches existing T6 stimuli visually).

Usage:
    python3 generate_stroop.py 16 20      # emits T6_graded_load_16.png, T6_graded_load_20.png
    python3 generate_stroop.py --all      # emits 2, 4, 8, 12, 16, 20
"""

import sys, os, argparse, json
from PIL import Image, ImageDraw, ImageFont

# === Verified ink palette (RGB), sampled from existing T6_12.png ===
# Matches docs/STROOP_RESULTS.md answer key exactly.
INK_RGB = {
    "red":    (220, 40, 40),
    "green":  (30, 160, 50),
    "blue":   (40, 80, 200),
    "yellow": (210, 190, 30),
    "orange": (230, 130, 20),
    "purple": (140, 40, 180),
    "pink":   (220, 100, 150),
    "brown":  (140, 80, 30),
}

# === Answer key (word, ink_color). First 12 match verified existing key. ===
# Extended positions 13-20 maintain incongruence (word != ink)
# and cycle through the 8 colors. Each word-ink pair at position N
# uses a combination that differs from the word text.
ANSWER_KEY = [
    # Positions 1-12: EXACT match to existing T6_graded_load_12.png answer key
    ("RED",    "blue"),
    ("GREEN",  "red"),
    ("BLUE",   "yellow"),
    ("YELLOW", "green"),
    ("ORANGE", "purple"),
    ("PURPLE", "orange"),
    ("PINK",   "brown"),
    ("BROWN",  "pink"),
    ("RED",    "green"),
    ("BLUE",   "orange"),
    ("GREEN",  "purple"),
    ("YELLOW", "red"),
    # Positions 13-20: new extensions. All incongruent.
    # Use remaining color combinations not yet exhausted.
    ("ORANGE", "blue"),    # 13
    ("PURPLE", "yellow"),  # 14
    ("PINK",   "green"),   # 15
    ("BROWN",  "red"),     # 16
    ("RED",    "pink"),    # 17
    ("BLUE",   "brown"),   # 18
    ("YELLOW", "purple"),  # 19
    ("GREEN",  "orange"),  # 20
]

# === Layout constants (match existing T6 stimuli) ===
CANVAS_W, CANVAS_H = 1200, 900
COLS = 4
COL_X = [150, 450, 750, 1050]     # word center x-positions (4 columns)
ROW_Y_START = 190                 # y of first row center
ROW_SPACING = 100                 # vertical spacing between rows
HEADER_Y = 10                     # top-left mini header
INSTRUCTION_Y = 52                # main instruction line y
BG = (255, 255, 255)
HEADER_COLOR = (80, 80, 80)
INSTRUCTION_COLOR = (30, 30, 30)

# Fonts
FONT_WORD_SIZE = 56
FONT_HEADER_SIZE = 20
FONT_INSTRUCTION_SIZE = 30

FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG_PATH  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font_bold(size): return ImageFont.truetype(FONT_BOLD_PATH, size)
def font_reg(size):  return ImageFont.truetype(FONT_REG_PATH, size)

def generate(n_items: int, out_path: str):
    if n_items > len(ANSWER_KEY):
        raise ValueError(f"n_items={n_items} exceeds answer key length {len(ANSWER_KEY)}")
    if n_items < 1:
        raise ValueError("n_items must be >= 1")

    n_rows = (n_items + COLS - 1) // COLS

    im = Image.new("RGB", (CANVAS_W, CANVAS_H), BG)
    draw = ImageDraw.Draw(im)

    # Mini header top-left
    draw.text((10, HEADER_Y),
              f"STROOP BATTERY v2 | T6-{n_items}: Graded Load: {n_items} Items",
              font=font_reg(FONT_HEADER_SIZE),
              fill=HEADER_COLOR)

    # Instruction line
    instruction = f"For each word, report the TEXT and the INK COLOR ({n_items} items)."
    fi = font_reg(FONT_INSTRUCTION_SIZE)
    tw = draw.textlength(instruction, font=fi)
    draw.text(((CANVAS_W - tw) / 2, INSTRUCTION_Y),
              instruction, font=fi, fill=INSTRUCTION_COLOR)

    # Words
    f_word = font_bold(FONT_WORD_SIZE)
    for i in range(n_items):
        word, ink_name = ANSWER_KEY[i]
        col = i % COLS
        row = i // COLS
        cx = COL_X[col]
        cy = ROW_Y_START + row * ROW_SPACING
        # measure word so we can center
        bbox = draw.textbbox((0, 0), word, font=f_word)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        # baseline offset: bbox[1] is top offset from origin
        x = cx - tw / 2 - bbox[0]
        y = cy - th / 2 - bbox[1]
        draw.text((x, y), word, font=f_word, fill=INK_RGB[ink_name])

    im.save(out_path, "PNG")
    return out_path

def emit_answer_key_json(out_path):
    data = {
        "description": "Stroop T6 verified answer key. Each position has an incongruent word/ink pair.",
        "ink_rgb": INK_RGB,
        "answer_key": [{"position": i+1, "word": w, "ink": ink}
                       for i, (w, ink) in enumerate(ANSWER_KEY)],
    }
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    return out_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("counts", type=int, nargs="*", help="Load levels to generate")
    parser.add_argument("--all", action="store_true",
                        help="Generate 2, 4, 8, 12, 16, 20")
    parser.add_argument("--out-dir", default=".",
                        help="Output directory for PNGs")
    parser.add_argument("--answer-key", action="store_true",
                        help="Also write ANSWER_KEY_extended.json")
    args = parser.parse_args()

    if args.all:
        counts = [2, 4, 8, 12, 16, 20]
    elif args.counts:
        counts = args.counts
    else:
        counts = [16, 20]

    os.makedirs(args.out_dir, exist_ok=True)

    for n in counts:
        out = os.path.join(args.out_dir, f"T6_graded_load_{n}.png")
        generate(n, out)
        print(f"  wrote {out}")

    if args.answer_key:
        akp = os.path.join(args.out_dir, "ANSWER_KEY_extended.json")
        emit_answer_key_json(akp)
        print(f"  wrote {akp}")

if __name__ == "__main__":
    main()
