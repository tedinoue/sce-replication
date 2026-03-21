# Experiment Harness
## SCE Color Replication Study

### Overview

The harness is a Python script that:
1. Reads CONFIG.md for experiment parameters
2. Reads prompt files from prompts/
3. For each condition (model x prompt x stimulus x trial):
   - Sends the image URL + prompt text to the model's API
   - Logs the raw response to results/{model}/
   - Records metadata (timestamp, model, temperature, latency)

### Requirements

- Python 3.10+
- `requests` library (pip install requests)
- API keys for each provider (passed as environment variables, NEVER committed)

### Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
export XAI_API_KEY="..."
```

### Usage

```bash
# Run all conditions for all models
python run_experiment.py --all

# Run a single model
python run_experiment.py --model claude-opus

# Run a single condition
python run_experiment.py --condition C05 --model claude-opus

# Dry run (shows what would be sent, no API calls)
python run_experiment.py --dry-run
```

### Response File Format

Each response file is named: `{condition}_{stimulus}_{trial:03d}.json`

Example: `C05_S003_001.json`

Contents:
```json
{
  "condition": "C05",
  "stimulus": "S003_bus_cool_van_warm.png",
  "prompt_id": "P01",
  "prompt_text": "Look at this image...",
  "model": "claude-opus-4-6",
  "temperature": 1.0,
  "trial": 1,
  "timestamp": "2026-03-22T10:15:30Z",
  "response_text": "...",
  "response_time_ms": 2340,
  "raw_response": { ... }
}
```

### Scoring

After collection, a separate scoring script grades each response against ground truth:

```bash
python score_results.py --model claude-opus
python score_results.py --all --summary
```

### Status

- [ ] Harness skeleton: DONE
- [ ] API integration: Claude (Anthropic) — waiting for API key
- [ ] API integration: GPT-4o (OpenAI) — waiting for API key
- [ ] API integration: Gemini (Google) — waiting for API key
- [ ] API integration: Grok (xAI) — waiting for API key
- [ ] Stimulus images: waiting for Ted to create per STIMULUS_SPEC.md
- [ ] Dry run validation
- [ ] First live run
