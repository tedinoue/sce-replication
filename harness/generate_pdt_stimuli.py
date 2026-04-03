#!/usr/bin/env python3
"""
generate_pdt_stimuli.py
Generates solid-color rectangle pairs for the Patch Discrimination Threshold (PDT) experiment.

Run: python3 generate_pdt_stimuli.py

Output: PDT-00.png through PDT-07.png in ./stimuli/

Design:
  Reference color: H=42 (canonical school bus yellow), S=0.85, V=0.80
  Shifts: 0, 3, 6 degrees (cooler = higher H value)
  Even numbers (00, 03, 06): LEFT patch shifted
  Odd numbers (01, 04, 07): RIGHT patch shifted
  PDT-00 and PDT-01 are identical-color controls (both H=42)

Rectangle dimensions match S003Patch format: 700x467 canvas, black background,
two rectangles of equal size centered vertically with horizontal gap.
"""

from PIL import Image, ImageDraw
import colorsys
import os
import json

# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = "stimuli"
CANVAS_W, CANVAS_H = 700, 467
RECT_W, RECT_H = 200, 200
GAP = 60  # pixels between rectangles
BG_COLOR = (0, 0, 0)  # black

# Reference color
REF_H = 42  # degrees
SAT = 0.85
VAL = 0.80

# Shift amounts in degrees
SHIFTS = [0, 3, 6]

# ============================================================
# HELPERS
# ============================================================

def hsv_to_rgb_int(h_deg, s, v):
    """Convert HSV (h in degrees, s and v 0-1) to RGB (0-255 ints)."""
    r, g, b = colorsys.hsv_to_rgb(h_deg / 360.0, s, v)
    return (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def make_stimulus(left_h, right_h, filename, label):
    """Generate a stimulus image with two solid rectangles."""
    img = Image.new("RGB", (CANVAS_W, CANVAS_H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Center the pair
    total_w = RECT_W * 2 + GAP
    x_start = (CANVAS_W - total_w) // 2
    y_start = (CANVAS_H - RECT_H) // 2

    # Left rectangle
    left_color = hsv_to_rgb_int(left_h, SAT, VAL)
    draw.rectangle(
        [x_start, y_start, x_start + RECT_W, y_start + RECT_H],
        fill=left_color
    )

    # Right rectangle
    right_color = hsv_to_rgb_int(right_h, SAT, VAL)
    draw.rectangle(
        [x_start + RECT_W + GAP, y_start,
         x_start + RECT_W * 2 + GAP, y_start + RECT_H],
        fill=right_color
    )

    filepath = os.path.join(OUTPUT_DIR, filename)
    img.save(filepath, "PNG")

    return {
        "file": filename,
        "label": label,
        "left_h": left_h,
        "right_h": right_h,
        "left_rgb": left_color,
        "right_rgb": right_color,
        "shift_degrees": abs(left_h - right_h),
        "shifted_side": "left" if left_h != REF_H else ("right" if right_h != REF_H else "none"),
        "ground_truth": (
            "identical" if left_h == right_h
            else ("left is cooler" if left_h > right_h else "right is cooler")
        )
    }


# ============================================================
# MAIN
# ============================================================

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    manifest = []

    for shift in SHIFTS:
        shifted_h = REF_H + shift

        # Even number: left patch shifted (cooler)
        even_id = f"PDT-{shift:02d}"
        info = make_stimulus(shifted_h, REF_H, f"{even_id}.png", 
                            f"Left shifted +{shift} degrees")
        manifest.append(info)
        print(f"  {even_id}: L=H{shifted_h} R=H{REF_H}  "
              f"L_RGB{info['left_rgb']} R_RGB{info['right_rgb']}  "
              f"[{info['ground_truth']}]")

        # Odd number: right patch shifted (cooler)
        odd_id = f"PDT-{shift + 1:02d}"
        info = make_stimulus(REF_H, shifted_h, f"{odd_id}.png",
                            f"Right shifted +{shift} degrees")
        manifest.append(info)
        print(f"  {odd_id}: L=H{REF_H} R=H{shifted_h}  "
              f"L_RGB{info['left_rgb']} R_RGB{info['right_rgb']}  "
              f"[{info['ground_truth']}]")

    # Write manifest
    manifest_path = os.path.join(OUTPUT_DIR, "PDT_MANIFEST.json")
    with open(manifest_path, "w") as f:
        json.dump({
            "experiment": "Patch Discrimination Threshold (PDT)",
            "date_generated": "2026-04-03",
            "reference_color": {"h": REF_H, "s": SAT, "v": VAL, "rgb": hsv_to_rgb_int(REF_H, SAT, VAL)},
            "canvas": {"width": CANVAS_W, "height": CANVAS_H},
            "rectangles": {"width": RECT_W, "height": RECT_H, "gap": GAP},
            "stimuli": manifest
        }, f, indent=2)
    print(f"\n  Manifest: {manifest_path}")

    # Print summary
    print(f"\n  Generated {len(manifest)} stimuli in {OUTPUT_DIR}/")
    print(f"  Reference: H={REF_H}, S={SAT}, V={VAL} = RGB{hsv_to_rgb_int(REF_H, SAT, VAL)}")
    print(f"  Shifts tested: {SHIFTS} degrees")
    print(f"  Controls (0 shift): PDT-00, PDT-01 (both identical, position-swapped)")


if __name__ == "__main__":
    main()
