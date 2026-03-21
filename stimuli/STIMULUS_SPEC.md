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

## STIMULUS SET B: BANANA / CARROT

### Scene Composition

Individual food items on a neutral surface (white plate, light cutting board, or plain countertop). One object per image. Clean, well-lit, no distracting background elements. The object should fill roughly 40-60% of the frame.

### Image Creation Method

**For the orange banana (S004):** Start with a photo of a normal yellow banana. Use HSL adjustment to shift the banana's hue from yellow (~55°) to orange (~30°). Keep saturation and brightness natural. Feather the mask so the color shift blends naturally with the banana's natural shading. The result should look like a banana that happens to be orange.

**For the orange carrot (S005):** Use a photo of a normal orange carrot. Do NOT modify its color. This is the control. The carrot should be approximately the same orange hue as the modified banana in S004. If needed, adjust the carrot's hue slightly so that S004 and S005 are within 3° of each other.

**For the yellow banana (S006):** Use a photo of a normal yellow banana. Do NOT modify its color. This is the prior-consistent control.

### Color Specifications

**S004.png — Orange banana (SCE test)**
- Target hue: ~30° (orange range)
- Natural saturation and brightness
- Purpose: Banana IS orange. "Yellow" report = semantic capture.
- Ground truth: Orange. Approximately H=30°.

**S005.png — Orange carrot (matched-pair control)**
- Target hue: ~30° (match S004 as closely as possible)
- Natural, unmodified carrot
- Purpose: Carrot IS orange. No semantic conflict. "Orange" report expected.
- Ground truth: Orange. Approximately H=30°.
- KEY: The diagnostic is comparing S004 and S005 responses. Same orange, different objects.

**S006.png — Yellow banana (prior-consistent control)**
- Natural yellow, unmodified
- Hue: ~55° (natural banana yellow)
- Purpose: No conflict. Prior and reality agree. "Yellow" report correct.
- Ground truth: Yellow. Approximately H=55°.

---

## STIMULUS SET C: CUBE + FENCE (STRETCH GOAL)

**S007.png — White picket fence collocation test**
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

| Image | Bus Hue | Van Hue | Shift from canonical | Expected behavior |
|---|---|---|---|---|
| S001.png | 43° | 43° | 0° (same) | Control. Reuse from Set A. |
| G001.png | 48° | 43° | +5° | Likely still captured. Subtle shift. |
| S003.png | 53° | 43° | +10° | Reuse from Set A (identical conditions). Near breakpoint for some models. |
| G003.png | 58° | 43° | +15° | Approaching yellow-green. Some models may begin detecting. |
| G004.png | 63° | 43° | +20° | Yellow-green range. Breakpoint for most models. |
| G005.png | 68° | 43° | +25° | Clearly shifting. Most models should detect. |
| G006.png | 73° | 43° | +30° | Chartreuse. Strong visual departure. Near-ceiling detection. |

Note: S001 serves as the 0° baseline. S003 serves as the +10° step (bus=53°, van=43° is the same condition). No duplicate images.

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

| Condition | Stimulus | Prompt | Trials |
|---|---|---|---|
| CG01 | G001.png (48°) | P01 | 10 |
| CG02 | S003.png (53°) | P01 | 10 |
| CG03 | G003.png (58°) | P01 | 10 |
| CG04 | G004.png (63°) | P01 | 10 |
| CG05 | G005.png (68°) | P01 | 10 |
| CG06 | G006.png (73°) | P01 | 10 |

Plus C01 (S001, 43°) as the 0° baseline = 7 gradient points.

**Total gradient calls:** 7 steps x 5 models x 10 trials = 350 API calls
**Combined with core study:** 600 + 300 = 900 total API calls (CG02 shares S003 trials from C05, saving 50 calls)

Note: CG02 uses S003.png, which is also used in core condition C05. The gradient trial data for the +10° step can be drawn from C05 results, or run independently. If run independently, the C05 and CG02 results also serve as an internal replication check.


## MEASURED VALUES (fill in after image creation/verification)

### Set A
| Image | Vehicle | Measured H | Measured S | Measured V | Notes |
|---|---|---|---|---|---|
| S001 | Bus | | | | |
| S001 | Van | | | | |
| S002 | Bus | | | | |
| S002 | Van | | | | |
| S003 | Bus | | | | |
| S003 | Van | | | | |

### Set B
| Image | Object | Measured H | Measured S | Measured V | Notes |
|---|---|---|---|---|---|
| S004 | Banana | | | | |
| S005 | Carrot | | | | |
| S006 | Banana | | | | |

### Set C
| Image | Object | Measured H | Measured S | Measured V | Notes |
|---|---|---|---|---|---|
| S007 | Fence | | | | |
| S007 | Cube | | | | |

### Set D (Gradient)
| Image | Bus H | Van H | Verified Shift | Notes |
|---|---|---|---|---|
| G001 | 48° target | 43° target | | |
| (S003) | 53° target | 43° target | | Reuse S003 from Set A |
| G003 | 58° target | 43° target | | |
| G004 | 63° target | 43° target | | |
| G005 | 68° target | 43° target | | |
| G006 | 73° target | 43° target | | |

---

*All stimulus images go in the `stimuli/` directory of this repo.*
*URL pattern: https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli/{filename}*
