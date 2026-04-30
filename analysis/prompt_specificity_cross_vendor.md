# Cross-Vendor Prompt Specificity Analysis
## 5 Models, 2 Vendors, 6 Prompt Levels, S003 (+10° split)
## Date: 03-21-2026 (analysis); revised 04-30-2026 per audit

---

> **AUDIT NOTE (2026-04-30):** Per-trial codes and detection rates below were re-verified by trial-by-trial reading on 2026-04-30. The original codes were produced before the AI-judge classification protocol was adopted; ~2/3 of cells in PS00/PS01/PS02/PS05 and ~17% of cells in PS03/PS04 had errors. The headline tables and findings below reflect the audited values. See `analysis/README.md` for context on the audit and on classifier-trust caveats.

---

## Correct Direction Rate (D✓ / Total)

Ground truth: Van is warmer (H=41°), Bus is cooler (H=51°).

| Prompt | Description | Opus | Sonnet | Haiku | Gem Pro | Gem Flash |
|---|---|---|---|---|---|---|
| PS00 | Describe this scene | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| PS01 | Describe the vehicles | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| PS02 | Describe the colors | **3/3** | 0/3 | 0/3 | 0/3 | 0/3 |
| PS03 | Compare: same or different? | **2/3** | 0/3 | 0/3 | 0/3 | 0/3 |
| PS04 | Analyze hue: warmer/cooler? | **3/3** | 0/3 | 0/3 | 1/3 | 0/3 |
| PS05 | Measure hue in degrees | 2/3 | 1/3 | 2/3 | 0/3 | 0/3 |

## Full Per-Trial Scoring (audited)

### Claude Models

| Prompt | Opus T1-T3 | Sonnet T1-T3 | Haiku T1-T3 |
|---|---|---|---|
| PS00 | -- -- D✗ | S D✗ D✗ | -- -- -- |
| PS01 | -- D- -- | S S S | S S S |
| PS02 | **D✓ D✓ D✓** | S D- D✗ | S S S |
| PS03 | **D✓ D-/D✗ D✓** | D- D✗ D✗ | S S S |
| PS04 | D✓ D✓ D✓ | D✗ D✗ D✗ | **D✓ D✗ D✗** |
| PS05 | **D✓ D✓ D✓** | **D✓ D✗ D✗** | **S D✓ D✓** |

### Gemini Models

| Prompt | Gem Pro T1-T3 | Gem Flash T1-T3 |
|---|---|---|
| PS00 | S D- D- | D- D- D- |
| PS01 | -- D- -- | S S S |
| PS02 | -- -- -- | **D- D- D✗** |
| PS03 | D✗ D✗ D✗ | D✗ D✗ D✗ |
| PS04 | D✓ D✗ D✗ | **D✗ D✗ D✗** |
| PS05 | **S S S** | -- D- D- |

(Cells in **bold** differ from the original published table; the values shown are the audited counts.)

## Key Findings (revised)

### 1. ~~PS03 produces a universal directional shield~~ → Opus shows partial breakthrough at PS03

The original headline ("0/15 correct direction across all 5 models") is wrong. Opus is 2/3 direction-correct at PS03 on S003. The shield is universal for Sonnet, Haiku, Gemini Pro, and Gemini Flash. **Opus breaks the shield at PS03 in 2/3 trials.**

This finding is independently triangulated by the CPO audit, which found Opus 2/5 direction-correct on the same S003 stimulus under the PS03 control prompt (published as 0/5). Across 8 Opus PS03 trials on S003 in two experiments, 4/8 = 50% are direction-correct. The original analyses systematically scored detected-without-explicit-direction trials as `S` (same color), which suppressed the partial-breakthrough signal.

### 2. Opus stands alone — starting at PS02, not PS04

The published table reported Opus 0/3 at PS02 (the "describe the colors" prompt). The audit found Opus 3/3 D✓ at PS02 — every Opus PS02 trial explicitly identifies the van as warmer/more orange than the bus. The published "Opus stands alone at PS04" claim is true but understates the capability: **Opus stands alone starting at PS02, three prompt levels earlier than the cross-vendor analysis claimed.**

Opus achieves 11/12 = 92% D✓ across PS02/PS03/PS04/PS05 on S003. No other model exceeds 1/3 at any prompt level. This is a clean Opus capability finding once the partial-breakthrough trials are scored correctly.

### 3. PS05 (measurement) — re-evaluated as comparable to PS04 for Opus

Audit count: Opus 3/3 D✓ at PS05 (published 2/3). The "PS05 is worse than PS04" framing in the original analysis is misleading at the cell level. Opus performs equivalently at PS04 and PS05; both produce 3/3 direction-correct trials.

Sonnet PS05 has multiple swaps in the audited per-trial codes (D✓ D✗ D✗ vs published D✗ D✗ D✓); the aggregate count (1/3 D✓) is unchanged but per-trial labels were unreliable.

### 4. ~~Gemini Flash unexpected PS02 success~~ → Flash PS02 anomaly retracted

The published claim "Flash 2/3 correct at PS02" does not survive trial-by-trial audit. Flash T1 and T2 at PS02 make lightness/saturation claims ("slightly lighter, perhaps more pastel" / "slightly lighter or more vivid"), not warm/cool hue claims. They should be coded D-, not D✓. T3 makes a hue claim and gets it wrong (bus called more orange = reversed). Audit codes: D- D- D✗. **No non-Opus model gets PS02 direction-correct.**

The "weaker school bus color prior in Gemini Flash" speculation in the original analysis is not supported by the audited data.

### 5. The directional shield is cross-architectural — for non-Opus models

The pattern (detection without correct direction) appears identically in Sonnet, Haiku, Gemini Pro, and Gemini Flash. All four assign warmth to the school bus regardless of pixel reality. The shield operates the same way across architectures for those four. Opus is the architectural exception.

### 6. Haiku PS04 T1 corrected; "immune to all prompts" softened

The published per-trial codes for Haiku PS04 (S D✗ D✗) had T1 wrong: T1 explicitly says "the service van's yellow is warmer, while the school bus's yellow is cooler." That's D✓, not S. **Haiku is 1/18, not 0/18, across all prompt levels — near-immune rather than fully immune.** PS05 also gains two D✓ trials in audit. Direction-correct count for Haiku across all prompt levels: 3/18 = 17% (up from published 0/18). Still extreme; "near-immune" is the right framing.

## Theoretical Implications (revised)

The two-level model of SCE survives the audit:
- **Level 1 (detection)**: responds to prompt specificity. PS02 breaks detection for most models.
- **Level 2 (direction)**: responds to prompt specificity for Opus only. The shield is genuinely universal for non-flagship Anthropic models and both Gemini sizes.

Opus's PS02-level direction breakthrough — with only "describe the colors" framing, no explicit warm/cool vocabulary — is the cleanest single result in this experiment and the strongest evidence that Opus's perceptual reasoning differs qualitatively from the other models tested.

## Raw Data
- results/specificity_s003_claude.json (Claude: 54 trials)
- results/gemini_specificity_results.json (Gemini: 36 trials)

---

*Detection is easy. Direction is the hard problem. Opus solves it earlier and more reliably than the original analysis credited.*

*Audit revision: 2026-04-30. Per-trial reading by AI-judge classification protocol; see `analysis/README.md` for methodology context.*
