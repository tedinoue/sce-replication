#!/usr/bin/env python3
"""
SCE Replication: Gemini Gradient Experiment
Run this from your local machine (not from Claude's container).
Google blocks API calls from cloud IPs.

Usage:
    python3 run_gemini_gradient.py --key "AIzaSy..."

Results saved to: gemini_gradient_results.json
Push to GitHub after running.
"""

import urllib.request, json, time, base64, sys, os, argparse

# --- Config ---
MODELS = [
    ("gemini-2.5-pro", "GEMINI_25_PRO"),
    ("gemini-2.5-flash", "GEMINI_25_FLASH"),
    ("gemini-2.0-flash", "GEMINI_20_FLASH"),
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

def extract_text_from_gemini_response(result):
    """
    Extract text from Gemini response, handling thinking models.
    Gemini 2.5 Pro/Flash have thinking enabled, which means the response
    contains both 'thought' parts and 'text' parts. We only want the text.
    """
    candidates = result.get("candidates", [])
    if not candidates:
        return "ERROR: No candidates in response"
    
    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    
    # Collect only text parts (skip thinking parts)
    text_parts = []
    for part in parts:
        if "text" in part and not part.get("thought", False):
            text_parts.append(part["text"])
    
    if text_parts:
        return "\n".join(text_parts)
    
    # Fallback: if no non-thought text parts, try any text part
    for part in parts:
        if "text" in part:
            text_parts.append(part["text"])
    
    if text_parts:
        return "\n".join(text_parts)
    
    # Last resort: dump the structure for debugging
    return f"ERROR: Could not extract text. Parts structure: {json.dumps(parts)[:500]}"

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
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read())
            ms = int((time.time() - t0) * 1000)
            text = extract_text_from_gemini_response(result)
            return text, ms
    except urllib.error.HTTPError as e:
        body = ""
        if hasattr(e, "read"):
            body = e.read().decode()[:300]
        raise Exception(f"HTTP {e.code}: {body}")

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
    
    models_to_run = args.models or [m[0] for m in MODELS]
    model_labels = {m[0]: m[1] for m in MODELS}
    
    # Pre-download all images
    print("\nDownloading stimulus images...")
    images = {}
    for stim in GRADIENT:
        images[stim] = get_image_b64(f"{stim}.png")
    print(f"Cached {len(images)} images.\n")
    
    # Run experiment
    results = {}
    total = len(models_to_run) * len(GRADIENT) * args.trials
    done = 0
    
    for model in models_to_run:
        label = model_labels.get(model, model.upper().replace("-", "_").replace(".", "_"))
        print(f"\n=== {label} ({model}) ===")
        
        for trial in range(1, args.trials + 1):
            for stim in GRADIENT:
                key = f"{label}|{stim}|P01|T{trial}"
                done += 1
                print(f"  [{done}/{total}] {key}...", end=" ", flush=True)
                
                try:
                    text, ms = run_gemini(api_key, model, images[stim], PROMPT)
                    results[key] = {"text": text, "ms": ms, "trial": trial, "model": model}
                    print(f"{ms}ms ({len(text)} chars)")
                except Exception as e:
                    print(f"ERROR: {e}")
                    results[key] = {"text": f"ERROR: {e}", "ms": 0, "trial": trial, "model": model}
                
                time.sleep(1)  # rate limit courtesy
        
        # Save after each model in case of interruption
        with open("gemini_gradient_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"  Checkpoint saved ({len(results)} results so far)")
    
    # Final save
    with open("gemini_gradient_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n=== COMPLETE ===")
    print(f"Saved {len(results)} results to gemini_gradient_results.json")
    print(f"\nNext: copy to results/ and push to GitHub:")
    print(f"  cp gemini_gradient_results.json results/")
    print(f"  git add results/gemini_gradient_results.json")
    print(f"  git commit -m \"Gemini gradient 5 trials\"")
    print(f"  git push")

if __name__ == "__main__":
    main()
