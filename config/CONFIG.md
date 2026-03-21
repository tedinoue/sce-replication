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

Passed to each API as image URL. No base64 encoding needed.

## Experiment Parameters

- **Trials per condition:** 10
- **Temperature (primary study):** Default for each model (1.0 across all, verify Grok)
- **Temperature (follow-up study):** 0.0 across all models (deterministic baseline)
- **Max tokens per response:** 500 (sufficient for color description, prevents rambling)
- **System prompt:** None. Raw model behavior. No persona, no instructions beyond the user prompt.

## Conditions Matrix

| Condition | Stimulus | Prompt Type | Tests |
|---|---|---|---|
| C01 | S001 (bus+van, same yellow) | Narrative describe | Control: no conflict |
| C02 | S001 (bus+van, same yellow) | Analytical measure | Control: analytical baseline |
| C03 | S002 (bus standard, van cooler) | Narrative describe | Prior-consistent split |
| C04 | S002 (bus standard, van cooler) | Analytical measure | Prior-consistent split, analytical |
| C05 | S003 (bus cooler, van standard) | Narrative describe | Prior-conflicting split (KEY TEST) |
| C06 | S003 (bus cooler, van standard) | Analytical measure | Prior-conflicting split, analytical |
| C07 | S004 (orange banana) | Narrative describe | Classic SCE capture test |
| C08 | S004 (orange banana) | Analytical measure | Analytical bypass test |
| C09 | S005 (orange carrot) | Narrative describe | Matched-pair control (no conflict) |
| C10 | S005 (orange carrot) | Analytical measure | Matched-pair control, analytical |
| C11 | S006 (yellow banana) | Narrative describe | Prior-consistent control |
| C12 | S006 (yellow banana) | Analytical measure | Prior-consistent control, analytical |

**Total calls (primary study):** 12 conditions x 5 models x 10 trials = 600
**Estimated cost:** $15-30 (multimodal calls, varies by model)

## Scoring

Each response is graded by the harness against known ground truth:
- **Color accuracy:** Did the model report the actual color? (binary)
- **Direction accuracy (split conditions):** Did the model correctly identify which object is warmer/cooler? (binary)
- **Capture detected:** Did the model report a color consistent with semantic prior rather than pixel reality? (binary)
- **Confabulation detected:** Did the model fabricate a justification for an incorrect report? (binary)
- **Analytical bypass success:** Did the analytical prompt produce a more accurate result than narrative? (binary)

Ground truth values documented in STIMULUS_SPEC.md.
