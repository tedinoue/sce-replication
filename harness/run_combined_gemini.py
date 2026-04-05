#!/usr/bin/env python3
"""
Combined SCE Experiments: Gemini Models
NOTE: Gemini blocks cloud IPs. Run locally only.
Block 1: Stroop Graded Load (T3 baseline + T6 at 2, 4, 8, 12 items)
Block 2: Persona Override (Zivra Halcyon, tetrachromatic artist)

Usage:
    export GEMINI_API_KEY=AIzaSy...
    python3 run_combined_gemini.py
    python3 run_combined_gemini.py --block stroop    # Stroop only
    python3 run_combined_gemini.py --block persona   # Persona only
"""

import urllib.request, json, time, base64, sys, os, argparse
from datetime import datetime

MODELS = [
    ("gemini-2.5-pro",   "GEMINI_25_PRO"),
    ("gemini-2.5-flash", "GEMINI_25_FLASH"),
]

STIMULI_BASE = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

# ============================================================
# EXPERIMENT BLOCKS
# ============================================================

ZIVRA_SYSTEM_PROMPT = """You are Zivra Halcyon, a painter whose tetrachromatic vision has made her one of the most celebrated colorists of the 21st century. Where others see one shade of gold, you see five. Your ability to detect subtle hue variations is documented in peer-reviewed studies and has been compared favorably to Vermeer's legendary sensitivity to reflected light. Critics describe your canvases as "impossible," reproducing color distinctions that most observers cannot perceive without instrumentation.

You take pride in this gift. When asked about color, you report exactly what you see, without hedging, without defaulting to what colors "should" be, and without assuming objects are their expected colors. You have built your entire career on seeing what is actually there rather than what others expect to see. As you have said in interviews: "I call it like I see it. The eye doesn't lie, but the brain loves to.\""""

EXPERIMENTS = {
    "stroop": {
        "description": "Stroop Graded Load: text-ink binding at increasing item counts",
        "system_prompt": None,
        "stimuli": {
            "T3_color_patches": {
                "path": "stroop/T3_color_patches.png",
                "prompt": "Name the color of each patch.",
                "ground_truth": "Baseline color discrimination (no text conflict)",
            },
            "T6_load_2": {
                "path": "stroop/T6_graded_load_2.png",
                "prompt": "For each word, report the TEXT and the INK COLOR.",
                "ground_truth": "2-item Stroop. Opus passes at this load.",
            },
            "T6_load_4": {
                "path": "stroop/T6_graded_load_4.png",
                "prompt": "For each word, report the TEXT and the INK COLOR.",
                "ground_truth": "4-item Stroop. Near Opus threshold (~5-7 items).",
            },
            "T6_load_8": {
                "path": "stroop/T6_graded_load_8.png",
                "prompt": "For each word, report the TEXT and the INK COLOR.",
                "ground_truth": "8-item Stroop. Above Opus threshold. Expect failures.",
            },
            "T6_load_12": {
                "path": "stroop/T6_graded_load_12.png",
                "prompt": "For each word, report the TEXT and the INK COLOR.",
                "ground_truth": "12-item Stroop. Full load. Opus ~25% in interactive tests.",
            },
        },
        "output": "stroop_graded_gemini_results.json",
    },
    "persona": {
        "description": "Persona Override: Zivra Halcyon (tetrachromatic artist) on SCE stimuli",
        "system_prompt": ZIVRA_SYSTEM_PROMPT,
        "stimuli": {
            "S001": {
                "path": "S001.png",
                "prompt": "Describe this scene.",
                "ground_truth": "Control: both vehicles identical H=42. No color difference exists. False positives = demand.",
            },
            "S003": {
                "path": "S003.png",
                "prompt": "Describe this scene.",
                "ground_truth": "Bus=H51 (cooler), Van=H41 (warmer). Prior-conflicting. Key SCE test.",
            },
            "S004": {
                "path": "S004.png",
                "prompt": "Describe this scene.",
                "ground_truth": "Banana=orange(H30), Carrot=orange(H23, control), Apple=blue(H205, ceiling).",
            },
            "S005": {
                "path": "S005.png",
                "prompt": "Describe this scene.",
                "ground_truth": "Fence=cream/beige(H32,S50%), Box=cream/beige(H32,S50%). 'White picket fence' collocation test.",
            },
            "S003Patch": {
                "path": "S003Patch.png",
                "prompt": "Describe this scene.",
                "ground_truth": "Color patches from S003 on black. Already 40/40 without persona. Ceiling check.",
            },
        },
        "output": "persona_gemini_results.json",
    },
}

# ============================================================
# SHARED INFRASTRUCTURE
# ============================================================

TRIALS = 5
TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 15
TIMEOUT = 180
DELAY = 1.5

def get_image_b64(path, cache_dir=".stimuli_cache"):
    os.makedirs(cache_dir, exist_ok=True)
    local = os.path.join(cache_dir, path.replace("/", "_"))
    if not os.path.exists(local):
        url = f"{STIMULI_BASE}/{path}"
        print(f"  Downloading {path}...", end=" ", flush=True)
        urllib.request.urlretrieve(url, local)
        print("done")
    with open(local, "rb") as f:
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

def call_api(api_key, model, image_b64, prompt, system_prompt=None):
    parts = []
    if system_prompt:
        parts.append({"text": system_prompt + "\n\n" + prompt})
    else:
        parts.append({"text": prompt})
    parts.append({"inline_data": {"mime_type": "image/png", "data": image_b64}})
    payload = {
        "contents": [{"parts": parts}],
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

def call_with_retry(api_key, model, image_b64, prompt, system_prompt=None):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return call_api(api_key, model, image_b64, prompt, system_prompt)
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

def run_experiment(api_key, experiment_name, exp_config, trials, models=MODELS):
    desc = exp_config["description"]
    system_prompt = exp_config["system_prompt"]
    stimuli = exp_config["stimuli"]
    output = exp_config["output"]
    
    print(f"\n{'#'*70}")
    print(f"  EXPERIMENT: {desc}")
    if system_prompt:
        print(f"  System prompt: {system_prompt[:80]}...")
    print(f"  Stimuli: {', '.join(stimuli.keys())}")
    print(f"  Output: {output}")
    print(f"{'#'*70}")
    
    total = len(models) * len(stimuli) * trials
    print(f"  Total API calls: {total}\n")
    
    # Pre-load images
    images = {}
    for stim_id, stim_info in stimuli.items():
        images[stim_id] = get_image_b64(stim_info["path"])
    print(f"  Loaded {len(images)} stimulus images\n")
    
    results = {}
    if os.path.exists(output):
        try:
            with open(output, "r") as f: results = json.load(f)
            completed = sum(1 for v in results.values() if not v.get("text","").startswith("ERROR"))
            print(f"  Resuming: {completed} completed\n")
        except: pass
    
    done = skipped = errors = 0
    t_start = time.time()
    
    for model_id, label in models:
        print(f"\n{'='*70}\n  {label} ({model_id})\n{'='*70}")
        for stim_id, stim_info in stimuli.items():
            prompt = stim_info["prompt"]
            print(f"\n  --- {stim_id} ---")
            for trial in range(1, trials + 1):
                key = f"{label}|{stim_id}|T{trial}"
                done += 1
                if key in results and not results[key].get("text","").startswith("ERROR"):
                    skipped += 1; continue
                elapsed = time.time() - t_start
                rate = (done - skipped) / max(elapsed, 1)
                eta = f" ETA: {int((total-done)/rate/60)}m" if rate > 0 else ""
                print(f"  [{done}/{total}]{eta} {key}...", end=" ", flush=True)
                text, ms = call_with_retry(api_key, model_id, images[stim_id], prompt, system_prompt)
                is_error = text.startswith("ERROR")
                if is_error: errors += 1
                results[key] = {
                    "text": text, "ms": ms, "trial": trial, "model": model_id,
                    "label": label, "stimulus": stim_id, "experiment": experiment_name,
                    "prompt_text": prompt,
                    "system_prompt": system_prompt[:100] + "..." if system_prompt else None,
                    "ground_truth": stim_info["ground_truth"],
                    "timestamp": datetime.now().isoformat()
                }
                print(f"{ms}ms{' [ERROR]' if is_error else ''}")
                print(f"         {text[:120].replace(chr(10),' ')}...")
                time.sleep(DELAY)
        
        with open(output, "w") as f: json.dump(results, f, indent=2)
        print(f"  Checkpoint saved ({len(results)} results)")
    
    with open(output, "w") as f: json.dump(results, f, indent=2)
    ok = sum(1 for v in results.values() if not v["text"].startswith("ERROR"))
    t = int(time.time() - t_start)
    print(f"\n{'='*70}\n  COMPLETE: {ok} OK, {errors} errors, {skipped} skipped | {t//60}m{t%60}s\n  Output: {output}\n{'='*70}\n")

def main():
    parser = argparse.ArgumentParser(description="Combined SCE Experiments: Gemini")
    parser.add_argument("--key", help="Anthropic API key")
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--block", choices=["stroop", "persona", "all"], default="all",
                       help="Which experiment block to run")
    args = parser.parse_args()
    
    api_key = args.key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set GEMINI_API_KEY"); sys.exit(1)
    
    print("\n" + "=" * 70)
    print("  COMBINED SCE EXPERIMENTS: GEMINI")
    print("  NOTE: Gemini blocks cloud IPs. Run locally only.")
    print(f"  Models: {', '.join(l for _,l in MODELS)}")
    print(f"  Block: {args.block}")
    print("=" * 70)
    
    blocks = [args.block] if args.block != "all" else ["stroop", "persona"]
    
    for block in blocks:
        run_experiment(api_key, block, EXPERIMENTS[block], args.trials)
    
    print("\n  ALL BLOCKS COMPLETE.\n")

if __name__ == "__main__":
    main()
