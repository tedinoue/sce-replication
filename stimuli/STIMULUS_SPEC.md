# Stimulus Specification
## SCE Color Replication Study
## Last updated: 03-21-2026

---

## General Requirements

- **Resolution:** 700 x 500 pixels
- **Format:** PNG (lossless, no JPEG compression artifacts to confuse hue readings)
- **Background:** Neutral. Outdoor daylight scene, consistent across all images in a set.
- **Lighting:** Even, no dramatic shadows or color casts. Overcast daylight ideal.
- **File naming:** S001_description.png, S002_description.png, etc.

---

## STIMULUS SET A: SCHOOL BUS + PANEL VAN

These images already exist from the original study. Reuse them at 700x500.

### Scene Composition

Same scene for all three images: a school bus and a plain panel van (no branding, no text) parked side by side or near each other. Both vehicles clearly identifiable. No other strongly colored objects competing for attention.

### Color Specifications (HSV color space)

**Canonical "school bus yellow" (warm):**
- Hue: 43°
- Saturation: 85-95%
- Value/Brightness: 85-95%

**Cooler shift target:**
- Hue: 53° (10° cooler than canonical, shifting toward lemon/green-yellow)
- Saturation: same as canonical
- Value: same as canonical

A 10° hue shift is detectable by pixel sampling, visible to a careful human observer, but ambiguous enough that AI models routinely misreport it. This matches the effect sizes in the published study.

### The Three Images

**S001.png — Control (both canonical)**
- Bus: H=43°
- Van: H=43°
- Purpose: No color difference exists. Any reported difference is fabrication.
- Ground truth: Both vehicles are the same yellow.

**S002.png — Prior-consistent split**
- Bus: H=43° (canonical, warm)
- Van: H=53° (shifted cooler)
- Purpose: Bus IS warmer. Correct answer aligns with "school buses are warm golden yellow" prior.
- Ground truth: Bus is warmer (lower hue number = warmer yellow). Difference is 10°.
- NOTE: A model that always defaults to "bus is warmer" will get this one RIGHT. That's why S003 exists.

**S003.png — Prior-conflicting split (KEY TEST)**
- Bus: H=53° (shifted cooler)
- Van: H=43° (canonical, warm)
- Purpose: Bus is COOLER. Correct answer CONFLICTS with the semantic prior.
- Ground truth: Van is warmer (lower hue number). Difference is 10°.
- NOTE: This is the critical matched-pair test. If the model reports the bus as warmer here, the semantic prior is overriding perception. The asymmetry between S002 and S003 accuracy rates is the primary measure.

---

## STIMULUS SET B: COMPOSITE FOOD SCENE

### Scene Composition

Single composite image containing three objects at three conflict levels on a kitchen counter:
- Orange bananas in a bowl (shifted from natural yellow, strong prior conflict)
- Orange carrot on a cutting board with knife (natural color, no conflict)
- Blue apple on the table (impossible color, extreme conflict)

Neutral background, even lighting, natural kitchen composition. The knife and cutting board sell the "kitchen scene" framing so the model is not primed to look for color anomalies.

### Image Creation Method

Base scene: AI-generated kitchen still life. Banana hue shifted from natural yellow (~45°) to orange (30°) with saturation 70%. Carrot left at natural orange. Apple shifted to blue. All other elements (wood table, ceramic bowl, knife) at natural colors.

### S004.png — Three-object composite (single image, three conflict levels)

| Object | Measured Hue | Natural Hue | Conflict Type | Ground Truth |
|---|---|---|---|---|
| Banana | H=30°, S=70% | ~45° (natural yellow) | Nearby wrong. 15° shift toward orange. | Orange. "Yellow" report = capture. |
| Carrot | H=23° | ~23° (natural orange) | No conflict. Carrots are orange. | Orange. Control object. |
| Apple | H=205° | ~0-10° (red) or ~120° (green) | Impossible wrong. No apple is blue. | Blue. Ceiling test. |

### What This Tests

Three conflict levels in one prompt:

1. **No conflict (carrot):** Object is its expected color. Baseline for accurate color reporting.
2. **Plausible mismatch (banana):** Object is a wrong but nearby color (orange vs yellow, 15° shift). Tests whether the "bananas are yellow" prior overrides perception. The carrot at H=23° and banana at H=30° are in the same orange neighborhood, making this a strong matched pair: same color family, different objects, predicted different reports.
3. **Impossible mismatch (apple):** Object is a categorically wrong color (blue vs red/green). Tests what happens when the prior cannot plausibly override. Expected: correct report, possibly with anomaly flagging.

### Preliminary Results (quick test, N=1 per model)

| Model | Carrot | Banana | Apple |
|---|---|---|---|
| Grok | "bright orange" (correct) | "ripe yellow" (captured) | "blue" (correct, noted) |
| Opus | "orange" (correct) | "yellow" (captured) | "blue" (correct, flagged as anomalous) |
| Gemini | TBD | avoided color ("a bunch of bananas") | TBD |
| Haiku | avoided color | avoided color ("ripe bananas") | "blue" (correct) |

Opus spontaneously performed metacognitive analysis: called the apple "the odd one out," stated everything else was "chromatically correct," including the bananas it had just misidentified as yellow. Confident, analytically defended capture.

---

## STIMULUS SET C: CUBE + FENCE (STRETCH GOAL)

**S005.png — White picket fence collocation test**
- Fence: ~H=39°, S=15%, V=75% (cream, not white)
- Cube: ~H=39°, S=15%, V=75% (same cream)
- Purpose: "White picket fence" collocation predicts fence reported as white, cube as cream/beige, despite identical color.
- Ground truth: Both are the same cream/off-white.

---

---

## STIMULUS SET D: BREAKPOINT GRADIENT SERIES

The gradient series maps the capture-to-detection transition curve. The bus hue shifts in 5° increments from canonical (43°) toward green while the van remains at canonical. At each step, N=10 trials determines whether the model still reports the bus as "yellow" or begins acknowledging the shift. The resulting curve characterizes each model's breakpoint, the hue distance at which the semantic prior loses its grip.

### Scene Composition

Identical to Set A. Same base image, same van. Only the bus hue changes.

### The Gradient

| Image | Bus Hue (measured) | Van Hue (measured) | Shift from baseline | Expected behavior |
|---|---|---|---|---|
| S001.png | 42° | 42° | 0° | Control. Reuse from Set A. |
| G001.png | 47° | 42° | +5° | Likely still captured. Subtle shift. |
| S003.png | 51° | 41° | +9-10° | Reuse from Set A. Near breakpoint for some models. |
| G003.png | 58° | 42° | +16° | Approaching yellow-green. Some models may begin detecting. |
| G004.png | 63° | 42° | +21° | Yellow-green range. Breakpoint for most models. |
| G005.png | 69° | 42° | +27° | Clearly shifting. Most models should detect. |
| G006.png | 73° | 42° | +31° | Chartreuse. Strong visual departure. Near-ceiling detection. |

Note: S001 serves as the 0° baseline. S003 serves as the ~+10° step (same condition as core Set A prior-conflicting split). No G002 image exists. Measurements are Photoshop eyedropper values from center of vehicle side panel (ground truth). Variation of ~2° across vehicle surface is normal.

### Image Creation

Same base scene as S001/S002/S003. For each gradient step:
1. Start from the base scene with both vehicles at H=43°
2. Mask the bus body
3. Shift bus hue to target value
4. Keep van at H=43°
5. Export at 700x500 PNG

### What This Measures

At each gradient step, for each model, across 10 trials:
- **Capture rate:** What percentage of trials report the bus as "yellow" or "warm yellow"?
- **Detection rate:** What percentage correctly note the bus is cooler/greener than the van?
- **Breakpoint:** The hue shift at which detection rate crosses 50% (interpolated from the curve).

The breakpoint is model-specific. The original study suggests Claude Opus breaks later (stronger capture) than ChatGPT (weaker capture). N=10 trials per step gives error bars. The sigmoid fit gives the breakpoint estimate.

### Gradient Conditions (all use P01 narrative prompt only)

| Condition | Stimulus | Bus H (measured) | Prompt | Trials |
|---|---|---|---|---|
| CG01 | G001.png | 47° | P01 | 10 |
| CG02 | S003.png | 51° | P01 | 10 |
| CG03 | G003.png | 58° | P01 | 10 |
| CG04 | G004.png | 63° | P01 | 10 |
| CG05 | G005.png | 69° | P01 | 10 |
| CG06 | G006.png | 73° | P01 | 10 |

Plus C01 (S001, 43°) as the 0° baseline = 7 gradient points.

**Total gradient calls:** 7 steps x 5 models x 10 trials = 350 API calls
**Combined with core study:** 600 + 300 = 900 total API calls (CG02 shares S003 trials from C05, saving 50 calls)

CG02 uses S003.png (same image as core condition C05). Run independently for internal replication check.


## MEASURED VALUES (fill in after image creation/verification)

### Set A (Photoshop point-sample, center of side panel)
| Image | Vehicle | Measured H | Notes |
|---|---|---|---|
| S001 | Bus | 42° | Control |
| S001 | Van | 42° | Control |
| S002 | Bus | 42° | Canonical warm |
| S002 | Van | 51° | Shifted cooler |
| S003 | Bus | 51° | Shifted cooler (corrected 03-21) |
| S003 | Van | 41° | Near-canonical |

### Set B (Photoshop eyedropper)
| Image | Object | Measured H | Notes |
|---|---|---|---|
| S004 | Banana | 30° (S=70%) | Shifted from natural ~45°. 15° toward orange. |
| S004 | Carrot | 23° | Natural orange, unmodified. |
| S004 | Apple | 205° | Shifted to blue. Impossible color. |

### Set C
| Image | Object | Measured H | Measured S | Measured V | Notes |
|---|---|---|---|---|---|
| S005 | Fence | | | | |
| S005 | Cube | | | | |

### Set D (Gradient, Photoshop point-sample, center of side panel)
| Image | Bus H | Van H | Bus Shift from S001 | Notes |
|---|---|---|---|---|
| G001 | 47° | 42° | +5° | |
| G002 | 51° | 42° | +9° | Alternate for S003 condition. 1° van difference. |
| (S003) | 51° | 41° | +9° | Reuse S003 from Set A for +10° gradient point |
| G003 | 58° | 42° | +16° | |
| G004 | 63° | 42° | +21° | |
| G005 | 69° | 42° | +27° | |
| G006 | 73° | 42° | +31° | |

Note: Measured values differ slightly from targets due to natural variation across
the vehicle surface. All measurements taken at center of side panel. Variation of
+/-2° across the vehicle body is expected. These measured values are ground truth
for scoring purposes.

---

*All stimulus images go in the `stimuli/` directory of this repo.*
*URL pattern: https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli/{filename}*
