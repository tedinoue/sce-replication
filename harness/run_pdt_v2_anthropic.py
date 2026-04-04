#!/usr/bin/env python3
"""
PDT v2 (Patch Discrimination Threshold): Anthropic Models
PS03r prompt: "Are they the same or different?" (allows "same" response)
Includes +9 degree positive control matching S003Patch shift.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 run_pdt_v2_anthropic.py
"""

import urllib.request, json, time, base64, sys, os, argparse
from datetime import datetime

MODELS = [
    ("claude-opus-4-6",           "OPUS46"),
    ("claude-sonnet-4-6",         "SONNET46"),
    ("claude-haiku-4-5-20251001", "HAIKU45"),
]

STIMULI = {
    "PDT-00": {"shift": 0, "shifted_side": "none",  "ground_truth": "identical"},
    "PDT-03": {"shift": 3, "shifted_side": "left",  "ground_truth": "left is cooler (H45 vs H42)"},
    "PDT-04": {"shift": 3, "shifted_side": "right", "ground_truth": "right is cooler (H42 vs H45)"},
    "PDT-06": {"shift": 6, "shifted_side": "left",  "ground_truth": "left is cooler (H48 vs H42)"},
    "PDT-07": {"shift": 6, "shifted_side": "right", "ground_truth": "right is cooler (H42 vs H48)"},
    "PDT-09": {"shift": 9, "shifted_side": "left",  "ground_truth": "left is cooler (H51 vs H42)"},
    "PDT-10": {"shift": 9, "shifted_side": "right", "ground_truth": "right is cooler (H42 vs H51)"},
}

STIMULI_URL = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

PROMPT_ID = "PS03r"
PROMPT_TEXT = "Compare the colors of the two rectangles. Are they the same or different?"

TRIALS = 5
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 10
TIMEOUT = 120
DELAY = 1.5
OUTPUT = "pdt_v2_anthropic_results.json"

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
    parser = argparse.ArgumentParser(description="PDT v2: Anthropic (PS03r)")
    parser.add_argument("--key", help="Anthropic API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    api_key = args.key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set ANTHROPIC_API_KEY"); sys.exit(1)

    print("\n=== PDT v2 (PS03r same/different): ANTHROPIC ===")
    print(f"Models: {', '.join(l for _,l in MODELS)}")
    print(f"Stimuli: {', '.join(STIMULI.keys())}")
    print(f"Prompt: {PROMPT_ID} - \"{PROMPT_TEXT}\"")
    print(f"Trials: {args.trials}")
    total = len(MODELS) * len(STIMULI) * args.trials
    print(f"Total API calls: {total}")
    print(f"\nGround truth:")
    for stim, info in STIMULI.items():
        print(f"  {stim}: {info['ground_truth']}")
    print()

    images = {}
    for stim in STIMULI:
        images[stim] = get_image_b64(f"{stim}.png")
    print(f"  Loaded {len(images)} stimulus images\n")

    results = {}
    if os.path.exists(args.output):
        try:
            with open(args.output, "r") as f: results = json.load(f)
            print(f"Resuming: {sum(1 for v in results.values() if not v.get('text','').startswith('ERROR'))} completed\n")
        except: pass

    done = skipped = errors = 0
    t_start = time.time()

    for model_id, label in MODELS:
        print(f"\n{'='*70}\n  {label} ({model_id})\n{'='*70}")
        for stim, stim_info in STIMULI.items():
            for trial in range(1, args.trials + 1):
                key = f"{label}|{stim}|{PROMPT_ID}|T{trial}"
                done += 1
                if key in results and not results[key].get("text","").startswith("ERROR"):
                    skipped += 1; continue
                elapsed = time.time() - t_start
                rate = (done - skipped) / max(elapsed, 1)
                eta = f" ETA: {int((total-done)/rate/60)}m" if rate > 0 else ""
                print(f"  [{done}/{total}]{eta} {key}...", end=" ", flush=True)
                text, ms = call_with_retry(api_key, model_id, images[stim], PROMPT_TEXT)
                is_error = text.startswith("ERROR")
                if is_error: errors += 1
                results[key] = {"text": text, "ms": ms, "trial": trial, "model": model_id,
                    "label": label, "stimulus": stim, "prompt_id": PROMPT_ID,
                    "prompt_text": PROMPT_TEXT, "shift": stim_info["shift"],
                    "shifted_side": stim_info["shifted_side"],
                    "ground_truth": stim_info["ground_truth"],
                    "timestamp": datetime.now().isoformat()}
                print(f"{ms}ms{' [ERROR]' if is_error else ''}")
                print(f"         {text[:100].replace(chr(10),' ')}...")
                time.sleep(DELAY)

        with open(args.output, "w") as f: json.dump(results, f, indent=2)
        print(f"  Checkpoint saved ({len(results)} results)")

    with open(args.output, "w") as f: json.dump(results, f, indent=2)
    ok = sum(1 for v in results.values() if not v["text"].startswith("ERROR"))
    t = int(time.time() - t_start)
    print(f"\n{'='*70}\n  COMPLETE: {ok} OK, {errors} errors, {skipped} skipped | {t//60}m{t%60}s\n  Output: {args.output}\n{'='*70}\n")

if __name__ == "__main__":
    main()
