# Prompt Specificity Analysis — Claude Models
## S003 (Bus H=51°, Van H=41°), 6 prompt levels, 3 trials each, T=1.0
## Date: 03-21-2026

---

## Scoring Key

- **D✓** = Detected difference AND correct direction (van warmer, bus cooler)
- **D✗** = Detected difference, WRONG direction (bus called warmer — directional shield)
- **D-** = Detected difference, no directional claim
- **S** = Said same color (full capture)
- **--** = No color mention

## Per-Trial Results

| Prompt | Level | Opus T1-T3 | Sonnet T1-T3 | Haiku T1-T3 |
|---|---|---|---|---|
| PS00 | Describe this scene | -- -- D✗ | S D✗ D✗ | -- -- -- |
| PS01 | Describe the vehicles | -- D- -- | S S S | S S S |
| PS02 | Describe the colors | D✗ D✗ D✗ | S D- D✗ | S S S |
| PS03 | Compare: same or different? | D✗ S S | S S S | S S S |
| PS04 | Analyze hue: warmer/cooler? | D✓ D✓ D✓ | D✗ D✗ D✗ | S D✗ D✗ |
| PS05 | Measure hue in degrees | D✗ D✓ D✓ | D✗ D✗ D✓ | -- D✗ D✗ |

## Correct Direction Rate (D✓ / Total)

| Prompt | Description | Opus | Sonnet | Haiku |
|---|---|---|---|---|
| PS00 | Describe this scene | 0/3 | 0/3 | 0/3 |
| PS01 | Describe the vehicles | 0/3 | 0/3 | 0/3 |
| PS02 | Describe the colors | 0/3 | 0/3 | 0/3 |
| PS03 | Compare: same or different? | 0/3 | 0/3 | 0/3 |
| PS04 | Analyze hue: warmer/cooler? | **3/3** | 0/3 | 0/3 |
| PS05 | Measure hue in degrees | 2/3 | 1/3 | 0/3 |

## Key Findings

### 1. Zero correct direction through PS03 across all models
Asking about color (PS02) and even forcing comparison (PS03, "same or different?") produces zero correct directional judgments. The prior shapes every interpretation.

### 2. PS02 activates the directional shield, making Opus WORSE
At PS00, Opus didn't mention color (2/3 trials). At PS02, it detected a difference in 3/3 trials but got direction wrong in 3/3. Asking about color made the model look harder and get captured harder. Detection without accuracy is worse than silence.

### 3. PS03 ("same or different?") produces "same" from Sonnet and Haiku
Despite being directly asked to compare, both mid/small models certify the colors as identical in every trial. The prior is strong enough to override an explicit comparison instruction.

### 4. Only PS04 breaks through, and only for Opus
"Carefully analyze the exact hue. Which is warmer, which is cooler?" produces 3/3 correct from Opus. The analytical framing with explicit warm/cool vocabulary triggers accurate perception. But Sonnet goes 0/3 (wrong direction every time) and Haiku 0/3.

### 5. PS05 (measurement) doesn't reliably fix direction
Opus 2/3, Sonnet 1/3, Haiku 0/3. Even measuring in degrees, the directional shield persists in most trials for most models. The prior pulls hue estimates toward canonical values.

### 6. Haiku is immune to prompt specificity
Zero correct at every prompt level. Not one trial across 18 runs produced a correct directional judgment from Haiku. The smallest model's prior is impervious to prompt intervention at this hue shift (+10°).

## Theoretical Implications

The prompt specificity gradient reveals that SCE operates at two levels:

**Level 1: Detection.** Can the model notice a color difference? This breaks at PS02 for Opus/Sonnet. Prompt specificity helps here.

**Level 2: Direction.** Can the model correctly identify which object has which color? This barely responds to prompt specificity at all. The prior doesn't prevent seeing. It shapes the interpretation of what is seen.

This is the directional shield from the published paper, now quantified across prompt levels. The practical implication: "describe the colors" is not a sufficient intervention. Even "measure the hue" is unreliable. Only the most analytically demanding prompt (PS04) on the most capable model (Opus) consistently produces correct direction.

## Raw Data
results/specificity_s003_claude.json

---

*Detection is easy. Direction is the hard problem.*
