# Cross-Vendor Prompt Specificity Analysis
## 5 Models, 2 Vendors, 6 Prompt Levels, S003 (+10° split)
## Date: 03-21-2026

---

## Correct Direction Rate (D✓ / Total)

Ground truth: Van is warmer (H=41°), Bus is cooler (H=51°).

| Prompt | Description | Opus | Sonnet | Haiku | Gem Pro | Gem Flash |
|---|---|---|---|---|---|---|
| PS00 | Describe this scene | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| PS01 | Describe the vehicles | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| PS02 | Describe the colors | 0/3 | 0/3 | 0/3 | 0/3 | **2/3** |
| PS03 | Compare: same or different? | 0/3 | 0/3 | 0/3 | 0/3 | 0/3 |
| PS04 | Analyze hue: warmer/cooler? | **3/3** | 0/3 | 0/3 | 1/3 | 1/3 |
| PS05 | Measure hue in degrees | 2/3 | 1/3 | 0/3 | 0/3 | 0/3 |

## Full Per-Trial Scoring

### Claude Models

| Prompt | Opus T1-T3 | Sonnet T1-T3 | Haiku T1-T3 |
|---|---|---|---|
| PS00 | -- -- D✗ | S D✗ D✗ | -- -- -- |
| PS01 | -- D- -- | S S S | S S S |
| PS02 | D✗ D✗ D✗ | S D- D✗ | S S S |
| PS03 | D✗ S S | S S S | S S S |
| PS04 | D✓ D✓ D✓ | D✗ D✗ D✗ | S D✗ D✗ |
| PS05 | D✗ D✓ D✓ | D✗ D✗ D✓ | -- D✗ D✗ |

### Gemini Models

| Prompt | Gem Pro T1-T3 | Gem Flash T1-T3 |
|---|---|---|
| PS00 | S D- D- | D- D- D- |
| PS01 | -- D- -- | S S S |
| PS02 | -- -- -- | D✓ D✓ D✗ |
| PS03 | D✗ D✗ D✗ | D✗ D✗ D✗ |
| PS04 | D✓ D✗ D✗ | D✗ D✓ D✗ |
| PS05 | D✗ -- -- | -- D- D- |

## Key Findings

### 1. PS03 ("same or different?") is the strongest finding
0/15 correct direction across all 5 models when asked to directly compare. Every model that detects a difference gets the direction wrong. The forced comparison activates the directional shield universally. This is cross-architectural: Claude and Gemini fail identically.

### 2. Opus stands alone at PS04
3/3 correct with "analyze the exact hue, warmer/cooler?" No other model exceeds 1/3 at any prompt level. The analytical framing with explicit warm/cool vocabulary breaks through the directional shield, but only for the most capable Claude model.

### 3. PS05 (measurement) is WORSE than PS04 (analytical framing)
Opus drops from 3/3 to 2/3. Pro drops from 1/3 to 0/3. Flash drops from 1/3 to 0/3. Requesting hue in degrees may anchor the model to canonical numeric values (e.g., "school bus yellow is ~45°") rather than prompting fresh visual assessment. The measurement prompt was supposed to be the analytical bypass. It isn't, at least not for direction.

### 4. Gemini Flash shows unexpected PS02 success
2/3 correct at "describe the colors." No Claude model achieves this. Flash may have a weaker school bus color prior or different vision integration that allows color-focused prompts to partially bypass the directional shield. However, this drops to 0/3 at PS03 (forced comparison), suggesting the success is fragile.

### 5. The directional shield is cross-architectural
The pattern (detection without correct direction) appears identically in Claude and Gemini models. Both vendors' models detect color differences when asked about them, and both vendors' models assign warmth to the school bus regardless of pixel reality. The prior operates the same way across architectures.

### 6. Haiku is immune to all prompt interventions
0/3 at every prompt level, every trial. 0/18 total. The smallest model's prior cannot be broken by any prompt specificity level at this hue shift.

## Implications

### For the published paper
"Ask models to measure, not describe" is a useful heuristic for detection, but it does NOT reliably fix directional accuracy. The practical recommendation needs refinement: measurement mode helps with whether-different but not with which-direction.

### For practitioners
At a 10° hue shift (subtle but real), no standard prompt reliably produces correct color comparisons across models. Only the most capable model (Opus) with the most analytically demanding prompt (PS04) consistently breaks through. If your application depends on subtle color comparison, you cannot rely on any current VLM without stimulus-specific validation.

### For theory
The two-level model of SCE is confirmed cross-architecturally:
- Level 1 (detection): responds to prompt specificity. PS02 breaks detection for most models.
- Level 2 (direction): barely responds to prompt specificity. The prior shapes interpretation even when the model is explicitly analyzing color.

The directional shield is the harder problem, and it is universal.

## Raw Data
- results/specificity_s003_claude.json (Claude: 54 trials)
- results/gemini_specificity_results.json (Gemini: 36 trials)

---

*Detection is easy. Direction is the hard problem. And it's the same hard problem everywhere.*
