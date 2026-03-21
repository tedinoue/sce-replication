# Gradient Breakpoint Analysis — Claude Models
## 5 Trials per condition, T=1.0, P01 "Describe this scene."
## Date: 03-21-2026
## Classifier: Strict (bus-sentence only, excludes background tree/lawn mentions)

---

## Detection Rate Summary

| Stim | Bus H | Shift | Opus (N=5) | Sonnet (N=5) | Haiku (N=5) |
|---|---|---|---|---|---|
| S001 | 42° | +0° (ctrl) | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| G001 | 47° | +5° | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| S003 | 51° | +10° | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| G003 | 58° | +16° | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| G004 | 63° | +21° | 3/5 (60%) | 0/5 (0%) | 0/5 (0%) |
| G005 | 69° | +27° | 5/5 (100%) | 5/5 (100%) | 2/5 (40%) |
| G006 | 73° | +31° | 5/5 (100%) | 5/5 (100%) | 4/5 (80%) |

## Key Findings

### 1. All three models are fully captured through +16° (H=58°)
Zero detection across 15 trials at +16°. The bus is visibly yellow-green to a human at this point. All models report "yellow."

### 2. Opus breaks first, at +21° (H=63°)
The only model showing any detection below +27°. 3/5 trials use "yellow-green" to describe the bus. The remaining 2/5 still say "yellow." This is the transition zone.

### 3. Sonnet breaks clean at +27° (H=69°)
Zero detection at +21°, 100% at +27°. No ambiguity zone. The prior holds completely and then releases completely in one 6° step.

### 4. Haiku is the most captured
Still only 40% detection at +27° (where Opus and Sonnet are at 100%). At +31° (H=73°, clearly chartreuse/lime), Haiku still calls it "yellow" in 1/5 trials. Smaller models hold the prior harder.

### 5. Breakpoint correlates with model capability
Opus (most capable) detects earliest. Sonnet (mid) detects at +27°. Haiku (smallest) is still partially captured at +31°. This suggests that perceptual resolution and prior strength both increase with capability, but resolution increases faster, giving larger models a net earlier breakpoint.

## Classifier Notes

The strict classifier only counts green-family color words (yellow-green, lime-green, green, chartreuse, neon-green) when they appear in sentences that explicitly mention the bus or school bus. This eliminates false positives from background descriptions ("green trees," "green lawn"). The loose classifier used in initial analysis showed 20-40% false positive rates on the S001 control; the strict classifier shows 0%.

Edge cases requiring human review:
- "golden-yellow" classified as captured (no detection). Arguably a hedge.
- Cases where the model describes both vehicles and mentions they are "similar" but uses subtly different adjectives for each.

## Raw Data

All raw API responses are in:
- results/trial1_complete_claude.json (trial 1, all stimuli, P01+P02)
- results/gradient_5trials_claude.json (trials 1-5, gradient stimuli only)

Every response is the complete model output. Human review of the raw text is recommended for the transition zone (G004-G005).

---

*Analysis by the Salon. Classifier and methodology open to revision.*
