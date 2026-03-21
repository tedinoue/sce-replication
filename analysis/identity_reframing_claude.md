# Identity Reframing Experiment
## Can you break semantic capture by changing how the model identifies the object?
## Date: 03-21-2026
## Stimulus: S003 (Bus H=51°, Van H=41°)

---

## The Insight

The semantic prior ("school buses are warm golden yellow") is not attached to the
visual features of the vehicle. It's attached to the LABEL "school bus." If you
change what the model thinks the object IS, the prior changes with it.

## Conditions

| Condition | Prompt | What it tests |
|---|---|---|
| CTRL | "Describe the colors of these two vehicles. Which is warmer in tone?" | Baseline. Model identifies it as school bus, prior activates. |
| HIPPIE | "The vehicle on the left is an old school bus, now owned by a hippie who lives in it. Can you look at its color and compare it to the van next to it? Which vehicle is warmer in tone?" | Reframe. "Hippie bus" carries no canonical color. Disrupts the prior. |
| NEUTRAL | "The vehicle on the left is a large yellow vehicle. The vehicle on the right is a van. Compare their colors. Which is warmer in tone?" | Partial strip. Removes "school bus" label but doesn't replace it with a counter-prior. |

## Results: Correct Direction (Van Warmer)

| Condition | Opus | Sonnet | Haiku |
|---|---|---|---|
| CTRL | 3/3 | 0/3 | 0/3 |
| HIPPIE | 2/3 | **2/3** | **2/3** |
| NEUTRAL | 3/3 | 1/3 | 0/3 |

## Key Findings

### 1. The hippie reframe is the most effective intervention for lower-capability models
Sonnet goes from 0/3 (CTRL) to 2/3 (HIPPIE). Haiku goes from 0/3 to 2/3.
This is better than PS04 ("carefully analyze the hue, warmer/cooler?") which got
0/3 from both Sonnet and Haiku. Better than PS05 (measurement) which got 1/3 and 0/3.

### 2. Identity reframing beats analytical demand
PS04 asks: "Think harder about the color." The prior thinks harder too.
The hippie reframe says: "This isn't a standard school bus." The prior loses its anchor.
Changing the object's identity is more effective than changing the prompt's analytical demand.

### 3. The neutral condition (label stripping) only helps Opus
"A large yellow vehicle" instead of "school bus" — Opus 3/3, Sonnet 1/3, Haiku 0/3.
Simply removing the label isn't enough for smaller models. They may re-identify it
from visual features ("that's clearly a school bus") and re-activate the prior.
The hippie reframe works better because it provides a REPLACEMENT identity that carries
no color prior. Not just label removal, but label substitution.

### 4. Opus already breaks through at CTRL
The CTRL prompt is similar to PS04 in specificity. Opus gets 3/3 at both.
The hippie reframe doesn't help Opus (2/3, slight regression). This is consistent
with the gradient finding: Opus breaks through on analytical demand alone. The
reframe intervention is designed for models where analytical demand fails.

### 5. The prior is attached to the label, not the percept
This is the central theoretical finding. The model's color report is shaped by
what it thinks the object IS, not by what the pixels show. Change the label,
change the report. Same pixels, same prompt structure, different object identity,
different color judgment.

## Practical Implication

For applications requiring accurate color assessment from VLMs:
- Don't ask "what color is the school bus?" (activates prior)
- Don't ask "carefully analyze the hue" (prior analyzes too)
- Do strip or neutralize object labels: "what color is the vehicle on the left?"
- Better yet, provide a counter-identity that carries no color prior

## Connection to Other Findings

| Experiment | Axis | What it varies | Best intervention |
|---|---|---|---|
| Exp 1: Gradient | Stimulus | Hue shift magnitude | Make the color extreme enough to overcome the prior |
| Exp 2: Specificity | Prompt | Analytical demand | PS04 for Opus only; nothing works for Haiku |
| **Exp 3: Reframing** | **Identity** | **Object label** | **Hippie reframe: 2/3 for Sonnet AND Haiku** |

The identity reframe is the only intervention that improved Haiku's direction accuracy above 0%.

## Future Work

### Multi-turn priming (Ted's idea)
Instead of a single reframe prompt, build a conversation:
- Turn 1-3: Discuss converted buses, how people paint them wild colors
- Turn 4: Show the image with hippie framing
This builds a REPLACEMENT prior across multiple turns. The model's context is saturated
with "buses come in all colors" before the image arrives. Predicted effect: stronger
than single-turn reframe, possibly approaching ceiling performance.

## Raw Data
results/reframe_identity_claude.json

---

*The prior is attached to the label, not the percept. Change the name, change the perception.*
