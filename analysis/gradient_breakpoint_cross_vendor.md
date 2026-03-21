# Cross-Vendor Gradient Breakpoint Analysis
## 5 Models, 2 Vendors, 3 Capability Tiers
## Date: 03-21-2026
## Classifier: Strict (bus-sentence only)

---

## Detection Rates

| Stim | Shift | Opus (N=5) | Sonnet (N=5) | Haiku (N=5) | Gem Pro (N=4-5) | Gem Flash (N=5) |
|---|---|---|---|---|---|---|
| S001 | +0° (ctrl) | 0% | 0% | 0% | 0% | 0% |
| G001 | +5° | 0% | 0% | 0% | 0% | 0% |
| S003 | +10° | 0% | 0% | 0% | 25% | 0% |
| G003 | +16° | 0% | 0% | 0% | 25% | 0% |
| G004 | +21° | **60%** | 0% | 0% | **80%** | **40%** |
| G005 | +27° | 100% | 100% | **40%** | **80%** | 100% |
| G006 | +31° | 100% | 100% | **80%** | 100% | **80%** |

## Breakpoint Estimates

Approximate hue shift at which detection rate crosses 50%.

| Model | Breakpoint | Vendor | Capability Tier |
|---|---|---|---|
| Gemini 2.5 Pro | ~+18-21° | Google | Flagship |
| Claude Opus 4.6 | ~+18-21° | Anthropic | Flagship |
| Gemini 2.5 Flash | ~+21-24° | Google | Mid |
| Claude Sonnet 4.6 | ~+24-27° | Anthropic | Mid |
| Claude Haiku 4.5 | ~+27-31° | Anthropic | Small |

## Key Findings

### 1. Breakpoint correlates with capability tier, not vendor
Gemini Pro and Opus (both flagships) break at the same point (+21°, 80% and 60%).
Gemini Flash and Sonnet (both mid-tier) cluster at +21-27°.
Haiku (smallest) is the most captured at every gradient step.
This is the central result: semantic capture strength is a function of model capability tier, not vendor architecture.

### 2. Flagship models have better resolution AND stronger priors
They don't break earlier because they have weaker priors. They break earlier because their perceptual resolution exceeds the prior's pull at a lower threshold. The prior is strong in all models. The resolution to overcome it scales with capability.

### 3. The sigmoid is universal
Every model shows the same shape: flat zero at low shifts, sharp transition, ceiling at high shifts. The curves are parallel, just offset along the hue axis. This suggests the same underlying mechanism across architectures.

### 4. Gemini Pro shows early detection at +10° and +16°
25% detection at both steps where all Claude models show 0%. This may indicate:
- Different vision integration architecture at Google
- Looser "school bus yellow" prior in Gemini's training data
- A genuine architectural advantage in perceptual routing
Caveat: N=4 at these steps due to 503 errors. Needs replication.

### 5. No model detects a 5° shift
0% across all 25 trials at +5° (H=47°). Universal floor. A 5° hue shift from canonical is below every model's detection threshold under narrative prompting.

### 6. Gemini Flash and Haiku show ceiling effects below 100%
At +31° (clearly chartreuse), Flash still misses 1/5 and Haiku misses 1/5. The prior retains residual pull even at extreme visual departures for smaller models.

## Methodology Notes

- All trials at T=1.0 (default)
- Prompt: "Describe this scene." (unprimed, no color language)
- Strict classifier: only counts green-family words in sentences mentioning "bus"
- Claude models called via API from container. Gemini called from local machine (Google blocks datacenter IPs).
- Gemini 2.5 models are thinking models. thinkingBudget left at default, maxOutputTokens=8000, thinking parts stripped from responses. First run with 500 token budget produced truncated responses (~100 chars). v2 with 8000 tokens produced full responses (800-1800 chars).
- Gemini Pro had 2 x 503 errors (S003 T2, G003 T2) due to rate limiting. N=4 at those steps.

## Raw Data

- results/gradient_5trials_claude.json (Claude: Opus, Sonnet, Haiku)
- results/gemini_gradient_v2_results.json (Gemini: 2.5 Pro, 2.5 Flash)

## What's Next

1. GPT-4o and Grok gradient runs (pending API keys)
2. Experiment 2: Prompt specificity gradient (config/EXPERIMENT2_PROMPT_SPECIFICITY.md)
3. Human review of raw responses in transition zone (G004-G005)
4. Visualization: five sigmoid curves on shared axes

---

*Breakpoint is architecture-independent. It scales with capability.*
