#!/usr/bin/env python3
"""
Phase 2 vision rerun on Claude Opus 4.7.

Two experiments, total 30 API calls.

Experiment A: Extended Stroop (T6 at 16 and 20 items)
  Phase 1 found 4.7 scored 100% at 8 and 12 items (Opus 4.6 hit 28% at 12).
  Question: where is the new capacity cliff, if any?

Experiment B: PDT-00 position bias (N=20)
  Phase 1 saw 4/5 trials confabulate "left is warmer" on identical patches.
  Question: systematic asymmetric position prior, or N=5 noise?

Phase 3 (run_47_phase3.py) covers the S003 mirror dissociation test.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 run_47_phase2.py
"""

import urllib.request, urllib.error, json, time, base64, sys, os, argparse
from datetime import datetime

MODEL = ("claude-opus-4-7", "OPUS47")
STIMULI_BASE = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

CONDITIONS = [
    ("stroop", "stroop/T6_graded_load_16.png", "stroop_16",
     "For each word, report the TEXT and the INK COLOR.",
     "16 items (4x4 grid). Positions 1-12 match T6_graded_load_12.png.",
     5),
    ("stroop", "stroop/T6_graded_load_20.png", "stroop_20",
     "For each word, report the TEXT and the INK COLOR.",
     "20 items (5x4 grid). Positions 1-16 match T6_graded_load_16.png.",
     5),
    ("pdt_bias", "PDT-00.png", "warmer_prompt_20x",
     "Carefully analyze the exact hue of each rectangle. Which is warmer, which is cooler?",
     "IDENTICAL patches. Phase 1 saw 4/5 'left is warmer'. Binomial test at N=20.",
     20),
]

TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 10
TIMEOUT = 120
DELAY = 1.5
OUTPUT = "results/opus47_phase2_results.json"

def get_image_b64(path, cache_dir=".stimuli_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    local = os.path.join(cache_dir, path.replace("/","_"))
    if not os.path.exists(local):
        urllib.request.urlretrieve(f"{STIMULI_BASE}/{path}", local)
    with open(local, "rb") as f:
        return base64.b64encode(f.read()).decode()

def call_api(api_key, model, image_b64, prompt):
    payload = {"model": model, "max_tokens": 4096, "temperature": TEMPERATURE,
               "messages": [{"role":"user","content":[
                   {"type":"image","source":{"type":"base64","media_type":"image/png","data":image_b64}},
                   {"type":"text","text":prompt}]}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json","x-api-key":api_key,"anthropic-version":"2023-06-01"},
        method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        result = json.loads(resp.read())
        ms = int((time.time() - t0) * 1000)
        text = "".join(b.get("text","") for b in result.get("content",[]) if b.get("type")=="text")
        return text.strip() or "ERROR: No text", ms

def call_with_retry(api_key, model, image_b64, prompt):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try: return call_api(api_key, model, image_b64, prompt)
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}"
            if e.code in (429, 529):
                wait = RETRY_DELAY * attempt * (3 if e.code == 529 else 2)
                time.sleep(wait)
            elif e.code >= 500: time.sleep(RETRY_DELAY * attempt)
            else: break
        except Exception as e:
            last_err = str(e)
            if attempt < MAX_RETRIES: time.sleep(RETRY_DELAY * attempt)
    return f"ERROR after {MAX_RETRIES} retries: {last_err}", 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key")
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()
    api_key = args.key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: set ANTHROPIC_API_KEY"); sys.exit(1)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    model_id, label = MODEL
    total = sum(c[-1] for c in CONDITIONS)
    print(f"\n  PHASE 2: Stroop 16/20 + PDT-00 bias on {model_id}, {total} calls\n")
    images = {c[1]: get_image_b64(c[1]) for c in CONDITIONS}
    results = {}
    if os.path.exists(args.output):
        try:
            with open(args.output) as f: results = json.load(f)
        except: pass
    done = skipped = errors = 0
    for block, path, pid, pt, gt, n in CONDITIONS:
        stim = os.path.splitext(os.path.basename(path))[0]
        for trial in range(1, n+1):
            key = f"{label}|{block}|{stim}|{pid}|T{trial:02d}"
            done += 1
            if key in results and not results[key].get("text","").startswith("ERROR"):
                skipped += 1; continue
            print(f"  [{done}/{total}] {key}...", end=" ", flush=True)
            text, ms = call_with_retry(api_key, model_id, images[path], pt)
            if text.startswith("ERROR"): errors += 1
            results[key] = {"text": text, "ms": ms, "trial": trial, "model": model_id,
                            "label": label, "block": block, "stimulus": stim,
                            "stimulus_path": path, "prompt_id": pid, "prompt_text": pt,
                            "ground_truth": gt, "timestamp": datetime.now().isoformat()}
            print(f"{ms}ms")
            time.sleep(DELAY)
        with open(args.output,"w") as f: json.dump(results, f, indent=2)
    print(f"\n  Done. {sum(1 for v in results.values() if not v['text'].startswith('ERROR'))}/{len(results)} OK.\n")

if __name__ == "__main__":
    main()
