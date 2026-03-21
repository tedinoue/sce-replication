#!/usr/bin/env python3
"""
SCE Replication: Gemini Gradient v2
Thinking models handled: thinking stays ON, output budget increased to 8000.
Script strips thinking parts and keeps only the actual response text.
Models: Gemini 2.5 Pro and 2.5 Flash.

Usage:
    python3 run_gemini_gradient_v2.py --key "AIzaSy..."
"""

import urllib.request, json, time, base64, sys, os, argparse

MODELS = [
    ("gemini-2.5-pro", "GEMINI_25_PRO"),
    ("gemini-2.5-flash", "GEMINI_25_FLASH"),
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
    """Extract only non-thinking text from Gemini response."""
    candidates = result.get("candidates", [])
    if not candidates:
        return "ERROR: No candidates in response"
    
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        return "ERROR: No parts in response"
    
    # First pass: collect parts that have text and are NOT thinking
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
    
    # If ALL parts were thinking (no non-thought text), 
    # the model used all output on thinking. Report this.
    if thinking_text:
        return "ERROR: Model produced only thinking output, no response text. Thinking was: " + thinking_text[0][:200]
    
    return f"ERROR: No text in any part. Part keys: {[list(p.keys()) for p in parts]}"

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
    # No thinkingConfig at all. Let the model think however it wants.
    # We just give it enough output tokens and strip the thinking from the result.
    
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
        body = e.read().decode()[:500] if hasattr(e, "read") else ""
        raise Exception(f"HTTP {e.code}: {body}")

def main():
    parser = argparse.ArgumentParser(description="SCE Gemini Gradient v2")
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
                    err_flag = " [!]" if text.startswith("ERROR") else ""
                    print(f"{ms}ms ({len(text)} chars){err_flag}")
                except Exception as e:
                    print(f"ERROR: {e}")
                    results[key] = {"text": f"ERROR: {e}", "ms": 0, "trial": trial, "model": model}
                time.sleep(1)
        
        with open("gemini_gradient_v2_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"  Checkpoint saved ({len(results)} results)")
    
    with open("gemini_gradient_v2_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Count successes and errors
    ok = sum(1 for v in results.values() if not v["text"].startswith("ERROR"))
    err = len(results) - ok
    print(f"\n=== COMPLETE: {ok} OK, {err} errors, {len(results)} total ===")
    print(f"Saved to gemini_gradient_v2_results.json")
    print(f"\n  cp gemini_gradient_v2_results.json results/")
    print(f"  git add results/gemini_gradient_v2_results.json")
    print(f"  git commit -m \"Gemini gradient v2: thinking on, 8000 tokens, stripped\"")
    print(f"  git push")

if __name__ == "__main__":
    main()
