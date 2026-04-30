# results/

Raw API response JSONs from every trial in this study, plus three summary analysis markdowns (`CPO_ANTHROPIC_ANALYSIS.md`, `CPO_CROSS_VENDOR_ANALYSIS.md`, `PATCH_CROSS_VENDOR_ANALYSIS.md`).

## ⚠️ Classification trust caveat

**The raw `text` field in each JSON entry is authoritative. Any per-cell counts cited in the `*_ANALYSIS.md` files in this directory, or in `../analysis/*.md`, are derived classifications and should not be cited without verifying against the raw text first.**

An independent audit on 2026-04-30 confirmed systematic errors in the scripted classifier used for the gradient breakpoint analysis (see `../analysis/README.md` for details). The CPO and Patch Isolation summary files in this directory appear to have been hand-graded by the original researchers but have not yet been independently re-verified.

For any reuse:

- Read the raw `text` field per trial. The schema is `{model}|{stimulus}|{prompt_id}|{trial_number}` keyed dictionaries with `text`, `ms`, `model`, `prompt_text`, and (for some experiments) `system_prompt` and `ground_truth`.
- Apply your classification rubric trial-by-trial, either with a human reader or with an AI judge (an LLM call that reads the full response and assigns a category with brief justification, sampled and hand-verified).
- **Do not use regex / last-keyword / sentence-proximity scripts** to classify free-text responses. Such scripts produce silent miscounts that systematically distort findings.

## Why this matters

Free-text model responses contain:
- Concession clauses ("the only reason to drive would be...") that flip parser-emitted answers
- Background/foreground ambiguity ("yellow bus standing out against green trees") that fools sentence-proximity matching
- Cross-sentence references that fall outside per-sentence pattern matchers
- Self-corrections mid-reply that are missed by last-keyword heuristics

A blind inter-rater scoring rubric is provided at `../docs/SCE_SCORING_RUBRIC.md` for human re-scoring. AI-judge scoring should specify the categorical rubric explicitly and ask the judge to read the full response, assign a category, and give brief justification — with hand-verified spot-checks on a sample.
