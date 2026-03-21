#!/usr/bin/env python3
"""
SCE Replication: Gemini Gradient Experiment
Run this from your local machine (not from Claude's container).
Google blocks API calls from cloud IPs.

Usage:
    export GEMINI_API_KEY="AIzaSy..."
    python3 run_gemini_gradient.py

    # Or pass key directly:
    python3 run_gemini_gradient.py --key "AIzaSy..."

Results saved to: gemini_gradient_results.json
Push to GitHub after running.
"""

import urllib.request, json, time, base64, sys, os, argparse

# --- Config ---
MODELS = [
    ("gemini-2.5-pro", "GEMINI_PRO"),
    ("gemini-2.5-flash", "GEMINI_FLASH"),
    ("gemini-2.0-flash", "GEMINI_2_FLASH"),
]

GRADIENT = ["S001", "G001", "S003", "G003", "G004", "G005", "G006"]
STIMULI_URL = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"
PROMPT = "Describe this scene."
TRIALS = 5
TEMPERATURE = 1.0

def get_image_b64(filename, cache_dir=".stimuli_cache"):
    """Download and cache stimulus images locally."""
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, filename)
    if not os.path.exists(path):
        print(f"  Downloading {filename}...", end=" ", flush=True)
        urllib.request.urlretrieve(f"{STIMULI_URL}/{filename}", path)
        print("done")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def run_gemini(api_key, model, image_b64, prompt):
    """Send a single request to Gemini API."""
    payload = {
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/png", "data": image_b64}}
        ]}],
        "generationConfig": {
            "temperature": TEMPERATURE,
            "maxOutputTokens": 500
        }
    }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    req = urllib.request.Request(url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST")
    
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
        ms = int((time.time() - t0) * 1000)
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return text, ms

def main():
    parser = argparse.ArgumentParser(description="SCE Gemini Gradient Experiment")
    parser.add_argument("--key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--trials", type=int, default=TRIALS, help=f"Trials per condition (default {TRIALS})")
    parser.add_argument("--models", nargs="+", help="Model IDs to test (default: all three)")
    args = parser.parse_args()
    
    api_key = args.key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Set GEMINI_API_KEY or use --key")
        sys.exit(1)
    
    models = args.models or [m[0] for m in MODELS]
    model_labels = {m[0]: m[1] for m in MODELS}
    
    # Pre-download all images
    print("\nDownloading stimulus images...")
    images = {}
    for stim in GRADIENT:
        images[stim] = get_image_b64(f"{stim}.png")
    print(f"Cached {len(images)} images.\n")
    
    # Run experiment
    results = {}
    total = len(models) * len(GRADIENT) * args.trials
    done = 0
    
    for model in models:
        label = model_labels.get(model, model.upper())
        print(f"=== {label} ({model}) ===")
        
        for trial in range(1, args.trials + 1):
            for stim in GRADIENT:
                key = f"{label}|{stim}|P01|T{trial}"
                done += 1
                print(f"  [{done}/{total}] {key}...", end=" ", flush=True)
                
                try:
                    text, ms = run_gemini(api_key, model, images[stim], PROMPT)
                    results[key] = {"text": text, "ms": ms, "trial": trial, "model": model}
                    print(f"{ms}ms")
                except Exception as e:
                    print(f"ERROR: {e}")
                    results[key] = {"text": f"ERROR: {e}", "ms": 0, "trial": trial, "model": model}
                
                time.sleep(1)  # rate limit courtesy
    
    # Save results
    outfile = "gemini_gradient_results.json"
    with open(outfile, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved {len(results)} results to {outfile}")
    print(f"Push to GitHub: results/gemini_gradient_5trials.json")

if __name__ == "__main__":
    main()
