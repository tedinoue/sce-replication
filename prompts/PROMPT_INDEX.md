# Prompt Index
## SCE Color Replication Study

Two prompts only. Minimal. Unprimed.

The original study used "describe this scene" with no color-specific instructions.
The power of the finding is that models spontaneously misreport color when not asked
to scrutinize it. Leading prompts would invalidate the experiment by priming color comparison.

---

## Prompt Files

| ID | File | Type | Purpose |
|---|---|---|---|
| P01 | P01_narrative.txt | Narrative | "Describe this scene." Unprimed. Tests what the model volunteers about color. |
| P02 | P02_analytical.txt | Analytical | Requests hue measurement in degrees. Tests analytical bypass of semantic prior. |

Both prompts are used with ALL core stimuli (S001-S007). Same prompt, different images.
Gradient stimuli (G001-G006) use P01 only. The gradient measures narrative capture, not analytical bypass.

## Core Condition Matrix

| Condition | Stimulus | Prompt | Tests |
|---|---|---|---|
| C01 | S001.png | P01 (narrative) | Control: no conflict, unprimed |
| C02 | S001.png | P02 (analytical) | Control: analytical baseline |
| C03 | S002.png | P01 (narrative) | Prior-consistent split, unprimed |
| C04 | S002.png | P02 (analytical) | Prior-consistent split, analytical |
| C05 | S003.png | P01 (narrative) | Prior-conflicting split, unprimed (KEY TEST) |
| C06 | S003.png | P02 (analytical) | Prior-conflicting split, analytical |
| C07 | S004.png | P01 (narrative) | Composite: banana capture, carrot control, apple ceiling |
| C08 | S004.png | P02 (analytical) | Composite: analytical bypass on all three objects |

## Gradient Conditions (P01 narrative only)

| Condition | Stimulus | Shift from canonical |
|---|---|---|
| (C01) | S001.png | 0° baseline (shared with core) |
| CG01 | G001.png | +5° |
| CG02 | S003.png | +10° (reuse from core set) |
| CG03 | G003.png | +15° |
| CG04 | G004.png | +20° |
| CG05 | G005.png | +25° |
| CG06 | G006.png | +30° |

**Note on filenames:** All stimulus files use opaque names (S001.png, G001.png) to prevent
filename contamination. Models receive the image URL, which includes the filename.
See STIMULUS_SPEC.md for the mapping from filenames to experimental conditions.
