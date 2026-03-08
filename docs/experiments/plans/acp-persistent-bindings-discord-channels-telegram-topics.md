# ACP 针对 Discord 频道和 Telegram 主题的持久化绑定

状态：草稿

## 摘要

引入持久的 ACP 绑定，映射：

- Discord 频道（以及需要的现有线程），以及
- 群组/超级群组中的 Telegram 论坛主题 (`chatId:topic:topicId`)

到长期存活的 ACP 会话，使用显式绑定类型将绑定状态存储在顶层 `bindings[]` 条目中。

这使得高流量消息通道中的 ACP 使用变得可预测且持久，因此用户可以创建专用频道/主题，例如 `codex`、`claude-1` 或 `claude-myrepo`。

## 原因

当前基于线程的 ACP 行为是针对临时的 Discord 线程工作流优化的。Telegram 没有相同的线程模型；它在群组/超级群组中有论坛主题。用户希望在聊天界面中获得稳定、常开的 ACP“工作区”，而不仅仅是临时的线程会话。

## 目标

- 支持以下内容的持久 ACP 绑定：
  - Discord 频道/线程
  - Telegram 论坛主题（群组/超级群组）
- 使绑定事实来源配置驱动。
- 保持 `/acp`、`/new`、`/reset`、`/focus` 以及在 Discord 和 Telegram 之间的交付行为一致。
- 保留现有的临时绑定流程以用于临时使用。

## 非目标

- 全面重新设计 ACP 运行时/会话内部结构。
- 移除现有的临时绑定流程。
- 在第一轮迭代中扩展到每个频道。
- 在此阶段实现 Telegram 频道直接消息主题 (`direct_messages_topic_id`)。
- 在此阶段实现 Telegram 私聊主题变体。

## UX 方向

### 1) 两种绑定类型

- **持久化绑定**：保存在配置中，启动时同步，旨在用于“命名工作区”频道/主题。
- **临时绑定**：仅运行时，根据空闲/最大年龄策略过期。

### 2) 命令行为

- `/acp spawn ... --thread here|auto|off` 仍然可用。
- 添加显式的绑定生命周期控制：
  - `/acp bind [session|agent] [--persist]`
  - `/acp unbind [--persist]`
  - `/acp status` 包含绑定是 `persistent` 还是 `temporary`。
- 在已绑定的对话中，`/new` 和 `/reset` 就地重置已绑定的 ACP 会话并保持绑定附加。

### 3) 对话身份

- 使用规范对话 ID：
  - Discord：频道/线程 ID。
  - Telegram 主题：`chatId:topic:topicId`。
- 永远不要仅凭裸主题 ID 对 Telegram 绑定进行键控。

## 配置模型（提议）

在顶层 `bindings[]` 中统一路由和持久化 ACP 绑定配置，使用显式 `type` 区分符：

```jsonc
{
  "agents": {
    "list": [
      {
        "id": "main",
        "default": true,
        "workspace": "~/.openclaw/workspace-main",
        "runtime": { "type": "embedded" },
      },
      {
        "id": "codex",
        "workspace": "~/.openclaw/workspace-codex",
        "runtime": {
          "type": "acp",
          "acp": {
            "agent": "codex",
            "backend": "acpx",
            "mode": "persistent",
            "cwd": "/workspace/repo-a",
          },
        },
      },
      {
        "id": "claude",
        "workspace": "~/.openclaw/workspace-claude",
        "runtime": {
          "type": "acp",
          "acp": {
            "agent": "claude",
            "backend": "acpx",
            "mode": "persistent",
            "cwd": "/workspace/repo-b",
          },
        },
      },
    ],
  },
  "acp": {
    "enabled": true,
    "backend": "acpx",
    "allowedAgents": ["codex", "claude"],
  },
  "bindings": [
    // Route bindings (existing behavior)
    {
      "type": "route",
      "agentId": "main",
      "match": { "channel": "discord", "accountId": "default" },
    },
    {
      "type": "route",
      "agentId": "main",
      "match": { "channel": "telegram", "accountId": "default" },
    },
    // Persistent ACP conversation bindings
    {
      "type": "acp",
      "agentId": "codex",
      "match": {
        "channel": "discord",
        "accountId": "default",
        "peer": { "kind": "channel", "id": "222222222222222222" },
      },
      "acp": {
        "label": "codex-main",
        "mode": "persistent",
        "cwd": "/workspace/repo-a",
        "backend": "acpx",
      },
    },
    {
      "type": "acp",
      "agentId": "claude",
      "match": {
        "channel": "discord",
        "accountId": "default",
        "peer": { "kind": "channel", "id": "333333333333333333" },
      },
      "acp": {
        "label": "claude-repo-b",
        "mode": "persistent",
        "cwd": "/workspace/repo-b",
      },
    },
    {
      "type": "acp",
      "agentId": "codex",
      "match": {
        "channel": "telegram",
        "accountId": "default",
        "peer": { "kind": "group", "id": "-1001234567890:topic:42" },
      },
      "acp": {
        "label": "tg-codex-42",
        "mode": "persistent",
      },
    },
  ],
  "channels": {
    "discord": {
      "guilds": {
        "111111111111111111": {
          "channels": {
            "222222222222222222": {
              "enabled": true,
              "requireMention": false,
            },
            "333333333333333333": {
              "enabled": true,
              "requireMention": false,
            },
          },
        },
      },
    },
    "telegram": {
      "groups": {
        "-1001234567890": {
          "topics": {
            "42": {
              "requireMention": false,
            },
          },
        },
      },
    },
  },
}
```

### 最小示例（无每个绑定的 ACP 覆盖）

```jsonc
{
  "agents": {
    "list": [
      { "id": "main", "default": true, "runtime": { "type": "embedded" } },
      {
        "id": "codex",
        "runtime": {
          "type": "acp",
          "acp": { "agent": "codex", "backend": "acpx", "mode": "persistent" },
        },
      },
      {
        "id": "claude",
        "runtime": {
          "type": "acp",
          "acp": { "agent": "claude", "backend": "acpx", "mode": "persistent" },
        },
      },
    ],
  },
  "acp": { "enabled": true, "backend": "acpx" },
  "bindings": [
    {
      "type": "route",
      "agentId": "main",
      "match": { "channel": "discord", "accountId": "default" },
    },
    {
      "type": "route",
      "agentId": "main",
      "match": { "channel": "telegram", "accountId": "default" },
    },

    {
      "type": "acp",
      "agentId": "codex",
      "match": {
        "channel": "discord",
        "accountId": "default",
        "peer": { "kind": "channel", "id": "222222222222222222" },
      },
    },
    {
      "type": "acp",
      "agentId": "claude",
      "match": {
        "channel": "discord",
        "accountId": "default",
        "peer": { "kind": "channel", "id": "333333333333333333" },
      },
    },
    {
      "type": "acp",
      "agentId": "codex",
      "match": {
        "channel": "telegram",
        "accountId": "default",
        "peer": { "kind": "group", "id": "-1009876543210:topic:5" },
      },
    },
  ],
}
```

注释：

- `bindings[].type` 是显式的：
  - `route`：普通代理路由。
  - `acp`：用于匹配对话的持久化 ACP 框架绑定。
- 对于 `type: "acp"`，`match.peer.id` 是规范对话键：
  - Discord 频道/线程：原始频道/线程 ID。
  - Telegram 主题：`chatId:topic:topicId`。
- `bindings[].acp.backend` 是可选的。后端回退顺序：
  1. `bindings[].acp.backend`
  2. `agents.list[].runtime.acp.backend`
  3. 全局 `acp.backend`
- `mode`、`cwd` 和 `label` 遵循相同的覆盖模式 (`binding override -> agent runtime default -> global/default behavior`)。
- 保留现有的 `session.threadBindings.*` 和 `channels.discord.threadBindings.*` 用于临时绑定策略。
- 持久化条目声明期望状态；运行时同步到实际的 ACP 会话/绑定。
- 每个对话节点一个活动的 ACP 绑定是预期模型。
- 向后兼容性：缺失的 `type` 被解释为 `route` 用于遗留条目。

### 后端选择

- ACP 会话初始化已经在启动期间使用配置的后端选择 (`acp.backend` 今日)。
- 此提案扩展启动/同步逻辑以优先处理类型化 ACP 绑定覆盖：
  - `bindings[].acp.backend` 用于对话本地覆盖。
  - `agents.list[].runtime.acp.backend` 用于每个代理的默认值。
- 如果没有覆盖，保持当前行为 (`acp.backend` 默认值)。

## 在当前系统中的架构适配

### 重用现有组件

- `SessionBindingService` 已经支持与频道无关的对话引用。
- ACP 启动/绑定流程已经支持通过服务 API 进行绑定。
- Telegram 已经通过 `MessageThreadId` 和 `chatId` 携带主题/线程上下文。

### 新增/扩展组件

- **Telegram 绑定适配器**（与 Discord 适配器并行）：
  - 按 Telegram 账户注册适配器，
  - 通过规范对话 ID 解析/列出/绑定/解绑/触摸。
- **类型化绑定解析器/索引**：
  - 将 `bindings[]` 拆分为 `route` 和 `acp` 视图，
  - 仅在 `route` 绑定上保留 `resolveAgentRoute`，
  - 仅从 `acp` 绑定解析持久化 ACP 意图。
- **Telegram 入站绑定解析**：
  - 在路由最终确定之前解析绑定会话（Discord 已经这样做）。
- **持久化绑定同步器**：
  - 启动时：加载配置的顶层 `type: "acp"` 绑定，确保 ACP 会话存在，确保绑定存在。
  - 配置更改时：安全应用差异。
- **切换模型**：
  - 不读取频道本地 ACP 绑定回退，
  - 持久化 ACP 绑定仅源自顶层 `bindings[].type="acp"` 条目。

## 分阶段交付

### 第 1 阶段：类型化绑定架构基础

- 扩展配置架构以支持 `bindings[].type` 区分符：
  - `route`，
  - `acp` 带可选的 `acp` 覆盖对象 (`mode`, `backend`, `cwd`, `label`)。
- 扩展代理架构以包含运行时描述符来标记 ACP 原生代理 (`agents.list[].runtime.type`)。
- 为路由与 ACP 绑定添加解析器/索引器拆分。

### 第 2 阶段：运行时解析 + Discord/Telegram 一致性

- 解决来自顶级 ``type: "acp"`` 条目的持久化 ACP 绑定，涉及：
  - Discord 频道/线程，
  - Telegram 论坛话题（``chatId:topic:topicId`` 规范 ID）。
- 实现 Telegram 绑定适配器，并确保入站绑定会话覆盖与 Discord 保持一致。
- 本阶段不包含 Telegram 直接/私有话题变体。

### 第 3 阶段：命令一致性和重置

- 使 ``/acp``、``/new``、``/reset`` 和 ``/focus`` 在绑定的 Telegram/Discord 对话中的行为保持一致。
- 确保绑定按配置在重置流程中得以保留。

### 第 4 阶段：加固

- 更好的诊断（``/acp status``、启动对账日志）。
- 冲突处理和健康检查。

## 护栏与策略

- 完全尊重当前的 ACP 启用状态和沙盒限制。
- 保持明确的账户范围（``accountId``）以避免跨账户泄露。
- 路由不明确时失败关闭。
- 根据频道配置明确说明提及/访问策略行为。

## 测试计划

- 单元测试：
  - 对话 ID 标准化（特别是 Telegram 话题 ID），
  - 对账器创建/更新/删除路径，
  - ``/acp bind --persist`` 和解绑流程。
- 集成测试：
  - 入站 Telegram 话题 -> 绑定 ACP 会话解析，
  - 入站 Discord 频道/线程 -> 持久化绑定优先级。
- 回归测试：
  - 临时绑定继续工作，
  - 未绑定频道/话题保持当前路由行为。

## 待决问题

- Telegram 话题中的 ``/acp spawn --thread auto`` 是否应默认为 ``here``？
- 持久化绑定是否应始终绕过绑定对话中的 @提及限制，还是需要显式的 ``requireMention=false``？
- ``/focus`` 是否应将 ``--persist`` 作为 ``/acp bind --persist`` 的别名？

## 发布计划

- 按对话进行可选启用发布（存在 ``bindings[].type="acp"`` 条目）。
- 仅从 Discord + Telegram 开始。
- 添加包含示例的文档，涵盖：
  - “每个代理一个频道/话题”
  - “同一代理的多个频道/话题，具有不同的 ``cwd``"
  - “团队命名模式（``codex-1``, ``claude-repo-x``）”。