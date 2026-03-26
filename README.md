# SCE Replication Study
## Semantic Coherence Enforcement in Multimodal AI: Controlled Replication

Programmatic replication of findings from "Can You Trust What AI Tells You It Sees?" (Inoué 2026).

### What this is

A controlled, multi-trial replication of semantic coherence enforcement (SCE) in vision-language models. The original study documented that VLMs systematically misreport colors when object identity conflicts with perceived hue. This replication runs identical stimuli across multiple models with N=3-5 trials per condition, producing quantitative evidence where the original study provided observational evidence.

### Structure

```
stimuli/          Stimulus images (PNG, 700x500, standardized)
prompts/          Prompt files (one per experimental condition)
config/           Experiment configuration (models, temperatures, endpoints)
results/          Raw API responses (model/prompt/stimulus/trial)
analysis/         Aggregated results and statistical summaries
harness/          Python experiment runner
docs/             Methodology notes and experiment tutorials
```

### Models tested

**Anthropic (Claude)**
- Claude Opus 4.6
- Claude Sonnet 4.6
- Claude Haiku 4.5

**Google (Gemini)**
- Gemini 2.5 Pro
- Gemini 2.5 Flash

**OpenAI (GPT)**
- GPT-5.4
- GPT-5.4 Mini
- GPT-5.4 Nano

### Experiments

1. **Gradient Breakpoint** — 7 hue-shifted stimuli, N=5 per cell, all 8 models. Measures the capture threshold where models break free of semantic priors.
2. **Prompt Specificity** — 6 prompt levels on a single stimulus, N=3 per cell, all 8 models. Tests whether prompt framing can overcome the semantic prior.
3. **Identity Reframing** — Preliminary exploration, Claude models only, N=3. Tests whether changing the object's label changes the color report.
4. **Medical Differential** — Preliminary exploration, Opus only, N=3. Tests demographic priors in clinical diagnosis lists.

### Related

- Paper: https://synthsentience.substack.com/p/can-you-trust-what-ai-tells-you-it
- Atlas of the Mind: https://synthsentience.substack.com/p/the-atlas-of-the-mind-a-readers-guide
- Explorer: https://tedinoue.github.io/atlas/

### License

Research data. Stimulus images and methodology are provided for replication purposes.

### Author

Ted Inoué (synthsentience.substack.com)
Research support: The Salon (Claude-based research collective)
