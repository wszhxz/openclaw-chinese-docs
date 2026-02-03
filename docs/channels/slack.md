---
summary: "Slack setup for socket or HTTP webhook mode"
read_when: "Setting up Slack or debugging Slack socket/HTTP mode"
title: "Slack"
---
以下是您提供的技术文档的中文翻译：

---

**Slack 集成配置指南**

**翻译说明**  
本文档详细介绍了如何配置和使用 Slack 与聊天机器人或 AI 助手的集成，涵盖各种设置、安全措施、工具操作等内容。以下是翻译后的中文版本：

---

### **翻译内容**

**1. 传输控制**  
- **出站文本**：按 `channels.slack.textChunkLimit`（默认 4000）进行分块。  
- **换行分块**：设置 `channels.slack.chunkMode="newline"` 以在长度分块前按空白行（段落边界）分割。  
- **媒体上传**：受 `channels.slack.mediaMaxMb`（默认 20）限制。

**2. 回复线程控制**  
默认情况下，OpenClaw 在主频道回复。使用 `channels.slack.replyToMode` 控制自动线程行为：

| 模式 | 行为 |  
|------|------|  
| `off` | **默认**。在主频道回复。仅在触发消息本身已处于线程时进行线程回复。 |  
| `first` | 第一次回复在线程（在触发消息下方），后续回复在主频道。适用于保持上下文可见性同时避免线程混乱。 |  
| `all` | 所有回复均在线程中。保持对话集中，但可能降低可见性。 |  

该模式适用于自动回复和代理工具调用（`slack sendMessage`）。

**3. 按聊天类型配置线程**  
可通过 `channels.slack.replyToModeByChatType` 为不同聊天类型设置不同的线程行为：

```json5
{
  channels: {
    slack: {
      replyToMode: "off", // 默认用于频道
      replyToModeByChatType: {
        direct: "all", // DMs 始终线程
        group: "first", // 群组 DMs/MPIM 首次回复线程
      },
    },
  }
}
```

**支持的聊天类型**：  
- `direct`：1:1 DMs（Slack `im`）  
- `group`：群组 DMs / MPIMs（Slack `mpim`）  
- `channel`：标准频道（公开/私有）  

**优先级**：  
1. `replyToModeByChatType.<chatType>`  
2. `replyToMode`  
3. 提供商默认值（`off`）  

**遗留配置**：`channels.slack.dm.replyToMode` 仍作为 `direct` 的备用设置（当未设置聊天类型覆盖时）。

**示例**：  
- **仅线程 DMs**：  
```json5
{
  channels: {
    slack: {
      replyToMode: "off",
      replyToModeByChatType: { direct: "all" },
    },
  }
}
```

- **线程群组 DMs 但保持频道在根**：  
```json5
{
  channels: {
    slack: {
    replyToMode: "off",
    replyToModeByChatType: { group: "first" },
    }
  }
}
```

- **线程频道，保持 DMs 在根**：  
```json5
{
  channels: {
    slack: {
    replyToMode: "first",
    replyToModeByChatType: { direct: "off", group: "off" },
    }
  }
}
```

**4. 手动线程标签**  
通过代理响应中的标签进行精细控制：  
- `[[reply_to_current]]` — 回复触发消息（开始/继续线程）。  
- `[[reply_to:<id>]]` — 回复特定消息 ID。

**5. 会话 + 路由**  
- DMs 共享 `main` 会话（类似 WhatsApp/Telegram）。  
- 频道映射到 `agent:<agentId>:slack:channel:<channelId>` 会话。  
- Slash 命令使用 `agent:<agentId>:slack:slash:<userId>` 会话（前缀可通过 `channels.slack.slashCommand.sessionPrefix` 配置）。  
- 如果 Slack 未提供 `channel_type`，OpenClaw 会根据频道 ID 前缀（`D`、`C`、`G`）推断类型，默认为 `channel` 以保持会话键稳定。  
- 原生命令注册使用 `commands.native`（全局默认 `"auto"` → Slack 关闭），可通过 `channels.slack.commands.native` 按工作区覆盖。文本命令需要独立的 `/...` 消息，可通过 `commands.text: false` 禁用。Slack Slash 命令在 Slack 应用中管理，不会自动移除。使用 `commands.useAccessGroups: false` 跳过命令的访问组检查。  
- 完整命令列表 + 配置：[Slash 命令](/tools/slash-commands)

**6. DM 安全性（配对）**  
- 默认：`channels.slack.dm.policy="pairing"` — 未知 DM 发送者会收到配对码（1 小时后过期）。  
- 审批方式：`openclaw pairing approve slack <code>`。  
- 允许任何人：设置 `channels.slack.dm.policy="open"` 并 `channels.slack.dm.allowFrom=["*"]`。  
- `channels.slack.dm.allowFrom` 可接受用户 ID、@ 处理或电子邮件（在令牌允许时启动时解析）。向导接受用户名并在设置时解析为 ID（当令牌允许时）。

**7. 群组策略**  
- `channels.slack.groupPolicy` 控制频道处理（`open|disabled|allowlist`）。  
- `allowlist` 要求频道列在 `channels.slack.channels` 中。  
- 如果仅设置 `SLACK_BOT_TOKEN`/`SLACK_APP_TOKEN` 且未创建 `channels.slack` 部分，运行时默认 `groupPolicy` 为 `open`。添加 `channels.slack.groupPolicy`、`channels.defaults.groupPolicy` 或频道白名单以锁定。  
- 配置向导接受 `#channel` 名称并解析为 ID（公开 + 私有）；如果存在多个匹配项，优先选择活动频道。  
- 启动时，OpenClaw 会解析允许列表中的频道/用户名称为 ID（当令牌允许时），并记录映射；未解析的条目保持原样。  
- 若要允许 **无频道**，设置 `channels.slack.groupPolicy: "disabled"`（或保持空白名单）。

**频道选项**（`channels.slack.channels.<id>` 或 `channels.slack.channels.<name>`）：  
- `allow`：在 `groupPolicy="allowlist"` 时允许/拒绝频道。  
- `requireMention`：频道的提及限制。  
- `tools`：可选的频道级工具策略覆盖（`allow`/`deny`/`alsoAllow`）。  
- `toolsBySender`：可选的频道内发送者级工具策略覆盖（键为发送者 ID/@ 处理/电子邮件