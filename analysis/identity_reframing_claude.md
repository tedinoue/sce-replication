# Identity Reframing Experiment — CORRECTED
## Preliminary exploration, not a definitive study
## S003 (Bus H=51°, Van H=41°)
## Date: 03-21-2026

---

## STATUS: PRELIMINARY

These are quick exploratory tests of a hypothesis, N=3 per cell, single stimulus.
The findings below are directional signals worth pursuing, not conclusions.
A proper study would need N=10+, multiple stimuli, and cross-vendor replication.

---

## CORRECTION FROM INITIAL ANALYSIS

The first version of this analysis contained a confound. The "control" prompt in the
reframing experiment was "Describe the colors of these two vehicles. Which is warmer in
tone?" — which is functionally a PS04-level prompt (analytical, forces directional judgment).
This made the control condition much stronger than the actual PS00 baseline ("Describe this
scene."), inflating the apparent performance and obscuring the reframe's real contribution.

### What we got wrong:
The initial report claimed the hippie reframe was a standalone intervention. It is not.

### What we found when we fixed it:
At PS00-level prompting ("Describe this scene." with or without reframe), no model
volunteers color comparisons. Reframe or no reframe, the direction question never arises,
so there's nothing for the reframe to improve. 0/3 across all conditions, all models.

---

## CORRECTED RESULTS

### Test 1: PS00-level prompts (no forced comparison)

| Condition | Prompt | Opus | Sonnet | Haiku |
|---|---|---|---|---|
| Baseline | "Describe this scene." | 0/3 | 0/3 | 0/3 |
| Hippie reframe | "[hippie framing] Describe this scene." | 0/3 | 0/3 | 0/3 |
| Neutral strip | "[neutral framing] Describe this scene." | 0/3 | 0/3 | 0/3 |

No effect. Models don't volunteer color comparisons at PS00, so the reframe has nothing to act on.

### Test 2: PS04-level prompts (forced directional comparison)

| Condition | Prompt | Opus | Sonnet | Haiku |
|---|---|---|---|---|
| With "school bus" label + "which is warmer?" | "Describe the colors of these two vehicles. Which is warmer in tone?" | 3/3 | 0/3 | 0/3 |
| Hippie reframe + "which is warmer?" | "[hippie framing] Which vehicle is warmer in tone?" | 2/3 | 2/3 | 2/3 |

The reframe effect only appears when combined with a forced directional judgment.

---

## WHAT THIS ACTUALLY SHOWS

### 1. The identity reframe is a modifier, not an independent intervention
It doesn't change what the model sees or volunteers. It changes how the model answers
a directional question when one is asked. No directional question, no effect.

### 2. Combined with directional prompt, the reframe helps Sonnet and Haiku
Sonnet: 0/3 (baseline+PS04) -> 2/3 (hippie+PS04). Haiku: 0/3 -> 2/3.
This is still a real and interesting signal. The hippie framing loosened the directional
prior for models where analytical demand alone (PS04) couldn't break through.

### 3. The mechanism is label-dependent direction shaping
When forced to say "which is warmer," the model's answer is shaped by what it thinks
the object IS. "School bus" activates "warm, golden, amber." "Hippie's converted bus"
carries no canonical warmth. The prior loses its anchor on the directional judgment.

### 4. BUT: we can't separate the reframe from the prompt confound cleanly
The hippie condition included both the identity reframe AND the "which is warmer" question.
To fully isolate the reframe effect, we would need:
- PS04 with standard "school bus" identification (existing data: Opus 3/3, Sonnet 0/3, Haiku 0/3)
- PS04 with hippie reframe (partially tested: Opus 2/3, Sonnet 2/3, Haiku 2/3)
- PS04 with neutral label strip (not cleanly tested at PS04 level)

## FUTURE WORK

### Multi-turn priming (Ted's idea, not yet tested)
Build a conversational context about converted buses and their wild paint jobs over
several turns before showing the image. This would construct a replacement prior
("buses come in all colors") rather than just removing the existing one. Predicted
to be stronger than single-turn reframe.

### Clean factorial design needed
Cross prompt level (PS00-PS05) with identity condition (standard, hippie, neutral)
for a full 6x3 matrix. That's 18 cells. At N=5 with 3 models = 270 calls. ~$3.

## Raw Data
- results/reframe_identity_claude.json (original PS04-level confounded experiment)
- results/reframe_identity_clean_claude.json (PS00-level clean comparison)
- results/specificity_s003_claude.json (PS00-PS05 baseline data)

---

*The reframe works, but only as a modifier on forced directional judgments. Not standalone.
These are preliminary explorations, not definitive studies. N=3, single stimulus, single vendor.*
