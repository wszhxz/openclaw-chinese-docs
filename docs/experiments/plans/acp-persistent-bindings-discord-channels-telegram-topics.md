# Discord 频道与 Telegram 主题的 ACP 持久化绑定

状态：草案

## 概述

引入持久化的 ACP 绑定机制，将以下对象映射至长期存活的 ACP 会话，并将绑定状态存储在顶层的 `bindings[]` 条目中，使用显式的绑定类型：

- Discord 频道（以及必要时已存在的线程），以及  
- 群组/超级群组中的 Telegram 论坛主题（`chatId:topic:topicId`）

此举可使高流量消息通道中的 ACP 使用具备可预测性与持久性，用户因而能够创建专用频道/主题，例如 `codex`、`claude-1` 或 `claude-myrepo`。

## 背景

当前基于线程的 ACP 行为针对临时性的 Discord 线程工作流进行了优化。Telegram 并不具备相同的线程模型；它在群组/超级群组中采用的是论坛主题。用户期望在聊天界面中拥有稳定、始终在线的 ACP“工作区”，而不仅限于临时的线程会话。

## 目标

- 支持以下场景的持久化 ACP 绑定：
  - Discord 频道/线程
  - Telegram 论坛主题（群组/超级群组）
- 使绑定的“唯一可信源”由配置驱动。
- 在 Discord 和 Telegram 上保持 `/acp`、`/new`、`/reset`、`/focus` 及投递行为的一致性。
- 保留现有临时绑定流程，以支持即席使用。

## 非目标

- 对 ACP 运行时/会话内部结构进行彻底重构。
- 移除现有的临时绑定流程。
- 在第一阶段即扩展至所有频道。
- 本阶段不实现 Telegram 频道私信主题（`direct_messages_topic_id`）。
- 本阶段不实现 Telegram 私聊主题变体。

## 用户体验方向

### 1）两种绑定类型

- **持久化绑定**：保存于配置中，启动时执行一致性校验，适用于“命名工作区”类频道/主题。
- **临时绑定**：仅存在于运行时，依据空闲时间/最大存活期策略过期。

### 2）命令行为

- `/acp spawn ... --thread here|auto|off` 命令仍可用。
- 新增显式的绑定生命周期控制命令：
  - `/acp bind [session|agent] [--persist]`
  - `/acp unbind [--persist]`
  - `/acp status` 中包含绑定类型标识：是 `persistent` 还是 `temporary`。
- 在已绑定的对话中，`/new` 和 `/reset` 将就地重置已绑定的 ACP 会话，同时保持绑定关系不变。

### 3）对话身份标识

- 使用标准对话 ID：
  - Discord：频道/线程 ID。
  - Telegram 主题：`chatId:topic:topicId`。
- Telegram 绑定绝不可仅以裸主题 ID 作为键。

## 配置模型（建议方案）

在顶层 `bindings[]` 中统一路由与持久化 ACP 绑定配置，并通过显式的 `type` 类型区分符进行识别：

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

### 最小示例（无每绑定 ACP 覆盖项）

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

说明：

- `bindings[].type` 显式声明：
  - `route`：常规代理路由。
  - `acp`：对匹配对话启用持久化 ACP 执行环境绑定。
- 对于 `type: "acp"`，`match.peer.id` 是标准对话键：
  - Discord 频道/线程：原始频道/线程 ID。
  - Telegram 主题：`chatId:topic:topicId`。
- `bindings[].acp.backend` 为可选项。后端回退顺序如下：
  1. `bindings[].acp.backend`
  2. `agents.list[].runtime.acp.backend`
  3. 全局 `acp.backend`
- `mode`、`cwd` 与 `label` 遵循相同的覆盖模式（`binding override -> agent runtime default -> global/default behavior`）。
- 保留现有 `session.threadBindings.*` 与 `channels.discord.threadBindings.*`，用于临时绑定策略。
- 持久化条目声明期望状态；运行时负责将其与实际 ACP 会话/绑定达成一致。
- 每个对话节点仅允许存在一个活跃的 ACP 绑定，此为预期模型。
- 向后兼容性：缺失 `type` 的旧条目将被解释为 `route`。

## 后端选择

- ACP 会话初始化已在启动过程中使用配置的后端选择（当前为 `acp.backend`）。
- 本提案将启动/一致性校验逻辑扩展为优先采用带类型的 ACP 绑定覆盖项：
  - `bindings[].acp.backend`：用于对话级覆盖。
  - `agents.list[].runtime.acp.backend`：用于每代理默认值。
- 若无覆盖项，则维持当前行为（默认为 `acp.backend`）。

## 在当前系统中的架构适配

### 复用现有组件

- `SessionBindingService` 已支持与频道无关的对话引用。
- ACP 启动/绑定流程已支持通过服务 API 实现绑定。
- Telegram 已通过 `MessageThreadId` 和 `chatId` 携带主题/线程上下文。

### 新增/扩展组件

- **Telegram 绑定适配器**（与 Discord 适配器并行）：
  - 按 Telegram 账户注册适配器，
  - 依据标准对话 ID 执行注册、列举、绑定、解绑及刷新操作。
- **带类型绑定解析器/索引器**：
  - 将 `bindings[]` 拆分为 `route` 与 `acp` 视图，
  - 仅对 `route` 绑定保留 `resolveAgentRoute`，
  - 仅从 `acp` 绑定中解析持久化 ACP 意图。
- **Telegram 的入站绑定解析**：
  - 在路由最终确定前解析已绑定会话（Discord 当前已实现此功能）。
- **持久化绑定一致性校验器**：
  - 启动时：加载配置的顶层 `type: "acp"` 绑定，确保 ACP 会话存在，确保绑定关系存在。
  - 配置变更时：安全应用增量更新。
- **切换模型**：
  - 不读取任何频道级 ACP 绑定回退项，
  - 持久化 ACP 绑定仅源自顶层 `bindings[].type="acp"` 条目。

## 分阶段交付

### 第一阶段：带类型绑定模式基础

- 扩展配置模式以支持 `bindings[].type` 类型区分符：
  - `route`，
  - `acp`，含可选的 `acp` 覆盖对象（`mode`、`backend`、`cwd`、`label`）。
- 在代理模式中扩展运行时描述符，以标记原生支持 ACP 的代理（`agents.list[].runtime.type`）。
- 增加解析器/索引器拆分，分别处理路由绑定与 ACP 绑定。

### 第二阶段：运行时解析 + Discord/Telegram 功能对齐

- 从顶层 ``type: "acp"`` 条目解析持久化的 ACP 绑定，适用于以下场景：
  - Discord 频道/主题，
  - Telegram 论坛话题（使用 ``chatId:topic:topicId`` 规范 ID）。
- 实现 Telegram 绑定适配器，并使入站已绑定会话的覆盖行为与 Discord 保持一致。
- 本阶段不包含 Telegram 直接/私有话题变体。

### 第三阶段：命令功能对齐与重置支持

- 在已绑定的 Telegram/Discord 对话中，统一 ``/acp``、``/new``、``/reset`` 和 ``/focus`` 的行为。
- 确保绑定在按配置执行的重置流程中仍能持续生效。

### 第四阶段：加固

- 提升诊断能力（``/acp status``、启动时的一致性校验日志）。
- 增强冲突处理机制与健康检查。

## 安全护栏与策略

- 严格遵循当前的 ACP 启用状态和沙箱限制。
- 保留显式的账号作用域控制（``accountId``），以避免跨账号数据泄露。
- 在路由不明确时采用“默认拒绝”策略（fail closed）。
- 每个频道的提及/访问策略行为需在频道配置中明确声明。

## 测试计划

- 单元测试：
  - 对话 ID 标准化（尤其是 Telegram 话题 ID），
  - 协调器（reconciler）的创建/更新/删除路径，
  - ``/acp bind --persist`` 及解绑流程。
- 集成测试：
  - 入站 Telegram 话题 → 已绑定 ACP 会话解析，
  - 入站 Discord 频道/主题 → 持久化绑定优先级。
- 回归测试：
  - 临时绑定继续正常工作，
  - 未绑定的频道/话题维持当前的路由行为。

## 待解决问题

- Telegram 话题中的 ``/acp spawn --thread auto`` 是否应默认设为 ``here``？
- 持久化绑定是否应在已绑定对话中始终绕过提及门控（mention-gating），还是必须显式启用 ``requireMention=false``？
- ``/focus`` 是否应将 ``--persist`` 作为 ``/acp bind --persist`` 的别名？

## 发布计划

- 以每对话为单位按需启用（仅当存在 ``bindings[].type="acp"`` 条目时生效）。
- 初始仅支持 Discord 和 Telegram。
- 补充文档并附带示例，涵盖以下场景：
  - “每个智能体对应一个频道/话题”，
  - “同一智能体对应多个频道/话题，但配置不同的 ``cwd``”，
  - “团队命名模式（``codex-1``、``claude-repo-x``）”。