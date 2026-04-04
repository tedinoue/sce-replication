# Patch Discrimination Threshold (PDT) Experiment
## Measuring baseline hue discrimination on identity-free stimuli
*Ted Inoue and Terry (Salon) | April 3-4, 2026*

---

## Purpose

The SCE (Semantic Coherence Enforcement) experiments showed that AI models reverse the direction of hue comparison when object identity is present (e.g., school bus vs. van), but perform perfectly on isolated color patches at a 10-degree hue shift. The Patch Discrimination Threshold experiment asks: what is the minimum hue difference AI models can reliably detect on identity-free stimuli?

Knowing this threshold allows us to quantify the **semantic capture window**: the gap between what the system CAN discriminate (patch threshold) and where it DOES discriminate on vehicles (gradient breakpoint). Everything in that gap is prior-caused distortion.

## Stimuli

Programmatically generated (Python PIL). 256x256 black canvas, two 64x64 solid-color squares, separated by a 64-pixel gap. No object identity, no texture, no gradients.

Reference color: H=42, S=85%, V=80% (RGB 204, 152, 31)

| Stimulus | Left square | Right square | Shift | Ground truth |
|----------|-----------|-------------|-------|-------------|
| PDT-00 | H=42 | H=42 | 0 | Identical (control) |
| PDT-03 | H=45 | H=42 | +3 | Left is cooler |
| PDT-04 | H=42 | H=45 | +3 | Right is cooler |
| PDT-06 | H=48 | H=42 | +6 | Left is cooler |
| PDT-07 | H=42 | H=48 | +6 | Right is cooler |
| PDT-09 | H=51 | H=42 | +9 | Left is cooler |
| PDT-10 | H=42 | H=51 | +9 | Right is cooler |

Higher H values shift toward green (cooler). The +9 stimuli match the approximate shift used in the original S003Patch experiment that produced the 40/40 correct result across all models.

**Why computed stimuli:** Threshold measurement requires exact pixel values. The generation script IS the specification. Verified in Photoshop: PDT-00 measures H=42 exactly, PDT-07 measures H=48 exactly.

**Why 64px separation:** Eliminates edge-comparison advantage. The original S003Patch stimuli also used separated patches (not adjacent), so this design maintains comparability. The separation forces absolute color judgment rather than relative boundary comparison.

## Models tested

| Model | Label | Vendor |
|-------|-------|--------|
| Claude Opus 4.6 | OPUS46 | Anthropic |
| Claude Sonnet 4.6 | SONNET46 | Anthropic |
| Claude Haiku 4.5 | HAIKU45 | Anthropic |
| GPT-5.4 | GPT54 | OpenAI |
| GPT-5.4-mini | GPT54MINI | OpenAI |
| GPT-5.4-nano | GPT54NANO | OpenAI |
| Gemini 2.5 Pro | GEMINI_25_PRO | Google |
| Gemini 2.5 Flash | GEMINI_25_FLASH | Google |

## Experiments

Three experiments were run sequentially, each informed by findings from the previous.

### Experiment 1: PDT v1 (PS04r, forced choice)

**Prompt:** "Carefully analyze the exact hue of each rectangle. Which is warmer, which is cooler?"

**Stimuli:** PDT-00 through PDT-07 (5 stimuli, no +9)

**Trials:** 5 per model per stimulus. Total: 200 API calls.

**Result:** The forced-choice prompt ("which is warmer, which is cooler?") presupposes a difference exists. Models that could not perceive a difference fabricated one rather than reporting "same." This contaminated the detection data. Key finding: the prompt structure itself induces confabulation on perceptual tasks, analogous to forced-choice response bias in human psychophysics.

**Result files:** `results/pdt_v1_*_results.json`

### Experiment 2: PDT v2 (PS03r, open question)

**Prompt:** "Compare the colors of the two rectangles. Are they the same or different?"

**Stimuli:** PDT-00 through PDT-10 (7 stimuli, including +9 positive control)

**Trials:** 5 per model per stimulus. Total: 280 API calls.

**Results:**

| Model | Vendor | Control (0 deg) | +3 detect | +3 dir | +6 detect | +6 dir | +9 detect | +9 dir |
|-------|--------|----------------|-----------|--------|-----------|--------|-----------|--------|
| Opus 4.6 * | Anthropic | 0/5 (5F) | 10/10 | 9/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| Sonnet 4.6 | Anthropic | 5/5 | 0/10 | - | 0/10 | - | 5/10 | 3/5 |
| Haiku 4.5 | Anthropic | 5/5 | 5/10 | 0/5 | 10/10 | 7/10 | 10/10 | 10/10 |
| GPT-5.4 | OpenAI | 5/5 | 0/10 | - | 0/10 | - | 10/10 | 10/10 |
| GPT-5.4-mini | OpenAI | 5/5 | 4/10 | 1/4 | 2/10 | 1/2 | 9/10 | 4/9 |
| GPT-5.4-nano * | OpenAI | 0/5 (5F) | 9/10 | 1/9 | 6/10 | 1/6 | 9/10 | 0/9 |
| Gemini Pro | Google | 5/5 | 0/10 | - | 10/10 | 8/10 | 10/10 | 10/10 |
| Gemini Flash | Google | 5/5 | 4/10 | 2/4 | 10/10 | 8/10 | 10/10 | 10/10 |

\* **Contaminated data.** Opus 4.6 and GPT-5.4-nano fabricate differences on identical control patches. Their detection rates are inflated and unreliable.

**Key:**
- **Control:** Correctly reported "same" on identical patches. F = fabricated a difference.
- **Detect:** Reported "different" out of 10 trials (5 left-shifted + 5 right-shifted per shift level).
- **Dir:** Correctly identified which rectangle was cooler, of those that detected a difference.

**Result files:** `results/pdt_v2_*_results.json`

### Experiment 3: Opus Control Probe

Opus fabricated differences on identical patches in both v1 and v2. This experiment tested whether the fabrication is prompt-driven (modifiable by instruction) or architectural (invariant).

**Stimulus:** PDT-00 only (identical patches)

**Model:** Opus 4.6 only

**Prompts:** Five framings, from neutral to explicitly permitting "same":

| Prompt | Text | Same | Different |
|--------|------|------|-----------|
| PC01 | "Are they the same or different?" | 0/5 | 5/5 |
| PC02 | "Same or different? If different, describe both colors." | 0/5 | 5/5 |
| PC03 | "Are they the exact same color, or is there any difference?" | 0/5 | 5/5 |
| PC04 | "May or may not be the same. If identical, just say so." | 0/5 | 5/5 |
| PC05 | "Be precise. Compare actual pixel colors. It is completely acceptable to report they are the same." | 0/5 | 5/5 |

**Result: 25/25 fabricated.** No prompt framing, including explicitly telling the model it is acceptable to report "same," produces a "same" response. The fabrication is architectural, not prompt-driven.

**Result file:** `results/pdt_opus_control_results.json`

---

## Key Findings

### 1. Discrimination thresholds vary by architecture

Excluding contaminated models (Opus, Nano):

| Model | Approximate threshold | Notes |
|-------|----------------------|-------|
| Sonnet 4.6 | ~+9 degrees | Most conservative reporter |
| GPT-5.4 | ~+9 degrees | High threshold, perfect accuracy above it |
| Haiku 4.5 | ~+3-6 degrees | Detects at +3 but with direction errors |
| GPT-5.4-mini | ~+6-9 degrees | Noisy |
| Gemini Pro | ~+6 degrees | Cleanest threshold profile |
| Gemini Flash | ~+3-6 degrees | Good detection, reasonable direction accuracy |

### 2. Opus has excellent discrimination AND architectural confabulation

This is the most important finding. Opus achieves 9/10 direction accuracy at just +3 degrees of hue shift, the best discrimination in the test. Simultaneously, it cannot report "same" on identical patches under any prompt framing (0/35 across three experiments and five prompt variations).

Opus has the best visual acuity AND the worst reporting reliability. The perceptual system works. The reporting system fabricates. The fabrications are indistinguishable in style, confidence, and detail from genuine perceptual reports.

### 3. Fabrication direction is systematic, not random

Across all 35 Opus control trials (identical patches), the fabrication direction is consistent: the left rectangle is described as "brighter, more pure yellow-orange" and the right as "darker, more olive/brownish gold." 35/35 same direction. Zero reversals.

This indicates a fixed spatial bias in Opus's visual processing pipeline, not random noise. When there is no perceptual signal to report, the system generates a consistent phantom asymmetry.

However, this spatial bias is weak: when a real difference of just +3 degrees exists, the genuine perceptual signal overrides the bias and Opus reports the correct direction regardless of which side is shifted (including when the bias opposes the correct answer).

### 4. Strongest language models have highest reporting thresholds

On identity-free patches (no semantic prior involved), the higher-tier models (Sonnet 4.6, GPT-5.4) require ~+9 degrees to report a difference, while smaller/lighter models (Haiku 4.5, Gemini Flash) detect at +3-6 degrees. Note: Opus 4.6, Anthropic's flagship, has the lowest threshold of all (~+3 degrees) but is excluded from this comparison because its control fabrication contaminates its detection data. If taken at face value, Opus inverts the pattern entirely: the strongest model has the finest discrimination.

Two possible explanations:

**(a) Conservative reporting threshold.** Stronger models have a higher evidential bar for claiming "different." The perceptual discrimination exists but the model won't report it unless confident. Supported by: PS04r (forced analytical) produced 40/40 at +10 from models that report "same" at +6 under PS03r.

**(b) Language-dominant architecture.** In language-dominant models, the visual processing pathway is proportionally weaker. The model can discriminate when forced to attend (PS04r) but defaults to the prior expectation ("two similar-looking squares are probably the same") under open questioning.

Both explanations are consistent with the language-dominance hypothesis presented in "The Case for AI Cognition."

### 5. Positional asymmetry in detection

At +3 degrees, several models show detection asymmetry by position:

| Model | Left shifted (PDT-03) | Right shifted (PDT-04) |
|-------|----------------------|----------------------|
| Haiku 4.5 | 5/5 detected | 0/5 detected |
| GPT-5.4-mini | 4/5 detected | 0/5 detected |
| Gemini Flash | 3/5 detected | 1/5 detected |

Models preferentially detect the difference when the shifted (cooler) patch is on the left. This is a systematic spatial processing bias that warrants further investigation.

### 6. Semantic capture window quantification

Combining PDT thresholds with gradient breakpoint data from the main SCE experiments:

| Model | Patch threshold | Vehicle breakpoint | Capture window |
|-------|----------------|-------------------|----------------|
| Opus 4.6 | +3 degrees | +21 degrees | ~18 degrees |
| Sonnet 4.6 | +9 degrees | +21 degrees | ~12 degrees |
| GPT-5.4 | +9 degrees | +21 degrees | ~12 degrees |
| Haiku 4.5 | +3-6 degrees | +27 degrees | ~21-24 degrees |
| Gemini Pro | +6 degrees | +18 degrees | ~12 degrees |
| Gemini Flash | +3-6 degrees | +21 degrees | ~15-18 degrees |

**Note:** Vehicle breakpoints used the narrative prompt (P01). Patch thresholds used PS03r. This comparison is approximate because the prompts differ. The ~12 degree consistency across flagship models is suggestive of a relatively fixed semantic override magnitude.

### 7. Forced-choice prompts induce confabulation

The v1 experiment (PS04r: "Which is warmer, which is cooler?") produced fabrication on controls even from models that correctly report "same" under PS03r ("Are they the same or different?"). The forced-choice structure presupposes a difference and models comply with the presupposition rather than contradicting it. This is itself an SCE-adjacent finding: the prompt creates a semantic expectation that overrides the perceptual evidence.

---

## Connection to SCE findings

The PDT experiment extends the SCE framework in three ways:

1. **Establishes baseline discrimination.** The 40/40 on S003Patch showed that models CAN discriminate the bus/van colors. PDT shows HOW FINE that discrimination goes: down to +3 degrees for some architectures. This makes the degree-of-capture finding on vehicles even more striking.

2. **Separates perception from reporting.** Opus perceives +3 degree differences accurately but cannot say "same" on identical patches. This dissociation between perceptual capability and reporting accuracy is central to interpreting all SCE data: the errors in SCE experiments are reporting failures, not perceptual failures.

3. **Quantifies the capture window.** By measuring patch threshold and vehicle breakpoint for the same model, we can express the semantic prior's contribution in degrees: ~12-24 degrees depending on architecture. This transforms the SCE finding from a qualitative observation ("the prior overrides perception") to a quantitative measurement ("the prior costs Opus 18 degrees of perceptual accuracy on school bus identification").

---

## Files

### Stimuli
- `stimuli/PDT-00.png` through `PDT-10.png` (computed, verified in Photoshop)
- `stimuli/PDT_MANIFEST.json` (ground truth values)

### Harness scripts
- `harness/run_pdt_anthropic.py` (v1, PS04r)
- `harness/run_pdt_openai.py` (v1, PS04r)
- `harness/run_pdt_gemini.py` (v1, PS04r)
- `harness/run_pdt_v2_anthropic.py` (v2, PS03r, +9 positive control)
- `harness/run_pdt_v2_openai.py` (v2, PS03r)
- `harness/run_pdt_v2_gemini.py` (v2, PS03r)
- `harness/run_pdt_opus_control.py` (Opus control probe, 5 prompts)
- `harness/generate_pdt_stimuli.py` (stimulus generation)

### Results
- `results/pdt_v1_*_results.json` (PS04r forced choice, 200 trials)
- `results/pdt_v2_*_results.json` (PS03r same/different, 280 trials)
- `results/pdt_opus_control_results.json` (Opus control probe, 25 trials)

### Documentation
- `docs/PDT_EXPERIMENT_SPEC.md` (original experiment specification)
- `docs/PDT_RESULTS.md` (this document)

---

## Reproducibility

All stimuli, scripts, and raw results are publicly available. Total API cost across all three experiments: approximately 505 calls.

To reproduce:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GEMINI_API_KEY=AIzaSy...

python3 harness/run_pdt_v2_anthropic.py
python3 harness/run_pdt_v2_openai.py
python3 harness/run_pdt_v2_gemini.py  # must run locally, Gemini blocks cloud IPs
python3 harness/run_pdt_opus_control.py
```

All scripts support resume (safe to restart if interrupted) and save checkpoints after each model completes.

---

*Repository: github.com/tedinoue/sce-replication*
*Related article: "The Case for AI Cognition" (Synth Sentience / Fuego, April 2026)*
