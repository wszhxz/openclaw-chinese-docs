---
summary: "Gmail Pub/Sub push wired into OpenClaw webhooks via gogcli"
read_when:
  - Wiring Gmail inbox triggers to OpenClaw
  - Setting up Pub/Sub push for agent wake
title: "Gmail PubSub"
---
# Gmail Pub/Sub → OpenClaw

目标：Gmail watch → Pub/Sub 推送 → `gog gmail watch serve` → OpenClaw webhook。

## 前置条件

- 已安装并登录 `gcloud`（[安装指南](https://docs.cloud.google.com/sdk/docs/install-sdk)）。
- 已安装并为 Gmail 账户授权 `gog`（gogcli）（[gogcli.sh](https://gogcli.sh/)）。
- 已启用 OpenClaw hooks（参见 [Webhooks](/automation/webhook)）。
- 已登录 `tailscale`（[tailscale.com](https://tailscale.com/)）。当前支持的部署方案使用 Tailscale Funnel 提供公共 HTTPS 端点。  
  其他隧道服务也可用，但属于 DIY / 不受支持方案，需手动配置连接。  
  目前仅正式支持 Tailscale。

示例 hook 配置（启用 Gmail 预设映射）：

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

若要将 Gmail 摘要投递至聊天界面，请在映射中覆盖预设，设置 `deliver` + 可选的 `channel`/`to`：

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

如需固定频道，请设置 `channel` + `to`；否则 `channel: "last"` 将使用最近一次投递路径（默认回退至 WhatsApp）。

如需强制 Gmail 运行时使用更低成本模型，请在映射中设置 `model`（`provider/model` 或其别名）。若强制启用 `agents.defaults.models`，请将其包含在该处。

如需为 Gmail hooks 单独指定默认模型与思维层级，请在配置中添加 `hooks.gmail.model` / `hooks.gmail.thinking`：

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

- 每个 hook 映射中的 `model`/`thinking` 仍会覆盖上述默认值。
- 回退顺序：`hooks.gmail.model` → `agents.defaults.model.fallbacks` → 主模型（认证/速率限制/超时）。
- 若设置了 `agents.defaults.models`，则 Gmail 所用模型必须位于白名单中。
- Gmail hook 内容默认以 external-content 安全边界封装。  
  如需禁用（危险操作），请设置 `hooks.gmail.allowUnsafeExternalContent: true`。

如需进一步自定义载荷处理逻辑，请添加 `hooks.mappings` 或在 `~/.openclaw/hooks/transforms` 下放置 JS/TS 转换模块（参见 [Webhooks](/automation/webhook)）。

## 向导（推荐）

使用 OpenClaw 辅助工具完成全部配置（macOS 上通过 brew 自动安装依赖）：

```bash
openclaw webhooks gmail setup \
  --account openclaw@gmail.com
```

默认行为：

- 使用 Tailscale Funnel 作为公共推送端点。
- 为 `openclaw webhooks gmail run` 生成 `hooks.gmail` 配置。
- 启用 Gmail hook 预设（`hooks.presets: ["gmail"]`）。

路径说明：当启用 `tailscale.mode` 时，OpenClaw 会自动将 `hooks.gmail.serve.path` 设为 `/`，同时保持公共路径为 `hooks.gmail.tailscale.path`（默认为 `/gmail-pubsub`），因为 Tailscale 在代理前会剥离 set-path 前缀。  
如需后端接收带前缀的路径，请将 `hooks.gmail.tailscale.target`（或 `--tailscale-target`）设为完整 URL（例如 `http://127.0.0.1:8788/gmail-pubsub`），并匹配 `hooks.gmail.serve.path`。

需要自定义端点？请使用 `--push-endpoint <url>` 或 `--tailscale off`。

平台说明：在 macOS 上，向导通过 Homebrew 安装 `gcloud`、`gogcli` 和 `tailscale`；在 Linux 上请先手动安装。

网关自动启动（推荐）：

- 当同时设置 `hooks.enabled=true` 和 `hooks.gmail.account` 时，网关将在系统启动时运行 `gog gmail watch serve`，并自动续订 watch。
- 设置 `OPENCLAW_SKIP_GMAIL_WATCHER=1` 可选择退出（适用于自行运行守护进程的场景）。
- 切勿同时运行手动守护进程，否则将触发 `listen tcp 127.0.0.1:8788: bind: address already in use`。

手动守护进程（启动 `gog gmail watch serve` + 自动续订）：

```bash
openclaw webhooks gmail run
```

## 一次性配置

1. 选择由 `gog` 所使用的 OAuth 客户端所属的 GCP 项目。

```bash
gcloud auth login
gcloud config set project <project-id>
```

注意：Gmail watch 要求 Pub/Sub 主题必须与 OAuth 客户端位于同一项目中。

2. 启用相关 API：

```bash
gcloud services enable gmail.googleapis.com pubsub.googleapis.com
```

3. 创建主题：

```bash
gcloud pubsub topics create gog-gmail-watch
```

4. 允许 Gmail 推送发布权限：

```bash
gcloud pubsub topics add-iam-policy-binding gog-gmail-watch \
  --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
  --role=roles/pubsub.publisher
```

## 启动 watch

```bash
gog gmail watch start \
  --account openclaw@gmail.com \
  --label INBOX \
  --topic projects/<project-id>/topics/gog-gmail-watch
```

保存输出中的 `history_id`（用于调试）。

## 运行推送处理器

本地示例（共享令牌认证）：

```bash
gog gmail watch serve \
  --account openclaw@gmail.com \
  --bind 127.0.0.1 \
  --port 8788 \
  --path /gmail-pubsub \
  --token <shared> \
  --hook-url http://127.0.0.1:18789/hooks/gmail \
  --hook-token OPENCLAW_HOOK_TOKEN \
  --include-body \
  --max-bytes 20000
```

注意事项：

- `--token` 用于保护推送端点（`x-gog-token` 或 `?token=`）。
- `--hook-url` 指向 OpenClaw 的 `/hooks/gmail`（已映射；独立运行 + 摘要发送至主通道）。
- `--include-body` 和 `--max-bytes` 控制发送至 OpenClaw 的请求体片段。

推荐方式：`openclaw webhooks gmail run` 封装相同流程，并自动续订 watch。

## 暴露处理器（高级，不受支持）

如需使用非 Tailscale 隧道，请手动配置，并在推送订阅中使用公共 URL（不受支持，无安全防护）：

```bash
cloudflared tunnel --url http://127.0.0.1:8788 --no-autoupdate
```

使用生成的 URL 作为推送端点：

```bash
gcloud pubsub subscriptions create gog-gmail-watch-push \
  --topic gog-gmail-watch \
  --push-endpoint "https://<public-url>/gmail-pubsub?token=<shared>"
```

生产环境：请使用稳定的 HTTPS 端点，配置 Pub/Sub OIDC JWT，然后运行：

```bash
gog gmail watch serve --verify-oidc --oidc-email <svc@...>
```

## 测试

向被监控的收件箱发送一条消息：

```bash
gog gmail send \
  --account openclaw@gmail.com \
  --to openclaw@gmail.com \
  --subject "watch test" \
  --body "ping"
```

检查 watch 状态与历史记录：

```bash
gog gmail watch status --account openclaw@gmail.com
gog gmail history --account openclaw@gmail.com --since <historyId>
```

## 故障排查

- `Invalid topicName`：项目不匹配（主题未位于 OAuth 客户端所属项目中）。
- `User not authorized`：主题上缺少 `roles/pubsub.publisher`。
- 消息为空：Gmail 推送仅提供 `historyId`；需通过 `gog gmail history` 获取完整内容。

## 清理

```bash
gog gmail watch stop --account openclaw@gmail.com
gcloud pubsub subscriptions delete gog-gmail-watch-push
gcloud pubsub topics delete gog-gmail-watch
```