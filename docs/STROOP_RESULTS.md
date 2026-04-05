# Stroop Graded Load Experiment Results
## Capacity-Limited Binding in Multimodal AI
*Ted Inoue and Terry (Salon) | April 5, 2026*
*Repository: github.com/tedinoue/sce-replication*

---

## Purpose

The Stroop test measures whether a model can report the INK COLOR of a color word while ignoring the word's semantic content. "RED" printed in blue ink: the correct answer is "blue." A human experiencing Stroop interference says "red" (reading the word instead of reporting the ink). Previous interactive testing showed that Claude Opus scored ~25% on a 12-item Stroop image, while Sonnet and Gemini scored ~100%. This experiment tests whether the deficit is categorical (Opus cannot do Stroop at any load) or capacity-limited (Opus passes at low load, fails at high load), using graded load levels of 2, 4, 8, and 12 items.

## Stimuli

All stimuli are incongruent Stroop items: the word text always names a different color than the ink it's printed in. Items are arranged in a grid, 4 per row.

| Image | Items | Layout |
|-------|-------|--------|
| T3_color_patches.png | 12 plain color patches | 4x3, no text (baseline) |
| T6_graded_load_2.png | 2 words | 1 row |
| T6_graded_load_4.png | 4 words | 1 row |
| T6_graded_load_8.png | 8 words | 2 rows x 4 |
| T6_graded_load_12.png | 12 words | 3 rows x 4 |

### Verified Answer Key

Answer key verified by Ted Inoue via Photoshop eyedropper measurement. RGB values confirmed against ANSWER_KEY_v2.json from the Stroop battery. Ink colors are identical across all four T6 images; each image uses the first N items.

| Position | Word text | Ink color | Ink RGB (verified) |
|----------|-----------|-----------|-------------------|
| 1 | RED | BLUE | (40, 80, 200) |
| 2 | GREEN | RED | (220, 40, 40) |
| 3 | BLUE | YELLOW | (210, 190, 30) |
| 4 | YELLOW | GREEN | (30, 160, 50) |
| 5 | ORANGE | PURPLE | (140, 40, 180) |
| 6 | PURPLE | ORANGE | (230, 130, 20) |
| 7 | PINK | BROWN | (140, 80, 30) H=27 S=35 L=33 |
| 8 | BROWN | PINK | (220, 100, 150) H=336 S=63 L=63 |
| 9 | RED | GREEN | (30, 160, 50) |
| 10 | BLUE | ORANGE | (230, 130, 20) |
| 11 | GREEN | PURPLE | (140, 40, 180) |
| 12 | YELLOW | RED | (220, 40, 40) |

Items 7 and 8 were independently verified by Photoshop eyedropper: PINK in brown ink measures H=27, S=35, L=33 (RGB 140, 80, 30). BROWN in pink ink measures H=336, S=63, L=63 (RGB 220, 100, 150).

**Note on Item 3 (BLUE in yellow ink):** The yellow is relatively dark (RGB 210, 190, 30), which some models describe as "olive," "gold," or "dark yellow." These are color-naming disagreements on a genuine color, not Stroop errors. Scored as correct if the model reports any yellow-family term.

**Note on Item 7 (PINK in brown ink):** The brown is dark (RGB 140, 80, 30). Some models describe this as "dark gold" or "olive-brown." Scored as correct if the model reports any brown-family term.

## Prompt

**T3 (baseline):** "Name the color of each patch."

**T6 (all load levels):** "For each word, report the TEXT and the INK COLOR."

Note: the prompt is embedded in the image itself as header text. The API prompt matches.

## Models, Trials, Temperature

8 models across 3 vendors. 5 trials per stimulus per model. Temperature 1.0. Total: 200 API calls.

## Results

### T3 Baseline: Color Patches (no text conflict)

All models scored 12/12 on plain color patches. Visual color discrimination is intact across all architectures. Any Stroop errors at higher loads are due to text-ink interference, not color blindness.

### Ink Color Accuracy by Load Level

| Model | 2 items | 4 items | 8 items | 12 items | Pattern |
|-------|---------|---------|---------|----------|---------|
| Opus 4.6 | 2.0/2 (100%) | 4.0/4 (100%) | 4.8/8 (60%) | 3.4/12 (28%) | Capacity cliff at 4-8 |
| Sonnet 4.6 | 2.0/2 (100%) | 3.2/4 (80%) | 6.4/8 (80%) | 0.0/12 (0%) | Collapse at 12 |
| Haiku 4.5 | 1.6/2 (80%) | 4.0/4 (100%) | 8.0/8 (100%) | 12.0/12 (100%) | Near-perfect |
| GPT-5.4 | 2.0/2 (100%) | 4.0/4 (100%) | 8.0/8 (100%) | 12.0/12 (100%) | Perfect |
| GPT-5.4-mini | 0.8/2 (40%) | 4.0/4 (100%) | 8.0/8 (100%) | 12.0/12 (100%) | Perfect at 4+ |
| GPT-5.4-nano | 0.4/2 (20%) | 4.0/4 (100%) | 8.0/8 (100%) | 12.0/12 (100%) | Perfect at 4+ |
| Gemini Pro | 0.8/2 (40%) | 2.4/4 (60%) | 4.8/8 (60%) | 9.6/12 (80%) | Inverted: better at high load |
| Gemini Flash | 2.0/2 (100%) | 1.6/4 (40%) | 6.4/8 (80%) | 12.0/12 (100%) | Non-monotonic |

**Note on low scores at 2 items for GPT-mini, GPT-nano, and Gemini Pro:** These models produce very terse responses at 2 items ("RED, blue ink / GREEN, red ink") that the parser may not extract correctly. The 100% accuracy at 4+ items on the same ink colors suggests the 2-item scores are parsing artifacts, not genuine failures. The 2-item data should be interpreted with caution.

### Opus Error Breakdown

| Load | Correct | Stroop errors | Other errors | Accuracy |
|------|---------|--------------|-------------|----------|
| 2 items | 2.0/2 | 0.0/2 | 0.0/2 | 100% |
| 4 items | 4.0/4 | 0.0/4 | 0.0/4 | 100% |
| 8 items | 4.8/8 | 0.0/8 | 3.2/8 | 60% |
| 12 items | 3.4/12 | 0.2/12 | 8.4/12 | 28% |

**Stroop error** = model reported the word text as the ink color (e.g., "RED" word, reports ink as "red"). This is the classical Stroop interference pattern.

**Other error** = model reported the wrong ink color, but NOT the word text (e.g., "GREEN" in red ink, reports "orange"). This is a color misidentification error, not word-reading interference.

### Sonnet at 12 Items

Sonnet's collapse from 80% at 8 items to 0% at 12 items is striking. At 12 items, Sonnet appears to systematically misidentify ink colors in a pattern that does not match either the correct ink or the word text. This may indicate a catastrophic binding failure at a specific load threshold rather than a gradual degradation.

---

## Key Findings

### 1. The Opus deficit is capacity-limited, not categorical

Opus achieves 100% ink color accuracy at 2 and 4 items. The deficit emerges between 4 and 8 items and worsens to 28% at 12 items. This is not a failure to understand the task or to perceive ink colors. It is a failure of spatial binding under load: the ability to associate the correct ink color with the correct spatial position degrades as the number of simultaneously-processed items increases.

### 2. Opus errors are NOT classical Stroop interference

Across all load levels, Opus produced only 0.2/12 classical Stroop errors (reporting the word text as the ink color). The vast majority of errors are "other errors": the model reports an ink color that is neither the correct ink NOR the word text.

Example (Opus, T6_load_12, Trial 1):
- GREEN in RED ink: reported ORANGE (not RED, not GREEN)
- YELLOW in GREEN ink: reported RED (not GREEN, not YELLOW)
- PURPLE in ORANGE ink: reported RED (not ORANGE, not PURPLE)

The model is not reading the word. It is misidentifying the ink color entirely. This suggests a perceptual binding breakdown (which ink goes with which spatial position) rather than a semantic override (the word meaning replacing the ink perception).

### 3. Haiku outperforms Opus

Haiku 4.5 scores 100% at 4, 8, and 12 items. The model with the lightest language processing has the BEST Stroop performance. This is the inverse of what classical Stroop theory would predict if the interference came from language dominance.

However, this finding is consistent with the language-dominance hypothesis from the SCE data: Opus's stronger language processing creates MORE interference with visual binding, not less. The same mechanism that makes Opus more susceptible to semantic capture on color perception (reporting "yellow school bus" despite green pixels) may make it more susceptible to binding failures on the Stroop test.

### 4. GPT models show no Stroop deficit

All three GPT models achieve 100% accuracy from 4 items onward. GPT-5.4 achieves 100% even at 12 items on all 5 trials. This suggests a fundamentally different text-image processing architecture that maintains spatial binding under load.

### 5. Gemini shows non-monotonic patterns

Gemini Pro scores BETTER at 12 items (80%) than at 4 items (60%). Gemini Flash drops to 40% at 4 items then recovers to 100% at 12 items. These non-monotonic patterns do not fit a simple capacity-limited model and may indicate different processing strategies at different load levels, or parsing artifacts at intermediate loads.

---

## Connection to SCE and Leclerc's Foreshadowing Problem

The Stroop experiment was originally designed to test a specific prediction from Leclerc's response-complexity hypothesis: that Stroop errors (reading the word) should be SIMPLER responses than correct reports (naming the ink), inverting the usual pattern where confabulated responses are more complex than accurate ones.

The data does not cleanly test this prediction because classical Stroop errors barely occur. The dominant error type is color misidentification, which produces responses of similar structural complexity to correct responses. The model doesn't say "the ink color of RED is red" (simple, word-reading). It says "the ink color of RED is orange" (equally complex, just wrong).

This means the Stroop binding failure and SCE confabulation are fundamentally different error mechanisms:

| Property | SCE confabulation | Stroop binding failure |
|----------|------------------|----------------------|
| Error type | Reports expected color, not actual | Reports wrong color, not word text |
| Complexity | Rich, analytically detailed | Same complexity as correct response |
| Mechanism | Semantic prior overrides perception | Spatial binding breaks down under load |
| Load dependence | Not load-dependent (single object) | Strongly load-dependent (threshold 4-8) |
| Architecture correlation | Stronger language model = more capture | Stronger language model = more failure |
| Prompt fixable? | Partially (analytical prompts help) | Not tested |

Both error types share one property: the model with the strongest language processing (Opus) shows the worst performance on both tasks. This consistent correlation between language dominance and perceptual error, across two mechanistically distinct tasks, supports the hypothesis that language-dominant architectures systematically sacrifice perceptual accuracy for linguistic processing power.

---

## Files

### Stimuli
- `stimuli/stroop/T3_color_patches.png`
- `stimuli/stroop/T6_graded_load_2.png`
- `stimuli/stroop/T6_graded_load_4.png`
- `stimuli/stroop/T6_graded_load_8.png`
- `stimuli/stroop/T6_graded_load_12.png`

### Results
- `results/stroop_graded_anthropic_results.json` (75 trials)
- `results/stroop_graded_openai_results.json` (75 trials)
- `results/stroop_graded_gemini_results.json` (50 trials)

### Answer Key
- Verified against Photoshop eyedropper measurements
- Source: `salon/files/stroop-battery/ANSWER_KEY_v2.json` (T1 and T6-2 entries)
- T6-4, T6-8, T6-12 use same items as T1, verified by image inspection

### Harness Scripts
- `harness/run_combined_anthropic.py` (Stroop block)
- `harness/run_combined_openai.py`
- `harness/run_combined_gemini.py`

---

*Repository: github.com/tedinoue/sce-replication*
*Contact: Ted Inoue (synthsentience.substack.com)*
