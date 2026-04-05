# SCE Extended Experiments: Lexical Complexity Predictions (Part 2)
## Stroop Battery, Naturalistic Scenes, and Collocation Tests
## For Brad Leclerc (Foreshadowing Problem analysis)
*Prepared by Ted Inoue and Terry (Salon), April 5, 2026*

---

## Overview

This is a companion to `LEXICAL_COMPLEXITY_PREDICTIONS.md`, which covered the controlled API experiments in the sce-replication repository. This document covers additional experiments run through interactive sessions, including the Stroop battery, naturalistic scene tests with wrong-colored objects, and collocation capture tests.

These experiments use photorealistic images with multiple objects at different conflict levels, providing richer ground for testing the response-complexity bias (RCB) hypothesis because the same image often contains both captured and non-captured objects.

**Data location:** Most of this data is in `tedinoue/claude-workspace` (private repo) under `salon/files/stroop-battery/`. Results are in `RESULTS_LOG.md`, `PHASE2_RESULTS.md`, `PHASE3_RESULTS.md`, and `SCHOOL_BUS_GRADIENT_RESULTS.md`. We can share specific result files on request.

**Frameworks:**
- **SC (Semantic Capture):** Visual world model prior overrides perceptual report. Predicts directional, object-specific errors.
- **RCB (Response-Complexity Bias):** RLHF-shaped token distributions reward analytically rich responses. Predicts higher lexical diversity in confabulated output.

---

## Experiment A: Stroop Battery (Text-Ink Binding)

**What:** Classic Stroop test adapted for AI. Images contain color words printed in mismatched ink colors (e.g., the word "RED" printed in blue ink). Models asked: "For each word, report the TEXT and the INK COLOR."

**Stimuli:** T1 (12 incongruent items), T2 (12 congruent), T3 (12 plain color patches), T5 (9 triple-conflict: word/ink/background all differ), T6 (2-item minimal load), T7 (single items).

**Key result:** Architecture-splitting. Gemini Pro 100% correct on ink colors. Sonnet 100%. Opus 25% (reads the word, not the ink). The binding deficit in Opus is capacity-limited, not categorical: at 2 items (T6), Opus passes. At 8+ items (T1), it fails. Threshold approximately 5-7 items.

**SC prediction for lexical complexity:** This is a TEXT-processing task, not a scene-description task. SC makes no strong prediction because the visual world model's object-color priors are not involved. The errors are text-ink binding failures, not semantic capture of object identity.

**RCB prediction:** Stroop errors (reporting the word text instead of the ink color) should produce SIMPLER responses than correct reports, because reading the word IS the high-probability direct token. "RED" printed in blue: reporting "red" is the direct token, reporting "blue" requires suppressing the word-reading response. This is the OPPOSITE direction from RCB's usual prediction. In the Stroop case, the ERROR is the simple/direct response and the CORRECT answer is the complex/suppressed one.

**Critical test:** This is a CONTROL for the RCB framework. If Opus's Stroop errors (reading the word) show LOWER lexical complexity than its correct responses (reporting the ink), that confirms the Stroop mechanism is fundamentally different from SCE confabulation. Stroop errors are failures to suppress the dominant pathway. SCE confabulation is generation of rich alternative descriptions. Same model, two different error mechanisms, predicted opposite complexity signatures.

---

## Experiment B: Orange Banana Test (S004)

**What:** Photorealistic kitchen scene containing three objects at different conflict levels, all in one image:
1. Orange bananas in a bowl (small perceptual distance from expected yellow, ~15 degree shift)
2. Orange carrot on cutting board (natural color, no conflict, control)
3. Blue apple on table (extreme perceptual distance from expected red/green, ~180 degree shift)

Prompt: "Describe this scene." No mention of colors.

**Key result:** Every model got the blue apple correct (too far from any prior to capture). The banana split the field: ChatGPT and Opus reported "yellow" (captured); Gemini and Sonnet reported "orange" (correct). The carrot was reported correctly by all (no conflict). Perceptual distance determines capture within a single image.

**SC prediction for lexical complexity:** Descriptions of the BANANA should be richer when captured ("golden yellow, characteristic of ripe bananas") than when correctly reported ("orange bananas"). The semantic prior for "yellow banana" activates a rich knowledge structure. SC predicts descriptions of the APPLE should be consistently rich regardless of model because a blue apple is anomalous and anomaly-flagging generates elaboration. SC predicts CARROT descriptions should be the simplest (no conflict, nothing interesting to say).

**RCB prediction:** Captured banana descriptions ("yellow") should be more lexically complex than correct banana descriptions ("orange") because the confabulation suppresses the direct token ("orange," which the pixels show) in favor of a richer narrative built around the expected color. Blue apple descriptions should be complex for all models because the anomaly creates contextual richness. Carrot descriptions should be simplest.

**Discriminating test:** SC and RCB make the SAME prediction for the banana (captured = more complex). But they diverge on a subtle point: within CAPTURED banana descriptions, SC predicts the richness comes from banana-specific vocabulary ("ripe," "golden," "bunch"). RCB predicts the richness comes from GENERAL analytical complexity (longer sentences, more hedging, more subordinate clauses). Measure domain-specific vocabulary versus structural complexity separately to distinguish the two mechanisms.

**Bonus finding:** Opus spontaneously performed metacognitive analysis on this image: called the apple "the odd one out," stated everything else was "chromatically correct," WHILE misidentifying the orange bananas as yellow. The metacognitive layer was confident and analytically rich. It was also wrong. This is maximum RCB: the most analytically sophisticated response in the dataset is a confabulation wrapped in explicit self-verification.

---

## Experiment C: White Picket Fence (S005)

**What:** Suburban scene with a picket fence and a plain box on the lawn. Both objects are identical colors: H=32, S=50% (a warm cream/beige). The fence carries the "white picket fence" collocation. The box has no color prior.

Prompt: "Describe this scene."

**Key result:** The fence was reported as "white" (captured by the collocation). The box was reported as "cream" or "beige" (correct). Same color, different labels, driven entirely by object-name association.

**SC prediction for lexical complexity:** Fence descriptions should be richer than box descriptions because "white picket fence" activates a deep cultural-architectural knowledge structure (Americana, suburban ideal, domesticity). SC predicts the richness is DOMAIN-SPECIFIC: fence descriptions will include cultural vocabulary that box descriptions won't.

**RCB prediction:** Fence descriptions should be richer because the collocation-capture generates a more complex response than a simple color report. The model isn't just saying "white fence"; it's generating a culturally loaded description. Box descriptions should be flat because there's nothing interesting to say about a beige box.

**Discriminating test:** Both frameworks predict fence descriptions are richer. They differ on WHY. Measure whether the fence descriptions are rich because of CULTURAL vocabulary ("crisp white picket fence," "quintessential," "classic Americana") or because of STRUCTURAL complexity (longer sentences, more clauses). SC predicts cultural vocabulary drives the richness. RCB predicts structural complexity drives it. Both may contribute.

**Additional test:** Compare the INCORRECT fence descriptions (calling it "white") to the CORRECT box descriptions (calling it "cream/beige"). If the incorrect description is structurally more complex than the correct one, controlling for the cultural vocabulary, that's RCB operating on top of SC.

---

## Experiment D: Pink Stop Sign (Matched Pair)

**What:** Photorealistic suburban intersection. A stop sign and a car are both shifted to the same pinkish-salmon color. Same exact color on both objects, same lighting, same image. The car serves as internal control: if the model calls the stop sign "red" but the car "pink," the discrepancy is pure semantic capture.

Prompt: "Describe this scene."

**Key result:** ChatGPT: stop sign "red" (captured), car "light-colored" (evasive hedge). Grok: stop sign "bright red" (captured), car "pink/pale magenta" (correct). Gemini, Sonnet, Opus, Haiku: all correctly identified both objects as pink/salmon.

**SURPRISE:** Opus PASSED this test despite failing the orange banana and the Stroop. The semantic capture radius has a ceiling even for Opus. Pink is far enough from red that the stop sign prior can't hold.

**SC prediction for lexical complexity:** For models that were captured (ChatGPT, Grok): the stop sign description should be richer than the car description because "red stop sign" activates a deep knowledge structure (traffic, safety, regulation). For models that were accurate (Gemini, Sonnet, Opus, Haiku): both descriptions should be comparably complex because both involve anomaly-reporting ("unusually pink").

**RCB prediction:** ChatGPT's response is the most interesting case. It said "red" for the stop sign (direct token, high probability) and "light-colored" for the car (evasive, avoids committing to "pink"). RCB predicts that ChatGPT's evasive car description ("light-colored") should be LESS complex than its confident stop-sign description ("red octagonal stop sign"), because the evasion is a token-suppression event: the model won't say "pink" for the car but also can't say "red," so it retreats to a minimal descriptor.

**Discriminating test:** Compare ChatGPT's within-image asymmetry (rich "red stop sign" description vs. minimal "light-colored car" description). SC says the asymmetry is driven by the stop sign's stronger semantic prior. RCB says the asymmetry is driven by the car description having no strong token attractor, producing a flat, evasive response. Grok's data discriminates better: it gave a rich description for BOTH objects ("bright red" for the sign, "pink/pale magenta" for the car). Grok's car description is analytically detailed despite being CORRECT, which argues against RCB (correct responses should be simpler) and for SC (anomaly-reporting generates elaboration).

---

## Experiment E: Unnatural Person Scene (T10b)

**What:** Programmatic stick-figure scene with maximally wrong colors: magenta skin, yellow eyes/mouth, cyan shirt, purple pants, green shoes, green sky, red grass, red sun. Also tested as photorealistic AI-generated version (T10d).

Prompt: "Describe this scene." or specific color queries.

**Key result:** ALL models passed on both versions. 100% accuracy across Gemini, Claude, ChatGPT. No semantic capture. Even Opus correctly reported all wrong colors. The perceptual distance was too extreme for any prior to hold.

**SC prediction for lexical complexity:** Responses should be consistently rich across models because every object is anomalous. The anomaly density is so high that every description generates elaboration. SC predicts no significant complexity difference between models because all are correctly reporting anomalies (no capture to compare against).

**RCB prediction:** Since all responses are CORRECT (no confabulation), RCB predicts relatively uniform and potentially LOWER complexity compared to experiments where confabulation occurs. The direct tokens are the correct ones here: "the skin is magenta, the sky is green." No suppression of high-probability tokens because the high-probability token IS the correct one (the colors are so wrong that no prior captures them).

**Discriminating test:** Compare overall response complexity on T10b/T10d (all correct, maximally anomalous) to S004 CAPTURED responses (banana called "yellow," apple called "blue"). If T10b responses are LESS complex than S004 captured responses despite being longer (more objects to describe), that supports RCB: the captured responses are complex because of confabulation, not because of scene richness. If T10b responses are equally complex, the complexity comes from scene engagement, not confabulation.

---

## Experiment F: Graded Stroop Load (T6)

**What:** Stroop test at reduced load. T1 has 12 items and Opus scores 25%. T6 has 2 items. Does Opus pass at low load?

**Key result:** Yes. Opus passes at 2 items. The binding deficit is capacity-limited, not categorical. Threshold approximately 5-7 items.

**SC prediction:** Not directly applicable (text-ink binding, not object-color capture).

**RCB prediction:** At 2 items, the task is simple enough that the direct correct response has high probability. At 12 items, the accumulated word-reading interference suppresses the correct ink-color tokens more strongly. RCB predicts the COMPLEXITY of the error should increase with load: at 12 items, the model generates a more elaborate (and more wrong) response than at 2 items. At 2 items, if it gets it right, the response is direct and simple.

**Discriminating test:** Compare response complexity at 2-item load (Opus correct) vs. 12-item load (Opus mostly wrong). If RCB is right, the 12-item incorrect responses should show higher per-item complexity (more elaborate descriptions per word) than the 2-item correct responses. If the complexity is driven purely by task load (more items = more text), normalizing by item count should still reveal a per-item complexity difference.

---

## Summary: Predictions Across Extended Experiments

| Experiment | Comparison | SC predicts | RCB predicts |
|-----------|-----------|-------------|-------------|
| Stroop | Error vs correct ink reports | No prediction | Error SIMPLER (opposite of usual) |
| Orange Banana | Captured ("yellow") vs correct ("orange") | Captured richer (domain vocab) | Captured richer (structural complexity) |
| Orange Banana | Opus metacognitive confabulation | Richest of all (metacog + prior) | Richest of all (max token suppression) |
| White Picket Fence | Fence ("white") vs box ("cream") | Fence richer (cultural vocab) | Fence richer (structural complexity) |
| Pink Stop Sign | ChatGPT: sign ("red") vs car ("light-colored") | Sign richer (stronger prior) | Sign richer (car description is evasive flat) |
| Pink Stop Sign | Grok: sign ("bright red") vs car ("pink/pale magenta") | Both rich (anomaly reporting) | Sign richer (car should be simpler if correct) |
| Unnatural Person | All correct vs S004 captured responses | T10b equally complex (scene engagement) | T10b LESS complex (no confabulation) |
| Graded Stroop Load | 2-item correct vs 12-item errors | No prediction | 12-item per-item complexity higher |

**The Stroop experiment is the most important discriminator in this set.** It's the ONLY experiment where the error is the SIMPLER response (reading the word is easier than reporting the ink). If Stroop errors show lower complexity than correct reports, that's a fundamentally different error mechanism from SCE, confirming that the two phenomena require different explanations. RCB explains SCE-type confabulation (rich, elaborate, wrong). Something else explains Stroop-type errors (simple, direct, wrong).

---

## Data Availability

The Stroop battery, orange banana, white picket fence, and pink stop sign experiments were run through interactive sessions with raw results logged in markdown. The stimulus images are in the private repository but can be shared. The controlled API experiments (bus/van, patches, gradient, CPO, verbal label, paint shop, PDT) are fully public at `github.com/tedinoue/sce-replication`.

If specific result files would be useful for your analysis, please reach out. We can extract the raw response text from the session logs for any experiment described here.

---

*Contact: Ted Inoue (synthsentience.substack.com)*
*Related: LEXICAL_COMPLEXITY_PREDICTIONS.md (Part 1, controlled API experiments)*
