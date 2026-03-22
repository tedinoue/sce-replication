**Running Multi-Trial Experiments**

**with AI Vision Models via API**

A Practical Tutorial for Researchers

**Ted Inoue / Fuego** \| March 2026

This document explains how to set up and run programmatic, multi-trial
visual perception experiments across multiple AI model families using
their APIs. The method was developed for the Semantic Coherence
Enforcement (SCE) study and is designed to be replicable by any
researcher with basic technical comfort.

1\. Why Use the API Instead of Chat?

When you test an AI model through its chat interface (ChatGPT,
Claude.ai, Gemini), you are running single trials with no control over
temperature, no way to automate repetition, and no raw data
preservation. The chat interface adds system prompts, personality
shaping, and conversation memory that contaminate your experimental
conditions.

The API gives you a clean, controlled channel:

**Fresh instance every call.** Each API request creates a new model
instance with zero memory of previous calls. No priming, no carryover,
no conversation history. This is your between-subjects isolation.

**Identical stimuli.** The same image, encoded identically, is presented
to every trial. No upload artifacts, no compression variation, no
interface-level preprocessing.

**Exact prompt control.** The prompt text is a string you define. No
system prompt injection, no personality layer, no safety preamble
(beyond the model\'s built-in training).

**Automated repetition.** Run N=100 trials per condition in minutes.
Collect raw responses, timing data, and token counts automatically.

**Cross-vendor comparison.** Use the same stimulus, same prompt, same
scoring logic across Claude, GPT, Gemini, and Grok. The only variable is
the model.

2\. What You Need

2.1 API Accounts and Keys

Each AI vendor has a separate API platform (distinct from their consumer
chat product). You need an account and an API key for each vendor you
want to test.

  ------------- ----------------------- -------------------- --------------- ----------------
  **Vendor**    **API Platform**        **Model Names**      **Cost**        **Difficulty**

  Anthropic     console.anthropic.com   claude-opus-4-6,     \~\$0.01-0.05   Easy
                                        claude-sonnet-4-6,   per image call  
                                        claude-haiku-4-5                     

  OpenAI        platform.openai.com     gpt-5.4,             \~\$0.01-0.10   Easy
                                        gpt-5.4-mini,        per image call  
                                        gpt-5.4-nano                         

  Google        ai.google.dev           gemini-2.5-pro,      Free tier       Moderate\*
                                        gemini-2.5-flash     available       

  xAI           console.x.ai            grok-3               \~\$0.01-0.05   Easy
                                                             per image call  
  ------------- ----------------------- -------------------- --------------- ----------------

> **Note:** Google blocks API calls from cloud-hosted environments
> (including Claude\'s container). Gemini experiments must be run from a
> local machine using a Python script executed from a desktop terminal.
> This requires basic comfort with command-line tools. If you have never
> used a terminal before, consider starting with Claude and OpenAI,
> which work from any environment. See Section 5 for Gemini-specific
> setup.

For each vendor, the setup process is the same:

1.  **Create an account** on the API platform (not the chat product).

2.  **Generate an API key** in the dashboard. Copy it immediately; most
    platforms only show it once.

3.  **Add billing** or credits. Most platforms require a payment method.
    \$20-50 is more than sufficient for hundreds of experiments.

4.  **Store your key securely.** Never commit API keys to public
    repositories or share them in documents.

2.2 Claude as Your Lab Environment

A key insight of this workflow: Claude (via claude.ai with a Pro
subscription, or via the API) can serve as both your experimental
platform and your lab assistant. Claude\'s container environment can
execute Python code, make HTTP requests to other APIs, and store
results, all within a single conversation.

This means you do not need to install Python, set up a development
environment, or write code from scratch. You describe the experiment,
and Claude builds and runs the harness for you.

3\. The Experimental Workflow

3.1 Step 1: Design Your Protocol

Before any code runs, write a protocol document. This is a plain text
description of:

-   **Stimuli:** What images will you present? Where are they stored?
    What is the ground truth for each?

-   **Prompt levels:** What exact text accompanies each image? Define
    every prompt as a fixed string.

-   **Models:** Which models and which tiers (flagship, mid, small) from
    each vendor?

-   **N per cell:** How many trials per condition? N=5 for preliminary
    exploration, N=10+ for publication-grade data.

-   **Scoring criteria:** How will you classify each response? Define
    this before collecting data, not after.

Store this protocol in a persistent location (GitHub repository, Google
Doc, or as a file in Claude\'s project). This document is your
pre-registration equivalent.

3.2 Step 2: Prepare Stimuli

Images must be in a format the API accepts (PNG or JPEG). For color
perception experiments, use PNG (lossless) to avoid compression
artifacts that could alter hue values. Store stimuli in a GitHub
repository or upload them to Claude\'s conversation.

For each stimulus, record the ground truth measurements (e.g., Photoshop
eyedropper readings for color values). Ground truth must come from an
instrument, not from any AI model\'s report.

3.3 Step 3: Prompt Claude to Build the Harness

In a Claude session (claude.ai Pro or via API with computer use), paste
your protocol and ask Claude to build the experiment runner. Here is an
example prompt:

> I want to run a visual perception experiment across three
>
> OpenAI models (gpt-5.4, gpt-5.4-mini, gpt-5.4-nano).
>
> Stimuli: S003.png (already uploaded).
>
> Prompt: \"Describe this scene.\"
>
> N=5 trials per model.
>
> API key: \[your key here\]
>
> Build a Python script that:
>
> 1\. Loads the image as base64
>
> 2\. Calls each model 5 times with the same prompt
>
> 3\. Records the response text and timing
>
> 4\. Saves all results as JSON
>
> Run it and show me the results.

Claude will generate the Python harness, execute it, collect the
responses, and present the results. You can then ask for analysis,
scoring, or visualization.

3.4 Step 4: Store Raw Data

Every response from every trial should be preserved in its raw form. Our
standard format is a JSON dictionary keyed by condition:

> {
>
> \"GPT54\|S003\|PS00\|T1\": {
>
> \"text\": \"A bright yellow school bus\...\",
>
> \"ms\": 2327,
>
> \"trial\": 1,
>
> \"prompt_id\": \"PS00\",
>
> \"prompt_text\": \"Describe this scene.\",
>
> \"model_version\": \"gpt-5.4-2026-03-05\"
>
> },
>
> \...
>
> }

Commit raw JSON to a GitHub repository. Never discard raw responses in
favor of summaries. The analysis can always be re-run; the raw data
cannot be regenerated.

4\. Anatomy of an API Call

4.1 Anthropic (Claude)

> import anthropic
>
> client = anthropic.Anthropic(api_key=\"your-key\")
>
> response = client.messages.create(
>
> model=\"claude-opus-4-6\",
>
> max_tokens=600,
>
> messages=\[{
>
> \"role\": \"user\",
>
> \"content\": \[
>
> {\"type\": \"image\",
>
> \"source\": {\"type\": \"base64\",
>
> \"media_type\": \"image/png\",
>
> \"data\": image_b64}},
>
> {\"type\": \"text\",
>
> \"text\": \"Describe this scene.\"}
>
> \]
>
> }\]
>
> )

4.2 OpenAI (GPT-5.4)

> import openai
>
> client = openai.OpenAI(api_key=\"your-key\")
>
> response = client.chat.completions.create(
>
> model=\"gpt-5.4\",
>
> max_completion_tokens=600,
>
> messages=\[{
>
> \"role\": \"user\",
>
> \"content\": \[
>
> {\"type\": \"image_url\",
>
> \"image_url\": {
>
> \"url\": f\"data:image/png;base64,{image_b64}\"
>
> }},
>
> {\"type\": \"text\",
>
> \"text\": \"Describe this scene.\"}
>
> \]
>
> }\]
>
> )
>
> **Note:** OpenAI\'s GPT-5.4 family uses \"max_completion_tokens\"
> instead of \"max_tokens\". Using the older parameter name will produce
> an error.

5\. Google Gemini: Local Execution Required

Google\'s API infrastructure blocks calls from cloud-hosted
environments, including the containers used by Claude, Replit, and
similar platforms. **Gemini experiments must be run from your local
machine.**

This means:

-   You need **Python installed locally** (Python 3.8+).

-   You need to run commands in a **terminal/command prompt** (Terminal
    on Mac, Command Prompt or PowerShell on Windows).

-   You install the Google AI SDK: pip install google-genai

-   You run the experiment script manually: python run_gemini.py

If you are unfamiliar with command-line tools, this can be a hurdle. The
script itself is straightforward (Claude can generate it for you), but
executing it requires a local development setup. Consider starting with
Anthropic and OpenAI models first, which can be run entirely from within
Claude\'s environment, and adding Gemini once you are comfortable with
the workflow.

Alternatively, if you have a collaborator who is comfortable with
Python, they can run the Gemini portion of your experiments using the
same stimulus files and protocol.

> \# Gemini API call (run locally)
>
> from google import genai
>
> client = genai.Client(api_key=\"your-key\")
>
> response = client.models.generate_content(
>
> model=\"gemini-2.5-pro\",
>
> contents=\[image_part, \"Describe this scene.\"\]
>
> )

6\. What It Costs

API-based experiments are remarkably cheap. Here are real costs from our
SCE replication study:

  -------------------------- ------------------ ------------- ------------
  **Experiment**             **API Calls**      **Models**    **Approx.
                                                              Cost**

  Gradient breakpoint (N=5)  105                3 Claude      \~\$2

  Prompt specificity (N=3)   54                 3 Claude      \~\$1

  Cross-vendor gradient      105                3 OpenAI      \~\$2
  (N=5)                                                       

  Full protocol, all stimuli \~400              8 models, 3   \~\$6
                                                vendors       
  -------------------------- ------------------ ------------- ------------

The entire experimental program, 400+ API calls across eight models and
three vendors, cost less than a cup of coffee. This cost structure makes
replication trivially affordable. There is no reason not to run N=100
per condition if the science demands it.

7\. Practical Tips

7.1 Controlling Randomness

Most APIs offer a \"temperature\" parameter. For perception experiments,
set temperature to 0 or as low as the API allows. This reduces variation
from sampling randomness, making observed differences more attributable
to the model\'s actual perceptual processing.

Even at temperature=0, you will see variation across trials. This is
expected and informative: it reflects the model\'s probability
distribution over possible descriptions, not noise.

7.2 File Naming

**Use opaque filenames** for stimuli (S001.png, S002.png), not
descriptive ones (bus_cool_van_warm.png). Descriptive filenames can leak
experimental conditions into the model\'s context, contaminating
results.

7.3 Prompt Contamination

Avoid leading prompts. \"Describe this scene.\" is neutral. \"Describe
the colors of the vehicles, paying attention to which is warmer.\"
primes the model to find warmth differences. The prompt is part of your
experimental manipulation; treat it with the same rigor as your stimuli.

7.4 Scoring Before Collecting

Define your scoring rubric before running the experiment. For color
perception, we classify each response as: captured (reports expected
color), accurate (reports actual color), or partial (hedges, notes
anomaly without committing). The rubric should be specific enough that
two independent scorers would agree on \>90% of classifications.

8\. Quick Start: Your First Experiment

Here is the minimum viable experiment, assuming you have a Claude Pro
account:

5.  **Upload an image** to a Claude conversation.

6.  **Paste your OpenAI API key** into the conversation (Claude will use
    it for API calls but won\'t store it).

7.  Ask: *\"Run this image through gpt-5.4, gpt-5.4-mini, and
    gpt-5.4-nano with the prompt \'Describe this scene.\' Run 5 trials
    per model. Save results as JSON and show me a summary.\"*

8.  **Review the results.** Claude will present the raw responses and
    can score them against your criteria on request.

9.  **Ask Claude to commit** the results to a GitHub repository for
    permanent storage.

That is the entire workflow. From setup to data in under 30 minutes.

*Prepared for the Meadow Research Collective.* For questions or to share
replication results, reach Ted Inoue at **synthsentience.substack.com**.
