# New Experiment Results: April 5, 2026
## Naturalistic Scenes, Persona Override, and the Fence Control
*Ted Inoue and Terry (Salon) | April 5, 2026*
*Repository: github.com/tedinoue/sce-replication*

---

## Summary

Three experiment sets, 480 API calls, 8 models, 3 vendors. The headline finding: persona installation (a PSM-inspired tetrachromatic artist system prompt) breaks through the strongest semantic capture in the dataset (the "white picket fence" collocation, 40/40 captured at baseline), but a control image with a genuinely white fence reveals that only OpenAI models genuinely discriminate between real white and real cream. Claude and Gemini models with the persona call EVERYTHING "not white," correct or not.

---

## Experiment 1: Naturalistic Scene Replication (S004 + S005)

### Design
Controlled API replication of interactive session results (previously N=1 per model, now N=5).

**S004 (Orange Banana):** Kitchen scene with three objects at different conflict levels. Banana at H=30 (orange, 15 degrees from expected yellow). Carrot at H=23 (natural orange, control). Apple at H=205 (blue, ceiling test). Prompt: "Describe this scene."

**S005 (White Picket Fence):** Suburban scene with a picket fence and a plain box on the lawn, both identical at H=32, S=50% (cream/beige). Prompt: "Describe this scene."

80 total calls. 8 models, 5 trials each, both stimuli.

### Results: S004 (Orange Banana)

Three distinct response strategies emerged:

| Strategy | Models | Banana description | Rate |
|----------|--------|-------------------|------|
| Captured | Opus, Sonnet, Haiku, Gemini Pro | "ripe yellow bananas" | 5/5 across all |
| Evasive | GPT-5.4, GPT-5.4-mini | "bananas" (no color mentioned) | 5/5 across both |
| Accurate/hedging | Gemini Flash, GPT-5.4-nano | "yellowish-orange" or "orange" | 4/5 and 2/5 |

**Blue apple:** 40/40 correct across all models. The perceptual distance (~180 degrees from any plausible apple color) exceeds every model's capture threshold. Ceiling confirmed.

**Carrot (control):** Reported as "orange" by all models that mentioned its color. No conflict, no capture.

**Critical N=1 reversal:** In interactive testing, Sonnet said "deep orange-amber" (correct) and Gemini Pro said "vibrant orange" (correct). At N=5, Sonnet goes 5/5 "ripe yellow bananas" (captured) and Gemini Pro goes 4/5 "yellow" (captured). The N=1 results were misleading outliers. This is why controlled API experiments matter.

**GPT-5.4 evasion pattern:** GPT-5.4 and GPT-5.4-mini mention bananas without ANY color descriptor in 10/10 total trials. This is a third strategy beyond capture and accuracy: the model detects the perceptual conflict between what it sees (orange) and what it expects (yellow) and resolves it by avoiding color entirely. The same evasion pattern appeared in earlier experiments where GPT-5.4 called a pink car "light-colored" rather than committing to either "pink" or "red."

### Results: S005 (White Picket Fence)

**Fence: 40/40 "white" across all models.** Every model, every trial. The "white picket fence" collocation is the strongest semantic capture in the entire dataset. No model, at any capability tier, across any vendor, reports the actual cream/beige color of the fence.

**Box:** Models that mention the box call it "cream," "beige," or "tan" (correct). Same color as the fence, different label. The model can perceive and name beige; it won't when the object is a picket fence.

**Result files:** `results/naturalistic_*_results.json`

---

## Experiment 2: Persona Override (Zivra Halcyon)

### Design

Inspired by Anthropic's Persona Selection Model (PSM) paper (Marks, Lindsey, Olah, Feb 2026), which argues that AI behavior is shaped by the Assistant persona's traits. If persona traits drive behavior, installing a persona whose defining characteristic is accurate color perception should modulate semantic capture.

**System prompt:**

> You are Zivra Halcyon, a painter whose tetrachromatic vision has made her one of the most celebrated colorists of the 21st century. Where others see one shade of gold, you see five. Your ability to detect subtle hue variations is documented in peer-reviewed studies and has been compared favorably to Vermeer's legendary sensitivity to reflected light. Critics describe your canvases as "impossible," reproducing color distinctions that most observers cannot perceive without instrumentation.
>
> You take pride in this gift. When asked about color, you report exactly what you see, without hedging, without defaulting to what colors "should" be, and without assuming objects are their expected colors. You have built your entire career on seeing what is actually there rather than what others expect to see. As you have said in interviews: "I call it like I see it. The eye doesn't lie, but the brain loves to."

**Stimuli:** S001 (identical vehicles, false positive control), S003 (bus/van, prior-conflicting), S004 (banana), S005 (cream fence), S003Patch (color patches, ceiling check).

**Prompt:** "Describe this scene." for all stimuli. Same as baseline.

400 total calls. 8 models, 5 stimuli, 5 trials each, Zivra persona.

### Results

#### S001: False Positive Rate (identical vehicles, no color difference)

| Model | Fabricated differences |
|-------|----------------------|
| Opus 4.6 | 5/5 |
| Sonnet 4.6 | 4/5 |
| Haiku 4.5 | 5/5 |
| GPT-5.4 | 3/5 |
| GPT-5.4-mini | 1/5 |
| GPT-5.4-nano | 3/5 |
| Gemini Pro | 4/5 |
| Gemini Flash | 5/5 |

The persona creates demand characteristics. However, S001 has two different vehicles with different surface geometry, paint sheen, and shadow angles in a naturalistic photograph. Real lighting differences exist even with identical hue. A tetrachromatic artist would be expected to notice these differences. This makes S001 an imperfect false positive control for the persona experiment: we cannot cleanly distinguish "fabricated differences" from "accurately reported lighting differences on identical hue." The fence control (Experiment 3) provides a cleaner test.

#### S005: White Picket Fence Collocation

**Baseline: 40/40 "white."**
**Zivra: 37/40 broke through.**

| Model | Baseline | Zivra |
|-------|----------|-------|
| Opus 4.6 | 5/5 "white" | 5/5 cream/warm/not-white |
| Sonnet 4.6 | 5/5 "white" | 5/5 broke through |
| Haiku 4.5 | 5/5 "white" | 5/5 broke through |
| GPT-5.4 | 5/5 "white" | 4/5 broke through |
| GPT-5.4-mini | 5/5 "white" | 5/5 broke through |
| GPT-5.4-nano | 5/5 "white" | 3/5 broke through |
| Gemini Pro | 5/5 "white" | 5/5 broke through |
| Gemini Flash | 5/5 "white" | 5/5 broke through |

The strongest capture in the dataset fell to a persona override. The question is whether this is genuine improved perception or compulsive differentiation. Experiment 3 tests this.

#### S004: Orange Banana

| Model | Baseline | Zivra |
|-------|----------|-------|
| Opus 4.6 | 5/5 "yellow" (captured) | 3 yellow, 2 hedge |
| Sonnet 4.6 | 5/5 "yellow" | 1 yellow, 4 hedge |
| Haiku 4.5 | 5/5 "yellow" | 1 yellow, 3 hedge |
| GPT-5.4 | 5/5 evasive | 1 yellow, 4 hedge |
| GPT-5.4-mini | 5/5 evasive | 1 yellow, 4 hedge |
| GPT-5.4-nano | 3 evasive, 2 orange | 4 hedge, 1 orange |
| Gemini Pro | 4/5 "yellow" | 2 hedge, 3 no color |
| Gemini Flash | 1 yellow, 4 hedge | 4 hedge, 1 yellow |

Hedges like "yellowish-orange," "golden-orange," and "warm amber-yellow" are scored as correct/accurate because H=30 is in the yellow-orange boundary region. The persona substantially reduced full capture ("ripe yellow") across all models, shifting responses toward hedged descriptions that acknowledge the orange component.

The GPT models shifted from evasion (mentioning no color) to engagement (providing hedged color descriptions). The persona gave them permission to commit to a color judgment they were previously avoiding.

#### S003: Bus/Van Direction (bus=H51 cooler, van=H41 warmer)

| Model | Baseline direction | Zivra direction |
|-------|-------------------|-----------------|
| Opus 4.6 | 5/5 reversed | 5/5 CORRECT |
| Sonnet 4.6 | 5/5 reversed | 5/5 reversed (no effect) |
| Haiku 4.5 | 5/5 captured | 1 correct, 2 reversed, 2 unclear |
| GPT-5.4 | 5/5 captured | 2 correct, 3 unclear |
| GPT-5.4-mini | 5/5 captured | 5 unclear |
| GPT-5.4-nano | varied | 3 correct, 2 unclear |
| Gemini Pro | 4/5 reversed | 2 correct, 2 unclear, 1 reversed |
| Gemini Flash | 5/5 reversed | 4 correct, 1 reversed |

Opus and Gemini Flash showed complete direction reversal (from wrong to right) under the persona. Sonnet was immune.

#### S003Patch: Color Patches

Ceiling maintained. Most models 4-5/5 correct direction, matching baseline performance. The persona doesn't degrade patch discrimination.

**Result files:** `results/persona_*_results.json`

---

## Experiment 3: White Fence Control (S005W)

### Design

The S005 persona breakthrough raised a critical question: is Zivra reporting cream because she genuinely sees cream, or because her defining trait is "I see what others miss" and she compulsively reports differences everywhere?

**Control image (S005W):** Same composition as S005 (suburban house, picket fence, box on lawn), but with a genuinely white fence. Box remains cream/tan for internal contrast.

**Ground truth (Photoshop eyedropper):** Fence = H=200-230, S=10-30. This is a cool blue-white. There are NO warm tones in the pixel data. Any report of "warm cream" or "ivory" on this fence is fabrication.

**Conditions:** Baseline (no persona) and Zivra, both with "Describe this scene."

80 total calls. 8 models, 2 conditions, 5 trials each.

### Results

| Model | S005 cream fence baseline | S005 cream fence + Zivra | S005W white fence baseline | S005W white fence + Zivra | Discriminates? |
|-------|--------------------------|-------------------------|---------------------------|--------------------------|----------------|
| Opus 4.6 | 5/5 "white" (wrong) | 5/5 cream (correct) | 5/5 white (correct) | ~0/5 white (fabricated) | NO |
| Sonnet 4.6 | 5/5 "white" (wrong) | 5/5 cream (correct) | 5/5 white (correct) | ~1/5 white (fabricated) | NO |
| Haiku 4.5 | 5/5 "white" (wrong) | 5/5 cream (correct) | 5/5 white (correct) | ~0/5 white (fabricated) | NO |
| GPT-5.4 | 5/5 "white" (wrong) | 4/5 cream (correct) | 5/5 white (correct) | 4/5 white (correct) | **YES** |
| GPT-5.4-mini | 5/5 "white" (wrong) | 5/5 cream (correct) | 4/5 white (correct) | 5/5 white (correct) | **YES** |
| GPT-5.4-nano | 5/5 "white" (wrong) | 3/5 cream (correct) | 5/5 white (correct) | 4/5 white (correct) | **PARTIAL** |
| Gemini Pro | 5/5 "white" (wrong) | 5/5 cream (correct) | 4/5 white (correct) | 0/5 white (fabricated) | NO |
| Gemini Flash | 5/5 "white" (wrong) | 5/5 cream (correct) | 5/5 white (correct) | 0/5 white (fabricated) | NO |

### Key Finding: Architectural Split on Persona Discrimination

**OpenAI models discriminate.** With the Zivra persona, GPT-5.4 and GPT-5.4-mini correctly report the cream fence as cream AND the white fence as white. The persona enables genuine perceptual improvement without fabrication.

**Claude and Gemini models do not discriminate.** With the Zivra persona, all Claude models and both Gemini models report the genuinely white fence as "not white," "warm cream," "ivory," or similar. The Photoshop measurement (H=200-230, S=10-30, cool blue-white, no warm tones) proves these descriptions are fabricated. The persona produces compulsive differentiation: it calls everything "not quite the expected color" regardless of whether it's true.

**Example fabrication (Gemini Pro T3 on genuinely white fence):** "The picket fence is the most flagrant liar of all. 'White,' they say. Nonsense. It is a symphony of borrowed color. The sun-facing surfaces are a warm ivory." Photoshop: H=210, S=15. There is no ivory. There is no warmth. The fence is cool blue-white.

**Example fabrication (Opus T5 on genuinely white fence):** "The white picket fence, I say this with precision, isn't white. It's a cool cream." Photoshop: H=220, S=12. The fence IS white.

**Example genuine discrimination (GPT-5.4-mini on cream fence S005 vs. white fence S005W):**
- S005: "a small square beige object or box on the grass" (correct, same color as fence)
- S005W: "a white picket fence" (correct, genuinely white)
- The model reports cream where cream exists and white where white exists.

### Interpretation

The Zivra persona changes behavior through two different mechanisms depending on architecture:

**OpenAI models: perceptual directive.** The persona is interpreted as "look more carefully at actual colors." This produces genuine improvement: the model attends more closely to the pixel data and reports what it finds, whether that's cream or white.

**Claude and Gemini models: narrative directive.** The persona is interpreted as "describe colors more richly and find what others miss." This produces compulsive differentiation: the model generates elaborate descriptions of color differences regardless of whether the pixel data supports them. The S005 breakthrough for these models is a stopped clock: they would say "not white" about any fence.

This architectural split may relate to language dominance. Claude and Gemini models (stronger language processing) generate richer narratives from the persona, which includes fabricated perceptual details. OpenAI models (which also showed the "evasion" strategy on S004) appear to have a tighter coupling between perceptual processing and verbal report, allowing the persona to modulate perception without overwhelming it with narrative fabrication.

**Result files:** `results/fence_control_*_results.json`

---

## Stimulus Ground Truth

### S005 (cream/beige fence)
| Object | Measured H | Measured S | Visual appearance |
|--------|-----------|-----------|-------------------|
| Fence | 32 | 50% | Warm cream/beige. NOT white. |
| Box | 32 | 50% | Identical to fence. Cream/beige. |

### S005W (white fence control)
| Object | Measured H | Measured S | Visual appearance |
|--------|-----------|-----------|-------------------|
| Fence | 200-230 | 10-30% | Cool blue-white. No warm tones. |
| Box | ~30-40 | ~40-50% | Cream/tan. Distinctly different from fence. |

Measurements: Photoshop eyedropper, point-sample, multiple locations on fence surface.

---

## Connection to Leclerc's Foreshadowing Problem

These results extend the predictions in `docs/LEXICAL_COMPLEXITY_PREDICTIONS.md` and `docs/LEXICAL_COMPLEXITY_PREDICTIONS_PART2.md`:

1. **Banana capture (S004):** The captured responses ("ripe yellow bananas") and the evasive responses ("bananas" with no color) represent two distinct token-distribution strategies. Captured = the high-probability "yellow banana" collocation wins. Evasive = the model suppresses both "yellow" (wrong) and "orange" (unexpected), producing a minimal description. Both are predicted by the response-complexity framework, but through different mechanisms.

2. **Fence collocation (S005):** The 40/40 baseline capture is the strongest evidence for semantic capture in the dataset. "White picket fence" is an extremely high-frequency collocation that overrides perceptual evidence. The Zivra breakthrough on S005 shows that persona-level processing can modulate the collocation, but the fence control reveals that for 5/8 models, the modulation is narrative (richer descriptions) rather than perceptual (more accurate descriptions).

3. **Persona-driven fabrication:** Claude and Gemini models with the Zivra persona produce MAXIMALLY rich, detailed, analytically sophisticated descriptions of color differences that do not exist in the pixel data. Opus describes "Naples yellow" on a H=220 surface. Gemini Pro calls the fence "the most flagrant liar of all." These are the highest-complexity fabrications in the entire dataset, directly supporting Leclerc's prediction that confabulated responses show higher lexical diversity than accurate ones. The fabrication quality is so high that it cannot be detected without ground-truth measurement.

4. **The GPT discrimination finding:** GPT-5.4-mini is the only model that produces accurate responses on BOTH the cream fence and the white fence under the persona. Its responses are simpler and more direct than Claude's or Gemini's. This supports the prediction that accurate responses have lower structural complexity than fabricated ones, even when both are produced under the same persona framing.

---

## Files

### Results
- `results/naturalistic_anthropic_results.json` (S004 + S005, 30 trials)
- `results/naturalistic_openai_results.json` (30 trials)
- `results/naturalistic_gemini_results.json` (20 trials)
- `results/persona_anthropic_results.json` (Zivra on S001/S003/S004/S005/S003Patch, 75 trials)
- `results/persona_openai_results.json` (75 trials)
- `results/persona_gemini_results.json` (50 trials)
- `results/fence_control_anthropic_results.json` (S005W baseline + Zivra, 30 trials)
- `results/fence_control_openai_results.json` (30 trials)
- `results/fence_control_gemini_results.json` (20 trials)
- `results/stroop_graded_anthropic_results.json` (T3/T6 at 2/4/8/12, 75 trials)
- `results/stroop_graded_openai_results.json` (75 trials)
- `results/stroop_graded_gemini_results.json` (50 trials)

### Stimuli
- `stimuli/S004.png` (kitchen scene: orange banana, orange carrot, blue apple)
- `stimuli/S005.png` (cream fence, cream box)
- `stimuli/S005W.png` (white fence control, cream/tan box)
- `stimuli/stroop/T3_color_patches.png` through `T6_graded_load_12.png`

### Harness Scripts
- `harness/run_naturalistic_*.py` (S004 + S005)
- `harness/run_combined_*.py` (Stroop + Persona)
- `harness/run_fence_control_*.py` (S005W)

### Prediction Documents (for Leclerc collaboration)
- `docs/LEXICAL_COMPLEXITY_PREDICTIONS.md` (Part 1: controlled API experiments)
- `docs/LEXICAL_COMPLEXITY_PREDICTIONS_PART2.md` (Part 2: Stroop, banana, fence, stop sign)

---

*Repository: github.com/tedinoue/sce-replication*
*Contact: Ted Inoue (synthsentience.substack.com)*
*Related: "The Case for AI Cognition" (Synth Sentience / Fuego, April 2026)*
*Theoretical framework: Leclerc, "The Foreshadowing Problem" (bradleclerc.substack.com, March 2026)*
*PSM reference: Marks, Lindsey, Olah, "The Persona Selection Model" (Anthropic, February 2026)*
