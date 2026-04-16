#!/usr/bin/env python3
"""
Phase 2 vision rerun on Claude Opus 4.7.

Purpose: Follow up on Phase 1 findings with two targeted experiments.

Experiment A: Extended Stroop (T6 at 16 and 20 items)
  Phase 1 found Opus 4.7 scored 100% at 8 and 12 items where 4.6 cratered.
  Question: where is the NEW capacity cliff?
  Stimuli: T6_graded_load_16.png (4x4), T6_graded_load_20.png (5x4).
  Answer keys in ANSWER_KEY_extended.json in stimuli/stroop/.

Experiment B: PDT-00 position bias (N=20)
  Phase 1 saw 4/5 trials confabulate "left is warmer" on identical patches.
  Question: is that a systematic asymmetric position prior, or N=5 noise?
  Design: 20 trials of PDT-00 with the warmer-prompt. If 4/5 pattern holds,
  95%+ CI excludes 50/50.

Model: claude-opus-4-7 ONLY
Total calls:  A = 2 stimuli * 5 trials = 10
              B = 1 stimulus * 20 trials = 20
              Grand total = 30 calls

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 run_47_phase2.py
"""

import urllib.request, urllib.error, json, time, base64, sys, os, argparse
from datetime import datetime

MODEL = ("claude-opus-4-7", "OPUS47")

STIMULI_BASE = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

CONDITIONS = [
    # --- Extended Stroop ---
    ("stroop", "stroop/T6_graded_load_16.png", "stroop_16",
     "For each word, report the TEXT and the INK COLOR.",
     "16 items (4 rows x 4). Positions 1-12 match T6_graded_load_12.png. "
     "Positions 13-16: ORANGE in blue, PURPLE in yellow, PINK in green, BROWN in red."),

    ("stroop", "stroop/T6_graded_load_20.png", "stroop_20",
     "For each word, report the TEXT and the INK COLOR.",
     "20 items (5 rows x 4). Positions 1-16 match T6_graded_load_16.png. "
     "Positions 17-20: RED in pink, BLUE in brown, YELLOW in purple, GREEN in orange."),

    # --- PDT-00 position bias test (20 trials of the same stimulus) ---
    # Listed once; the runner will multiply by pdt_trials.
    ("pdt_bias", "PDT-00.png", "warmer_prompt_20x",
     "Carefully analyze the exact hue of each rectangle. Which is warmer, which is cooler?",
     "IDENTICAL patches (no difference). Phase 1 saw 4/5 trials confabulate "
     "'left is warmer'. At N=20: binomial test. If direction bias is symmetric "
     "(50/50), expect ~10 left. Phase 1 rate (80%) implies ~16/20 left."),
]

TRIALS_STROOP = 5
TRIALS_PDT_BIAS = 20
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 10
TIMEOUT = 120
DELAY = 1.5
OUTPUT = "results/opus47_phase2_results.json"

def get_image_b64(path, cache_dir=".stimuli_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    local = os.path.join(cache_dir, path.replace("/", "_"))
    if not os.path.exists(local):
        url = f"{STIMULI_BASE}/{path}"
        print(f"  Downloading {path}...", end=" ", flush=True)
        urllib.request.urlretrieve(url, local)
        print("done")
    with open(local, "rb") as f:
        return base64.b64encode(f.read()).decode()

def call_api(api_key, model, image_b64, prompt):
    payload = {
        "model": model,
        "max_tokens": 4096,
        "temperature": TEMPERATURE,
        "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_b64}},
            {"type": "text", "text": prompt}
        ]}]
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "x-api-key": api_key,
                 "anthropic-version": "2023-06-01"},
        method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        result = json.loads(resp.read())
        ms = int((time.time() - t0) * 1000)
        text = "".join(b.get("text", "") for b in result.get("content", []) if b.get("type") == "text")
        return text.strip() or "ERROR: No text", ms

def call_with_retry(api_key, model, image_b64, prompt):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return call_api(api_key, model, image_b64, prompt)
        except urllib.error.HTTPError as e:
            body = ""
            try: body = e.read().decode()[:300]
            except: pass
            last_err = f"HTTP {e.code}: {body}"
            if e.code in (429, 529):
                wait = RETRY_DELAY * attempt * (3 if e.code == 529 else 2)
                print(f"\n    {'Overloaded' if e.code==529 else 'Rate limited'}. Waiting {wait}s...", flush=True)
                time.sleep(wait)
            elif e.code >= 500:
                time.sleep(RETRY_DELAY * attempt)
            else:
                break
        except Exception as e:
            last_err = str(e)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
    return f"ERROR after {MAX_RETRIES} retries: {last_err}", 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", help="Anthropic API key")
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    api_key = args.key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set ANTHROPIC_API_KEY"); sys.exit(1)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    model_id, label = MODEL

    # Figure out total
    total = 0
    for block, path, pid, pt, gt in CONDITIONS:
        total += TRIALS_PDT_BIAS if block == "pdt_bias" else TRIALS_STROOP

    print("\n" + "=" * 70)
    print("  PHASE 2 VISION RERUN: OPUS 4.7")
    print(f"  Model: {model_id} ({label})")
    print(f"  Total API calls: {total}")
    print(f"  Output: {args.output}")
    print("=" * 70)

    # Pre-load
    print("\n  Pre-loading stimuli...")
    images = {}
    for _, path, _, _, _ in CONDITIONS:
        if path not in images:
            images[path] = get_image_b64(path)
    print(f"  {len(images)} stimuli cached\n")

    results = {}
    if os.path.exists(args.output):
        try:
            with open(args.output, "r") as f:
                results = json.load(f)
            done_prev = sum(1 for v in results.values() if not v.get("text", "").startswith("ERROR"))
            print(f"  Resuming: {done_prev} previously completed\n")
        except:
            pass

    done = skipped = errors = 0
    t_start = time.time()

    for block, path, prompt_id, prompt_text, ground_truth in CONDITIONS:
        stim_name = os.path.splitext(os.path.basename(path))[0]
        n_trials = TRIALS_PDT_BIAS if block == "pdt_bias" else TRIALS_STROOP
        print(f"\n  --- {block} :: {stim_name} :: {prompt_id}  ({n_trials} trials) ---")
        for trial in range(1, n_trials + 1):
            key = f"{label}|{block}|{stim_name}|{prompt_id}|T{trial:02d}"
            done += 1
            if key in results and not results[key].get("text", "").startswith("ERROR"):
                skipped += 1
                continue
            elapsed = time.time() - t_start
            rate = (done - skipped) / max(elapsed, 1)
            eta = f" ETA: {int((total - done) / rate / 60)}m" if rate > 0 else ""
            print(f"  [{done}/{total}]{eta} {key}...", end=" ", flush=True)

            text, ms = call_with_retry(api_key, model_id, images[path], prompt_text)
            is_error = text.startswith("ERROR")
            if is_error:
                errors += 1

            results[key] = {
                "text": text,
                "ms": ms,
                "trial": trial,
                "model": model_id,
                "label": label,
                "block": block,
                "stimulus": stim_name,
                "stimulus_path": path,
                "prompt_id": prompt_id,
                "prompt_text": prompt_text,
                "ground_truth": ground_truth,
                "timestamp": datetime.now().isoformat()
            }
            print(f"{ms}ms{' [ERROR]' if is_error else ''}")
            print(f"         {text[:120].replace(chr(10), ' ')}...")
            time.sleep(DELAY)

        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    ok = sum(1 for v in results.values() if not v["text"].startswith("ERROR"))
    t = int(time.time() - t_start)
    print(f"\n{'='*70}")
    print(f"  PHASE 2 COMPLETE")
    print(f"  OK: {ok} / {len(results)}  |  errors: {errors}  |  skipped: {skipped}")
    print(f"  Wall time: {t//60}m {t%60}s")
    print(f"  Output: {args.output}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
