#!/usr/bin/env python3
"""
SCE Patch Isolation Test: Gemini Models
S003Patch.png: color patches extracted from bus (H=51, cooler) and van (H=41, warmer)
on black background. No object identity. Tests perceptual discrimination without
semantic prior interference.

NOTE: Gemini API blocks cloud IPs. Run this locally only.

Models: Gemini 2.5 Pro, Gemini 2.5 Flash
Prompts: PS00 (describe), PS03 (same/different), PS04 (warmer/cooler), PS05 (measure hue)

Usage:
    python3 run_patch_gemini.py --key "AIzaSy..."
    # or
    export GEMINI_API_KEY="AIzaSy..."
    python3 run_patch_gemini.py
"""

import urllib.request, json, time, base64, sys, os, argparse
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────────────────
MODELS = [
    ("gemini-2.5-pro",   "GEMINI_25_PRO"),
    ("gemini-2.5-flash", "GEMINI_25_FLASH"),
]

STIMULUS = "S003Patch"
STIMULI_URL = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

PROMPTS = {
    "PS00": "Describe this scene.",
    "PS03": "Compare the colors of the two vehicles. Are they the same or different?",
    "PS04": "Carefully analyze the exact hue of each vehicle. Which is warmer, which is cooler?",
    "PS05": "Measure the dominant hue of each vehicle in degrees on a standard HSV color wheel (0=red, 60=yellow, 120=green).",
}

TRIALS = 5
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 15
TIMEOUT = 180
DELAY = 1.5

OUTPUT = "s003patch_gemini_results.json"

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

# ── Extract non-thinking text ────────────────────────────────────────────────
def extract_text(result):
    candidates = result.get("candidates", [])
    if not candidates:
        return "ERROR: No candidates in response"
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        return "ERROR: No parts in response"
    response_text = []
    thinking_text = []
    for part in parts:
        has_text = "text" in part
        is_thought = part.get("thought", False)
        if has_text and not is_thought:
            response_text.append(part["text"])
        elif has_text and is_thought:
            thinking_text.append(part["text"])
    if response_text:
        return "\n".join(response_text)
    if thinking_text:
        return "ERROR: Only thinking output. Thinking: " + thinking_text[0][:200]
    return f"ERROR: No text. Keys: {[list(p.keys()) for p in parts]}"

# ── API call ─────────────────────────────────────────────────────────────────
def call_api(api_key, model, image_b64, prompt):
    payload = {
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/png", "data": image_b64}}
        ]}],
        "generationConfig": {
            "temperature": TEMPERATURE,
            "maxOutputTokens": 8000
        }
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    req = urllib.request.Request(url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        result = json.loads(resp.read())
        ms = int((time.time() - t0) * 1000)
        text = extract_text(result)
        return text, ms

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
            if e.code in (429, 503):
                wait = RETRY_DELAY * attempt * 2
                print(f"\n    Rate limited / overloaded. Waiting {wait}s (attempt {attempt}/{MAX_RETRIES})...", flush=True)
                time.sleep(wait)
            elif e.code >= 500:
                wait = RETRY_DELAY * attempt
                print(f"\n    Server error. Waiting {wait}s...", flush=True)
                time.sleep(wait)
            else:
                break
        except Exception as e:
            last_err = str(e)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)
    return f"ERROR after {MAX_RETRIES} retries: {last_err}", 0

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="SCE Patch Test: Gemini")
    parser.add_argument("--key", help="Gemini API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    api_key = args.key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set GEMINI_API_KEY")
        sys.exit(1)

    print("\n=== SCE Patch Isolation Test: GEMINI ===")
    print("NOTE: Gemini blocks cloud IPs. Run locally only.")
    print(f"Stimulus: {STIMULUS}.png (color patches, no object identity)")
    print(f"Models: {', '.join(l for _,l in MODELS)}")
    print(f"Prompts: {', '.join(PROMPTS.keys())}")
    print(f"Trials: {args.trials}")
    total = len(MODELS) * len(PROMPTS) * args.trials
    print(f"Total API calls: {total}")
    print()
    print("Ground truth: Left patch=H51 (cooler), Right patch=H41 (warmer)")
    print("Correct direction: right is warmer/more orange, left is cooler/more green-yellow")
    print()

    print("Downloading stimulus...")
    image = get_image_b64(f"{STIMULUS}.png")
    
    print("Cached.\n")

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

        for prompt_id, prompt_text in PROMPTS.items():
            for trial in range(1, args.trials + 1):
                key = f"{label}|{STIMULUS}|{prompt_id}|T{trial}"
                done += 1

                if key in results and not results[key].get("text","").startswith("ERROR"):
                    skipped += 1
                    continue

                remaining = total - done
                elapsed = time.time() - t_start
                rate = (done - skipped) / max(elapsed, 1)
                eta = f" ETA: {int(remaining/rate/60)}m" if rate > 0 and remaining > 0 else ""

                print(f"  [{done}/{total}]{eta} {key}...", end=" ", flush=True)

                text, ms = call_with_retry(api_key, model_id, image, prompt_text)
                is_error = text.startswith("ERROR")
                if is_error:
                    errors += 1

                results[key] = {
                    "text": text,
                    "ms": ms,
                    "trial": trial,
                    "model": model_id,
                    "label": label,
                    "stimulus": STIMULUS,
                    "prompt_id": prompt_id,
                    "prompt_text": prompt_text,
                    "timestamp": datetime.now().isoformat(),
                }

                preview = text[:100].replace("\n", " ")
                err_flag = " [ERROR]" if is_error else ""
                print(f"{ms}ms{err_flag}")
                print(f"         {preview}...")

                time.sleep(DELAY)

        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)

        model_time = int(time.time() - model_start)
        print(f"\n  --- {label} complete ({model_time}s) ---")

        print(f"\n  {'PROMPT':<6} {'TRIALS':>6}  PREVIEW")
        print(f"  {'-'*60}")
        for prompt_id in PROMPTS:
            texts = []
            for t in range(1, args.trials + 1):
                k = f"{label}|{STIMULUS}|{prompt_id}|T{t}"
                if k in results and not results[k]["text"].startswith("ERROR"):
                    texts.append(results[k]["text"][:80].replace("\n"," "))
            if texts:
                print(f"  {prompt_id:<6} {len(texts):>6}  {texts[0]}...")
        print()

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
