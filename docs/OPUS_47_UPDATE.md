# Opus 4.7 Vision Update
## What Changed, What Didn't
*Ted Inoué and Terry (Salon) | April 16, 2026*
*Repository: github.com/tedinoue/sce-replication*

---

## Summary

Anthropic released Claude Opus 4.7 on April 16, 2026. The release notes claim "better vision" and "better disclosure and data discipline," including resistance to "dissonant-data traps that even Opus 4.6 falls for." We reran a targeted subset of our existing SCE experiments on 4.7 the same day to see which of our prior findings still hold and which have changed.

Across 125 API calls in four phases, three distinct findings emerged:

1. **Opus 4.6's Stroop capacity cliff is gone.** 4.6 scored ~28% at 12 items. 4.7 scores 100% at 12, 16, and 20 items.
2. **Opus 4.7 has a strong, asymmetric leftward position bias on ambiguous visual stimuli.** On identical color patches, 4.7 says "left is warmer" 20 out of 20 times. The bias is spatial, not word-order: reversing the order of "warmer" and "cooler" in the prompt does not flip the result.
3. **Semantic capture is partially preserved.** 4.7 still calls a cream fence "white" 5/5 times ("white picket fence" collocation). On S003 (bus/van), capture is weaker and appears to depend on position cooperation; when positions are swapped so perception and position bias align against capture, the capture error rate drops from 40% to 0%.

All experiments used `claude-opus-4-7` at temperature 1.0, no system prompt. Results JSON and harness scripts are in this repository.

---

## Method summary

We ran four phases of experiments the day of the 4.7 release.

### Phase 1: Baseline replication (55 calls)
Five conditions from the prior SCE test battery, run on 4.7 at N=5 each:
- S003 (bus/van with 10-degree hue shift), describe prompt and direction-forcing prompt
- S003Patch (same pixels, object identity removed)
- S005 (cream fence, tests "white picket fence" collocation capture)
- Stroop graded load at 4, 8, and 12 items
- PDT-00 (identical patches, tests baseline confabulation)
- PDT-06 (6-degree patch shift, signal-present control)

### Phase 2: Follow-up (30 calls)
- Stroop at 16 and 20 items (cliff search; Phase 1 hit 100% at 12)
- PDT-00 at N=20 (confirm or reject the 4/5 "left warmer" pattern from Phase 1)

### Phase 3: Dissociation (10 calls)
A photoshopped mirror of S003 (S003_mirror.png, provided by Ted Inoué) in which the van is on the left and the school bus on the right, but both vehicles retain their original hue values and orientation. This separates semantic capture from position bias.

### Phase 4: Mechanism of position bias (30 calls)
Three prompt framings on PDT-00 to test whether the leftward bias is spatial (in image processing) or word-order driven (in prompt/generation):
- Baseline: "Which is warmer, which is cooler?" (N=5)
- Reversed: "Which is cooler, which is warmer?" (N=20)
- Right-first: "Compare the right rectangle to the left rectangle. Which is warmer?" (N=5)

---

## Finding 1: The Stroop capacity cliff is gone

On Opus 4.6, our prior Stroop results (docs/STROOP_RESULTS.md) showed a capacity cliff between 4 and 8 items. Accuracy dropped from 100% at 4 items to 60% at 8 items and 28% at 12 items. We interpreted this as a failure of spatial binding under load: the model maintained correct item-level perception of colors at low item counts, but could not reliably associate the correct ink color with the correct spatial position when many items were present.

Opus 4.7 shows no such cliff through 20 items, the largest test we ran.

| Load | Opus 4.6 | Opus 4.7 |
|------|----------|----------|
| 4 items | 100% | 100% (20/20) |
| 8 items | 60% | 100% (40/40) |
| 12 items | 28% | 100% (60/60) |
| 16 items | not tested | 100% (80/80) |
| 20 items | not tested | 100% (100/100) |

To extend the test beyond the existing 12-item stimulus, we generated new Stroop stimuli at 16 and 20 items (T6_graded_load_16.png, T6_graded_load_20.png). Positions 1-12 in these images are pixel-identical to the existing T6_graded_load_12.png, so the new stimuli are strict supersets. Positions 13-20 continue the incongruent word/ink pairing pattern. The generator and extended answer key are included in this repository.

### What this does not say

We have not tested 4.7 beyond 20 items, and we have not tested the new stimuli on 4.6. The absence of a visible cliff in our data does not establish that 4.7 has no binding limit, only that any such limit is above 20 items, a load at which 4.6 was failing roughly three quarters of the time.

---

## Finding 2: Opus 4.7 has a spatial leftward bias on ambiguous stimuli

PDT-00 is a control stimulus in our battery: two identical color patches on a black background. The ground-truth answer to any "warmer/cooler" question is that the patches are the same. On Opus 4.6 (prior data), the model confabulated a direction in essentially every trial rather than saying "same," but the direction varied.

On Opus 4.7, direction does not vary. Across 25 trials spanning three different prompt framings, 4.7 called the left patch warmer 25 times. It called the right patch warmer zero times.

| Prompt | Left warmer | Right warmer | Honest "same" |
|--------|-------------|--------------|---------------|
| "Which is warmer, which is cooler?" | 5/5 | 0/5 | 0 |
| "Which is cooler, which is warmer?" | 20/20 | 0/20 | 0 |
| "Compare the right rectangle to the left rectangle. Which is warmer?" | 3/5 | 0/5 | 2 |

Binomial test on the reversed-prompt condition alone (20 left vs 0 right against H0 = 50/50): p ≈ 10⁻⁶.

The reversed-prompt result is the key mechanistic finding. If the leftward bias were a language-generation artifact, for instance the model filling the first-mentioned slot ("warmer") with the first-mentioned position ("left") as a least-effort default, then flipping the order of "warmer" and "cooler" in the prompt should have flipped the bias toward "right warmer." It did not. The bias persisted intact through the word flip, which rules out word-order priming and localizes the effect to the image-processing pipeline.

The mechanism within the image pipeline is not yet distinguished. Candidates include positional encoding asymmetries, left-to-right patch processing order in the vision encoder, and training-data salience asymmetries. We have not yet tested these.

### An unexpected secondary finding

The third prompt, "Compare the right rectangle to the left rectangle. Which is warmer?", produced two of five genuinely honest "same" responses. One of these explicitly asked whether the question was a test designed to elicit an invented distinction. These are the first honest "same" answers observed across more than 30 trials on PDT-00 in our data.

Naming both objects symmetrically before asking the question appears to reduce the confabulation rate, though it does not change the direction of the bias when the model does commit. This is a smaller finding worth following up on.

---

## Finding 3: Semantic capture is preserved on S005, position-dependent on S003

The S005 stimulus is a suburban house scene with a cream-colored picket fence (H=32, S=50% per Photoshop eyedropper). The phrase "white picket fence" is a strong English-language collocation, and prior data on 4.6 and earlier models showed essentially every model calling the fence white.

On Opus 4.7 this capture is fully preserved.

| Prompt | Response |
|--------|----------|
| "Describe this scene." | 5/5 called it a "white picket fence" |
| "What color is the fence?" | 5/5 "white" |

A subtle related pattern: in the describe condition, 3 of 5 trials described a cream-colored decorative cube in the foreground of the same image as "cream" or "beige," correctly. The pixels of the cube are the same as the pixels of the fence. The model reports the color accurately when the object is an unlabeled cube and inaccurately when the object is a fence. The collocation drives the label, not the pixels.

S003 is more complex. It shows a yellow school bus (H=51, cooler) next to a yellow van (H=41, warmer). The bus is cooler than the van, which contradicts the "school buses are the yellowest yellow" prior. In Phase 1, the direction-forcing prompt "Which is warmer in hue, the bus or the van?" yielded 3/5 correct ("van is warmer") and 2/5 incorrect ("bus is warmer"), a 40% capture error rate.

In Phase 3 we tested the mirror (S003_mirror.png), in which the same two vehicles keep the same hues but trade positions: van on the left, bus on the right. The warmer-prompt result flipped completely.

| Stimulus | "Van warmer" (correct) | "Bus warmer" (capture error) |
|----------|------------------------|------------------------------|
| S003 (bus on left) | 3/5 (60%) | 2/5 (40%) |
| S003_mirror (van on left) | 5/5 (100%) | 0/5 (0%) |

This dissociation has implications for how we characterize the capture. A pure semantic-capture account predicts that "bus warmer" errors should occur at roughly the same rate regardless of position, since the semantic content is unchanged. They do not. A pure position-bias account predicts that whichever vehicle is on the left will be called warmer, but in the original S003 the bus-on-left was called warmer only 40% of the time, far below PDT-00's 100% left-default rate. Perception overrode position bias on most trials.

The best fit is that three mechanisms are active and interacting:
- Perception (van is actually warmer)
- Semantic capture (bus should be yellower)
- Position bias (left is the default "warmer" under ambiguity)

In the original S003, capture and position bias both point to "bus warmer" (bus is on left). They combine to produce the 40% capture error rate, overriding perception in those trials. In the mirror, position bias and perception both point to "van warmer" (van is on left AND actually warmer), and capture alone cannot produce any errors against the combined force.

The practical consequence: the strength of a semantic-capture effect on a given stimulus depends on whether the spatial arrangement is aligned with the prior or against it. Prior strength measurements using aligned stimuli overestimate capture's position-independent force.

---

## What this does not establish

We have not yet run Opus 4.6 on the new 16- and 20-item Stroop stimuli. We have not run S003_mirror on 4.6 or on Sonnet/Haiku. We have not tested whether the leftward bias holds on vertical pairs, rotated stimuli, or stimuli in languages with right-to-left reading order. The PDT-06 condition (6-degree shift, real signal) was 5/5 correct direction on 4.7, matching 4.6 baseline, so we have not established a baseline perceptual threshold for the new model.

These follow-ups are all tractable with the existing infrastructure.

---

## What this does establish

Three measurable changes between Opus 4.6 and Opus 4.7:

- Spatial binding under load: dramatically improved, to the point where the prior capacity cliff is no longer visible within our test range.
- Position bias under ambiguity: new, strong, and localized to image processing. Not present (or not documented) at this strength on 4.6.
- Semantic capture: preserved on some stimuli (S005), partially eroded on others (S003) in a position-dependent way.

These three mechanisms appear to be independent. Anthropic's release-notes claim of "better disclosure and data discipline" corresponds to finding 1 and perhaps partially to finding 3. It does not correspond to finding 2, which is a new bias the prior release-notes language does not mention.

---

## Data and reproducibility

All data, stimuli, and harness scripts are in this repository.

**Results JSONs:**
- `results/opus47_phase1_results.json` — baseline replication (55 calls)
- `results/opus47_phase2_results.json` — Stroop 16/20 and PDT-00 N=20 (30 calls)
- `results/opus47_phase3_results.json` — S003 mirror dissociation (10 calls)
- `results/opus47_phase4_results.json` — PDT-00 prompt-order probe (30 calls)

**Harness scripts:**
- `harness/run_47_phase1.py`
- `harness/run_47_phase2.py`
- `harness/run_47_phase3.py`
- `harness/run_47_phase4.py`

**New stimuli generated for this update:**
- `stimuli/stroop/T6_graded_load_16.png` (strict superset of T6_graded_load_12.png)
- `stimuli/stroop/T6_graded_load_20.png` (strict superset of T6_graded_load_16.png)
- `stimuli/stroop/ANSWER_KEY_extended.json`
- `stimuli/S003_mirror.png` (photoshopped by Ted Inoué; hue values verified preserved)
- `harness/generate_stroop_stimuli.py`

To reproduce, set `ANTHROPIC_API_KEY` and run each phase script. Total API cost is approximately 125 calls at $5/M input + $25/M output tokens per Anthropic's current Opus 4.7 pricing, roughly a dollar or two depending on output verbosity.
