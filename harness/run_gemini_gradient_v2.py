#!/usr/bin/env python3
"""
SCE Replication: Gemini Gradient Experiment v2
Fixed: maxOutputTokens=2000, thinking budget separate.
Also disabled thinking for 2.5 models to get clean text output.

Usage:
    python3 run_gemini_gradient_v2.py --key "AIzaSy..."
"""

import urllib.request, json, time, base64, sys, os, argparse

MODELS = [
    ("gemini-2.5-flash", "GEMINI_25_FLASH"),
    ("gemini-2.5-pro", "GEMINI_25_PRO"),
]

GRADIENT = ["S001", "G001", "S003", "G003", "G004", "G005", "G006"]
STIMULI_URL = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"
PROMPT = "Describe this scene."
TRIALS = 5
TEMPERATURE = 1.0

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
    # Fallback: any text part
    for part in parts:
        if "text" in part:
            text_parts.append(part["text"])
    if text_parts:
        return "\n".join(text_parts)
    return f"ERROR: No text. Parts: {json.dumps(parts)[:300]}"

def run_gemini(api_key, model, image_b64, prompt):
    payload = {
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": "image/png", "data": image_b64}}
        ]}],
        "generationConfig": {
            "temperature": TEMPERATURE,
            "maxOutputTokens": 2000,
            "thinkingConfig": {"thinkingBudget": 0}
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
            text = extract_text(result)
            return text, ms
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:300] if hasattr(e, "read") else ""
        raise Exception(f"HTTP {e.code}: {body}")

def main():
    parser = argparse.ArgumentParser(description="SCE Gemini Gradient v2")
    parser.add_argument("--key", help="Gemini API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--models", nargs="+", help="Model IDs")
    args = parser.parse_args()
    
    api_key = args.key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: provide --key or set GEMINI_API_KEY")
        sys.exit(1)
    
    models_to_run = args.models or [m[0] for m in MODELS]
    model_labels = {m[0]: m[1] for m in MODELS}
    
    print("\nDownloading stimulus images...")
    images = {}
    for stim in GRADIENT:
        images[stim] = get_image_b64(f"{stim}.png")
    print(f"Cached {len(images)} images.\n")
    
    results = {}
    total = len(models_to_run) * len(GRADIENT) * args.trials
    done = 0
    
    for model in models_to_run:
        label = model_labels.get(model, model.upper().replace("-","_").replace(".","_"))
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
                time.sleep(1)
        
        with open("gemini_gradient_v2_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"  Checkpoint saved ({len(results)} results)")
    
    with open("gemini_gradient_v2_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n=== COMPLETE: {len(results)} results ===")
    print(f"Saved to gemini_gradient_v2_results.json")
    print(f"\n  cp gemini_gradient_v2_results.json results/")
    print(f"  git add results/gemini_gradient_v2_results.json")
    print(f"  git commit -m \"Gemini gradient v2: thinking disabled, 2000 tokens\"")
    print(f"  git push")

if __name__ == "__main__":
    main()
