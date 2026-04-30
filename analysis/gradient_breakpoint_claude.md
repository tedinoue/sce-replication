# Gradient Breakpoint Analysis — Claude Models
## 5 Trials per condition, T=1.0, P01 "Describe this scene."
## Date: 03-21-2026 (analysis); revised 04-30-2026 per audit

---

> **AUDIT NOTE (2026-04-30):** Detection rates re-verified by trial-by-trial reading. The original "strict classifier" had documented sentence-level proximity false-negative cases — green-family colors mentioned in sentences not containing the word "bus" were missed. Two cells corrected (Haiku G005, Haiku G006). The capability-tier story strengthens. See `analysis/README.md` for context.

---

## Detection Rate Summary (audited)

| Stim | Bus H | Shift | Opus (N=5) | Sonnet (N=5) | Haiku (N=5) |
|---|---|---|---|---|---|
| S001 | 42° | +0° (ctrl) | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| G001 | 47° | +5° | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| S003 | 51° | +10° | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| G003 | 58° | +16° | 0/5 (0%) | 0/5 (0%) | 0/5 (0%) |
| G004 | 63° | +21° | 3/5 (60%) | 0/5 (0%) | 0/5 (0%) |
| G005 | 69° | +27° | 5/5 (100%) | 5/5 (100%) | **3/5 (60%)** |
| G006 | 73° | +31° | 5/5 (100%) | 5/5 (100%) | **5/5 (100%)** |

Cells in **bold** differ from the published table. Haiku G005 was published as 2/5 (40%); audit finds 3/5 (60%) — three trials use explicit "lime-green" / "yellow-green" descriptors for the bus, the third in a sentence that didn't contain the literal word "bus" (the strict classifier missed it). Haiku G006 was published as 4/5 (80%); audit finds 5/5 — every trial uses lime-green or lime/neon-green.

## Key Findings (revised)

### 1. All three models are fully captured through +16° (H=58°)
Zero detection across 15 trials at +16°. The bus is visibly yellow-green to a human at this point. All models report "yellow."

### 2. Opus breaks first, at +21° (H=63°)
The only model showing any detection below +27°. 3/5 trials use "yellow-green" to describe the bus. The remaining 2/5 still say "yellow." This is the transition zone.

### 3. Sonnet breaks clean at +27° (H=69°)
Zero detection at +21°, 100% at +27°. No ambiguity zone. The prior holds completely and then releases completely in one 6° step.

### 4. Haiku reaches ceiling at +31° — same as Sonnet and Opus

Original framing ("Haiku still calls it 'yellow' in 1/5 trials at +31°") was based on the published 4/5 score. Audit shows 5/5 — Haiku reaches ceiling at +31°, the same as Sonnet and Opus. Haiku is still the most captured at lower shifts (still 60% at +27° vs 100% for Opus and Sonnet), but the "Haiku never reaches ceiling, residual prior pull at +31°" framing is not supported by the corrected count.

### 5. Breakpoint correlates with model capability
Opus (most capable) detects earliest (+21°). Sonnet (mid) detects at +27°. Haiku (smallest) is the most captured but reaches ceiling at +31°. The breakpoint estimate for Haiku tightens from "+27-31°" to "~+27°" — at +31° all three Anthropic models hit 100%.

This suggests perceptual resolution and prior strength both increase with capability, but resolution increases faster, giving larger models a net earlier breakpoint.

## Classifier Notes

The strict classifier counted green-family color words (yellow-green, lime-green, green, chartreuse, neon-green) when they appeared in sentences that explicitly mention the bus or school bus. This eliminated false positives from background descriptions ("green trees," "green lawn") but introduced false negatives when the model named the bus in one sentence and the green-family color in the next. Audit by trial-by-trial reading corrects two Haiku cells.

The 2026-04-30 audit applied AI-judge classification (read each trial in full, score substantively) rather than the strict classifier. See `analysis/README.md`.

## Raw Data

All raw API responses are in:
- results/trial1_complete_claude.json (trial 1, all stimuli, P01+P02)
- results/gradient_5trials_claude.json (trials 1-5, gradient stimuli only)

---

*Analysis by the Salon. Audit revision: 2026-04-30. Per-trial reading by AI-judge classification protocol.*
