# analysis/

Aggregated detection rates and statistical summaries derived from the raw response data in `../results/`.

## ⚠️ Classification trust caveat

**The per-cell counts in these analysis files were produced by scripted classifiers, not by trial-by-trial human or AI-judge reading.** An independent audit on 2026-04-30 found systematic errors in this layer.

### Confirmed errors in `gradient_breakpoint_cross_vendor.md` and `gradient_breakpoint_claude.md`

The "strict classifier" used for the gradient experiment counts green-family color words (yellow-green, lime-green, green, chartreuse, neon-green) when they appear in sentences that also mention "bus" or "school bus." This heuristic has two failure modes confirmed against the raw data:

1. **False positives from background green.** The classifier flagged Gemini 2.5 Pro as having 25% detection at +10° (S003) and +16° (G003). Reading the four completed Pro responses at each step, every one describes the bus as "iconic bright yellow" / "vibrant yellow body" — the only "green" in those responses is in formulaic phrases like *"iconic yellow paint standing out against the lush greenery behind it"* (background). True detection at those steps is 0/4. The downstream finding that "Gemini Pro shows early detection at +10° and +16°" with speculation about "different vision integration architecture at Google" is a **parser artifact**, not a finding.

2. **False negatives across sentence boundaries.** The classifier missed five cells where the model named "school bus" in one sentence and the green-family color in the next. Most consequential: Flash and Haiku both reach 100% (5/5) at +31°, not the reported 80%. The published claim that "Flash and Haiku show ceiling effects below 100% at +31°, suggesting residual prior pull at extreme visual departures" is **also parser artifact, not signal**. Haiku 40% at +27° corrects to 60%; Pro 80% at +21° and +27° corrects to 100%.

The capability-tier-staggered breakpoint story survives the audit and is cleaner under correct counting (Haiku breakpoint tightens to ~+27°; Pro's onset moves to +21°; the flagship / mid / small ordering is preserved). But the specific cell counts and two of the speculative explanatory threads in `gradient_breakpoint_cross_vendor.md` are wrong.

### Likely-but-unaudited issues in other analyses

The other analysis files (`prompt_specificity_*.md`, `identity_reframing_claude.md`, `medical_differential_preliminary.md`) use coding schemes (D✓ / D✗ / D- / S / -- and similar) that appear to be hand-coded rather than scripted. They have not been audited as of this writing. Treat their per-cell counts as provisional until verified the same way the gradient counts have been.

The associated `*_ANALYSIS.md` files in `../results/` (CPO and Patch Isolation) quote response excerpts extensively and appear to have been hand-graded; they have not been audited either.

## Recommended practice for any reuse

If you cite a specific count from any file in this directory, verify against the raw text in `../results/{experiment}_results.json` before publishing. The raw response data is authoritative; the per-cell counts are derived classifications and are subject to the failure modes above.

For new analyses, **route classification through an AI judge or a human reading the full response, not a regex / keyword script.** Scripted classifiers on free-text model output produce silent miscounts that systematically distort downstream findings.
