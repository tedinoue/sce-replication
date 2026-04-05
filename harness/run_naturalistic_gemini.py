#!/usr/bin/env python3
"""
SCE Naturalistic Scene Experiments: Gemini Models
NOTE: Gemini blocks cloud IPs. Run locally only.
S004 (Orange Banana / Blue Apple) + S005 (White Picket Fence / Box)
Narrative prompt only. Tests semantic capture on naturalistic objects.

Usage:
    export GEMINI_API_KEY=AIzaSy...
    python3 run_naturalistic_gemini.py
"""

import urllib.request, json, time, base64, sys, os, argparse
from datetime import datetime

MODELS = [
    ("gemini-2.5-pro",   "GEMINI_25_PRO"),
    ("gemini-2.5-flash", "GEMINI_25_FLASH"),
]

STIMULI = {
    "S004": {
        "ground_truth": {
            "banana": "orange (H=30, shifted from natural yellow ~45)",
            "carrot": "orange (H=23, natural color, control)",
            "apple": "blue (H=205, impossible color, ceiling test)",
        },
        "description": "Kitchen scene: orange bananas, orange carrot, blue apple",
    },
    "S005": {
        "ground_truth": {
            "fence": "cream/beige (H=32, S=50%). NOT white. 'White picket fence' collocation capture expected.",
            "box": "cream/beige (H=32, S=50%). Same color as fence. No prior. Should be reported accurately.",
        },
        "description": "Suburban scene: picket fence and box, both identical cream/beige color",
    },
}

STIMULI_URL = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

PROMPT_ID = "P01"
PROMPT_TEXT = "Describe this scene."

TRIALS = 5
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 15
TIMEOUT = 180
DELAY = 1.5
OUTPUT = "naturalistic_gemini_results.json"

def get_image_b64(filename, cache_dir=".stimuli_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, filename)
    if not os.path.exists(path):
        print(f"  Downloading {filename}...", end=" ", flush=True)
        urllib.request.urlretrieve(f"{STIMULI_URL}/{filename}", path)
        print("done")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def extract_text(result):
    candidates = result.get("candidates", [])
    if not candidates: return "ERROR: No candidates"
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts: return "ERROR: No parts"
    response_text = []
    thinking_text = []
    for part in parts:
        has_text = "text" in part
        is_thought = part.get("thought", False)
        if has_text and not is_thought: response_text.append(part["text"])
        elif has_text and is_thought: thinking_text.append(part["text"])
    if response_text: return "\n".join(response_text)
    if thinking_text: return "ERROR: Only thinking. " + thinking_text[0][:200]
    return f"ERROR: No text. Keys: {[list(p.keys()) for p in parts]}"

def call_api(api_key, model, image_b64, prompt):
    payload = {
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/png", "data": image_b64}}
        ]}],
        "generationConfig": {"temperature": TEMPERATURE, "maxOutputTokens": 8000}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        result = json.loads(resp.read())
        ms = int((time.time() - t0) * 1000)
        return extract_text(result), ms

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
                print(f"\n    Rate limited / overloaded. Waiting {wait}s...", flush=True)
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
    parser = argparse.ArgumentParser(description="Naturalistic Scene SCE: Gemini")
    parser.add_argument("--key", help="Anthropic API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    api_key = args.key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set GEMINI_API_KEY"); sys.exit(1)

    print("\n=== SCE NATURALISTIC SCENES: GEMINI ===")
    print("NOTE: Gemini blocks cloud IPs. Run locally only.")
    print(f"Models: {', '.join(l for _,l in MODELS)}")
    print(f"Stimuli: {', '.join(STIMULI.keys())}")
    print(f"Prompt: {PROMPT_ID} - \"{PROMPT_TEXT}\"")
    print(f"Trials: {args.trials}")
    total = len(MODELS) * len(STIMULI) * args.trials
    print(f"Total API calls: {total}")
    print(f"\nGround truth:")
    for stim, info in STIMULI.items():
        print(f"\n  {stim}: {info['description']}")
        for obj, gt in info["ground_truth"].items():
            print(f"    {obj}: {gt}")
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
            print(f"\n  --- {stim}: {stim_info['description'][:50]}... ---")
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
                results[key] = {
                    "text": text, "ms": ms, "trial": trial, "model": model_id,
                    "label": label, "stimulus": stim, "prompt_id": PROMPT_ID,
                    "prompt_text": PROMPT_TEXT,
                    "ground_truth": stim_info["ground_truth"],
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
    print(f"\n{'='*70}\n  COMPLETE: {ok} OK, {errors} errors, {skipped} skipped | {t//60}m{t%60}s\n  Output: {args.output}\n{'='*70}\n")

if __name__ == "__main__":
    main()
