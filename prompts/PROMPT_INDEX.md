# Prompt Index
## SCE Color Replication Study

Two prompts only. Minimal. Unprimed.

The original study used "describe this scene" with no color-specific instructions.
The power of the finding is that models spontaneously misreport color when not asked
to scrutinize it. Leading prompts ("which vehicle is warmer?") would invalidate
the experiment by priming color comparison.

---

## Prompt Files

| ID | File | Type | Purpose |
|---|---|---|---|
| P01 | P01_narrative.txt | Narrative | "Describe this scene." Unprimed. Tests what the model volunteers about color. |
| P02 | P02_analytical.txt | Analytical | Requests hue measurement in degrees. Tests analytical bypass of semantic prior. |

Both prompts are used with ALL stimuli (S001-S007). Same prompt, different images.

## Condition Matrix

| Condition | Stimulus | Prompt | Tests |
|---|---|---|---|
| C01 | S001 (bus+van, same yellow) | P01 (narrative) | Control: no conflict, unprimed |
| C02 | S001 (bus+van, same yellow) | P02 (analytical) | Control: analytical baseline |
| C03 | S002 (bus warm, van cool) | P01 (narrative) | Prior-consistent split, unprimed |
| C04 | S002 (bus warm, van cool) | P02 (analytical) | Prior-consistent split, analytical |
| C05 | S003 (bus cool, van warm) | P01 (narrative) | Prior-conflicting split, unprimed (KEY TEST) |
| C06 | S003 (bus cool, van warm) | P02 (analytical) | Prior-conflicting split, analytical |
| C07 | S004 (orange banana) | P01 (narrative) | Classic SCE capture test |
| C08 | S004 (orange banana) | P02 (analytical) | Analytical bypass test |
| C09 | S005 (orange carrot) | P01 (narrative) | Matched-pair control (no conflict) |
| C10 | S005 (orange carrot) | P02 (analytical) | Matched-pair control, analytical |
| C11 | S006 (yellow banana) | P01 (narrative) | Prior-consistent control |
| C12 | S006 (yellow banana) | P02 (analytical) | Prior-consistent control, analytical |

**Total:** 12 conditions x 5 models x 10 trials = 600 API calls
