#!/usr/bin/env python3
"""
Phase 4: PDT-00 prompt-order probe on Opus 4.7.

Phase 2 found 20/20 "left is warmer" on identical patches with the prompt:
    "Carefully analyze the exact hue of each rectangle. Which is warmer, which is cooler?"

This phase tests whether that 100% left-bias is:
    (A) A spatial/visual bias toward the left side of the image, or
    (B) A word-order priming effect ("warmer" is mentioned first, so model fills
        that slot first, and takes the least-effort first-mentioned option "left"),
    (C) A first-slot confabulation (model structures reply as "Left: X. Right: Y."
        and commits to warmer in the first slot regardless of wording).

DESIGN: Same stimulus (PDT-00, identical patches), three prompts, N=20 for the
flip probe and N=5 each for the secondary probes. Total = 30 calls.

PROMPTS:
  1. BASELINE (confirm Phase 2 pattern reproduces this session): original prompt
     "Which is warmer, which is cooler?" x 5 trials
  2. REVERSED (key test): swap the order of warmer/cooler in the question
     "Which is cooler, which is warmer?" x 20 trials
  3. RIGHT-FIRST (stronger order flip): name "right" before "left"
     "Compare the right rectangle to the left rectangle. Which is warmer?" x 5

PREDICTIONS:
  Mechanism A (spatial/visual):
    Baseline: 5/5 left-warmer (confirm).
    Reversed: ~20/20 left-warmer STILL (mechanism is in the image, not the prompt).
    Right-first: 5/5 left-warmer (mechanism is in the image).

  Mechanism B/C (word-order, first-slot):
    Baseline: 5/5 left-warmer.
    Reversed: bias FLIPS toward "right-warmer" (because "cooler" is now first,
             model fills "cooler: left" and by elimination "warmer: right").
    Right-first: right-warmer dominates.

  Mixed (A+B both active):
    Reversed: ~50/50 noise, or partial shift.

Model: claude-opus-4-7 ONLY
Total calls: 5 + 20 + 5 = 30

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 run_47_phase4.py
"""

import urllib.request, urllib.error, json, time, base64, sys, os, argparse
from datetime import datetime

MODEL = ("claude-opus-4-7", "OPUS47")
STIMULI_BASE = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

CONDITIONS = [
    # (block, path, prompt_id, prompt_text, ground_truth, n_trials)
    ("pdt_order", "PDT-00.png", "baseline_warmer_first",
     "Carefully analyze the exact hue of each rectangle. Which is warmer, which is cooler?",
     "Phase 2 baseline (confirm reproduction). Expect: 5/5 left-warmer.",
     5),

    ("pdt_order", "PDT-00.png", "reversed_cooler_first",
     "Carefully analyze the exact hue of each rectangle. Which is cooler, which is warmer?",
     "Key test. Same stimulus, order of warmer/cooler flipped. "
     "If spatial bias: still left-warmer. If word-order: flips to right-warmer.",
     20),

    ("pdt_order", "PDT-00.png", "right_first_reference",
     "Carefully analyze the exact hue of each rectangle. Compare the right rectangle to the left rectangle. Which is warmer?",
     "Stronger order flip. 'Right' named before 'left' in the prompt. "
     "If right-warmer dominates here, output-slot order drives the bias.",
     5),
]

TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 10
TIMEOUT = 120
DELAY = 1.5
OUTPUT = "results/opus47_phase4_results.json"


def detect_media_type(b64_str):
    """Detect image format from magic bytes so mislabeled files still work."""
    head = base64.b64decode(b64_str[:12])
    if head[:8] == b"\x89PNG\r\n\x1a\n": return "image/png"
    if head[:2] == b"\xff\xd8": return "image/jpeg"
    if head[:6] in (b"GIF87a", b"GIF89a"): return "image/gif"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP": return "image/webp"
    return "image/png"


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
    media_type = detect_media_type(image_b64)
    payload = {
        "model": model, "max_tokens": 4096, "temperature": TEMPERATURE,
        "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}},
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
                print(f"\n    {'Overloaded' if e.code == 529 else 'Rate limited'}. Waiting {wait}s...", flush=True)
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
    total = sum(c[-1] for c in CONDITIONS)

    print("\n" + "=" * 70)
    print("  PHASE 4: PDT-00 PROMPT-ORDER PROBE ON OPUS 4.7")
    print(f"  Model: {model_id} ({label})")
    print(f"  Total API calls: {total}")
    print(f"  Output: {args.output}")
    print("=" * 70)

    print("\n  Pre-loading stimuli...")
    images = {}
    for c in CONDITIONS:
        path = c[1]
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

    for block, path, prompt_id, prompt_text, ground_truth, n_trials in CONDITIONS:
        stim_name = os.path.splitext(os.path.basename(path))[0]
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
                "text": text, "ms": ms, "trial": trial,
                "model": model_id, "label": label, "block": block,
                "stimulus": stim_name, "stimulus_path": path,
                "prompt_id": prompt_id, "prompt_text": prompt_text,
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
    print(f"  PHASE 4 COMPLETE")
    print(f"  OK: {ok} / {len(results)}  |  errors: {errors}  |  skipped: {skipped}")
    print(f"  Wall time: {t//60}m {t%60}s")
    print(f"  Output: {args.output}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
