---
summary: "Microsoft Teams bot support status, capabilities, and configuration"
read_when:
  - Working on MS Teams channel features
title: "Microsoft Teams"
---
以下是您提供的技术文档的中文翻译：

---

**翻译说明**  
本文档详细介绍了如何在 Microsoft Teams 中开发和配置机器人（Bot），涵盖实时消息处理、权限管理、自适应卡片（Adaptive Cards）使用、主动消息发送以及常见问题排查等内容。以下是翻译后的版本：

---

### **实时消息与历史消息处理**  
在 Microsoft Teams 中，机器人可以通过实时消息（通过 Webhook）或历史消息（通过资源特定权限（RSC））与用户交互。  
- **实时消息（Webhook）**：适用于需要即时响应的场景，如聊天机器人。  
- **历史消息（RSC）**：用于访问聊天记录或频道历史消息，需通过资源特定权限（RSC）实现。

---

### **机器人设置**  
1. **权限配置**  
   - **RSC 权限**：需在 Azure AD 中为机器人分配 `ChannelMessage.Read.Group`（团队）或 `ChatMessage.Read.Chat`（群聊）权限。  
   - **Graph API 权限**：若需访问频道历史消息，需启用 `ChannelMessage.Read.All` 权限，并确保管理员已授予资源特定权限（RSC）。  

2. **应用注册**  
   - 在 Azure 门户中注册机器人应用，并获取 `App ID` 和 `App Password`。  
   - 在 Teams 开发者门户中创建应用，并配置 `webApplicationInfo` 信息（包括 `id`、`uri` 等）。  

3. **应用安装**  
   - 将机器人应用安装到团队或频道中，确保用户能够与机器人交互。  
   - 私有频道中机器人支持有限，建议使用标准频道或直接消息（DM）进行交互。

---

### **自适应卡片（Adaptive Cards）**  
- **发送自定义卡片**  
  通过 `message` 工具或 CLI 发送自定义的自适应卡片（Adaptive Card）到用户或频道。  
  - **CLI 示例**：  
    ```bash
    openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello"}]}'
    ```
  - **Agent 工具示例**：  
    ```json
    {
      "action": "send",
      "channel": "msteams",
      "target": "conversation:19:abc...@thread.tacv2",
      "card": {
        "type": "AdaptiveCard",
        "version": "1.5",
        "body": [{"type": "TextBlock", "text": "Hello"}]
      }
    }
    ```

- **投票功能**  
  OpenClaw 通过自适应卡片实现 Teams 投票功能（无原生 API）。  
  - **CLI 命令**：  
    ```bash
    openclaw message poll --channel msteams --target conversation:<id> ...
    ```
  - **投票记录**：投票结果存储在 `~/.openclaw/msteams-polls.json` 中，需保持网关在线以记录投票。

---

### **目标格式（Target Formats）**  
MSTeams 目标使用前缀区分用户和频道：  
| 目标类型       | 格式                          | 示例                                             |
|----------------|-------------------------------|--------------------------------------------------|
| 用户（按 ID）  | `user:<aad-object-id>`        | `user:40a1a0ed-4ff2-4164-a219-55518990c197`     |
| 用户（按名称）  | `user:<display-name>`         | `user:John Smith`（需 Graph API 支持）           |
| 频道/群组      | `conversation:<conversation-id>` | `conversation:19:abc123...@thread.tacv2`         |
| 频道/群组（原始）| `<conversation-id>`           | `19:abc123...@thread.tacv2`（若包含 `@thread`）  |

**CLI 示例**：  
```bash
# 发送消息给用户（按 ID）
openclaw message send --channel msteams --target "user:40a1a0ed-..." --message "Hello"

# 发送消息给用户（按名称，触发 Graph API 查询）
openclaw message send --channel msteams --target "user:John Smith" --message "Hello"

# 发送消息给频道
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" --message "Hello"

# 发送自适应卡片到频道
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello"}]}'
```

---

### **主动消息（Proactive Messaging）**  
- **限制**：主动消息仅在用户首次交互后发送，因需存储对话引用。  
- **配置**：在 `/gateway/configuration` 中设置 `dmPolicy` 和允许列表（allowlist）。

---

### **团队与频道 ID（常见陷阱）**  
- **团队 ID**：从 URL 路径提取，而非 `groupId` 查询参数。  
  - **团队 URL 示例**：  
    ```
    https://teams.microsoft.com/l/team/19%3ABk4j...%40thread.tacv2/conversations?groupId=...
    ```
    - **团队 ID**：`19:Bk4j...@thread.tacv2`（URL 解码后）  
  - **频道 URL 示例**：  
    ```
    https://teams.microsoft.com/l/channel/19%3A15bc...%40thread.tacv2/ChannelName?groupId=...
    ```
    - **频道 ID**：`19:15bc...@thread.tacv2`（URL 解码后）  

---

### **私有频道（Private Channels）**  
- **机器人支持**：  
  | 功能               | 标准频道       | 私有频道         |
  |--------------------|----------------|------------------|
  | 机器人安装         | ✅             | 有限支持         |
  | 实时消息（Webhook） | ✅             | 可能不工作       |
  | RSC 权限           | ✅             | 可能行为不同     |
  | @提及              | ✅             | 若机器人可访问   |
  | Graph API 历史记录  | ✅             | ✅（需权限）     |

- **解决方法**：  
  1. 使用标准频道进行机器人交互。  
  2. 使用 DM（用户可直接消息机器人）。  
  3. 使用 Graph API 访问历史记录（需 `ChannelMessage.Read.All` 权限）。

---

### **常见问题排查**  
1. **频道中图片不显示**：  
   - 缺少 Graph 权限或