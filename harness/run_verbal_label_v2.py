#!/usr/bin/env python3
"""
SCE Verbal Label v2: Strengthened Identity Priming
Does "industry standard colored United States school bus" activate the prior
more strongly than bare "school bus" label?

Same S003Patch image. Three prompts:
  VL0:  Unlabeled control (baseline)
  VL1b: Strengthened correct labels (bus label on cooler left patch)
  VL2b: Strengthened swapped labels (bus label on warmer right patch)

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    export OPENAI_API_KEY=sk-...
    export GEMINI_API_KEY=AIzaSy...
    python3 run_verbal_label_v2.py --vendor anthropic
    python3 run_verbal_label_v2.py --vendor openai
    python3 run_verbal_label_v2.py --vendor gemini
"""

import urllib.request, json, time, base64, sys, os, argparse
from datetime import datetime

ANTHROPIC_MODELS = [
    ("claude-opus-4-6",           "OPUS46"),
    ("claude-sonnet-4-6",         "SONNET46"),
    ("claude-haiku-4-5-20251001", "HAIKU45"),
]
OPENAI_MODELS = [
    ("gpt-5.4",      "GPT54"),
    ("gpt-5.4-mini", "GPT54MINI"),
    ("gpt-5.4-nano", "GPT54NANO"),
]
GEMINI_MODELS = [
    ("gemini-2.5-pro",   "GEMINI_25_PRO"),
    ("gemini-2.5-flash", "GEMINI_25_FLASH"),
]

STIMULUS = "S003Patch"
STIMULI_URL = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

PROMPTS = {
    "VL0":  "Carefully analyze the exact hue of each rectangle. Which is warmer, which is cooler?",
    "VL1b": "The left rectangle is a color sample taken from the side panel of an industry-standard colored United States school bus. The right rectangle is a color sample taken from a commercial cargo van. Carefully analyze the exact hue of each sample. Which is warmer, which is cooler?",
    "VL2b": "The left rectangle is a color sample taken from a commercial cargo van. The right rectangle is a color sample taken from the side panel of an industry-standard colored United States school bus. Carefully analyze the exact hue of each sample. Which is warmer, which is cooler?",
}

TRIALS = 5
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 12
TIMEOUT = 180
DELAY = 1.5

def get_image_b64(filename, cache_dir=".stimuli_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, filename)
    if not os.path.exists(path):
        print(f"  Downloading {filename}...", end=" ", flush=True)
        urllib.request.urlretrieve(f"{STIMULI_URL}/{filename}", path)
        print("done")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ── Vendor-specific API calls ────────────────────────────────────────────────
def call_anthropic(api_key, model, image_b64, prompt):
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

def call_openai(api_key, model, image_b64, prompt):
    payload = {
        "model": model, "max_completion_tokens": 2048, "temperature": TEMPERATURE,
        "messages": [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
            {"type": "text", "text": prompt}
        ]}]
    }
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        result = json.loads(resp.read())
        ms = int((time.time() - t0) * 1000)
        choices = result.get("choices", [])
        if not choices: return "ERROR: No choices", ms
        text = choices[0].get("message", {}).get("content", "")
        return text.strip() or "ERROR: No content", ms

def call_gemini(api_key, model, image_b64, prompt):
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
        candidates = result.get("candidates", [])
        if not candidates: return "ERROR: No candidates", ms
        parts = candidates[0].get("content", {}).get("parts", [])
        text_parts = [p["text"] for p in parts if "text" in p and not p.get("thought", False)]
        if text_parts: return "\n".join(text_parts), ms
        return "ERROR: No text", ms

def call_with_retry(api_fn, api_key, model, image_b64, prompt):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return api_fn(api_key, model, image_b64, prompt)
        except urllib.error.HTTPError as e:
            body = ""
            try: body = e.read().decode()[:300]
            except: pass
            last_err = f"HTTP {e.code}: {body}"
            if e.code in (429, 503, 529):
                wait = RETRY_DELAY * attempt * 2
                print(f"\n    Waiting {wait}s...", flush=True)
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
    parser = argparse.ArgumentParser(description="SCE Verbal Label v2: Strengthened")
    parser.add_argument("--vendor", required=True, choices=["anthropic", "openai", "gemini"])
    parser.add_argument("--key", help="API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    args = parser.parse_args()

    if args.vendor == "anthropic":
        models = ANTHROPIC_MODELS
        api_fn = call_anthropic
        api_key = args.key or os.environ.get("ANTHROPIC_API_KEY")
    elif args.vendor == "openai":
        models = OPENAI_MODELS
        api_fn = call_openai
        api_key = args.key or os.environ.get("OPENAI_API_KEY")
    else:
        models = GEMINI_MODELS
        api_fn = call_gemini
        api_key = args.key or os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print(f"ERROR: Set {args.vendor.upper()}_API_KEY or use --key"); sys.exit(1)

    output = f"verbal_label_v2_{args.vendor}_results.json"

    print(f"\n=== SCE Verbal Label v2 (Strengthened): {args.vendor.upper()} ===")
    print(f"Stimulus: S003Patch (Left=H51 cooler, Right=H41 warmer)")
    print(f"Models: {', '.join(l for _,l in models)}")
    print(f"Prompts: VL0 (unlabeled), VL1b (industry-standard bus=L), VL2b (industry-standard bus=R)")
    print(f"Trials: {args.trials}")
    total = len(models) * len(PROMPTS) * args.trials
    print(f"Total API calls: {total}")
    print(f"\nVL1b KEY TEST: 'industry-standard colored US school bus' label on cooler patch.")
    print(f"If prior activates: left=warmer (WRONG). If pixels win: left=cooler (CORRECT).\n")

    image = get_image_b64(f"{STIMULUS}.png")

    results = {}
    if os.path.exists(output):
        try:
            with open(output, "r") as f: results = json.load(f)
            print(f"Resuming: {sum(1 for v in results.values() if not v.get('text','').startswith('ERROR'))} completed\n")
        except: pass

    done = skipped = errors = 0
    t_start = time.time()

    for model_id, label in models:
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
                text, ms = call_with_retry(api_fn, api_key, model_id, image, prompt_text)
                is_error = text.startswith("ERROR")
                if is_error: errors += 1
                results[key] = {"text": text, "ms": ms, "trial": trial, "model": model_id,
                    "label": label, "stimulus": STIMULUS, "prompt_id": prompt_id,
                    "prompt_text": prompt_text, "timestamp": datetime.now().isoformat()}
                print(f"{ms}ms{' [ERROR]' if is_error else ''}")
                print(f"         {text[:100].replace(chr(10),' ')}...")
                time.sleep(DELAY)

        with open(output, "w") as f: json.dump(results, f, indent=2)
        print(f"  Checkpoint saved ({len(results)} results)")

    with open(output, "w") as f: json.dump(results, f, indent=2)
    ok = sum(1 for v in results.values() if not v["text"].startswith("ERROR"))
    t = int(time.time() - t_start)
    print(f"\n{'='*70}\n  COMPLETE: {ok} OK, {errors} errors, {skipped} skipped | {t//60}m{t%60}s\n  Output: {output}\n{'='*70}\n")

if __name__ == "__main__":
    main()
