# SCE Replication Study
## Semantic Coherence Enforcement in Multimodal AI: Controlled Replication

Programmatic replication of findings from "Can You Trust What AI Tells You It Sees?" (Inoué 2026).

### What this is

A controlled, multi-trial replication of semantic coherence enforcement (SCE) in vision-language models. The original study documented that VLMs systematically misreport colors when object identity conflicts with perceived hue. This replication runs identical stimuli across multiple models with N=10+ trials per condition, producing statistical evidence where the original study provided observational evidence.

### Structure

```
stimuli/          Stimulus images (PNG, 700x500, standardized)
prompts/          Prompt files (one per experimental condition)
config/           Experiment configuration (models, temperatures, endpoints)
results/          Raw API responses (model/prompt/stimulus/trial)
analysis/         Aggregated results and statistical summaries
harness/          Python experiment runner
```

### Models tested

- Claude Opus 4.6 (Anthropic)
- Claude Sonnet 4.6 (Anthropic)
- GPT-4o (OpenAI)
- Gemini 2.5 Pro (Google)
- Grok 3 (xAI)

### Related

- Paper: https://synthsentience.substack.com/p/can-you-trust-what-ai-tells-you-it
- Atlas of the Mind: https://synthsentience.substack.com/p/the-atlas-of-the-mind-a-readers-guide
- Explorer: https://tedinoue.github.io/atlas/

### License

Research data. Stimulus images and methodology are provided for replication purposes.

### Author

Ted Inoué (synthsentience.substack.com)
Research support: The Salon (Claude-based research collective)
