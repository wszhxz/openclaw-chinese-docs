---
summary: "Gmail Pub/Sub push wired into OpenClaw webhooks via gogcli"
read_when:
  - Wiring Gmail inbox triggers to OpenClaw
  - Setting up Pub/Sub push for agent wake
title: "Gmail PubSub"
---
# Gmail Pub/Sub -> OpenClaw

目标：Gmail watch -> Pub/Sub 推送 -> `gog gmail watch serve` -> OpenClaw Webhook。

## 前提条件

- `gcloud` 已安装并登录（[安装指南](https://docs.cloud.google.com/sdk/docs/install-sdk)）。
- `gog`（gogcli）已安装并为 Gmail 账户授权（[gogcli.sh](https://gogcli.sh/)）。
- OpenClaw Webhook 已启用（参见 [Webhooks](/automation/webhook)）。
- `tailscale` 已登录（[tailscale.com](https://tailscale.com/)）。支持的设置使用 Tailscale Funnel 作为公共 HTTPS 端点。
  其他隧道服务也可使用，但需自行配置且不受支持，需要手动连接。
  目前我们支持的是 Tailscale。

示例 Hook 配置（启用 Gmail 预设映射）：

```json5
{
  hooks: {
    enabled: true,
    token: "OPENCLAW_HOOK_TOKEN",
    path: "/hooks",
    presets: ["gmail"],
  },
}
```

为了将 Gmail 摘要传递到聊天界面，用映射覆盖预设，设置 `deliver` + 可选的 `channel`/`to`：

```json5
{
  hooks: {
    enabled: true,
    token: "OPENCLAW_HOOK_TOKEN",
    presets: ["gmail"],
    mappings: [
      {
        match: { path: "gmail" },
        action: "agent",
        wakeMode: "now",
        name: "Gmail",
        sessionKey: "hook:gmail:{{messages[0].id}}",
        messageTemplate: "New email from {{messages[0].from}}\nSubject: {{messages[0].subject}}\n{{messages[0].snippet}}\n{{messages[0].body}}",
        model: "openai/gpt-5.2-mini",
        deliver: true,
        channel: "last",
        // to: "+15551234567"
      },
    ],
  },
}
```

如果你想使用固定频道，设置 `channel` + `to`。否则 `channel: "last"` 会使用最后的传递路由（回退到 WhatsApp）。

为了强制 Gmail 运行使用更便宜的模型，在映射中设置 `model`（`provider/model` 或别名）。如果你强制 `agents.defaults.models`，请在该处包含它。

为了为 Gmail Webhook 设置默认模型和思考级别，添加 `hooks.gmail.model` / `hooks.gmail.thinking` 到你的配置中：

```json5
{
  hooks: {
    gmail: {
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
    },
  },
}
```

注意事项：

- 映射中的每个 Hook `model`/`thinking` 仍会覆盖这些默认值。
- 回退顺序：`hooks.gmail.model` → `agents.defaults.model.fallbacks` → 主要（认证/速率限制/超时）。
- 如果设置了 `agents.defaults.models`，Gmail 模型必须在允许列表中。
- Gmail Webhook 内容默认被外部内容安全边界包裹。
  要禁用（危险），设置 `hooks.gmail.allowUnsafeExternalContent: true`。

为了进一步自定义负载处理，添加 `hooks.mappings` 或 JS/TS 转换模块到 `hooks.transformsDir` 下（参见 [Webhooks](/automation/webhook)）。

## 向导（推荐）

使用 OpenClaw 辅助工具将所有内容连接起来（在 macOS 上通过 brew 安装依赖）：

```bash
openclaw webhooks gmail setup \
  --account openclaw@gmail.com
```

默认值：

- 使用 Tailscale Funnel 作为公共推送端点。
- 为 `openclaw webhooks gmail run` 写入 `hooks.gmail` 配置。
- 启用 Gmail Webhook 预设（`hooks.presets: ["gmail"]`）。

路径说明：当 `tailscale.mode` 启用时，OpenClaw 会自动设置
`hooks.gmail.serve.path` 为 `/`，并保持公共路径在
`hooks.gmail.tailscale.path`（默认 `/gmail-pubsub`）因为 Tailscale
在代理前会剥离设置的路径前缀。如果你需要后端接收带前缀的路径，请设置
`hooks.gmail.tailscale.target`（或 `--tailscale-target`）为完整 URL，如
`http://127.0.0.1:8788/gmail-pubsub`，并匹配 `hooks.gmail.serve.path`。

想要自定义端点？使用 `--push-endpoint <url>` 或 `--tailscale off`。

平台说明：在 macOS 上，向导通过 Homebrew 安装 `gcloud`、`gogcli` 和 `tailscale`；在 Linux 上请先手动安装它们。

网关自动启动（推荐）：

- 当 `hooks.enabled=true` 且 `hooks.gmail.account` 设置时，网关在启动时启动
  `gog gmail watch serve` 并自动续订 watch。
- 设置 `OPENCLAW_SKIP_GMAIL_WATCHER=1` 以退出（如果你自己运行守护进程很有用）。
- 不要同时运行手动守护进程，否则会遇到
  `listen tcp 127.0.0.1:8788: bind: address already in use`。

手动守护进程（启动 `gog gmail watch serve` + 自动续订）：

```bash
openclaw webhooks gmail run
```

## 一次性设置

1. 选择 **拥有 `gog` 使用的 OAuth 客户端** 的 GCP 项目。

```bash
gcloud auth login
gcloud config set project <project-id>
```

注意：Gmail watch 要求 Pub/Sub 主题与 OAuth 客户端位于同一项目中。

2. 启用 API：

```bash
gcloud services enable gmail.googleapis.com pubsub.googleapis.com
```

3. 创建主题：

```bash
gcloud pubsub topics create gog-gmail-watch
```

4. 允许 Gmail 推送发布：

```bash
gcloud pubsub topics add-iam