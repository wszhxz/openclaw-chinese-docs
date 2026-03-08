---
summary: "First-run onboarding flow for OpenClaw (macOS app)"
read_when:
  - Designing the macOS onboarding assistant
  - Implementing auth or identity setup
title: "Onboarding (macOS App)"
sidebarTitle: "Onboarding: macOS App"
---
# 入门引导（macOS 应用）

本文档描述了**当前**的首次运行入门引导流程。目标是实现顺畅的"day 0"体验：选择 Gateway 的运行位置，连接 auth，运行 wizard，并让 agent 自行 bootstrap。
有关入门路径的概览，请参阅 [入门引导概览](/start/onboarding-overview)。

<Steps>
<Step title="Approve macOS warning">
<Frame>
<img src="/assets/macos-onboarding/01-macos-warning.jpeg" alt="" />
</Frame>
</Step>
<Step title="Approve find local networks">
<Frame>
<img src="/assets/macos-onboarding/02-local-networks.jpeg" alt="" />
</Frame>
</Step>
<Step title="Welcome and security notice">
<Frame caption="Read the security notice displayed and decide accordingly">
<img src="/assets/macos-onboarding/03-security-notice.png" alt="" />
</Frame>

Security trust model:

- By default, OpenClaw is a personal agent: one trusted operator boundary.
- Shared/multi-user setups require lock-down (split trust boundaries, keep tool access minimal, and follow [Security](/gateway/security)).
- Local onboarding now defaults new configs to __CODE_BLOCK_0__ so fresh local setups keep filesystem/runtime tools without forcing the unrestricted __CODE_BLOCK_1__ profile.
- If hooks/webhooks or other untrusted content feeds are enabled, use a strong modern model tier and keep strict tool policy/sandboxing.

</Step>
<Step title="Local vs Remote">
<Frame>
<img src="/assets/macos-onboarding/04-choose-gateway.png" alt="" />
</Frame>

Where does the **Gateway** run?

- **This Mac (Local only):** onboarding can configure auth and write credentials
  locally.
- **Remote (over SSH/Tailnet):** onboarding does **not** configure local auth;
  credentials must exist on the gateway host.
- **Configure later:** skip setup and leave the app unconfigured.

<Tip>
**Gateway auth tip:**

- The wizard now generates a **token** even for loopback, so local WS clients must authenticate.
- If you disable auth, any local process can connect; use that only on fully trusted machines.
- Use a **token** for multi‑machine access or non‑loopback binds.

</Tip>
</Step>
<Step title="Permissions">
<Frame caption="Choose what permissions do you want to give OpenClaw">
<img src="/assets/macos-onboarding/05-permissions.png" alt="" />
</Frame>

Onboarding requests TCC permissions needed for:

- Automation (AppleScript)
- Notifications
- Accessibility
- Screen Recording
- Microphone
- Speech Recognition
- Camera
- Location

</Step>
<Step title="CLI">
  <Info>This step is optional</Info>
  The app can install the global __CODE_BLOCK_2__ CLI via npm/pnpm so terminal
  workflows and launchd tasks work out of the box.
</Step>
<Step title="Onboarding Chat (dedicated session)">
  After setup, the app opens a dedicated onboarding chat session so the agent can
  introduce itself and guide next steps. This keeps first‑run guidance separate
  from your normal conversation. See [Bootstrapping](/start/bootstrapping) for
  what happens on the gateway host during the first agent run.
</Step>
</Steps>