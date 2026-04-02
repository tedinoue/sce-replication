#!/usr/bin/env python3
"""
SCE Contextual Prior Override: Gemini Models
Tests whether a green-tint contextual frame shifts the semantic prior
driving SCE direction reversal.

NOTE: Gemini API blocks cloud IPs. Run this locally only.

Stimuli: S002 (prior-consistent), S003 (prior-conflicting)
Models: Gemini 2.5 Pro, Gemini 2.5 Flash

Usage:
    python3 run_cpo_gemini.py --key "AIzaSy..."
    # or
    export GEMINI_API_KEY="AIzaSy..."
    python3 run_cpo_gemini.py
"""

import urllib.request, json, time, base64, sys, os, argparse
from datetime import datetime

# ── Config ───────────────────────────────────────────────────────────────────
MODELS = [
    ("gemini-2.5-pro",   "GEMINI_25_PRO"),
    ("gemini-2.5-flash", "GEMINI_25_FLASH"),
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
RETRY_DELAY = 15
TIMEOUT = 180  # thinking models can be slow
DELAY = 1.5

OUTPUT = "cpo_gemini_results.json"

GROUND_TRUTH = {
    "S002": "Bus=H42 (WARMER), Van=H51 (cooler). Prior-CONSISTENT.",
    "S003": "Bus=H51 (COOLER), Van=H41 (warmer). Prior-CONFLICTING.",
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

# ── Extract non-thinking text from Gemini response ──────────────────────────
def extract_text(result):
    candidates = result.get("candidates", [])
    if not candidates:
        return "ERROR: No candidates in response"
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        return "ERROR: No parts in response"

    # Collect non-thinking text parts
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
        return "ERROR: Model produced only thinking output. Thinking: " + thinking_text[0][:200]
    return f"ERROR: No text in any part. Keys: {[list(p.keys()) for p in parts]}"

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
    parser = argparse.ArgumentParser(description="SCE CPO: Gemini")
    parser.add_argument("--key", help="Gemini API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    api_key = args.key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set GEMINI_API_KEY")
        sys.exit(1)

    print("\n=== SCE Contextual Prior Override: GEMINI ===")
    print("NOTE: Gemini blocks cloud IPs. This must run locally.")
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

                    preview = text[:100].replace("\n", " ")
                    err_flag = " [ERROR]" if is_error else ""
                    print(f"{ms}ms{err_flag}")
                    print(f"         {preview}...")

                    time.sleep(DELAY)

        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)

        model_time = int(time.time() - model_start)
        print(f"\n  --- {label} complete ({model_time}s) ---")

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
