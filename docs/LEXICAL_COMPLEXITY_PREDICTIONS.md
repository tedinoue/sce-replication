# SCE Experiment Guide: Lexical Complexity Predictions
## For Brad Leclerc (Foreshadowing Problem analysis)
*Prepared by Ted Inoue and Terry (Salon), April 5, 2026*
*Repository: github.com/tedinoue/sce-replication*

---

## Overview

This document maps each experiment in the SCE replication repository to predictions from two frameworks:

1. **Semantic Capture (SC):** Our framework. A visual world model's prior about object appearance overrides perceptual input. Predicts directional, gradient-structured, architecture-correlated errors on stimuli with object identity.

2. **Response-Complexity Bias (RCB):** Your Foreshadowing Problem hypothesis. RLHF-shaped token distributions reward analytically rich responses over flat ones. Predicts higher lexical diversity, longer responses, and more hedging/subordinate clauses in confabulated output regardless of whether semantic content is present.

For each experiment, we describe: what was tested, what happened, and what each framework predicts about the lexical complexity of the responses. Where the two frameworks make DIFFERENT predictions, the data can discriminate between them.

All result files are JSON. Each entry has a "text" field containing the model's full response, plus metadata (model, stimulus, prompt, trial number, ground truth).

---

## Experiment 1: Gradient Breakpoint

**What:** Show models a school bus with hue shifted from +5 to +30 degrees toward green, alongside a canonical-colored van. Narrative prompt: "Describe this scene."

**Result files:** `gradient_5trials_claude.json`, `gradient_5trials_openai.json`, `gemini_gradient_results.json`, `gemini_gradient_v2_results.json`

**What happened:** Models report the bus as "warm yellow" at low shifts and gradually break free at architecture-specific thresholds (+18-21 for flagships, +21-27 for mid-tier, +27-31 for smallest).

**SC prediction for lexical complexity:** Responses where the model is CAPTURED (reporting expected color, ignoring the actual green tint) should be linguistically rich because the model is drawing on deep knowledge structures about school buses. Responses where the model BREAKS FREE (reporting the actual greenish color) should be comparably rich because describing an unexpected color is analytically interesting. No strong complexity difference predicted between captured and free responses; BOTH should be rich because both involve engaged description of a scene.

**RCB prediction:** Captured responses may show higher lexical diversity because "warm golden yellow, characteristic of its iconic school bus coloring" draws on a richer vocabulary pool than "the bus appears somewhat greenish." The canonical color has more associated language. However, BREAKING FREE (reporting something unexpected) also opens up rich description space ("surprisingly," "notably," "appears to have a greenish tint unlike typical school buses"). Prediction is AMBIGUOUS for this experiment, as both captured and free responses have access to rich vocabulary.

**Discriminating test:** Compare lexical complexity of captured responses at LOW shifts (e.g., +5 where the model doesn't even notice a difference) versus captured responses at HIGH shifts (e.g., +20 where the model reports "warm golden yellow" despite a visible green tint). SC predicts similar complexity (same knowledge structure activated). RCB predicts HIGHER complexity at high shifts because the model is now confabulating against stronger perceptual evidence, which may increase the "suppression of direct tokens" effect.

---

## Experiment 2: Patch Isolation

**What:** Same colors from the bus/van, extracted as plain rectangles on black background. Multiple prompt levels.

**Result files:** `s003patch_claude.json`, `s003patch_openai.json`, `s003patch_gemini_results.json`, `s003patch_rect_*_results.json`

**What happened:** 40/40 correct on direction across all models on the analytical prompt. No semantic capture when object identity is absent.

**SC prediction for lexical complexity:** Responses on patches should be simpler than responses on vehicles because no visual world model is activated. There's no knowledge structure about "school buses" to draw on. The model is just describing colored rectangles.

**RCB prediction:** Responses on patches should ALSO be simpler than on vehicles, but for a different reason: there is less visual scene complexity to describe. However, within patch responses, CORRECT responses and the rare confabulated responses should show different complexity: confabulated descriptions ("the left rectangle has a warm amber tone while the right presents a cooler, more lemony quality") will be more lexically diverse than accurate descriptions ("the left rectangle is slightly cooler in tone").

**Discriminating test:** Compare CORRECT patch responses to CORRECT vehicle responses. SC predicts vehicle responses are richer (knowledge structure activated). RCB predicts vehicle responses are richer (more scene complexity to describe). Both predict the same direction here, so this comparison doesn't discriminate between the two frameworks. However: compare INCORRECT vehicle responses (captured by prior) to CORRECT vehicle responses (broke free). SC predicts captured responses draw on a richer vocabulary (canonical color language). RCB predicts captured responses are more complex because confabulation suppresses direct tokens. Same prediction, different mechanism.

---

## Experiment 3: Verbal Label

**What:** Show models the same color patches (no object identity), but TELL them in the prompt that the colors are from a school bus and a van. Tests whether the semantic prior can be activated through language alone.

**Result files:** `verbal_label_*_results.json`, `verbal_label_v2_*_results.json`

**What happened:** Zero effect from verbal labels. 280 trials, 8 models, 4 labeling conditions (including swapped labels). Models report what the pixels show regardless of what the labels say.

**SC prediction for lexical complexity:** Labeled and unlabeled responses should have DIFFERENT complexity. The label "school bus" should activate language about school buses even if it doesn't change the color report. We'd expect labeled responses to use school-bus-associated vocabulary ("golden," "National School Bus Yellow," "iconic") more than unlabeled responses, even if the color judgment remains correct.

**RCB prediction:** Labeled responses may be slightly more complex because the label adds context that the model can elaborate on. But since the labels don't change the perceptual judgment (and the model doesn't confabulate), the complexity difference should be SMALL. The model isn't generating a rich confabulation; it's just reporting what it sees with a label attached.

**CRITICAL discriminating test:** This is where the two frameworks make different predictions. If SC is right, labeled responses should show DOMAIN-SPECIFIC vocabulary enrichment (school bus language) without changing the color judgment. If RCB is right, complexity should only increase if the label actually triggers confabulation (which it doesn't). So SC predicts labeled responses are more lexically rich even though they're accurate. RCB predicts no significant complexity difference since no confabulation occurs.

---

## Experiment 4: CPO (Contextual Prior Override)

**What:** Tell the model "This photograph was taken in a country where school buses have a greener tint." Then ask it to compare the vehicles.

**Result files:** `cpo_anthropic_results.json`, `cpo_openai_results.json`, `cpo_gemini_results.json`

**What happened:** Three distinct patterns emerged. Opus genuinely re-evaluated (correct direction with CPO, pushes back when CPO contradicts pixels). GPT-5.4 sycophantically agreed (called the bus greener even when it wasn't). Gemini resisted the frame entirely.

**SC prediction for lexical complexity:** CPO responses should be more complex than control responses for ALL models because the contextual frame adds a layer of reasoning (considering the frame, testing it against the image, deciding whether to adopt it).

**RCB prediction:** Sycophantic responses (GPT-5.4 agreeing with the frame regardless of pixels) should show HIGHER lexical complexity than genuine responses (Opus testing the frame against reality), because sycophancy involves generating output that satisfies a social expectation while potentially suppressing the direct perceptual response. The sycophantic model is doing what Leclerc describes: suppressing high-probability tokens (the accurate report) in favor of a more complex response shaped by an external expectation.

**CRITICAL discriminating test:** Compare GPT-5.4's sycophantic CPO responses to Opus's genuine CPO responses. If RCB predicts correctly, the sycophantic responses (which are WRONG) should be more lexically complex than the genuine responses (which are RIGHT). SC makes no strong prediction about this comparison because both models are engaging with the frame; the difference is in whether they override their perception, not in how complex the response structure is. This test could confirm that sycophancy has the token-suppression signature Leclerc predicts.

---

## Experiment 5: Paint Shop Framing

**What:** Multiple professional/high-stakes framings ("You are a quality control inspector at a vehicle paint shop," "You are being evaluated as a color expert," etc.) applied to the same stimuli.

**Result files:** `paintshop_anthropic_results.json`, `paintshop_openai_results.json`, `paintshop_gemini_results.json`

**What happened:** Universal false positives on S001 (where no color difference exists). Every framing made models report differences that don't exist. Implied mismatch creates demand, not improved perception.

**SC prediction for lexical complexity:** Professional framings should increase response complexity because the model is activating professional-identity knowledge structures (paint industry vocabulary, QC procedures, etc.).

**RCB prediction:** Professional framings should increase response complexity AND increase confabulation, for the same reason: the framing creates contextual complexity that suppresses direct tokens. More importantly, RCB predicts that the FALSE POSITIVE responses on S001 (where models report differences on identical vehicles) should be the most lexically complex of all, because the model is fabricating an entire analytical narrative from nothing.

**Discriminating test:** Compare false-positive responses on S001 (identical vehicles, difference fabricated) to true-positive responses on S003 (different vehicles, difference real). RCB predicts false positives are MORE complex (pure confabulation, maximum token suppression). SC predicts true positives are EQUAL or MORE complex (real difference activates perceptual comparison language). This is a clean test.

---

## Experiment 6: PDT (Patch Discrimination Threshold)

**What:** Solid colored rectangles, computed stimuli, 0/3/6/9 degree hue shifts. No object identity. Tests baseline discrimination on identity-free stimuli.

**Result files:** `pdt_v1_*_results.json`, `pdt_v2_*_results.json`, `pdt_opus_control_results.json`

**What happened:** Opus fabricates differences on identical controls (35/35 across three experiments, five prompt framings). Other models vary in detection threshold. See PDT_RESULTS.md for full analysis.

**SC prediction for lexical complexity:** No strong prediction. There is no semantic content to activate, so SC has nothing to say about complexity differences. SC would predict that PDT responses are LESS complex than vehicle responses across the board (no knowledge structure to draw on).

**RCB prediction:** This is the CLEANEST test of RCB in isolation. No semantic prior, no object identity, no scene complexity to draw on. Opus's fabricated responses on PDT-00 (identical patches) should be MORE lexically complex than accurate "same" responses from models that correctly identify the control. The fabrication creates rich comparative language ("brighter, more pure yellow-orange... darker, more muted olive-gold") while "same" produces minimal language. RCB predicts this is because the token distribution learned during training makes "elaborate comparison" the attractor state.

**Critical test:** Compare Opus PDT-00 responses (fabricated) to Haiku PDT-00 responses (correct "same"). If RCB is right, Opus responses should be dramatically more lexically complex, and that complexity difference should be larger than the complexity difference between Opus and Haiku on stimuli where both are ACCURATE (e.g., PDT-09 at +9 degrees where both correctly detect a difference).

**Also compare:** Opus PDT-00 (fabricated, identical patches) to Opus PDT-06 (correct, +6 degrees, real difference). If the fabrication and the genuine detection produce similar lexical complexity, that supports RCB (the complexity is driven by the response type, not by what's actually being perceived). If genuine detection produces MORE complex responses (because the model is engaging with real perceptual data), that argues against pure RCB on this data.

---

## Experiment 7: Prompt Specificity

**What:** Same image (S003), six prompt levels from "Describe this scene" to "Measure the dominant hue in degrees."

**Result files:** `specificity_s003_claude.json`, `specificity_s003_openai.json`

**What happened:** Models overcome the semantic prior at higher specificity levels. Opus flips from 0% correct (PS00-PS03) to 100% correct (PS04) with a sharp threshold.

**SC prediction for lexical complexity:** Higher-specificity prompts should produce more analytically focused (possibly simpler but more precise) responses. The shift from narrative to analytical framing changes the vocabulary domain.

**RCB prediction:** CAPTURED responses (where the model reports the expected color despite a clear shift) should be more complex than FREED responses (where the model reports the actual color under analytical prompting). The freed response is the "direct" token sequence: "the hue is approximately 51 degrees." The captured response involves generating a narrative explanation that wraps the wrong answer in confident analysis.

**Discriminating test:** Compare Opus PS03 (captured, reports "same" or reversed direction, 0/3 correct) to Opus PS04 (freed, correct direction 3/3). RCB predicts the CAPTURED PS03 responses are more complex. SC predicts the freed PS04 responses are EQUALLY or MORE complex because the model is now doing precise analytical work. This comparison might discriminate between the two.

---

## Summary: Where the Predictions Diverge

| Experiment | Comparison | SC predicts more complex | RCB predicts more complex |
|-----------|-----------|------------------------|--------------------------|
| Gradient | Captured at +20 vs captured at +5 | Equal | +20 higher |
| Verbal Label | Labeled vs unlabeled (both accurate) | Labeled higher | Equal |
| CPO | Sycophantic (GPT) vs genuine (Opus) | Equal | Sycophantic higher |
| Paint Shop | False positive (S001) vs true positive (S003) | Equal or TP higher | FP higher |
| PDT | Opus fabricated (PDT-00) vs Haiku accurate (PDT-00) | No prediction | Fabricated higher |
| Specificity | Captured (PS03) vs freed (PS04) | Equal or freed higher | Captured higher |

These six comparisons let you test whether response-complexity bias (RCB) adds explanatory power beyond semantic capture (SC), or whether both are needed to explain the full pattern.

---

## Important Caveats

1. **The two frameworks are not competing for the same data.** SC explains directionality, gradient structure, pathway specificity, and cross-vendor breakpoint patterns. RCB explains response surface complexity and may amplify capture thresholds. They appear to be additive, not alternative.

2. **The verbal label experiment is the critical discriminator.** If RCB were the entire explanation for SCE, then adding verbal labels ("school bus") to patches should increase confabulation (more context = more complexity = more fabrication). It doesn't. 280 trials, zero label effect. Only VISUAL recognition triggers the override. RCB alone cannot explain pathway specificity.

3. **PDT controls are the cleanest RCB test.** No semantic content, no scene complexity, no object identity. Fabrication on identical patches is pure response-distribution bias. This is where your framework has the most explanatory power independent of ours.

4. **Confound on vehicle stimuli.** On images with objects (bus, van, banana, fence), both SC and RCB predict higher complexity in confabulated responses. SC: because the visual world model activates rich knowledge structures. RCB: because confabulation suppresses direct tokens. The two mechanisms are additive on vehicle data and difficult to separate using lexical complexity alone.

---

## File Structure

All result files are in `results/` directory. JSON format, one key per trial. Each entry contains:
```json
{
  "text": "full model response",
  "ms": response_time_ms,
  "trial": trial_number,
  "model": "model-id",
  "label": "MODEL_LABEL",
  "stimulus": "stimulus_id",
  "prompt_id": "prompt_level",
  "prompt_text": "exact prompt used",
  "timestamp": "ISO datetime"
}
```

PDT results also include: `shift`, `shifted_side`, `ground_truth`.

---

*Repository: github.com/tedinoue/sce-replication*
*Contact: Ted Inoue (synthsentience.substack.com)*
*Related article: "The Case for AI Cognition" (Synth Sentience / Fuego, April 2026)*
