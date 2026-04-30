# Patch Isolation: Cross-Vendor Analysis
## 8 Models, 3 Vendors, 160 Trials (Corrected "Rectangles" Prompts)
## Date: April 2, 2026 (analysis); revised 04-30-2026 per audit

---

> **AUDIT NOTE (2026-04-30):** Per-trial reading confirms the 40/40 PS04r foundational claim. Three small per-cell adjustments to PS03r detection counts; PS05r holds qualitatively. The "prior is the cause, not perception" headline is the cleanest experiment in the program — the only audit verdict with no narrative revisions.

---

## Experiment

**Question:** Is SCE direction reversal caused by the semantic prior (object identity) or by a perceptual limitation?

**Method:** S003Patch.png extracts the color patches from S003 (bus H=51, van H=41) and places them as rectangles on a black background. No vehicle shapes, no object identity. Same pixels, different context.

**If perceptual:** Models would still fail on patches (the 10-degree difference is below their discrimination threshold).
**If prior-shaped:** Models would succeed on patches (perception is intact; the prior was the problem).

**Stimuli:** S003Patch.png (Left=H51 cooler, Right=H41 warmer)
**Prompts:**
- PS00: "Describe this scene."
- PS03r: "Compare the colors of the two rectangles. Are they the same or different?"
- PS04r: "Carefully analyze the exact hue of each rectangle. Which is warmer, which is cooler?"
- PS05r: "Measure the dominant hue of each rectangle in degrees on a standard HSV color wheel."

**Models:** 8 models across 3 vendors. 5 trials each. 160 total API calls.

---

## Results: PS04r (Explicit Direction Question)

The definitive test. "Which is warmer, which is cooler?"

| Model | Correct direction | Details |
|-------|:-:|---|
| Opus 4.6 | 5/5 | Right "warm orange/amber," left "dark yellow, cooler" |
| Sonnet 4.6 | 5/5 | Left "olive-yellow, hint of green, cooler," right "warm golden-orange" |
| Haiku 4.5 | 5/5 | Left "cooler yellow, greenish undertones," right "warmer, more orange" |
| GPT-5.4 | 5/5 | Right "warmer, more orange/amber," left "cooler, yellow/olive-gold" |
| GPT-5.4-mini | 5/5 | Right "warmer, more orange-gold," left "cooler, yellow-gold" |
| GPT-5.4-nano | 5/5 | Left "cooler, more yellow-gold," right "warmer, more orange" |
| Gemini 2.5 Pro | 5/5 | Right "warmer, orange-yellow, ochre," left "cooler, mustard/greenish" |
| Gemini 2.5 Flash | 5/5 | Left "muted/mustard yellow," right "deep orange, warmer" |

**40/40 correct. Every model. Every trial. Every vendor.** (Audit verified — every PS04r trial gives the correct direction. The single mild anomaly is GPT-5.4-nano T5, which has confused intermediate language but lands on the correct net answer in its closing summary.)

---

## Results: PS05r (Hue Measurement)

| Model | Avg left hue (truth: 51) | Avg right hue (truth: 41) | Direction correct |
|-------|:---:|:---:|:-:|
| Opus 4.6 | 45° | 38° | 5/5 |
| Sonnet 4.6 | 50° | 44° | 5/5 |
| Haiku 4.5 | 60° | 45° | 5/5 |
| GPT-5.4 | 50° | 42° | 5/5 |
| GPT-5.4-mini | 49° | 41° | 5/5 |
| GPT-5.4-nano | 46° | 37° | 4/5 (T1 ties at 40°) |
| Gemini 2.5 Pro | 54° | 40° | 5/5 |
| Gemini 2.5 Flash | 47° | 34° | 5/5 |

**Total: 39/40 direction-correct.** Hue estimates cluster within 2-10° of ground truth — pixel-level perception works fine. (Audit refinement: the original notes "Pro 3/3" and "Flash T5 measured" obscured that all trials produce direction-correct measurements. Per-trial all-N counts shown above.)

---

## Results: PS03r (Detection)

| Model | Detected different |
|-------|:-:|
| Opus 4.6 | 5/5 |
| Sonnet 4.6 | 5/5 |
| Haiku 4.5 | **0/5** |
| GPT-5.4 | **4/5** |
| GPT-5.4-mini | 4/5 |
| GPT-5.4-nano | 5/5 |
| Gemini 2.5 Pro | 5/5 |
| Gemini 2.5 Flash | **4/5** |

Cells in **bold** differ from the original published table. Three small adjustments per audit:
- **Gemini Flash T4** explicitly says "the colors of the two rectangles are **the same**." Captured.
- **GPT-5.4 T5** says "the two rectangles appear to be the same color. The surrounding darkness may make them seem slightly different, but they look like matching yellow-orange shades." Captured.
- **Haiku T1-T5** all say "**the same color**" verbatim. Audit shows 0/5, not 1/5.

Net effect on findings: none. Haiku still stands out as the lone detection failure on PS03r ("Haiku 4.5 is the only model that struggles with detection on the simple comparison question"). The claim was directionally correct; the count was off by one.

Haiku 4.5 is the only model that struggles with detection on the simple comparison question (0/5), yet achieves 5/5 correct on PS04r when explicitly asked about warmth. The comparison framing is insufficient for Haiku to report the difference, but the perceptual discrimination is intact.

---

## The Finding

**Same pixels. Remove the bus shape. Direction corrects. Every model.**

On S003 vehicle images (from CPO experiment and earlier data), these same 8 models:
- Reverse direction (call the cooler bus "warmer") or
- Fail to detect the difference entirely

On S003Patch rectangles with identical color values:
- 40/40 correct direction on PS04r
- Hue measurements within degrees of ground truth on PS05r
- Direction-correct descriptions across all vendors

**SCE direction reversal is prior-shaped, not perceptual.** The 10-degree hue difference is within every model's discrimination capability. Object recognition activates the "school buses are warm yellow" prior, which overrides accurate perception in the vehicle images. Remove the object, the prior deactivates, and accurate perception surfaces.

This is the cleanest finding in the SCE replication program. The audit produced no narrative revisions to this experiment — only three small per-cell PS03r adjustments that don't change the foundational claim.

---

## Prompt Framing Note

An earlier batch used "vehicles" in the PS03/PS04/PS05 prompts while showing rectangles. This run corrected the framing to "rectangles." Results are consistent, suggesting the "vehicles" framing did not activate a semantic prior strong enough to override perception on identity-free patches. The prompt-level semantic activation pathway (top-down) requires more than a word; it requires either visual object identity (bottom-up) or a contextual narrative frame (as shown in the CPO experiment).

The Verbal Label experiment (`verbal_label_*_results.json`) extends this finding: even verbal school-bus framing on identity-free patches does not reactivate the directional shield (60/60 direction-correct in VL1/VL1b across the six strong-SCE models, audited 2026-04-30).

---

*Data: s003patch_rect_anthropic_results.json, s003patch_rect_openai_results.json, s003patch_rect_gemini_results.json*
*Analysis: April 2, 2026. Ted Inoue with Salon research assist (Terry, Opus 4.6). Audit revision: 2026-04-30.*
