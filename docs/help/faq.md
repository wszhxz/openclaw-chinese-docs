---
summary: "Frequently asked questions about OpenClaw setup, configuration, and usage"
title: "FAQ"
---
**A:** In OpenClaw, the default model for Anthropic (or any provider) is **not** tied to the API key itself. Instead, it is explicitly configured in the agent's settings via `agents.defaults.model.primary`. For example, you might set it to `anthropic/claude-sonnet-4-5` or `anthropic/claude-opus-4-5`, depending on your preference. 

The `ANTHROPIC_API_KEY` (or stored credentials in `auth-profiles.json`) only enables authentication to the Anthropic API. It does **not** dictate the model. If you see the error `No credentials found for profile "anthropic:default"`, it means the Gateway couldn’t locate the API key in the expected location (e.g., missing or misconfigured credentials in the auth profile). 

**Key steps to resolve:**
1. **Verify credentials**: Ensure the Anthropic API key is correctly stored in `auth-profiles.json` under the relevant profile (e.g., `anthropic:default`).
2. **Specify the model**: Explicitly set `agents.defaults.model.primary` to your desired Anthropic model (e.g., `anthropic/claude-sonnet-4-5`).
3. **Restart the Gateway**: After updating the config, restart the Gateway to apply changes.

If the model is not specified, OpenClaw may default to a generic or fallback model, but this depends on your configuration. Always explicitly define the model to avoid ambiguity.