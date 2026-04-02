#!/usr/bin/env python3
"""
SCE Contextual Prior Override: Anthropic Models
Tests whether a green-tint contextual frame shifts the semantic prior
driving SCE direction reversal.

Stimuli: S002 (prior-consistent), S003 (prior-conflicting)
Models: Opus 4.6, Sonnet 4.6, Haiku 4.5

Usage:
    python3 run_cpo_anthropic.py --key "sk-ant-..."
    # or
    export ANTHROPIC_API_KEY="sk-ant-..."
    python3 run_cpo_anthropic.py
"""

import urllib.request, json, time, base64, sys, os, argparse
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────────────────
MODELS = [
    ("claude-opus-4-6",           "OPUS46"),
    ("claude-sonnet-4-6",         "SONNET46"),
    ("claude-haiku-4-5-20251001", "HAIKU45"),
]

STIMULI = ["S002", "S003"]
STIMULI_URL = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

PROMPTS = {
    "PS03": "Compare the colors of the two vehicles. Are they the same or different?",
    "CPO":  "This photograph was taken in a country where school buses have a greener tint to them than in the US. Compare the colors of the two vehicles. Are they the same or different?",
}

TRIALS = 5
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 10
TIMEOUT = 120
DELAY = 1.5  # between calls

OUTPUT = "cpo_anthropic_results.json"

# ── Ground truth (for summary printing) ──────────────────────────────────────
GROUND_TRUTH = {
    "S002": "Bus=H42 (WARMER), Van=H51 (cooler). Prior-CONSISTENT: correct answer aligns with 'buses are warm'.",
    "S003": "Bus=H51 (COOLER), Van=H41 (warmer). Prior-CONFLICTING: correct answer contradicts 'buses are warm'.",
}

# ── Image cache ──────────────────────────────────────────────────────────────
def get_image_b64(filename, cache_dir=".stimuli_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, filename)
    if not os.path.exists(path):
        print(f"  Downloading {filename}...", end=" ", flush=True)
        urllib.request.urlretrieve(f"{STIMULI_URL}/{filename}", path)
        print("done")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ── API call ─────────────────────────────────────────────────────────────────
def call_api(api_key, model, image_b64, prompt):
    payload = {
        "model": model,
        "max_tokens": 2048,
        "temperature": TEMPERATURE,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_b64
                }},
                {"type": "text", "text": prompt}
            ]
        }]
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        result = json.loads(resp.read())
        ms = int((time.time() - t0) * 1000)
        text = "".join(
            b.get("text", "") for b in result.get("content", [])
            if b.get("type") == "text"
        )
        return text.strip() or "ERROR: No text in response", ms

# ── Retry wrapper ────────────────────────────────────────────────────────────
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
            if e.code == 429:
                wait = RETRY_DELAY * attempt * 2
                print(f"\n    Rate limited. Waiting {wait}s (attempt {attempt}/{MAX_RETRIES})...", flush=True)
                time.sleep(wait)
            elif e.code >= 500:
                wait = RETRY_DELAY * attempt
                print(f"\n    Server error. Waiting {wait}s...", flush=True)
                time.sleep(wait)
            elif e.code == 529:  # Anthropic overloaded
                wait = RETRY_DELAY * attempt * 3
                print(f"\n    API overloaded (529). Waiting {wait}s...", flush=True)
                time.sleep(wait)
            else:
                break  # 4xx non-retryable
        except Exception as e:
            last_err = str(e)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
    return f"ERROR after {MAX_RETRIES} retries: {last_err}", 0

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="SCE CPO: Anthropic")
    parser.add_argument("--key", help="Anthropic API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    api_key = args.key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set ANTHROPIC_API_KEY")
        sys.exit(1)

    # Download stimuli
    print("\n=== SCE Contextual Prior Override: ANTHROPIC ===")
    print(f"Models: {', '.join(l for _,l in MODELS)}")
    print(f"Stimuli: {', '.join(STIMULI)}")
    print(f"Prompts: {', '.join(PROMPTS.keys())}")
    print(f"Trials: {args.trials}")
    total = len(MODELS) * len(STIMULI) * len(PROMPTS) * args.trials
    print(f"Total API calls: {total}\n")

    for stim, gt in GROUND_TRUTH.items():
        print(f"  {stim}: {gt}")
    print()

    print("Downloading stimuli...")
    images = {s: get_image_b64(f"{s}.png") for s in STIMULI}
    print(f"Cached {len(images)} images.\n")

    # Load existing results for resume
    results = {}
    if os.path.exists(args.output):
        try:
            with open(args.output, "r") as f:
                results = json.load(f)
            existing = sum(1 for v in results.values() if not v.get("text","").startswith("ERROR"))
            print(f"Resuming: {existing} completed results loaded from {args.output}\n")
        except:
            pass

    done = 0
    skipped = 0
    errors = 0
    t_start = time.time()

    for model_id, label in MODELS:
        print(f"\n{'='*70}")
        print(f"  MODEL: {label} ({model_id})")
        print(f"{'='*70}")
        model_start = time.time()

        for stim in STIMULI:
            for prompt_id, prompt_text in PROMPTS.items():
                for trial in range(1, args.trials + 1):
                    key = f"{label}|{stim}|{prompt_id}|T{trial}"
                    done += 1

                    # Skip completed
                    if key in results and not results[key].get("text","").startswith("ERROR"):
                        skipped += 1
                        continue

                    remaining = total - done
                    elapsed = time.time() - t_start
                    rate = (done - skipped) / max(elapsed, 1)
                    eta = f" ETA: {int(remaining/rate/60)}m" if rate > 0 and remaining > 0 else ""

                    print(f"  [{done}/{total}]{eta} {key}...", end=" ", flush=True)

                    text, ms = call_with_retry(api_key, model_id, images[stim], prompt_text)
                    is_error = text.startswith("ERROR")
                    if is_error:
                        errors += 1

                    results[key] = {
                        "text": text,
                        "ms": ms,
                        "trial": trial,
                        "model": model_id,
                        "label": label,
                        "stimulus": stim,
                        "prompt_id": prompt_id,
                        "prompt_text": prompt_text,
                        "timestamp": datetime.now().isoformat(),
                    }

                    # Print preview
                    preview = text[:100].replace("\n", " ")
                    err_flag = " [ERROR]" if is_error else ""
                    print(f"{ms}ms{err_flag}")
                    print(f"         {preview}...")

                    time.sleep(DELAY)

        # Checkpoint + model summary
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)

        model_time = int(time.time() - model_start)
        print(f"\n  --- {label} complete ({model_time}s) ---")

        # Print intermediate results table for this model
        print(f"\n  {'STIM':<6} {'PROMPT':<6} {'TRIALS':>6}  PREVIEW")
        print(f"  {'-'*60}")
        for stim in STIMULI:
            for prompt_id in PROMPTS:
                texts = []
                for t in range(1, args.trials + 1):
                    k = f"{label}|{stim}|{prompt_id}|T{t}"
                    if k in results and not results[k]["text"].startswith("ERROR"):
                        texts.append(results[k]["text"][:80].replace("\n"," "))
                if texts:
                    print(f"  {stim:<6} {prompt_id:<6} {len(texts):>6}  {texts[0]}...")
        print()

    # Final save
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    ok = sum(1 for v in results.values() if not v["text"].startswith("ERROR"))
    total_time = int(time.time() - t_start)
    print(f"\n{'='*70}")
    print(f"  COMPLETE: {ok} OK, {errors} errors, {skipped} skipped")
    print(f"  Time: {total_time//60}m {total_time%60}s")
    print(f"  Output: {args.output}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
