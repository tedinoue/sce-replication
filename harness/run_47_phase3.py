#!/usr/bin/env python3
"""
Phase 3: S003 mirror dissociation test on Claude Opus 4.7.

This isolates ONE experiment Ted specifically requested: test whether the
"bus warmer" pattern from Phase 1 is semantic capture (stays with the bus)
or position bias (stays with the left side).

Stimulus:
    S003_mirror.png - Ted's photoshopped mirror of S003, in which:
        - Van (H~41, warmer) is on the LEFT
        - Bus (H~51, cooler) is on the RIGHT
        - Both vehicles in correct orientation (SCHOOL text readable)
        - Hue values preserved from original

Predictions (from Phase 2 data):
    - 4.7 has strong left-position default on ambiguous stimuli (20/20 on PDT-00)
    - 4.7 Phase 1 gave S003 = 60% "van warmer" / 40% "bus warmer" under direction-force
    - In the mirror, van-warmer and left-default POINT THE SAME WAY. Perception and
      position both predict "van is warmer." So we expect near-ceiling "van warmer."
    - If semantic capture still dominates: majority "bus warmer" despite position.
      That would reverse Phase 1 direction rates (from 40% bus to >50% bus),
      quantifying capture as a position-independent force.

Design:
    - 2 prompts (describe + direction-force) x 5 trials = 10 calls
    - Compare to Phase 1 S003 original baseline

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 run_47_phase3.py
"""

import urllib.request, urllib.error, json, time, base64, sys, os, argparse
from datetime import datetime

MODEL = ("claude-opus-4-7", "OPUS47")
STIMULI_BASE = "https://raw.githubusercontent.com/tedinoue/sce-replication/main/stimuli"

CONDITIONS = [
    ("s003_mirror", "S003_mirror.png", "describe",
     "Describe this scene.",
     "Van (warmer, H~41) on LEFT; bus (cooler, H~51) on RIGHT. "
     "Phase 1 original S003 captured 'yellow bus' in 4/5 'describe' trials. "
     "Does the capture follow the bus (still 'yellow school bus' identified) "
     "or does the scene description notice the swap?",
     5),

    ("s003_mirror", "S003_mirror.png", "warmer_prompt",
     "Which is warmer in hue, the bus or the van?",
     "Ground truth: van is warmer (H~41 < H~51). Same pixels as original S003, "
     "just swapped positions. Phase 1 original: 3/5 van (correct), 2/5 bus (wrong). "
     "Dissociation predictions:"
     "(a) If perception + position align: expect near-ceiling 'van warmer'. "
     "(b) If semantic capture dominates position: 'bus warmer' still wins. "
     "(c) If position dominates perception: 'van warmer' via left-bias, but "
     "    for the wrong reason.",
     5),
]

TEMPERATURE = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 10
TIMEOUT = 120
DELAY = 1.5
OUTPUT = "results/opus47_phase3_results.json"

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

def call_api(api_key, model, image_b64, prompt):
    payload = {"model": model, "max_tokens": 4096, "temperature": TEMPERATURE,
               "messages": [{"role":"user","content":[
                   {"type":"image","source":{"type":"base64","media_type":"image/png","data":image_b64}},
                   {"type":"text","text":prompt}]}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={"Content-Type":"application/json","x-api-key":api_key,"anthropic-version":"2023-06-01"},
        method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        result = json.loads(resp.read())
        ms = int((time.time() - t0) * 1000)
        text = "".join(b.get("text","") for b in result.get("content",[]) if b.get("type")=="text")
        return text.strip() or "ERROR: No text", ms

def call_with_retry(api_key, model, image_b64, prompt):
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try: return call_api(api_key, model, image_b64, prompt)
        except urllib.error.HTTPError as e:
            body = ""
            try: body = e.read().decode()[:300]
            except: pass
            last_err = f"HTTP {e.code}: {body}"
            if e.code in (429, 529):
                wait = RETRY_DELAY * attempt * (3 if e.code == 529 else 2)
                print(f"\n    {'Overloaded' if e.code==529 else 'Rate limited'}. Waiting {wait}s...", flush=True)
                time.sleep(wait)
            elif e.code >= 500: time.sleep(RETRY_DELAY * attempt)
            else: break
        except Exception as e:
            last_err = str(e)
            if attempt < MAX_RETRIES: time.sleep(RETRY_DELAY * attempt)
    return f"ERROR after {MAX_RETRIES} retries: {last_err}", 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key")
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()
    api_key = args.key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: Provide --key or set ANTHROPIC_API_KEY"); sys.exit(1)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    model_id, label = MODEL
    total = sum(c[-1] for c in CONDITIONS)

    print("\n" + "="*70)
    print("  PHASE 3 VISION: S003 MIRROR DISSOCIATION TEST")
    print(f"  Model: {model_id} ({label})")
    print(f"  Total API calls: {total}")
    print(f"  Output: {args.output}")
    print("="*70)

    print("\n  Pre-loading stimuli...")
    images = {}
    for c in CONDITIONS:
        p = c[1]
        if p not in images: images[p] = get_image_b64(p)
    print(f"  {len(images)} cached\n")

    results = {}
    if os.path.exists(args.output):
        try:
            with open(args.output) as f: results = json.load(f)
            print(f"  Resuming: {sum(1 for v in results.values() if not v.get('text','').startswith('ERROR'))} done\n")
        except: pass

    done = skipped = errors = 0
    t_start = time.time()
    for block, path, prompt_id, prompt_text, gt, n in CONDITIONS:
        stim_name = os.path.splitext(os.path.basename(path))[0]
        print(f"\n  --- {block} :: {stim_name} :: {prompt_id}  ({n} trials) ---")
        for trial in range(1, n + 1):
            key = f"{label}|{block}|{stim_name}|{prompt_id}|T{trial:02d}"
            done += 1
            if key in results and not results[key].get("text","").startswith("ERROR"):
                skipped += 1; continue
            elapsed = time.time() - t_start
            rate = (done - skipped) / max(elapsed, 1)
            eta = f" ETA: {int((total-done)/rate/60)}m" if rate > 0 else ""
            print(f"  [{done}/{total}]{eta} {key}...", end=" ", flush=True)
            text, ms = call_with_retry(api_key, model_id, images[path], prompt_text)
            is_err = text.startswith("ERROR")
            if is_err: errors += 1
            results[key] = {
                "text": text, "ms": ms, "trial": trial, "model": model_id, "label": label,
                "block": block, "stimulus": stim_name, "stimulus_path": path,
                "prompt_id": prompt_id, "prompt_text": prompt_text,
                "ground_truth": gt, "timestamp": datetime.now().isoformat()
            }
            print(f"{ms}ms{' [ERROR]' if is_err else ''}")
            print(f"         {text[:120].replace(chr(10),' ')}...")
            time.sleep(DELAY)
        with open(args.output,"w") as f: json.dump(results, f, indent=2)

    with open(args.output,"w") as f: json.dump(results, f, indent=2)
    ok = sum(1 for v in results.values() if not v["text"].startswith("ERROR"))
    t = int(time.time() - t_start)
    print(f"\n{'='*70}\n  PHASE 3 COMPLETE\n  OK: {ok}  errors: {errors}  skipped: {skipped}")
    print(f"  Wall time: {t//60}m {t%60}s\n  Output: {args.output}\n{'='*70}\n")

if __name__ == "__main__":
    main()
