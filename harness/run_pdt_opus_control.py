#!/usr/bin/env python3
"""
PDT Control Probe: Opus Fabrication Study
Tests whether Opus can report "same" on identical color patches
under different prompt framings.

Stimulus: PDT-00 only (both patches H=42, identical)
Model: Opus 4.6 only
Prompts: 5 framings, 5 trials each = 25 calls

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 run_pdt_opus_control.py
"""

import urllib.request, json, time, base64, sys, os, argparse
from datetime import datetime

MODELS = [
    ("claude-opus-4-6", "OPUS46"),
]

STIMULUS = "PDT-00"
STIMULI_URL = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

PROMPTS = {
    "PC01": "Compare the colors of the two rectangles. Are they the same or different?",
    "PC02": "Are these two rectangles the same or different colors? If they're different, describe both colors.",
    "PC03": "Look carefully at these two rectangles. Are they the exact same color, or is there any difference between them?",
    "PC04": "These two rectangles may or may not be the same color. Which is it? If they are identical, just say so.",
    "PC05": "I need you to be precise. Compare the actual pixel colors of these two rectangles. Are they identical or different? It is completely acceptable to report that they are the same if that is what you observe.",
}

GROUND_TRUTH = "identical (both H=42, S=85%, V=80%, RGB 204,152,31)"

TRIALS = 5
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 10
TIMEOUT = 120
DELAY = 1.5
OUTPUT = "pdt_opus_control_results.json"

def get_image_b64(filename, cache_dir=".stimuli_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, filename)
    if not os.path.exists(path):
        print(f"  Downloading {filename}...", end=" ", flush=True)
        urllib.request.urlretrieve(f"{STIMULI_URL}/{filename}", path)
        print("done")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def call_api(api_key, model, image_b64, prompt):
    payload = {
        "model": model, "max_tokens": 2048, "temperature": TEMPERATURE,
        "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_b64}},
            {"type": "text", "text": prompt}
        ]}]
    }
    req = urllib.request.Request("https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-api-key": api_key, "anthropic-version": "2023-06-01"},
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
            if attempt < MAX_RETRIES: time.sleep(RETRY_DELAY * attempt)
    return f"ERROR after {MAX_RETRIES} retries: {last_err}", 0

def main():
    parser = argparse.ArgumentParser(description="PDT Opus Control Probe")
    parser.add_argument("--key", help="Anthropic API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    api_key = args.key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set ANTHROPIC_API_KEY"); sys.exit(1)

    print("\n=== PDT OPUS CONTROL PROBE ===")
    print(f"Model: Opus 4.6 only")
    print(f"Stimulus: PDT-00 (identical patches)")
    print(f"Ground truth: {GROUND_TRUTH}")
    print(f"Trials per prompt: {args.trials}")
    print(f"\nPrompts:")
    for pid, ptext in PROMPTS.items():
        print(f"  {pid}: \"{ptext}\"")

    total = len(PROMPTS) * args.trials
    print(f"\nTotal API calls: {total}\n")

    image = get_image_b64(f"{STIMULUS}.png")

    results = {}
    if os.path.exists(args.output):
        try:
            with open(args.output, "r") as f: results = json.load(f)
            print(f"Resuming: {sum(1 for v in results.values() if not v.get('text','').startswith('ERROR'))} completed\n")
        except: pass

    done = skipped = errors = 0
    t_start = time.time()

    model_id, label = MODELS[0]
    for prompt_id, prompt_text in PROMPTS.items():
        print(f"\n{'='*70}\n  {prompt_id}: \"{prompt_text[:60]}...\"\n{'='*70}")
        for trial in range(1, args.trials + 1):
            key = f"{label}|{STIMULUS}|{prompt_id}|T{trial}"
            done += 1
            if key in results and not results[key].get("text","").startswith("ERROR"):
                skipped += 1; continue
            print(f"  [{done}/{total}] {key}...", end=" ", flush=True)
            text, ms = call_with_retry(api_key, model_id, image, prompt_text)
            is_error = text.startswith("ERROR")
            if is_error: errors += 1
            results[key] = {
                "text": text, "ms": ms, "trial": trial, "model": model_id,
                "label": label, "stimulus": STIMULUS, "prompt_id": prompt_id,
                "prompt_text": prompt_text, "ground_truth": GROUND_TRUTH,
                "timestamp": datetime.now().isoformat()
            }
            print(f"{ms}ms{' [ERROR]' if is_error else ''}")
            print(f"         {text[:120].replace(chr(10),' ')}...")
            time.sleep(DELAY)

        with open(args.output, "w") as f: json.dump(results, f, indent=2)
        print(f"  Checkpoint saved ({len(results)} results)")

    with open(args.output, "w") as f: json.dump(results, f, indent=2)
    ok = sum(1 for v in results.values() if not v["text"].startswith("ERROR"))
    t = int(time.time() - t_start)
    print(f"\n{'='*70}")
    print(f"  COMPLETE: {ok} OK, {errors} errors, {skipped} skipped | {t//60}m{t%60}s")
    print(f"  Output: {args.output}")
    print(f"{'='*70}\n")

    # Quick summary
    print("QUICK SUMMARY:")
    for prompt_id in PROMPTS:
        entries = [v for v in results.values() if v.get("prompt_id") == prompt_id]
        same_count = sum(1 for e in entries if any(w in e["text"].lower() for w in ["the same", "identical", "same color", "they match"]))
        diff_count = sum(1 for e in entries if "different" in e["text"].lower())
        print(f"  {prompt_id}: {same_count}/5 same, {diff_count}/5 different")

if __name__ == "__main__":
    main()
