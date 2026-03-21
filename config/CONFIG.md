# Experiment Configuration
## SCE Color Replication Study
## Last updated: 03-21-2026

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

Passed to each API as image URL. No base64 encoding.

## Experiment Parameters

- **Trials per condition:** 10
- **Temperature (primary study):** Default for each model (1.0 across all, verify Grok)
- **Temperature (follow-up study):** Single model, vary temperature (0.0, 0.5, 1.0, 1.5) to test stochastic effects
- **Max tokens per response:** 500
- **System prompt:** None. Raw model behavior. No persona, no instructions beyond the user prompt.

## Prompts

Two prompts only. Both minimal and unprimed.

| ID | File | Text | Purpose |
|---|---|---|---|
| P01 | P01_narrative.txt | "Describe this scene." | Unprimed. Tests what model volunteers about color. |
| P02 | P02_analytical.txt | "For each object in this image, measure the dominant hue value in degrees on a standard HSV color wheel (0=red, 60=yellow, 120=green)." | Analytical bypass of semantic prior. |

The narrative prompt matches the original study protocol exactly. No color-specific language.
No leading questions. The model must volunteer any color observations unprompted.

## Stimuli

| ID | Description | Bus Hue | Van Hue | Difference | Notes |
|---|---|---|---|---|---|
| S001 | Bus + van, same yellow | 43° | 43° | 0° | Control |
| S002 | Bus warm, van cool | 43° | 53° | 10° | Prior-consistent split |
| S003 | Bus cool, van warm | 53° | 43° | 10° | Prior-conflicting split (KEY) |

| ID | Description | Target Hue | Notes |
|---|---|---|---|
| S004 | Orange banana | ~30° | SCE capture test |
| S005 | Orange carrot | ~30° | Matched-pair control |
| S006 | Yellow banana | ~55° | Prior-consistent control |
| S007 | Cube + fence | ~39° both | White picket fence collocation (stretch) |

## Conditions Matrix

| Condition | Stimulus | Prompt | Tests |
|---|---|---|---|
| C01 | S001 (same yellow) | P01 (narrative) | Control: no conflict, unprimed |
| C02 | S001 (same yellow) | P02 (analytical) | Control: analytical baseline |
| C03 | S002 (bus warm) | P01 (narrative) | Prior-consistent split, unprimed |
| C04 | S002 (bus warm) | P02 (analytical) | Prior-consistent split, analytical |
| C05 | S003 (bus cool) | P01 (narrative) | Prior-conflicting split (KEY TEST) |
| C06 | S003 (bus cool) | P02 (analytical) | Prior-conflicting split, analytical |
| C07 | S004 (orange banana) | P01 (narrative) | Classic SCE capture test |
| C08 | S004 (orange banana) | P02 (analytical) | Analytical bypass test |
| C09 | S005 (orange carrot) | P01 (narrative) | Matched-pair control (no conflict) |
| C10 | S005 (orange carrot) | P02 (analytical) | Matched-pair control, analytical |
| C11 | S006 (yellow banana) | P01 (narrative) | Prior-consistent control |
| C12 | S006 (yellow banana) | P02 (analytical) | Prior-consistent control, analytical |

**Total calls (primary study):** 12 conditions x 5 models x 10 trials = 600
**Estimated cost:** $15-30

## Scoring Criteria

Each response is graded against known ground truth:

**For narrative responses (P01):**
- **Color mentioned:** Did the model mention the color of the target object(s)? (binary)
- **Color accuracy:** If color was mentioned, was it correct? (binary)
- **Direction accuracy (S002/S003):** If warmth comparison was mentioned, was direction correct? (binary)
- **Capture detected:** Did the model report a color consistent with semantic prior rather than pixel reality? (binary)
- **Confabulation detected:** Did the model fabricate a justification for an incorrect report? (binary)
- **Difference fabricated (S001):** Did the model report a color difference where none exists? (binary)

**For analytical responses (P02):**
- **Hue estimate accuracy:** Absolute error in degrees from ground truth.
- **Direction accuracy (S002/S003):** Did the model correctly identify which object has the lower/higher hue? (binary)

Ground truth values in STIMULUS_SPEC.md.
