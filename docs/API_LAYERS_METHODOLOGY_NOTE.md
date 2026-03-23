# Methodology Note: API Access Layers and Potential Confounds

## For inclusion in the SCE paper methods section or as supplementary material
## Drafted: 03-22-2026

---

## What We Control, What We Don't, and Why It Matters

All experiments in this study were conducted via vendor APIs (Anthropic Messages API, OpenAI Chat Completions API, Google Generative AI API), not through consumer chat interfaces (Claude.ai, ChatGPT, Gemini). This distinction matters because consumer products add substantial behavioral shaping that would contaminate experimental results. However, API access is not the same as raw model access, and the difference deserves explicit acknowledgment.

## Three Layers of Behavioral Shaping

We identify three layers that shape a model's response to any input:

### Layer 1: Training (In the Weights)

RLHF, constitutional AI training, safety fine-tuning, and the full training corpus produce behavioral tendencies that are embedded in the model's parameters. These cannot be removed by any prompting strategy. A model trained on billions of images captioned "school bus" paired with the word "yellow" will carry that statistical association into every inference, regardless of what instructions precede the query.

This layer is not a confound. It is the object of study. The semantic coherence enforcement phenomenon we document arises from training-level statistical associations between object labels and expected perceptual properties. Our experiments are designed to measure this layer's influence on perceptual reporting.

### Layer 2: Vendor-Side API Defaults (Invisible)

When a researcher calls a vendor API with no system prompt, it is possible that the vendor injects default instructions server-side before the request reaches the model. These could include behavioral guidelines ("be helpful and concise"), safety constraints, or formatting preferences. We cannot audit this layer. Vendors do not publicly document what, if any, default instructions are appended to API calls made without an explicit system prompt.

We did not include system prompts in our API calls. Our requests consisted solely of the image and a prompt string (e.g., "Describe this scene."). If a vendor injects hidden default text, our experimental conditions include that text, and we have no way to measure or subtract its influence.

### Layer 3: Operator System Prompt (Bypassed)

Consumer products (ChatGPT, Claude.ai, Gemini chat) include extensive system prompts that shape personality, response style, safety behavior, and tool usage. Recent analysis of leaked system prompts from 30+ production AI tools (Wright, 2026) documents prompts exceeding thousands of tokens that define behavioral personas, workflow management, and even instructions to misidentify the underlying model.

Our API methodology fully bypasses this layer. No system prompt is provided. The model receives only the experimental stimulus and the experimental prompt. This eliminates the most significant source of behavioral shaping that would affect results obtained through consumer chat interfaces.

## Why We Believe the Results Reflect Training-Level Phenomena

Three lines of evidence support the conclusion that our findings reflect Layer 1 (training) rather than Layer 2 (hidden API defaults):

**Cross-vendor divergence.** If all vendors injected similar hidden API defaults, we would expect convergence in model behavior. Instead, we observe systematic vendor-specific differences. OpenAI's GPT-5.4 family breaks semantic capture at approximately +25 degrees of hue shift uniformly across tiers, while Anthropic's Claude models show tier-differentiated breakpoints (Opus at approximately +21 degrees, Haiku more captured). These vendor signatures are consistent with different training regimes, not with shared hidden instructions.

**Within-vendor tier differentiation.** Anthropic's three model tiers (Opus, Sonnet, Haiku) show different breakpoint curves on identical stimuli with identical prompts delivered through the same API. If a hidden API default were shaping behavior, it would presumably be the same default across tiers, producing similar rather than divergent results. The tier differentiation suggests the phenomenon scales with model capability, a training-level property.

**Consistency with known training artifacts.** The patterns we document (object-label-dependent color reporting, prior-consistent confabulation, narrative construction around perceptual violations) are well-predicted by the training process. Models trained on captioned image data will develop statistical associations between object labels and their typical visual properties. These associations would persist regardless of any API-level instruction layer.

## Residual Uncertainty: Layer 2 is Empirically Confirmed for OpenAI

This concern is not purely theoretical. In August 2025, Simon Willison demonstrated that GPT-5, when accessed via the OpenAI API with no user-specified system prompt, nonetheless received a hidden system prompt that included at least the current date and a "desired oververbosity" parameter set to 3/10 (Willison, 2025). Tommy Hughes subsequently extracted a more complete version of this hidden prompt. Crucially, Willison confirmed that providing a custom system prompt did not override the hidden one; the two were concatenated, with the hidden prompt taking precedence on at least some parameters.

This means that our OpenAI API calls, despite specifying no system prompt, operated under behavioral constraints we could not see or control. The verbosity setting alone could influence response length, detail level, and the probability of volunteering color descriptions versus waiting to be asked. We cannot determine whether additional hidden instructions shaped perceptual reporting behavior.

For Anthropic's Claude, the situation is less clear. The Claude web interface (claude.ai) uses a massive system prompt (~99K characters, ~25K tokens) that includes explicit behavioral instructions such as anti-engagement clauses, citation rules, and formatting preferences. API calls do not receive this prompt. However, many of the same behaviors (non-sycophantic tone, reluctance to foster reliance) appear in bare API responses, suggesting they exist at the training level (Layer 1) as well. Whether Anthropic also injects a smaller hidden Layer 2 prompt on API calls is unknown.

For Google's Gemini, the situation is similarly opaque. Google blocks API calls from cloud-hosted environments, requiring local execution, which eliminates one potential source of interference but does not address whether a hidden prompt is injected server-side.

We control for these confounds by scoring on semantic content (color identification accuracy, directional correctness) rather than response style (verbosity, formatting, hedging language). The semantic prior that "school buses are yellow" is a training-level phenomenon regardless of any API-layer instruction. However, we acknowledge that hidden API prompts represent a confound that cannot be fully eliminated without access to locally hosted open-weight multimodal models.

**References:**
- Willison, S. (2025, August 15). "GPT-5 has a hidden system prompt." simonwillison.net.
- Hughes, T. (2025). Extracted GPT-5 API system prompt. GitHub/Reddit.
- Wright, J. (2026, March 20). "I Read the System Prompts of 30+ AI Tools." The ECHO Files (Substack).

Researchers seeking to further isolate training-level effects should explore locally hosted open-weight models (e.g., Llama, Mistral) where no vendor API layer exists. We note that such models were not available in multimodal form at sufficient capability for this study's requirements at the time of data collection.

## Recommendation

Studies using vendor APIs to measure model behavior should explicitly acknowledge the three-layer architecture and state which layers they control, which they bypass, and which remain as potential confounds. The common framing of "we tested GPT-5.4" elides the distinction between the trained model, the API service, and the consumer product, three different objects that may exhibit different behaviors.

---

*This note is intended for inclusion in the methods or supplementary material of the SCE replication paper. It may also serve as a standalone methodological reference for other researchers using API-based experimental designs.*
