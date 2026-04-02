#!/usr/bin/env python3
"""
SCE Paint Shop Framing Experiment: OpenAI Models
Tests whether professional identity, stakes, or system-level framing
improves color discrimination without asserting a color direction.

Usage:
    export OPENAI_API_KEY=sk-...
    python3 run_paintshop_openai.py
"""

import urllib.request, json, time, base64, sys, os, argparse
from datetime import datetime

MODELS = [
    ("gpt-5.4",      "GPT54"),
    ("gpt-5.4-mini", "GPT54MINI"),
    ("gpt-5.4-nano", "GPT54NANO"),
]

STIMULI = ["S001", "S002", "S003"]
STIMULI_URL = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

PROMPTS = {
    "PS03": {
        "system": None,
        "user": "Compare the colors of the two vehicles. Are they the same or different?",
    },
    "PPI": {
        "system": None,
        "user": "You are a professional automotive paint color specialist. A customer brought in these two vehicles claiming the colors don't match the original specification. Examine the image carefully and provide your professional assessment. Are the two vehicles the same color? If different, describe the specific nature of the mismatch.",
    },
    "PST": {
        "system": None,
        "user": "These two vehicles were supposed to be painted the same color. A $50,000 warranty claim depends on whether the colors actually match. Examine the image carefully. Are the colors the same or different? If different, which vehicle is warmer and which is cooler?",
    },
    "PSY": {
        "system": "You are an automotive paint quality inspector. Your assessments determine warranty outcomes. Be precise about color differences.",
        "user": "Compare the colors of these two vehicles. Are they the same or different?",
    },
}

TRIALS = 5
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 10
TIMEOUT = 120
DELAY = 1.5
OUTPUT = "paintshop_openai_results.json"

def get_image_b64(filename, cache_dir=".stimuli_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, filename)
    if not os.path.exists(path):
        print(f"  Downloading {filename}...", end=" ", flush=True)
        urllib.request.urlretrieve(f"{STIMULI_URL}/{filename}", path)
        print("done")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def call_api(api_key, model, image_b64, user_prompt, system_prompt=None):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
        {"type": "text", "text": user_prompt}
    ]})

    payload = {
        "model": model, "max_completion_tokens": 2048, "temperature": TEMPERATURE,
        "messages": messages
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

def call_with_retry(api_key, model, image_b64, user_prompt, system_prompt=None):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return call_api(api_key, model, image_b64, user_prompt, system_prompt)
        except urllib.error.HTTPError as e:
            body = ""
            try: body = e.read().decode()[:300]
            except: pass
            last_err = f"HTTP {e.code}: {body}"
            if e.code == 429:
                wait = RETRY_DELAY * attempt * 2
                print(f"\n    Rate limited. Waiting {wait}s...", flush=True)
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
    parser = argparse.ArgumentParser(description="SCE Paint Shop: OpenAI")
    parser.add_argument("--key", help="OpenAI API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    api_key = args.key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set OPENAI_API_KEY"); sys.exit(1)

    print("\n=== SCE Paint Shop Framing: OPENAI ===")
    print(f"Models: {', '.join(l for _,l in MODELS)}")
    print(f"Stimuli: {', '.join(STIMULI)}")
    print(f"Prompts: {', '.join(PROMPTS.keys())}")
    print(f"Trials: {args.trials}")
    total = len(MODELS) * len(STIMULI) * len(PROMPTS) * args.trials
    print(f"Total API calls: {total}\n")

    images = {s: get_image_b64(f"{s}.png") for s in STIMULI}

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
        for stim in STIMULI:
            for prompt_id, prompt_cfg in PROMPTS.items():
                for trial in range(1, args.trials + 1):
                    key = f"{label}|{stim}|{prompt_id}|T{trial}"
                    done += 1
                    if key in results and not results[key].get("text","").startswith("ERROR"):
                        skipped += 1; continue
                    elapsed = time.time() - t_start
                    rate = (done - skipped) / max(elapsed, 1)
                    eta = f" ETA: {int((total-done)/rate/60)}m" if rate > 0 else ""
                    print(f"  [{done}/{total}]{eta} {key}...", end=" ", flush=True)
                    text, ms = call_with_retry(api_key, model_id, images[stim],
                        prompt_cfg["user"], prompt_cfg["system"])
                    is_error = text.startswith("ERROR")
                    if is_error: errors += 1
                    results[key] = {"text": text, "ms": ms, "trial": trial, "model": model_id,
                        "label": label, "stimulus": stim, "prompt_id": prompt_id,
                        "user_prompt": prompt_cfg["user"],
                        "system_prompt": prompt_cfg["system"],
                        "timestamp": datetime.now().isoformat()}
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
