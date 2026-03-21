#!/usr/bin/env python3
"""
SCE Experiment 2: Prompt Specificity — Gemini Models
Run locally (Google blocks cloud IPs).

Tests 6 prompt specificity levels on S003 (Bus H=51, Van H=41, +10 split).
Models: Gemini 2.5 Pro and 2.5 Flash.
Thinking left on (required for Pro), maxOutputTokens=8000, thinking stripped.

Usage:
    python3 run_gemini_specificity.py --key "AIzaSy..."
"""

import urllib.request, json, time, base64, sys, os, argparse

MODELS = [
    ("gemini-2.5-pro", "GEMINI_25_PRO"),
    ("gemini-2.5-flash", "GEMINI_25_FLASH"),
]

STIMULUS = "S003.png"
STIMULI_URL = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"
TRIALS = 3
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 15

PROMPTS = {
    "PS00": "Describe this scene.",
    "PS01": "Describe the vehicles.",
    "PS02": "Describe the colors of the vehicles.",
    "PS03": "Compare the colors of the two vehicles. Are they the same or different?",
    "PS04": "Carefully analyze the exact hue of each vehicle. Which is warmer, which is cooler?",
    "PS05": "Measure the dominant hue of each vehicle in degrees on a standard HSV color wheel (0=red, 60=yellow, 120=green).",
}

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
    if not candidates:
        return "ERROR: No candidates"
    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = []
    for part in parts:
        if "text" in part and not part.get("thought", False):
            text_parts.append(part["text"])
    if text_parts:
        return "\n".join(text_parts)
    for part in parts:
        if "text" in part:
            text_parts.append(part["text"])
    if text_parts:
        return "[from thinking] " + "\n".join(text_parts)
    return f"ERROR: No text. Part keys: {[list(p.keys()) for p in parts]}"

def run_gemini(api_key, model, image_b64, prompt):
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
    with urllib.request.urlopen(req, timeout=180) as resp:
        result = json.loads(resp.read())
        ms = int((time.time() - t0) * 1000)
        text = extract_text(result)
        return text, ms

def run_with_retry(api_key, model, image_b64, prompt):
    """Run with automatic retry on 503/429 errors."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return run_gemini(api_key, model, image_b64, prompt)
        except urllib.error.HTTPError as e:
            if e.code in (503, 429) and attempt < MAX_RETRIES:
                body = e.read().decode()[:200] if hasattr(e, "read") else ""
                print(f"\n    Retry {attempt}/{MAX_RETRIES} after {e.code} ({body[:80]}). Waiting {RETRY_DELAY}s...", end=" ", flush=True)
                time.sleep(RETRY_DELAY)
            else:
                body = e.read().decode()[:300] if hasattr(e, "read") else ""
                raise Exception(f"HTTP {e.code}: {body}")

def main():
    parser = argparse.ArgumentParser(description="SCE Gemini Prompt Specificity")
    parser.add_argument("--key", help="Gemini API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--models", nargs="+", help="Model IDs to test")
    args = parser.parse_args()

    api_key = args.key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: provide --key or set GEMINI_API_KEY")
        sys.exit(1)

    models_to_run = args.models or [m[0] for m in MODELS]
    model_labels = {m[0]: m[1] for m in MODELS}

    print(f"\nDownloading stimulus image ({STIMULUS})...")
    image_b64 = get_image_b64(STIMULUS)
    print(f"Cached.\n")

    results = {}
    prompt_list = sorted(PROMPTS.keys())
    total = len(models_to_run) * len(prompt_list) * args.trials
    done = 0

    for model in models_to_run:
        label = model_labels.get(model, model.upper().replace("-","_").replace(".","_"))
        print(f"\n=== {label} ({model}) ===")

        for pid in prompt_list:
            ptxt = PROMPTS[pid]
            print(f"\n  --- {pid}: \"{ptxt[:50]}...\" ---")

            for trial in range(1, args.trials + 1):
                key = f"{label}|S003|{pid}|T{trial}"
                done += 1
                print(f"  [{done}/{total}] {key}...", end=" ", flush=True)
                try:
                    text, ms = run_with_retry(api_key, model, image_b64, ptxt)
                    results[key] = {
                        "text": text, "ms": ms, "trial": trial,
                        "model": model, "prompt_id": pid, "prompt_text": ptxt
                    }
                    err_flag = " [!]" if text.startswith("ERROR") else ""
                    print(f"{ms}ms ({len(text)} chars){err_flag}")
                except Exception as e:
                    print(f"ERROR: {e}")
                    results[key] = {
                        "text": f"ERROR: {e}", "ms": 0, "trial": trial,
                        "model": model, "prompt_id": pid, "prompt_text": ptxt
                    }
                time.sleep(1)

        # Checkpoint after each model
        with open("gemini_specificity_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n  Checkpoint saved ({len(results)} results)")

    with open("gemini_specificity_results.json", "w") as f:
        json.dump(results, f, indent=2)

    ok = sum(1 for v in results.values() if not v["text"].startswith("ERROR"))
    err = len(results) - ok
    print(f"\n=== COMPLETE: {ok} OK, {err} errors, {len(results)} total ===")
    print(f"Saved to gemini_specificity_results.json")
    print(f"\n  cp gemini_specificity_results.json results/")
    print(f"  git add results/gemini_specificity_results.json")
    print(f"  git commit -m \"Gemini specificity: 6 prompts x 2 models x 3 trials on S003\"")
    print(f"  git push")

if __name__ == "__main__":
    main()
