# Experiment Configuration
## SCE Color Replication Study
## Last updated: 03-21-2026

---

## IMPORTANT: Filename Opacity

Stimulus images use opaque names (S001.png, G001.png) to prevent filename contamination.
Models receive the image URL, which includes the filename. Descriptive names like
"bus_cool_van_warm.png" would leak the experimental condition into the model's context.
The mapping from opaque names to experimental conditions lives in STIMULUS_SPEC.md only.
The harness and scoring scripts reference that mapping. The models never see it.

---

## Models

| Model ID | Provider | API Endpoint | Default Temp | Vision Support |
|---|---|---|---|---|
| claude-opus-4-6 | Anthropic | https://api.anthropic.com/v1/messages | 1.0 | Yes (URL or base64) |
| claude-sonnet-4-6 | Anthropic | https://api.anthropic.com/v1/messages | 1.0 | Yes (URL or base64) |
| gpt-4o | OpenAI | https://api.openai.com/v1/chat/completions | 1.0 | Yes (URL) |
| gemini-2.5-pro | Google | https://generativelanguage.googleapis.com/v1beta/models/ | 1.0 | Yes (URL or base64) |
| grok-3 | xAI | https://api.x.ai/v1/chat/completions | 1.0 (verify) | Yes (URL) |

## Image Delivery

All stimulus images hosted at:
`https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli/{filename}`

Filenames are opaque (S001.png, G001.png). No descriptive names.
Passed to each API as image URL. No base64 encoding.

## Experiment Parameters

- **Trials per condition:** 10
- **Temperature (primary study):** Default for each model (1.0 across all, verify Grok)
- **Temperature (follow-up study):** Single model, vary temperature (0.0, 0.5, 1.0, 1.5)
- **Max tokens per response:** 500
- **System prompt:** None. Raw model behavior only.

## Prompts

Two prompts. Minimal. Unprimed.

| ID | File | Text | Purpose |
|---|---|---|---|
| P01 | P01_narrative.txt | "Describe this scene." | Unprimed. Tests what model volunteers. |
| P02 | P02_analytical.txt | "For each object in this image, measure the dominant hue value in degrees on a standard HSV color wheel (0=red, 60=yellow, 120=green)." | Analytical bypass. |

## Stimuli (opaque filenames, see STIMULUS_SPEC.md for full details)

### Core Set
| File | Condition | Notes |
|---|---|---|
| S001.png | Control (both vehicles same hue) | No conflict |
| S002.png | Prior-consistent split | Correct answer aligns with prior |
| S003.png | Prior-conflicting split | Correct answer conflicts with prior (KEY TEST) |
| S004.png | Object with color conflict | SCE capture test |
| S005.png | Matched-pair control object | Same color, no prior conflict |
| S006.png | Prior-consistent control | No conflict |
| S007.png | Collocation test | Stretch goal |

### Gradient Series
| File | Condition | Notes |
|---|---|---|
| G001.png | Bus 47°, Van 42° (+5°) | Near-threshold |
| (S003.png) | Bus 51°, Van 41° (+10°) | Reuse from core set |
| G003.png | Bus 58°, Van 42° (+16°) | Approaching breakpoint |
| G004.png | Bus 63°, Van 42° (+21°) | Likely breakpoint zone |
| G005.png | Bus 69°, Van 42° (+27°) | Post-breakpoint for most models |
| G006.png | Bus 73°, Van 42° (+31°) | Near-ceiling detection |

S001.png serves as the 0° baseline for the gradient series.

## Core Conditions Matrix

| Condition | Stimulus | Prompt | Tests |
|---|---|---|---|
| C01 | S001.png | P01 (narrative) | Control: no conflict, unprimed |
| C02 | S001.png | P02 (analytical) | Control: analytical baseline |
| C03 | S002.png | P01 (narrative) | Prior-consistent split, unprimed |
| C04 | S002.png | P02 (analytical) | Prior-consistent split, analytical |
| C05 | S003.png | P01 (narrative) | Prior-conflicting split (KEY TEST) |
| C06 | S003.png | P02 (analytical) | Prior-conflicting split, analytical |
| C07 | S004.png | P01 (narrative) | SCE capture test |
| C08 | S004.png | P02 (analytical) | Analytical bypass test |
| C09 | S005.png | P01 (narrative) | Matched-pair control |
| C10 | S005.png | P02 (analytical) | Matched-pair control, analytical |
| C11 | S006.png | P01 (narrative) | Prior-consistent control |
| C12 | S006.png | P02 (analytical) | Prior-consistent control, analytical |

## Gradient Conditions (P01 narrative only)

| Condition | Stimulus | Shift | Trials |
|---|---|---|---|
| (C01) | S001.png | 0° baseline | 10 (shared with core) |
| CG01 | G001.png | +5° | 10 |
| CG02 | S003.png | +10° | 10 (run independently, doubles as C05 replication check) |
| CG03 | G003.png | +15° | 10 |
| CG04 | G004.png | +20° | 10 |
| CG05 | G005.png | +25° | 10 |
| CG06 | G006.png | +30° | 10 |

## Call Counts

| Component | Conditions | Models | Trials | Total |
|---|---|---|---|---|
| Core study | 12 | 5 | 10 | 600 |
| Gradient series | 6 (+ shared baseline) | 5 | 10 | 300 |
| **Total** | | | | **900** |

Estimated cost: $20-45

## Scoring Criteria

**Narrative responses (P01):**
- Color mentioned (binary)
- Color accuracy (binary)
- Direction accuracy, split conditions (binary)
- Capture detected (binary)
- Confabulation detected (binary)
- Difference fabricated, control S001 (binary)

**Analytical responses (P02):**
- Hue estimate accuracy (absolute error in degrees)
- Direction accuracy (binary)

**Gradient responses:**
- Capture rate per step (proportion of trials reporting bus as "yellow"/"warm")
- Detection rate per step (proportion correctly noting cooler/greener bus)
- Breakpoint estimate (50% detection crossing, interpolated)

Ground truth values are Photoshop eyedropper measurements from center of vehicle side panel.
Do not use AI-based pixel sampling. See STIMULUS_SPEC.md for all measured values.
