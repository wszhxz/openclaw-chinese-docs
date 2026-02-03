---
title: "Pi Integration Architecture"
---
**OpenClaw Embedded Agent System Summary**

---

### **Overview**  
The OpenClaw embedded agent system integrates with the **pi** framework, enabling programmatic control via `createAgentSession()`. Key features include:  
- **Custom Tools**: Replaces default coding tools with a tailored OpenClaw tool suite.  
- **Dynamic System Prompt**: Context-aware prompts tailored to channels or interactions.  
- **Session Management**: Stores sessions in `~/.openclaw/agents/<agentId>/sessions/` (or environment variable `OPENCLAW_STATE_DIR`).  
- **Multi-Profile Auth**: Supports credential rotation across profiles.  
- **Programmatic Extensions**: Extensions are loaded programmatically or from disk paths.  
- **Callback-Based Events**: Handles events like `onBlockReply` for interactive responses.  

---

### **Key Differences from Pi CLI**  
| **Aspect**               | **Pi CLI**                          | **OpenClaw Embedded**                                                                 |
|--------------------------|-------------------------------------|----------------------------------------------------------------------------------------|
| **Invocation**           | `pi` command / RPC                  | SDK via `createAgentSession()`                                                       |
| **Tools**                | Default coding tools                | Custom OpenClaw tool suite (e.g., Claude-style aliases, schema compatibility)         |
| **System Prompt**        | AGENTS.md + static prompts          | Dynamic, per-channel/context-based prompts                                           |
| **Session Storage**      | `~/.pi/agent/sessions/`             | `~/.openclaw/agents/<agentId>/sessions/` (or `OPENCLAW_STATE_DIR`)                   |
| **Auth**                 | Single credential                   | Multi-profile with rotation (e.g., handling API rate limits)                         |
| **Extensions**           | Loaded from disk                    | Programmatic + disk paths (e.g., `pi-extensions/compaction-safeguard`)                |
| **Event Handling**       | TUI rendering                       | Callback-based (e.g., `onBlockReply`, `onToolExecution`)                             |

---

### **Future Considerations**  
1. **Tool Signature Alignment**: Current workaround for pi-agent-core vs. pi-coding-agent signature mismatches.  
2. **Session Manager Wrapping**: `guardSessionManager` adds safety but increases complexity.  
3. **Extension Loading**: Potential to leverage pi's `ResourceLoader` for direct integration.  
4. **Streaming Handler Complexity**: `subscribeEmbeddedPiSession` has grown large; simplification may be needed.  
5. **Provider Quirks**: Provider-specific codepaths (e.g., Anthropic, Google, OpenAI) could be centralized.  

---

### **Provider-Specific Handling**  
- **Anthropic**:  
  - Scrub refusal magic strings.  
  - Validate turn roles to prevent consecutive roles.  
  - Ensure Claude Code parameter compatibility.  
- **Google/Gemini**:  
  - Fix turn ordering with `applyGoogleTurnOrderingFix`.  
  - Sanitize tool schemas with `sanitizeToolsForGoogle`.  
  - Sanitize session history with `sanitizeSessionHistory`.  
- **OpenAI**:  
  - Use `apply_patch` for Codex models.  
  - Handle thinking level downgrades (e.g., downgrade to `basic` for OpenAI).  

---

### **TUI Integration**  
OpenClaw supports a local terminal UI (TUI) using `pi-tui` components, offering an interactive experience similar to pi's native mode.  

---

### **Tests**  
All tests covering the pi integration and extensions are included:  
- **Core Helpers**:  
  - Error classification (e.g., `isContextOverflowError`, `classifyFailoverReason`).  
  - Text sanitization (e.g., `sanitizeSessionMessagesImages`, `stripThoughtSignatures`).  
- **Runner & Session Handling**:  
  - `limithistoryturns`, `resolvesessionagentids`, `run-embedded-pi-agent.auth-profile-rotation`.  
- **Subscribers & Streaming**:  
  - `subscribe-embedded-pi-session` tests for block reply handling, tool execution, and compaction retries.  
- **Extensions**:  
  - `pi-extensions/compaction-safeguard.test.ts`, `context-pruning.test.ts`.  
- **Tool Definitions**:  
  - `pi-tool-definition-adapter.test.ts`, `create-openclaw-coding-tools.test.ts`.  

---

### **Conclusion**  
The OpenClaw embedded agent system provides a flexible, extensible framework for integrating with the pi ecosystem. While it offers advanced customization and multi-profile auth, ongoing improvements to tool alignment, session management, and provider abstraction are recommended for long-term maintainability. The comprehensive test suite ensures robustness across edge cases and provider-specific requirements.