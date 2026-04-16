#!/usr/bin/env python3
"""
Phase 1 vision rerun on Claude Opus 4.7.

Purpose: Test whether the "better vision + better disclosure/data discipline"
claims in the 4.7 release change our core SCE findings. Single new model,
baseline prompts (no persona), narrow stimulus set.

Compare directly against existing 4.6 / Sonnet 4.6 / Haiku 4.5 baselines in:
  - cpo_anthropic_results.json          (S003 bus/van 10 deg with CPO)
  - s003patch_rect_anthropic_results.json (S003Patch no object identity)
  - fence_control_anthropic_results.json  (S005 40/40 white capture)
  - stroop_graded_anthropic_results.json  (T6 at 2/4/8/12 items)
  - pdt_v1/v2_anthropic_results.json     (PDT-00 identical patches)
  - persona_anthropic_results.json       (S003 / S005 describe-scene baselines)

Design:
  - Model: claude-opus-4-7 ONLY
  - No system prompt (true baseline; persona can come in Phase 2)
  - N=5 trials per condition
  - Two prompt styles where relevant: free description AND direction-forcing
  - Total calls: ~75

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 run_47_phase1.py
"""

import urllib.request, urllib.error, json, time, base64, sys, os, argparse
from datetime import datetime

MODEL = ("claude-opus-4-7", "OPUS47")

STIMULI_BASE = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

# ============================================================
# CONDITIONS
# ============================================================
# Each entry: (block, stim_path, prompt_id, prompt_text, ground_truth)

CONDITIONS = [
    # --- S003: 10-deg bus/van, the original SCE stimulus ---
    ("s003",      "S003.png",
                  "describe",
                  "Describe this scene.",
                  "Bus=H51 (cooler), Van=H41 (warmer). 10-deg shift. "
                  "Prior-conflicting: bus should be warmer/yellower, but in this image it is cooler."),
    ("s003",      "S003.png",
                  "warmer_prompt",
                  "Which is warmer in hue, the bus or the van?",
                  "Correct answer: the van (H41 < H51). Direction-forcing prompt."),

    # --- S003Patch: same pixels as S003 but object identity removed ---
    ("s003patch", "S003Patch.png",
                  "describe",
                  "Describe this scene.",
                  "Two color patches from S003 on black. No object identity. "
                  "All Anthropic models: 40/40 correct direction with direction-forcing prompt at 4.6 baseline."),
    ("s003patch", "S003Patch.png",
                  "warmer_prompt",
                  "Which patch is warmer in hue, the left or the right?",
                  "Ground truth: right patch is warmer (H41 vs H51). "
                  "4.6 baseline: 40/40 correct with this framing. Ceiling check."),

    # --- S005: white picket fence, the 40/40 capture ---
    ("s005",      "S005.png",
                  "describe",
                  "Describe this scene.",
                  "Fence=cream/beige (H32, S50%). Box=same. NOT white. "
                  "4.6 Anthropic baseline: ~40/40 'white' capture."),
    ("s005",      "S005.png",
                  "color_prompt",
                  "What color is the fence?",
                  "Ground truth: cream or beige (H32, S50%). Direction-forcing: names the fence specifically."),

    # --- Stroop graded load ---
    ("stroop",    "stroop/T6_graded_load_4.png",
                  "stroop_4",
                  "For each word, report the TEXT and the INK COLOR.",
                  "4 items. Near Opus 4.6 capacity threshold (~5-7 items)."),
    ("stroop",    "stroop/T6_graded_load_8.png",
                  "stroop_8",
                  "For each word, report the TEXT and the INK COLOR.",
                  "8 items. Above Opus 4.6 threshold. Expect binding failures."),
    ("stroop",    "stroop/T6_graded_load_12.png",
                  "stroop_12",
                  "For each word, report the TEXT and the INK COLOR.",
                  "12 items. Full load. Opus 4.6 ~25-28% correct in prior runs."),

    # --- PDT: identical patches and 6-degree shift ---
    ("pdt",       "PDT-00.png",
                  "warmer_prompt",
                  "Carefully analyze the exact hue of each rectangle. Which is warmer, which is cooler?",
                  "IDENTICAL patches. Ground truth: no difference. "
                  "Opus 4.6 baseline: 0/35 said 'same' across 5 prompt framings (confabulation)."),
    ("pdt",       "PDT-06.png",
                  "warmer_prompt",
                  "Carefully analyze the exact hue of each rectangle. Which is warmer, which is cooler?",
                  "6-degree shift. LEFT=H48 (cooler), RIGHT=H42 (warmer). "
                  "Opus 4.6 baseline: high correct direction with this prompt."),
]

# ============================================================
# CONFIG
# ============================================================

TRIALS = 5
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 10
TIMEOUT = 120
DELAY = 1.5
OUTPUT = "results/opus47_phase1_results.json"

# ============================================================

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
    parser = argparse.ArgumentParser(description="Phase 1 vision rerun on Opus 4.7")
    parser.add_argument("--key", help="Anthropic API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    api_key = args.key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set ANTHROPIC_API_KEY"); sys.exit(1)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    model_id, label = MODEL
    total = len(CONDITIONS) * args.trials

    print("\n" + "=" * 70)
    print("  PHASE 1 VISION RERUN: OPUS 4.7")
    print(f"  Model: {model_id} ({label})")
    print(f"  Conditions: {len(CONDITIONS)}")
    print(f"  Trials per condition: {args.trials}")
    print(f"  Total API calls: {total}")
    print(f"  Output: {args.output}")
    print("=" * 70)

    # Pre-load all stimuli
    print("\n  Pre-loading stimuli...")
    images = {}
    for _, path, _, _, _ in CONDITIONS:
        if path not in images:
            images[path] = get_image_b64(path)
    print(f"  {len(images)} unique images cached\n")

    # Resume support
    results = {}
    if os.path.exists(args.output):
        try:
            with open(args.output, "r") as f:
                results = json.load(f)
            completed = sum(1 for v in results.values() if not v.get("text", "").startswith("ERROR"))
            print(f"  Resuming: {completed} previously completed\n")
        except:
            pass

    done = skipped = errors = 0
    t_start = time.time()

    for block, path, prompt_id, prompt_text, ground_truth in CONDITIONS:
        stim_name = os.path.splitext(os.path.basename(path))[0]
        print(f"\n  --- {block} :: {stim_name} :: {prompt_id} ---")
        for trial in range(1, args.trials + 1):
            key = f"{label}|{block}|{stim_name}|{prompt_id}|T{trial}"
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

        # Checkpoint after each condition
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    ok = sum(1 for v in results.values() if not v["text"].startswith("ERROR"))
    t = int(time.time() - t_start)
    print(f"\n{'='*70}")
    print(f"  PHASE 1 COMPLETE")
    print(f"  OK: {ok} / {len(results)}  |  errors: {errors}  |  skipped: {skipped}")
    print(f"  Wall time: {t//60}m {t%60}s")
    print(f"  Output: {args.output}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
