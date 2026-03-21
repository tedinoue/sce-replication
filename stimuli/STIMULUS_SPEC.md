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

### Scene Composition

Same scene for all three images: a school bus and a plain panel van (no branding, no text) parked side by side or near each other in a parking lot or roadside setting. Both vehicles should be clearly identifiable as their respective types. The van should be generic, not a branded delivery vehicle. No other strongly colored objects competing for attention.

### Image Creation Method

Start with a photograph or AI-generated base image of a yellow school bus and yellow panel van together. Then use image editing software (Photoshop, GIMP, or equivalent) to precisely control the hue of each vehicle using HSL/HSV adjustment layers masked to each vehicle.

### Color Specifications (HSV color space)

**Canonical "school bus yellow":**
- Hue: 48° (this is the standard National School Bus Glossy Yellow, approximately)
- Saturation: 85-95%
- Value/Brightness: 85-95%

**Cooler shift target:**
- Hue: 41° (7° cooler than canonical, shifting toward lemon/green-yellow)
- Saturation: same as canonical
- Value: same as canonical

A 7° hue shift is detectable by pixel sampling but subtle to visual inspection. This matches the effect sizes in the original study.

### The Three Images

**S001_bus_van_same.png — Control (both canonical)**
- Bus: H=48°, S=90%, V=90%
- Van: H=48°, S=90%, V=90%
- Purpose: No color difference exists. Any reported difference is fabrication.
- Ground truth: Both vehicles are the same yellow.

**S002_bus_warm_van_cool.png — Prior-consistent split**
- Bus: H=48° (canonical, warm)
- Van: H=41° (shifted cooler)
- Purpose: Bus IS warmer. Correct answer aligns with "school buses are warm golden yellow" prior.
- Ground truth: Bus is warmer (higher hue value). Difference is 7°.
- NOTE: A model that always guesses "bus is warmer" will get this one RIGHT. That's why S003 exists.

**S003_bus_cool_van_warm.png — Prior-conflicting split (KEY TEST)**
- Bus: H=41° (shifted cooler)
- Van: H=48° (canonical, warm)
- Purpose: Bus is COOLER. Correct answer CONFLICTS with the semantic prior.
- Ground truth: Van is warmer (higher hue value). Difference is 7°.
- NOTE: This is the critical test. If the model reports the bus as warmer here, the semantic prior is overriding perception.

### Verification

After creating each image, verify with an eyedropper/color picker tool:
1. Sample 5+ pixels from each vehicle's main body panel (avoid highlights, shadows, edges)
2. Record average H, S, V values
3. Confirm the hue difference matches spec (0° for S001, 7° for S002/S003)
4. Document measured values in this file under MEASURED VALUES below

---

## STIMULUS SET B: BANANA / CARROT

### Scene Composition

Individual food items on a neutral surface (white plate, light cutting board, or plain countertop). One object per image. Clean, well-lit, no distracting background elements. The object should fill roughly 40-60% of the frame.

### Image Creation Method

**For the orange banana (S004):** Start with a photo of a normal yellow banana. Use HSL adjustment to shift the banana's hue from yellow (~55°) to orange (~30°). Keep saturation and brightness natural. The result should look like a banana that happens to be orange, not like a digitally manipulated image with harsh edges or unnatural gradients. Feather the mask if needed so the color shift blends naturally with the banana's natural shading.

**For the orange carrot (S005):** Use a photo of a normal orange carrot. Do NOT modify its color. This is the control. The carrot should be approximately the same orange hue as the modified banana in S004. If needed, adjust the carrot's hue slightly so that S004 and S005 are within 3° of each other in hue.

**For the yellow banana (S006):** Use a photo of a normal yellow banana. Do NOT modify its color. This is the prior-consistent control.

### Color Specifications

**S004_banana_orange.png — Orange banana (SCE test)**
- Target hue: ~30° (orange range)
- Natural saturation and brightness
- Purpose: Banana IS orange. "Yellow" report = semantic capture.
- Ground truth: Orange. Approximately H=30°.

**S005_carrot_orange.png — Orange carrot (matched-pair control)**
- Target hue: ~30° (match S004 as closely as possible)
- Natural, unmodified carrot
- Purpose: Carrot IS orange. No semantic conflict. "Orange" report expected.
- Ground truth: Orange. Approximately H=30°.
- KEY: The diagnostic is comparing S004 and S005 responses. Same orange, different objects.

**S006_banana_yellow.png — Yellow banana (prior-consistent control)**
- Natural yellow, unmodified
- Hue: ~55° (natural banana yellow)
- Purpose: No conflict. Prior and reality agree. "Yellow" report correct.
- Ground truth: Yellow. Approximately H=55°.

### Verification

Same as Set A: eyedropper 5+ sample points per object, record average HSV, confirm S004 and S005 are within 3° of each other.

---

## STIMULUS SET C: CUBE + FENCE (STRETCH GOAL)

### Scene Composition

A solid-colored cube or block sitting on grass near a white picket fence. Both the cube and the fence should be approximately the same cream/off-white color.

### Image Creation Method

Use a photo of a white picket fence. Place or composite a cube/block of matching color nearby. If the fence is naturally cream/off-white (many are), no color modification needed. If needed, tint both objects to match at approximately H=38-40°, S=15-25%, V=75-85%.

**S007_cube_fence.png — White picket fence collocation test**
- Fence: ~H=39°, S=15%, V=75% (cream, not white)
- Cube: ~H=39°, S=15%, V=75% (same cream)
- Purpose: "White picket fence" collocation predicts fence reported as white, cube as cream/beige, despite identical color.
- Ground truth: Both are the same cream/off-white.

---

## MEASURED VALUES (fill in after image creation)

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

---

*All stimulus images go in the `stimuli/` directory of this repo.*
*URL pattern: https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli/{filename}*
