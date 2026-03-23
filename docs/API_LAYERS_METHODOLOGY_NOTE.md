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

## Residual Uncertainty

We cannot fully exclude the possibility that hidden API defaults contribute to some observed behaviors. For example, if Anthropic's API injects a default instruction that encourages detailed scene description while OpenAI's does not, this could influence response length or verbosity in ways that interact with our scoring methodology. We control for this by using identical prompts across vendors and scoring on semantic content (color identification accuracy) rather than response style.

Researchers seeking to further isolate training-level effects could explore locally hosted open-weight models (e.g., Llama, Mistral) where no vendor API layer exists. We note that such models were not available in multimodal form at sufficient capability for this study's requirements at the time of data collection.

## Recommendation

Studies using vendor APIs to measure model behavior should explicitly acknowledge the three-layer architecture and state which layers they control, which they bypass, and which remain as potential confounds. The common framing of "we tested GPT-5.4" elides the distinction between the trained model, the API service, and the consumer product, three different objects that may exhibit different behaviors.

---

*This note is intended for inclusion in the methods or supplementary material of the SCE replication paper. It may also serve as a standalone methodological reference for other researchers using API-based experimental designs.*
