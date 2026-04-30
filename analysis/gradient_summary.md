# Gradient Breakpoint Analysis
## 9 Trials, T=1.0, Claude Opus/Sonnet/Haiku
## 03-21-2026 (analysis); revised 04-30-2026 per audit

> **AUDIT NOTE:** Two Haiku cells corrected by trial-by-trial reading. See `analysis/README.md`.

## Detection Rates (audited)

| Stim | Shift | Opus | Sonnet | Haiku |
|---|---|---|---|---|
| S001 | +0° | 0% | 0% | 0% |
| G001 | +5° | 0% | 0% | 0% |
| S003 | +10° | 0% | 0% | 0% |
| G003 | +16° | 0% | 0% | 0% |
| G004 | +21° | 67% | 11% | 0% |
| G005 | +27° | 100% | 100% | **67%** |
| G006 | +31° | 100% | 100% | **100%** |

Cells in **bold** differ from the original published table. Haiku G005 was published as 56% (5/9); audit finds 6/9 = 67%. Haiku G006 was published as 78% (7/9); audit finds 9/9 = 100%. Same Type B (cross-sentence reference) classifier failure mode as the 5-trial cross-vendor data.

## Findings (revised)
1. 0% detection through +16° across all models (27/27 trials captured)
2. Opus breaks at +21° (0% to 67%). Sharpest transition.
3. Sonnet breaks at +27° (11% to 100%). One step later than Opus.
4. Haiku reaches 100% ceiling at +31° (was published as 78%). Most captured of the three at +27° (67% vs 100% for Opus/Sonnet) but does reach ceiling.
5. Opus = best resolution AND strongest priors. First to escape capture.
6. Raw data: results/gradient_9trials_claude.json (189 responses)

*Audit revision: 2026-04-30. Per-trial reading by AI-judge classification protocol.*
