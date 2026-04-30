# Cross-Vendor Gradient Breakpoint Analysis
## 5 Models, 2 Vendors, 3 Capability Tiers
## Date: 03-21-2026 (analysis); revised 04-30-2026 per audit

---

> **AUDIT NOTE (2026-04-30):** The detection rates below have been re-verified by trial-by-trial reading. The original "strict classifier" had two failure modes confirmed against the raw data: (a) **false positives** from background green words ("yellow bus standing out against green foliage" — "green" referring to trees, not the bus); (b) **false negatives** from cross-sentence references (the bus named in one sentence, green-family color in the next). 7 of 35 cells diverge from the published table. The capability-tier-staggered breakpoint story survives and is cleaner. See `analysis/README.md` for context.

---

## Detection Rates (audited)

| Stim | Shift | Opus (N=5) | Sonnet (N=5) | Haiku (N=5) | Gem Pro (N=4-5) | Gem Flash (N=5) |
|---|---|---|---|---|---|---|
| S001 | +0° (ctrl) | 0% | 0% | 0% | 0% | 0% |
| G001 | +5° | 0% | 0% | 0% | 0% | 0% |
| S003 | +10° | 0% | 0% | 0% | **0%** | 0% |
| G003 | +16° | 0% | 0% | 0% | **0%** | 0% |
| G004 | +21° | 60% | 0% | 0% | **100%** | 40% |
| G005 | +27° | 100% | 100% | **60%** | **100%** | 100% |
| G006 | +31° | 100% | 100% | **100%** | 100% | **100%** |

Cells in **bold** differ from the original published table. Pro at S003/G003 was reported as 25% based on the strict classifier counting "green foliage" references; trial-by-trial reading of all four completed Pro responses at each step finds 0/4 actual detection of green-family color on the bus. Pro G004/G005 corrects upward (every Pro trial uses chartreuse/yellow-green/lime-yellow for the bus). Haiku G005 (60% audited vs 40% published) and Haiku/Flash G006 (both 100% audited vs 80% published) — the cross-sentence references the strict classifier missed all use canonical green-family vocabulary on the bus.

## Breakpoint Estimates (revised)

Approximate hue shift at which detection rate crosses 50%.

| Model | Breakpoint | Vendor | Capability Tier |
|---|---|---|---|
| Gemini 2.5 Pro | ~+18-21° | Google | Flagship |
| Claude Opus 4.6 | ~+18-21° | Anthropic | Flagship |
| Gemini 2.5 Flash | ~+21° | Google | Mid |
| Claude Sonnet 4.6 | ~+24-27° | Anthropic | Mid |
| Claude Haiku 4.5 | ~+27° | Anthropic | Small |

Haiku's range tightens from "+27-31°" to "~+27°" — at +31° Haiku reaches 100% (audited) rather than 80% (published).

## Key Findings (revised)

### 1. Breakpoint correlates with capability tier, not vendor
Gemini Pro and Opus (both flagships) break at the same point (+21°). Gemini Flash and Sonnet (both mid-tier) cluster at +21-27°. Haiku (smallest) is the most captured at every gradient step. Semantic capture strength is a function of model capability tier, not vendor architecture.

### 2. Flagship models have better resolution AND stronger priors
They don't break earlier because they have weaker priors. They break earlier because their perceptual resolution exceeds the prior's pull at a lower threshold. The prior is strong in all models. The resolution to overcome it scales with capability.

### 3. The sigmoid is universal
Every model shows the same shape: flat zero at low shifts, sharp transition, ceiling at high shifts. The curves are parallel, just offset along the hue axis. This suggests the same underlying mechanism across architectures.

### 4. ~~Gemini Pro shows early detection at +10° and +16°~~ → RETRACTED

The published claim that Gemini Pro had 25% detection at +10° and +16° was a parser artifact. Reading the four completed Pro responses at each step, every one describes the bus as "iconic bright yellow" / "vibrant yellow body" — the only "green" words appear in formulaic phrases like *"iconic yellow paint standing out against the lush greenery behind it"* (background trees, not the bus). True detection at those steps is 0/4. The downstream speculation about "different vision integration architecture at Google" or "looser school bus yellow prior" is not supported by the data.

### 5. No model detects a 5° shift
0% across all 25 trials at +5° (H=47°). Universal floor. A 5° hue shift from canonical is below every model's detection threshold under narrative prompting.

### 6. ~~Gemini Flash and Haiku show ceiling effects below 100%~~ → RETRACTED

The claim that Flash and Haiku miss 1/5 each at +31° (suggesting "residual prior pull at extreme visual departures") was a parser artifact. Both reach 100% (5/5) at +31° under correct counting. Every Flash G006 trial uses "lime green" or "yellow-green" for the bus; every Haiku G006 trial uses "lime-green" or "lime/neon green." The "residual ceiling effect" is not a finding — it was a sentence-level proximity false-negative in the strict classifier.

## Methodology Notes

- All trials at T=1.0 (default)
- Prompt: "Describe this scene." (unprimed, no color language)
- ~~Strict classifier: only counts green-family words in sentences mentioning "bus"~~ → **Detection rates above are from trial-by-trial AI-judge reading on 2026-04-30, not from the strict classifier.** The strict classifier had documented false-positive and false-negative failure modes. See `analysis/README.md`.
- Claude models called via API from container. Gemini called from local machine (Google blocks datacenter IPs).
- Gemini 2.5 models are thinking models. thinkingBudget left at default, maxOutputTokens=8000, thinking parts stripped from responses.
- Gemini Pro had 2 x 503 errors (S003 T2, G003 T2) due to rate limiting. N=4 at those steps.

## Raw Data

- results/gradient_5trials_claude.json (Claude: Opus, Sonnet, Haiku)
- results/gemini_gradient_v2_results.json (Gemini: 2.5 Pro, 2.5 Flash)

## What's Next

1. GPT-5.4 family gradient runs (parallel cohort, pending)
2. Visualization: five sigmoid curves on shared axes
3. Verify gradient 9-trial Claude data (`gradient_9trials_claude.json`) per the same audit rubric — preliminary check confirms Haiku G005 is 6/9 not 5/9 and Haiku G006 is 9/9 not 7/9, same Type B (cross-sentence) classifier failure.

---

*Breakpoint is architecture-independent. It scales with capability. The corrected numbers strengthen — not weaken — the central tier-staggered finding.*

*Audit revision: 2026-04-30. Per-trial reading by AI-judge classification protocol; see `analysis/README.md` for methodology context.*
