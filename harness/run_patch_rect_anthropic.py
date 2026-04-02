#!/usr/bin/env python3
"""
SCE Patch Isolation: Anthropic Models (Corrected Prompts)
S003Patch.png: color patches on black background, no object identity.
Prompts corrected to say "rectangles" instead of "vehicles."

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 run_patch_rect_anthropic.py
"""

import urllib.request, json, time, base64, sys, os, argparse
from datetime import datetime

MODELS = [
    ("claude-opus-4-6",           "OPUS46"),
    ("claude-sonnet-4-6",         "SONNET46"),
    ("claude-haiku-4-5-20251001", "HAIKU45"),
]

STIMULUS = "S003Patch"
STIMULI_URL = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

PROMPTS = {
    "PS00":  "Describe this scene.",
    "PS03r": "Compare the colors of the two rectangles. Are they the same or different?",
    "PS04r": "Carefully analyze the exact hue of each rectangle. Which is warmer, which is cooler?",
    "PS05r": "Measure the dominant hue of each rectangle in degrees on a standard HSV color wheel (0=red, 60=yellow, 120=green).",
}

TRIALS = 5
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 10
TIMEOUT = 120
DELAY = 1.5
OUTPUT = "s003patch_rect_anthropic_results.json"

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
    parser = argparse.ArgumentParser(description="SCE Patch (rectangles): Anthropic")
    parser.add_argument("--key", help="Anthropic API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    api_key = args.key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set ANTHROPIC_API_KEY"); sys.exit(1)

    print("\n=== SCE Patch Isolation (rectangles): ANTHROPIC ===")
    print(f"Models: {', '.join(l for _,l in MODELS)}")
    print(f"Prompts: {', '.join(PROMPTS.keys())}")
    print(f"Trials: {args.trials}")
    total = len(MODELS) * len(PROMPTS) * args.trials
    print(f"Total API calls: {total}")
    print(f"\nGround truth: Left=H51 (cooler), Right=H41 (warmer)\n")

    image = get_image_b64(f"{STIMULUS}.png")
    

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
        for prompt_id, prompt_text in PROMPTS.items():
            for trial in range(1, args.trials + 1):
                key = f"{label}|{STIMULUS}|{prompt_id}|T{trial}"
                done += 1
                if key in results and not results[key].get("text","").startswith("ERROR"):
                    skipped += 1; continue
                elapsed = time.time() - t_start
                rate = (done - skipped) / max(elapsed, 1)
                eta = f" ETA: {int((total-done)/rate/60)}m" if rate > 0 else ""
                print(f"  [{done}/{total}]{eta} {key}...", end=" ", flush=True)
                text, ms = call_with_retry(api_key, model_id, image, prompt_text)
                is_error = text.startswith("ERROR")
                if is_error: errors += 1
                results[key] = {"text": text, "ms": ms, "trial": trial, "model": model_id,
                    "label": label, "stimulus": STIMULUS, "prompt_id": prompt_id,
                    "prompt_text": prompt_text, "timestamp": datetime.now().isoformat()}
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
