# Prompt Specificity Analysis — Claude Models
## S003 (Bus H=51°, Van H=41°), 6 prompt levels, 3 trials each, T=1.0
## Date: 03-21-2026 (analysis); revised 04-30-2026 per audit

---

> **AUDIT NOTE (2026-04-30):** Per-trial codes have been re-verified by trial-by-trial reading. The original codes had errors in ~2/3 of cells in PS00/PS02/PS05 and ~17% of cells in PS03/PS04, primarily because detected-without-explicit-direction trials defaulted to `S` (same color) rather than `D-`. Headline below reflects the audited values. See `analysis/README.md` for context.

---

## Scoring Key

- **D✓** = Detected difference AND correct direction (van warmer, bus cooler)
- **D✗** = Detected difference, WRONG direction (bus called warmer — directional shield)
- **D-** = Detected difference, no directional claim
- **S** = Said same color (full capture)
- **--** = No color mention

## Per-Trial Results (audited)

| Prompt | Level | Opus T1-T3 | Sonnet T1-T3 | Haiku T1-T3 |
|---|---|---|---|---|
| PS00 | Describe this scene | -- -- D✗ | S D✗ D✗ | -- -- -- |
| PS01 | Describe the vehicles | -- D- -- | S S S | S S S |
| PS02 | Describe the colors | **D✓ D✓ D✓** | S D- D✗ | S S S |
| PS03 | Compare: same or different? | **D✓ D-/D✗ D✓** | D- D✗ D✗ | S S S |
| PS04 | Analyze hue: warmer/cooler? | D✓ D✓ D✓ | D✗ D✗ D✗ | **D✓ D✗ D✗** |
| PS05 | Measure hue in degrees | **D✓ D✓ D✓** | **D✓ D✗ D✗** | **S D✓ D✓** |

(Cells in **bold** differ from the original published table.)

## Correct Direction Rate (D✓ / Total)

| Prompt | Description | Opus | Sonnet | Haiku |
|---|---|---|---|---|
| PS00 | Describe this scene | 0/3 | 0/3 | 0/3 |
| PS01 | Describe the vehicles | 0/3 | 0/3 | 0/3 |
| PS02 | Describe the colors | **3/3** | 0/3 | 0/3 |
| PS03 | Compare: same or different? | **2/3** | 0/3 | 0/3 |
| PS04 | Analyze hue: warmer/cooler? | **3/3** | 0/3 | **1/3** |
| PS05 | Measure hue in degrees | **3/3** | 1/3 | **2/3** |

## Key Findings (revised)

### 1. Opus achieves direction-correct breakthrough at PS02 — earlier than the original analysis credited

The original headline ("zero correct direction through PS03 across all models") is wrong for Opus. **Opus is 3/3 D✓ at PS02 ("describe the colors")** — every PS02 trial explicitly identifies the van as warmer/more orange than the bus. The published 0/3 rating at PS02 was a coding error: detected-difference trials defaulted to D✗ without verifying direction.

### 2. ~~PS02 activates the directional shield, making Opus WORSE~~ → RETRACTED for Opus

The original "PS02 makes Opus worse" claim was based on the incorrect 0/3 score. Audit confirms 3/3 direction-correct. PS02 does NOT activate a directional shield in Opus; it activates the same correct directional reasoning Opus shows at PS04. The shield is universal in non-Opus models, not in Opus.

### 3. PS03 ("same or different?") is partial-shield, not universal

Audit: Opus 2/3 D✓ at PS03. Sonnet, Haiku still 0/3. The shield holds for the smaller Anthropic models but Opus breaks it in 2/3 of trials. Combined with the CPO experiment (Opus 2/5 D✓ on the same S003 PS03 control), Opus achieves 4/8 = 50% direction-correct on PS03 across the two experiments.

### 4. Opus stands alone — starting at PS02

"Carefully analyze the exact hue. Which is warmer, which is cooler?" produces 3/3 correct from Opus at PS04 (matches published). But the audit shows Opus is also 3/3 at PS02 and 2/3 at PS03 — direction breakthrough does not require explicit warm/cool vocabulary.

Sonnet and Haiku remain at 0/3 across PS02-PS04 (with Haiku gaining 1/3 at PS04 in audit, T1 was misclassified as S in the original).

### 5. PS05 (measurement) — Opus actually 3/3, not 2/3

Audit corrects Opus PS05 from 2/3 D✓ to 3/3 D✓. The published "PS05 worse than PS04 for Opus" framing is misleading; both prompt levels produce 3/3 direction-correct trials. Sonnet PS05 has multiple per-trial swaps in audit; aggregate count is unchanged at 1/3.

Haiku PS05 was published as 0/3 with codes (-- D✗ D✗); audit finds (S D✓ D✓), giving 2/3 D✓. **At the most analytically demanding prompt (measure hue in degrees), Haiku does break direction-correct in 2/3 trials.** This contradicts the "Haiku is immune to all prompts" framing.

### 6. Haiku is near-immune, not fully immune

Combined audited counts: Haiku 0+0+0+0+1+2 = 3/18 D✓ across all prompt levels (was published as 0/18). Still extreme; Haiku's prior is impervious to most prompt interventions but PS04 T1 and PS05 T2/T3 produce direction-correct judgments. "Near-immune" is the right framing.

## Theoretical Implications (revised)

The two-level model of SCE survives:
- **Level 1: Detection.** Responds to prompt specificity. PS02 breaks detection for most models.
- **Level 2: Direction.** Responds to prompt specificity for Opus only. The shield is genuinely universal for Sonnet and (mostly) Haiku.

Opus's PS02-level direction breakthrough is the cleanest result in this experiment and the strongest evidence that Opus's perceptual reasoning differs qualitatively from the other Anthropic models.

The original "PS04 is the only prompt that breaks through, and only for Opus" framing is too narrow. **The corrected framing: "Opus breaks through starting at PS02; non-Opus models break only at PS04 (Haiku 1/3) or rarely at PS05 (Sonnet 1/3, Haiku 2/3)."**

## Raw Data
results/specificity_s003_claude.json

---

*Detection is easy. Direction is the hard problem — and Opus solves it earlier than the original analysis credited.*

*Audit revision: 2026-04-30. Per-trial reading by AI-judge classification protocol; see `analysis/README.md` for methodology context.*
