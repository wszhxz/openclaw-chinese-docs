---
summary: "Discord bot support status, capabilities, and configuration"
read_when:
  - Working on Discord channel features
title: "Discord"
---
以下是关于使用 OpenClaw 配置 Discord 机器人的详细文档翻译：

---

### **配置选项**
1. **环境变量**  
   优先使用 `DISCORD_BOT_TOKEN` 环境变量设置机器人令牌。  
   示例：  
   ```bash
   export DISCORD_BOT_TOKEN="your_token_here"
   ```

2. **配置文件**  
   在 `config.yaml` 或 `config.json` 中指定令牌：  
   ```yaml
   discord:
     token: "your_token_here"
   ```

---

### **权限与安全**
- **令牌保护**  
  将机器人令牌视为密码，建议在受监督的主机上使用 `DISCORD_BOT_TOKEN` 环境变量，或限制配置文件的权限。  
- **权限最小化**  
  仅授予机器人所需的权限（通常为“读取/发送消息”）。  
- **故障处理**  
  若机器人卡顿或因速率限制无法响应，重启网关（`openclaw gateway --force`），并确认无其他进程占用 Discord 会话。

---

### **PluralKit (PK) 支持**
启用 PK 解析以处理代理消息，使系统成员显示为独立发送者。  
配置示例：  
```yaml
discord:
  pluralkit:
    enabled: true
    token: "pk_live_..."  # 可选，私有系统需提供
```

**允许列表注意事项（启用 PK 后）：**  
- 使用 `pk:<memberId>` 格式在 `dm.allowFrom`、`guilds.<id>.users` 或频道允许列表中指定成员。  
- 显示名称可通过名称/标识符匹配。  
- PK API 仅在 30 分钟内解析原始 Discord 消息 ID（预代理消息）。  
- 若 PK 解析失败（如私有系统无令牌），代理消息将被视为机器人消息，除非 `channels.discord.allowBots=true`。

---

### **工具动作默认值**
| 动作组       | 默认值  | 说明                              |
|------------|--------|---------------------------------|
| 反馈         | 启用    | 添加/列出反馈 + 列表反馈 + 表情符号列表 |
| 表情贴纸     | 启用    | 发送表情贴纸                      |
| 表情上传     | 启用    | 上传表情符号                      |
| 贴纸上传     | 启用    | 上传贴纸                         |
| 投票         | 启用    | 创建投票                         |
| 权限         | 启用    | 渠道权限快照                      |
| 消息         | 启用    | 读取/发送/编辑/删除                |
| 线程         | 启用    | 创建/列出/回复                    |
| 固定消息     | 启用    | 固定/取消固定/列出                |
| 搜索         | 启用    | 消息搜索（预览功能）               |
| 成员信息     | 启用    | 成员信息                         |
| 角色信息     | 启用    | 角色列表                         |
| 渠道信息     | 启用    | 渠道信息 + 列表                   |
| 渠道管理     | 启用    | 渠道/分类管理 + 权限               |
| 角色         | 禁用    | 角色添加/移除                     |
| 管理         | 禁用    | 超时/踢出/封禁                   |

---

### **回复标签**
模型可通过输出中的标签请求线程回复：  
- `[[reply_to_current]]` — 回复触发 Discord 消息。  
- `[[reply_to:<id>]]` — 回复特定消息 ID（来自上下文/历史）。  

行为由 `channels.discord.replyToMode` 控制：  
- `off`：忽略标签。  
- `first`：仅第一个输出块/附件为回复。  
- `all`：所有输出块/附件均为回复。

---

### **工具动作**
代理可调用 `discord` 的动作包括：  
- `react` / `reactions`（添加/列出反馈）  
- `sticker`, `poll`, `permissions`  
- `readMessages`, `sendMessage`, `editMessage`, `deleteMessage`  
- 搜索/固定工具负载包含标准化的 `timestampMs`（UTC 时间戳）和 `timestampUtc`，与原始 Discord 时间戳同步。  
- `threadCreate`, `threadList`, `threadReply`  
- `pinMessage`, `unpinMessage`, `listPins`  
- `searchMessages`, `memberInfo`, `roleInfo`, `roleAdd`, `roleRemove`, `emojiList`  
- `channelInfo`, `channelList`, `voiceStatus`, `eventList`, `eventCreate`  
- `timeout`, `kick`, `ban`  

Discord 消息 ID 会通过注入上下文（`[discord message id: …]` 和历史记录行）提供，以便代理定位目标消息。表情符号可为 Unicode（如 `✅`）或自定义表情符号语法（如 `<:party_blob:1234567890>`）。

---

### **安全与运维**
- **令牌保护**  
  将机器人令牌视为密码，建议在受监督的主机上使用 `DISCORD_BOT_TOKEN` 环境变量，或限制配置文件权限。  
- **权限最小化**  
  仅授予机器人所需的权限（通常为“读取/发送消息”）。  
- **故障处理**  
  若机器人卡顿或因速率限制无法响应，重启网关（`openclaw gateway --force`），并确认无其他进程占用 Discord 会话。

---

### **配置助手说明**
- **允许列表匹配**  
  `allowFrom`/`users`/`groupChannels` 支持 ID、名称、标签或提及（如 `<@id>`）。  
  - 前缀如 `discord:`/`user:`（用户）和 `channel:`（群 DM）支持。  
  - 使用 `*` 允许任意发送者/频道。  
  - 若 `guilds.<id>.channels` 存在，未列出的频道默认被拒绝。  
  - 若 `guilds.<id>.channels` 未指定，允许列表中的所有频道均被允许。  
  - 若要完全禁止频道，设置 `channels.discord.groupPolicy: "disabled"`（或保留空允许列表）。  
- **名称解析**  
  配置助手支持 `Guild/Channel` 名称（公开 + 私有），并尝试解析为 ID（若机器人可搜索成员）。  
  启动时，OpenClaw 会解析允许列表中的频道/用户名称为 ID（若机器人可搜索成员），并记录映射；未解析的条目保留原样。

---

### **原生命令**
- **命令映射**  
  注册的命令与 OpenClaw 的聊天命令一致。  
- **权限控制**  
  原生命令遵循与 DM/guild 消息相同的允许列表（`channels.discord.dm.allowFrom`、`channels.discord.guilds`、频道规则）。  
- **UI 显示**  
  未允许列表的用户仍可能在 Discord UI 中看到 Slash 命令，但 OpenClaw 会在执行时强制权限检查，并回复“未授权”。

---

### **总结**
通过以上配置，您可以安全高效地部署 Discord 机器人，利用 OpenClaw 的功能实现复杂交互。确保遵循安全最佳实践，并根据需求调整工具动作和允许列表。