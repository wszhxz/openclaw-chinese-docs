---
summary: "Testing kit: unit/e2e/live suites, Docker runners, and what each test covers"
read_when:
  - Running tests locally or in CI
  - Adding regressions for model/provider bugs
  - Debugging gateway + agent behavior
title: "Testing"
---
Here's a conversational summary of the technical document you provided:

---

**Live Testing for AI Models: A Developer's Guide**

This document outlines how to set up and run live tests for various AI models (like OpenAI, Anthropic, Google Gemini, etc.) to ensure they work as expected. Here's the breakdown:

### **Key Concepts**
1. **Live Testing**: You run tests using real models and credentials to catch issues like authentication errors, rate limits, or unexpected behavior.
2. **CI-Safe Tests**: These are mock tests that simulate real scenarios without actual provider APIs, useful for CI/CD pipelines.
3. **Docker Runners**: Optional tools to test in a Linux environment, mounting your local config and workspace to the container.

### **Recommended Models to Test**
- **Modern Models**: 
  - OpenAI (e.g., `gpt-5.2`, `gpt-5.1`)
  - Anthropic (`claude-opus-4-5`, `claude-sonnet-4-5`)
  - Google Gemini (API and Antigravity variants)
  - Z.AI (`glm-4.7`)
  - MiniMax (`minimax-m2.1`)
- **Optional Add-ons**: Mistral, Cerebras, LM Studio, etc., if you have access.

### **Testing Scenarios**
- **Tool Calling**: Verify models can execute tasks (e.g., reading files, API calls).
- **Image Support**: Test models that handle image inputs (e.g., vision models).
- **Aggregators**: Use platforms like OpenRouter or OpenCode Zen for broader model coverage.

### **Credentials & Setup**
- **Profile Store**: Default location is `~/.openclaw/credentials/`. Use this for secure key management.
- **Environment Variables**: If you prefer env vars (like `OPENCLAW_CONFIG_PATH`), ensure they’re set before running tests.
- **Docker**: Run tests in containers to isolate environments, mounting your local config and workspace.

### **Special Cases**
- **Audio Transcription**: Use Deepgram for live audio-to-text tests.
- **Agent Reliability**: Existing tests check if agents follow rules (e.g., skill compliance) and handle multi-step workflows.

### **Best Practices**
- **Narrow Tests**: Focus on specific models or scenarios to avoid overwhelming the system.
- **CI-Safe First**: Start with mock tests to catch bugs without real API dependencies.
- **Document Everything**: Avoid hardcoding all models; let the system discover available models based on your keys.

### **Why It Matters**
Live testing ensures your AI workflows work reliably in production. By covering key models and scenarios, you catch edge cases early, saving time and resources.

---

Let me know if you'd like a step-by-step guide for a specific part (like setting up Docker or running a test)!