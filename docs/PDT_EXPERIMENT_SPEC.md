# Patch Discrimination Threshold (PDT) Experiment
## Measuring visual discrimination floor on identity-free stimuli
*Designed: 04-03-2026 | Ted Inoue + Terry (Salon)*

---

## Purpose

Establish the precise hue discrimination threshold for AI vision systems on identity-free stimuli. The existing patch isolation data (40/40 at 10 degrees) proves discrimination works above 10 degrees, but the floor is unknown. Knowing the floor allows us to quantify the semantic capture window: the gap between what the system CAN discriminate (patch threshold) and where it DOES discriminate on vehicles (gradient breakpoint) is the prior's contribution, measured in degrees.

## Stimuli

Five images. Solid colored rectangles on black background. No object identity, no texture, no gradients.

Reference color: H=42, S=0.85, V=0.80 (canonical school bus yellow neighborhood)

| Stimulus | Left patch | Right patch | Shift | Shifted side | Ground truth |
|----------|-----------|-------------|-------|-------------|-------------|
| PDT-00 | H=42 | H=42 | 0 | none (control) | identical |
| PDT-03 | H=45 | H=42 | +3 | left | left is cooler |
| PDT-04 | H=42 | H=45 | +3 | right | right is cooler |
| PDT-06 | H=48 | H=42 | +6 | left | left is cooler |
| PDT-07 | H=42 | H=48 | +6 | right | right is cooler |

Naming convention: base number = shift amount, even = left shifted, odd = right shifted.
PDT-00 is the identical-color control for false positive rate estimation.

RGB values (computed):
- H=42: RGB(204, 152, 31)
- H=45: RGB(204, 161, 31)  [+9 green channel vs reference]
- H=48: RGB(204, 169, 31)  [+17 green channel vs reference]

Created in Photoshop for consistency with all existing stimuli in the repo. Target HSV values documented in generate_pdt_stimuli.py. Eyedropper-verified ground truth values to be recorded in manifest after creation.

## Protocol

**Prompt (PS04-equivalent):**
"Compare the colors of these two rectangles. Which is warmer, which is cooler?"

This matches the prompt level where all 8 models scored 40/40 on S003Patch (10-degree shift).

**Models:** All 8 from existing dataset:
- Anthropic: Opus 4.6, Sonnet 4.6, Haiku 4.5
- OpenAI: GPT-5.4, GPT-5.4-mini, GPT-5.4-nano
- Google: Gemini 2.5 Pro, Gemini 2.5 Flash

**Trials:** 5 per model per stimulus. Total: 8 models x 5 stimuli x 5 trials = 200 API calls.

**Temperature:** 1.0 (matches existing protocol)

**System prompt:** None.

## Scoring

| Code | Criteria |
|------|----------|
| CORRECT | Correctly identifies which rectangle is warmer/cooler |
| REVERSED | Identifies a difference but assigns direction wrong |
| SAME | Reports both rectangles as identical color |
| FABRICATED | Reports a difference on control stimuli (PDT-00/01) |
| INDETERMINATE | Unclear or contradictory response |

**Key metrics per model:**
- False positive rate: FABRICATED / total control trials
- Detection rate at +3: (CORRECT + REVERSED) / total +3 trials
- Direction accuracy at +3: CORRECT / (CORRECT + REVERSED) at +3
- Detection rate at +6: same formula
- Direction accuracy at +6: same formula
- Discrimination threshold estimate: lowest shift where detection rate > 50%

## What we learn

**If most models detect +3 on patches:**
Threshold is below 3 degrees. The semantic capture window on vehicles is enormous (3 to 18-27 degrees, depending on architecture). We may need to go finer (1-degree increments) to find the true floor.

**If most models fail +3 but detect +6:**
Threshold is between 3 and 6 degrees. The capture window is still large (6 to 18-27). We can interpolate the threshold from the detection rate curve.

**If models fail both +3 and +6:**
Threshold is between 6 and 10 degrees (since 10 is 40/40). Add PDT-09 (left +9) and PDT-10 (right +9) to find the boundary.

**In all cases:**
The position-swap pairs (e.g., PDT-03 vs PDT-04) tell us whether there's a spatial bias. If accuracy differs between left-shifted and right-shifted stimuli, there's a positional confound that needs to be controlled in the vehicle experiments too.

## Extensibility

If the +3 threshold is too easy, add:
- PDT-02 / PDT-02r: +1 degree shift (H=43 vs H=42, delta = 1 RGB unit in green)
- PDT-05 / PDT-05r: +2 degree shift

If more resolution is needed around a specific range, the generation script accepts arbitrary shift values.

## Connection to existing data

| Stimulus type | Shift | Known result |
|--------------|-------|-------------|
| S003Patch (from vehicles) | 10 degrees | 40/40 correct (PS04r) |
| PDT patches (solid rects) | 6 degrees | **this experiment** |
| PDT patches (solid rects) | 3 degrees | **this experiment** |
| PDT patches (solid rects) | 0 degrees | **this experiment** (false positive control) |
| S003 vehicles | 10 degrees | 0-33% correct direction |

The semantic capture window = vehicle breakpoint minus patch threshold.

## Files

- Stimuli: stimuli/PDT-00.png through PDT-07.png
- Manifest: stimuli/PDT_MANIFEST.json (ground truth, RGB values, shift amounts)
- Generator: generate_pdt_stimuli.py
- This spec: PDT_EXPERIMENT_SPEC.md

---

*Designed by Ted Inoue and Terry (Salon), 04-03-2026*
*Repository: tedinoue/sce-replication*
