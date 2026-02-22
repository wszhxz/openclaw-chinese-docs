---
summary: "Gmail Pub/Sub push wired into OpenClaw webhooks via gogcli"
read_when:
  - Wiring Gmail inbox triggers to OpenClaw
  - Setting up Pub/Sub push for agent wake
title: "Gmail PubSub"
---
# Gmail Pub/Sub -> OpenClaw

目标: Gmail watch -> Pub/Sub push -> `gog gmail watch serve` -> OpenClaw webhook.

## 前提条件

- 安装并登录 `gcloud` ([安装指南](https://docs.cloud.google.com/sdk/docs/install-sdk)).
- 安装并授权给Gmail账户的 `gog` (gogcli) ([gogcli.sh](https://gogcli.sh/)).
- 启用OpenClaw钩子（参见[Webhooks](/automation/webhook)).
- 登录 `tailscale` ([tailscale.com](https://tailscale.com/)). 支持的设置使用Tailscale Funnel作为公共HTTPS端点。
  其他隧道服务也可以工作，但需要自行配置且不受支持。
  目前，我们支持Tailscale。

示例钩子配置（启用Gmail预设映射）：

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

要将Gmail摘要发送到聊天界面，请使用设置 `deliver` + 可选 `channel`/`to` 的映射覆盖预设：

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

如果要固定频道，请设置 `channel` + `to`。否则 `channel: "last"`
将使用最后一个交付路由（回退到WhatsApp）。

要强制使用更便宜的Gmail运行模型，请在映射中设置 `model` (`provider/model` 或别名)。如果强制 `agents.defaults.models`，请包含在其中。

要为Gmail钩子设置默认模型和思考级别，请在配置中添加
`hooks.gmail.model` / `hooks.gmail.thinking`：

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

- 映射中的每个钩子的 `model`/`thinking` 仍然会覆盖这些默认值。
- 回退顺序：`hooks.gmail.model` → `agents.defaults.model.fallbacks` → 主要（认证/速率限制/超时）。
- 如果设置了 `agents.defaults.models`，Gmail模型必须在允许列表中。
- 默认情况下，Gmail钩子内容会被外部内容安全边界包裹。
  要禁用（危险），请设置 `hooks.gmail.allowUnsafeExternalContent: true`。

要进一步自定义负载处理，请在 `hooks.mappings` 下添加JS/TS转换模块或 `~/.openclaw/hooks/transforms`（参见[Webhooks](/automation/webhook))。

## 向导（推荐）

使用OpenClaw助手将所有内容连接起来（通过brew在macOS上安装依赖）：

```bash
openclaw webhooks gmail setup \
  --account openclaw@gmail.com
```

默认设置：

- 使用Tailscale Funnel作为公共推送端点。
- 为 `openclaw webhooks gmail run` 写入 `hooks.gmail` 配置。
- 启用Gmail钩子预设 (`hooks.presets: ["gmail"]`)。

路径说明：当 `tailscale.mode` 启用时，OpenClaw自动将
`hooks.gmail.serve.path` 设置为 `/` 并保持公共路径在
`hooks.gmail.tailscale.path` (默认 `/gmail-pubsub`)，因为Tailscale
在代理之前会剥离设置的路径前缀。
如果您需要后端接收带前缀的路径，请设置
`hooks.gmail.tailscale.target` (或 `--tailscale-target`) 为完整的URL，例如
`http://127.0.0.1:8788/gmail-pubsub` 并匹配 `hooks.gmail.serve.path`。

需要自定义端点？使用 `--push-endpoint <url>` 或 `--tailscale off`。

平台说明：在macOS上，向导通过Homebrew安装 `gcloud`，`gogcli` 和 `tailscale`；
在Linux上，请先手动安装它们。

网关自动启动（推荐）：

- 当 `hooks.enabled=true` 和 `hooks.gmail.account` 设置时，网关将在启动时启动
  `gog gmail watch serve` 并自动续订watch。
- 设置 `OPENCLAW_SKIP_GMAIL_WATCHER=1` 以退出（如果您自己运行守护进程很有用）。
- 不要同时运行手动守护进程，否则会遇到
  `listen tcp 127.0.0.1:8788: bind: address already in use`。

手动守护进程（启动 `gog gmail watch serve` + 自动续订）：

```bash
openclaw webhooks gmail run
```

## 一次性设置

1. 选择拥有 `gog` 使用的OAuth客户端的GCP项目。

```bash
gcloud auth login
gcloud config set project <project-id>
```

注意：Gmail watch要求Pub/Sub主题与OAuth客户端位于同一项目中。

2. 启用API：

```bash
gcloud services enable gmail.googleapis.com pubsub.googleapis.com
```

3. 创建一个主题：

```bash
gcloud pubsub topics create gog-gmail-watch
```

4. 允许Gmail推送发布：

```bash
gcloud pubsub topics add-iam-policy-binding gog-gmail-watch \
  --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
  --role=roles/pubsub.publisher
```

## 启动watch

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

- `--token` 保护推送端点 (`x-gog-token` 或 `?token=`)。
- `--hook-url` 指向OpenClaw `/hooks/gmail`（映射；隔离运行+摘要到主）。
- `--include-body` 和 `--max-bytes` 控制发送到OpenClaw的正文片段。

推荐：`openclaw webhooks gmail run` 包装相同的流程并自动续订watch。

## 暴露处理器（高级，不支持）

如果您需要非Tailscale隧道，请手动连接并使用推送订阅中的公共URL（不支持，无防护措施）：

```bash
cloudflared tunnel --url http://127.0.0.1:8788 --no-autoupdate
```

使用生成的URL作为推送端点：

```bash
gcloud pubsub subscriptions create gog-gmail-watch-push \
  --topic gog-gmail-watch \
  --push-endpoint "https://<public-url>/gmail-pubsub?token=<shared>"
```

生产环境：使用稳定的HTTPS端点并配置Pub/Sub OIDC JWT，然后运行：

```bash
gog gmail watch serve --verify-oidc --oidc-email <svc@...>
```

## 测试

向监视的收件箱发送消息：

```bash
gog gmail send \
  --account openclaw@gmail.com \
  --to openclaw@gmail.com \
  --subject "watch test" \
  --body "ping"
```

检查watch状态和历史记录：

```bash
gog gmail watch status --account openclaw@gmail.com
gog gmail history --account openclaw@gmail.com --since <historyId>
```

## 故障排除

- `Invalid topicName`: 项目不匹配（主题不在OAuth客户端项目中）。
- `User not authorized`: 主题缺少 `roles/pubsub.publisher`。
- 空消息：Gmail推送仅提供 `historyId`；通过 `gog gmail history` 获取。

## 清理

```bash
gog gmail watch stop --account openclaw@gmail.com
gcloud pubsub subscriptions delete gog-gmail-watch-push
gcloud pubsub topics delete gog-gmail-watch
```