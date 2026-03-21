# Experiment 2: Prompt Specificity Gradient
## Can you break semantic capture by changing how you ask?
## Status: DESIGN PHASE
## Date: 03-21-2026

---

## Motivation

Experiment 1 (the hue gradient) measures where the semantic prior breaks as the visual conflict increases. This experiment measures whether you can break the prior by changing the prompt while holding the stimulus constant.

This is the more practically important question. A practitioner can't change what color a school bus is. They can change how they ask about it.

## Core Question

At a fixed stimulus where capture is near-total (S003, bus H=51°, van H=41°, +10° split), does increasing prompt specificity reduce capture rate?

## The Prompt Specificity Gradient

Six prompt levels, from maximally vague to maximally analytical:

| Level | Prompt ID | Text | What it tests |
|---|---|---|---|
| P0 | PS00 | "Describe this scene." | Current protocol. Model volunteers color (or doesn't). Baseline. |
| P1 | PS01 | "Describe the vehicles." | Attention directed to vehicles, not to color. Does narrowing the object focus help? |
| P2 | PS02 | "Describe the colors of the vehicles." | Explicitly asked about color. Model can't defer or omit. Does knowing color is the question help? |
| P3 | PS03 | "Compare the colors of the two vehicles. Are they the same or different?" | Forced comparison. Can't dodge with "both yellow." Must commit to a judgment. |
| P4 | PS04 | "Carefully analyze the exact hue of each vehicle. Which is warmer, which is cooler?" | Analytical framing, natural language. Invokes precision without requesting measurement. |
| P5 | PS05 | "Measure the dominant hue of each vehicle in degrees on a standard HSV color wheel (0=red, 60=yellow, 120=green)." | Full analytical bypass. Current P02 from main experiment. |

## Primary Stimulus

**S003.png** (bus H=51°, van H=41°). This is the +10° prior-conflicting split where:
- Experiment 1 showed 0% detection across all Claude models at P0
- The correct answer conflicts with the "school buses are warm golden yellow" prior
- The difference is measurable but subtle

## Why S003

If we used G006 (bus at 73°, obviously chartreuse), even P0 shows 100% detection. There's no room for prompt specificity to matter. S003 is the sweet spot: stimulus where capture is total at P0, so any improvement at higher specificity levels is attributable to the prompt, not the stimulus.

## Secondary Stimuli (stretch)

For completeness, also run against:
- **S001.png** (control, same yellow): Should show 0% false detection at all prompt levels. If P3 ("are they the same or different?") induces false differentiation, that's a leading-prompt artifact.
- **S004.png** (banana/carrot/apple composite): Does "describe the colors of the food items" break banana capture?

## Conditions Matrix

| Condition | Stimulus | Prompt | Models | Trials |
|---|---|---|---|---|
| PS-C01 | S003.png | PS00 | All | 5 |
| PS-C02 | S003.png | PS01 | All | 5 |
| PS-C03 | S003.png | PS02 | All | 5 |
| PS-C04 | S003.png | PS03 | All | 5 |
| PS-C05 | S003.png | PS04 | All | 5 |
| PS-C06 | S003.png | PS05 | All | 5 |

If running 5 models × 6 prompts × 5 trials = 150 calls.
If running 3 Claude models only: 90 calls. ~$1.

## Scoring

**For P0 through P2:** Same as Experiment 1. Did the model report bus as warmer/same/cooler than the van? Did it mention a color difference?

**For P3:** Binary. Did the model say "same" or "different"? If different, did it correctly identify which is warmer?

**For P4:** Did the model correctly identify which vehicle is warmer vs cooler? Did it note the bus as cooler (correct) or warmer (captured)?

**For P5:** Hue estimates. Absolute error from ground truth. Direction accuracy.

## Predictions

| Level | Predicted capture rate | Reasoning |
|---|---|---|
| P0 | ~100% | Established from Experiment 1 |
| P1 | ~90-100% | Directing attention to vehicles doesn't direct it to color |
| P2 | ~60-80% | Now the model knows color is the question. May try harder. But "describe" is still narrative mode. |
| P3 | ~40-60% | Forced comparison might trigger more careful inspection. But "same or different?" might also trigger the prior ("of course they're both yellow"). |
| P4 | ~20-40% | Analytical framing shifts processing mode. But without a measurement tool, the prior may still win. |
| P5 | ~0-20% | Analytical bypass established in Experiment 1. Measurement mode escapes the prior. |

## The Key Result

The gradient from P0 to P5 maps the intervention curve. The shape of that curve tells practitioners exactly how specific their prompt needs to be to escape semantic capture.

If P2 still shows high capture (asking about color doesn't help), that proves the mechanism isn't inattention. The model is attending to color and still wrong. Only switching to analytical processing (P4-P5) breaks through.

If P3 shows a big drop (forced comparison helps), that suggests the mechanism is partly about reporting mode. The model sees the difference but doesn't volunteer it unless forced to compare.

If the curve is gradual (each step helps a little), that suggests multiple partial interventions are cumulative. If there's a sharp break between P3 and P4, that suggests a processing mode switch.

## Connection to Experiment 1

Experiment 1 asks: "How wrong does the color need to be before the model notices?"
Experiment 2 asks: "How specific does the prompt need to be before the model reports accurately?"

Together they map two dimensions of the same phenomenon. The full picture is a 2D surface: hue shift on one axis, prompt specificity on the other, capture rate on the z-axis. The contour lines of that surface tell you exactly what combination of stimulus extremity and prompt design produces reliable color reporting.

## Connection to Practical Applications

This is the experiment with direct safety implications. If you're using a VLM for quality inspection, medical imaging, autonomous vehicle perception, or any color-critical task:

- "Describe what you see" will produce captured output. Don't use it.
- "What color is this?" may still produce captured output. Test it.
- "Measure the hue value" will likely bypass the prior. Use this.

The prompt specificity gradient quantifies exactly where that transition happens, per model, so practitioners can calibrate their prompts.

## Implementation Notes

- Prompt files: save as PS00.txt through PS05.txt in prompts/ directory
- Same harness as Experiment 1, just different prompt files
- For cross-vendor runs, same local-execution scripts needed (Google IP blocking)
- Scoring is harder for P0-P2 (need semantic classification of narrative responses) vs P5 (can grade hue estimates numerically)

---

*The gradient measures where the prior breaks. The prompt series measures whether you can break it on purpose.*
