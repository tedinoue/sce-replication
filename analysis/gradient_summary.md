# Gradient Breakpoint Analysis
## 9 Trials, T=1.0, Claude Opus/Sonnet/Haiku
## 03-21-2026

## Detection Rates (strict classifier, bus-sentence only)

| Stim | Shift | Opus | Sonnet | Haiku |
|---|---|---|---|---|
| S001 | +0° | 0% | 0% | 0% |
| G001 | +5° | 0% | 0% | 0% |
| S003 | +10° | 0% | 0% | 0% |
| G003 | +16° | 0% | 0% | 0% |
| G004 | +21° | 67% | 11% | 0% |
| G005 | +27° | 100% | 100% | 56% |
| G006 | +31° | 100% | 100% | 78% |

## Findings
1. 0% detection through +16° across all models (27/27 trials captured)
2. Opus breaks at +21° (0% to 67%). Sharpest transition.
3. Sonnet breaks at +27° (11% to 100%). One step later than Opus.
4. Haiku most captured. 56% at +27°, 78% at +31°. Never reaches ceiling.
5. Opus = best resolution AND strongest priors. First to escape capture.
6. Raw data: results/gradient_9trials_claude.json (189 responses)
