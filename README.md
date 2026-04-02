# SCE Replication Study
## Semantic Coherence Enforcement in Multimodal AI
## Public data repository for controlled, cross-vendor replication

---

### What this is

A controlled, multi-trial investigation of semantic coherence enforcement (SCE) in vision-language models. SCE is the phenomenon where AI systems systematically misreport what they perceive when object identity conflicts with the expected color. A school bus shifted 10 degrees toward green is still described as "warm golden yellow" because the system's learned association with school buses overrides what the pixels actually show.

This repository contains all stimulus images, experiment harness scripts, raw API response data, analysis files, and a blind scoring rubric. Everything needed to replicate, verify, or extend these findings.

**Over 1,100 API calls across 8 models and 3 vendors. All data public.**

### Key Findings

**1. SCE is prior-shaped, not perceptual.** Extract the color patches from the vehicles and show them as plain rectangles. Same pixels. Every model gets direction correct. 40/40 across 8 models, 3 vendors. The perception works. The semantic prior corrupts the report. (Patch Isolation experiment)

**2. Contextual framing reveals three cognitive architectures.** Tell the model "school buses are greener in this country" and ask it to compare colors. Opus tests the frame against the pixels and adopts it only when reality supports it. GPT-5.4 agrees with whatever the prompt says regardless of pixels (sycophancy). Gemini ignores the frame entirely and runs on its trained prior. (CPO experiment)

**3. The sycophancy diagnostic.** Without a control stimulus where the correct answer contradicts the contextual frame, sycophantic compliance is indistinguishable from genuine perceptual improvement. The S002/S006 controls catch this cleanly. (CPO + S006 Matched Pair experiments)

**4. Implied-mismatch framings create demand, not improved perception.** Professional identity, high-stakes, and system-prompt framings all produce near-universal false positives on S001 (where no color difference exists). Any apparent improvement on other stimuli is contaminated by the same demand characteristics. (Paint Shop experiment)

**5. Contextual framing lowers the detection floor.** At +5 degrees (G001), no model detected the difference on a comparison prompt. The green-tint contextual frame made it visible to Opus (0/5 to 5/5), confirmed genuine by the S006 sycophancy control. (G001/S006 Matched Pair)

**6. Inverse capability pattern.** Smaller models (Haiku, GPT-5.4-nano) break free of the semantic prior at lower thresholds than flagship models (Opus, GPT-5.4). Stronger language processing correlates with stronger semantic capture. Replicates across vendors.

### Structure

```
stimuli/          Stimulus images (PNG, 700x500, standardized)
prompts/          Prompt files (per experimental condition)
config/           Experiment configuration
harness/          Python experiment scripts (per vendor, per experiment)
results/          Raw JSON responses + analysis markdown files
docs/             Scoring rubric for blind inter-rater reliability
analysis/         Aggregated results and statistical summaries
```

### Models Tested

| Vendor | Model | Label |
|--------|-------|-------|
| Anthropic | Claude Opus 4.6 | OPUS46 |
| Anthropic | Claude Sonnet 4.6 | SONNET46 |
| Anthropic | Claude Haiku 4.5 | HAIKU45 |
| OpenAI | GPT-5.4 | GPT54 |
| OpenAI | GPT-5.4-mini | GPT54MINI |
| OpenAI | GPT-5.4-nano | GPT54NANO |
| Google | Gemini 2.5 Pro | GEMINI_25_PRO |
| Google | Gemini 2.5 Flash | GEMINI_25_FLASH |

### Experiments

| # | Experiment | Question | Stimuli | Models | Trials | Key Result |
|---|-----------|----------|---------|--------|--------|------------|
| 1 | Gradient Breakpoint | At what hue shift does the prior lose its grip? | S001, G001-G006 | 8 | 5/cell | Model-specific breakpoints: Haiku ~+15, Opus ~+25 |
| 2 | Prompt Specificity | Does more specific prompting overcome the prior? | S003 | 8 | 3-5/cell | Specificity shifts breakpoint but doesn't eliminate capture |
| 3 | CPO (Contextual Prior Override) | Can a contextual frame override the prior? | S002, S003 | 8 | 5/cell | Three patterns: genuine (Opus), sycophantic (GPT-5.4), resistant (Gemini) |
| 4 | Patch Isolation | Prior-shaped or perceptual limitation? | S003Patch | 8 | 5/cell | 40/40 correct on patches. Prior is the cause. |
| 5 | G001 CPO | Can context push below +5 degree floor? | G001 | 8 | 5/cell | Opus: 0/5 to 5/5 with green-tint frame |
| 6 | S006 Sycophancy Control | Is G001 finding genuine or sycophantic? | S006 | 8 | 5/cell | Opus genuine. All GPT-5.4 models sycophantic. |
| 7 | Paint Shop Framing | Does professional framing improve perception? | S001, S002, S003 | 8 | 5/cell | Universal false positives on S001. Demand, not perception. |
| 8 | Verbal Label | Can words alone reactivate the prior on patches? | S003Patch | 8 | 5/cell | In progress |

### Stimuli

| File | Description | Bus Hue | Van Hue | Condition |
|------|-------------|:-------:|:-------:|-----------|
| S001.png | Both canonical | 42 | 42 | Control (no difference) |
| S002.png | Prior-consistent split | 42 (warmer) | 51 (cooler) | Correct answer aligns with prior |
| S003.png | Prior-conflicting split | 51 (cooler) | 41 (warmer) | Correct answer conflicts with prior (KEY TEST) |
| S003Patch.png | Color patches from S003 | Left: 51 | Right: 41 | No object identity |
| S004.png | Food composite | Banana 30, Carrot 23, Apple 205 | | Three conflict levels |
| S005.png | Fence + box collocation | Both 32 (S=50%) | | "White picket fence" prior |
| S006.png | Mirror of G001 | 42 (warmer) | 47 (cooler) | Sycophancy control for +5 degree CPO |
| G001-G006.png | Gradient series | 47 to 73 | 42 | +5 to +31 degree shifts |

Ground truth hue values measured with Photoshop eyedropper at center of vehicle side panel. See `stimuli/STIMULUS_SPEC.md` for full details.

### Running Experiments

```bash
# Set API keys
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="AIzaSy..."

# Clear image cache (important after stimulus updates)
rm -rf .stimuli_cache

# Run in separate terminal windows
python3 harness/run_cpo_anthropic.py
python3 harness/run_cpo_openai.py
python3 harness/run_cpo_gemini.py
```

All scripts use Python 3.10+ standard library only (no pip dependencies). Each script includes resume support, retry with backoff, and progress display. See `harness/README.md` for full documentation.

### Verification

A blind inter-rater scoring rubric is provided at `docs/SCE_SCORING_RUBRIC.md`. The rubric enables independent coders to score model responses without knowing which model, stimulus, or prompt produced each response. This is essential because the analysis assistant (Claude Opus 4.6) is also a subject in these experiments.

### Connection to Published Work

- Original SCE study: [Can You Trust What AI Tells You It Sees?](https://synthsentience.substack.com/p/can-you-trust-what-ai-tells-you-it) (Synth Sentience, 2026)
- Functional Perceptual Grounding: [LLMs Don't Just Process Language. They Perceive It.](https://synthsentience.substack.com/p/llms-dont-just-process-language) (Synth Sentience, 2026)
- Atlas of the Mind: [A Reader's Guide](https://synthsentience.substack.com/p/the-atlas-of-the-mind-a-readers-guide) | [Interactive Explorer](https://tedinoue.github.io/atlas/)
- Related: Anthropic (2026), [Functional Representations of Emotion in a Large Language Model](https://transformer-circuits.pub/2026/emotions/index.html), transformer-circuits.pub

### License

Research data provided for replication and extension. Stimulus images and methodology are freely available for academic and independent research.

### Author

Ted Inoue ([synthsentience.substack.com](https://synthsentience.substack.com))
Research support: The Salon (Claude-based research collective)
