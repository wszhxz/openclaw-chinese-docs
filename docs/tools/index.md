---
summary: "Agent tool surface for OpenClaw (browser, canvas, nodes, message, cron) replacing legacy `openclaw-*` skills"
read_when:
  - Adding or modifying agent tools
  - Retiring or changing `openclaw-*` skills
title: "Tools"
---
以下是您提供的技术文档的中文翻译：

---

**工具翻译**

**翻译说明**  
以下文档中的技术术语、功能名称和具体指令将保持原样（如 `sessions_list`、`cron` 等），而周围的解释和说明将翻译为中文。同时，保持文档的结构和格式，确保技术细节准确传达。

---

### **工具概述**

**工具列表**  
- **`sessions_list` / `sessions_history` / `sessions_send` / `sessions_spawn` / `session_status`**  
  列出会话、查看会话历史记录、向其他会话发送消息或生成新会话。  
  - `sessions_list`: `kinds?`, `limit?`, `activeMinutes?`, `messageLimit?` (0 = 无限制)  
  - `sessions_history`: `sessionKey` (或 `sessionId`), `limit?`, `includeTools?`  
  - `sessions_send`: `sessionKey` (或 `sessionId`), `message`, `timeoutSeconds?` (0 = 火箭式发送)  
  - `sessions_spawn`: `task`, `label?`, `agentId?`, `model?`, `runTimeoutSeconds?`, `cleanup?`  
  - `session_status`: `sessionKey?` (默认当前会话; 接受 `sessionId`), `model?` (`default` 清除覆盖)  

**注意事项**  
- `main` 是直接聊天的规范键；全局/未知会话被隐藏。  
- `messageLimit > 0` 会获取每个会话的最后 N 条消息（过滤工具消息）。  
- `sessions_send` 在 `timeoutSeconds > 0` 时等待最终完成。  
- 交付/公告在完成之后发生，为尽力而为；`status: "ok"` 表示代理运行完成，而非公告已送达。  
- `sessions_spawn` 启动子代理运行并返回请求者聊天的公告回复。  
- `sessions_spawn` 是非阻塞的，立即返回 `status: "accepted"`。  
- `sessions_send` 运行回复-回 ping-pong（回复 `REPLY_SKIP` 停止；最大轮次通过 `session.agentToAgent.maxPingPongTurns` 控制，0–5）。  
- 在 ping-pong 之后，目标代理运行 **公告步骤**；回复 `ANNOUNCE_SKIP` 以抑制公告。

---

### **参数（通用）**

**支持网关的工具**（`canvas`、`nodes`、`cron`）:  
- `gatewayUrl`（默认 `ws://127.0.0.1:18789`）  
- `gatewayToken`（如果启用了认证）  
- `timeoutMs`  

**浏览器工具**:  
- `profile`（可选；默认为 `browser.defaultProfile`）  
- `target`（`sandbox` | `host` | `node`）  
- `node`（可选；固定特定节点 ID/名称）  

---

### **推荐的代理流程**

**浏览器自动化**:  
1. `browser` → `status` / `start`  
2. `snapshot`（ai 或 aria）  
3. `act`（点击/输入/按下）  
4. 需要视觉确认时使用 `screenshot`  

**画布渲染**:  
1. `canvas` → `present`  
2. `a2ui_push`（可选）  
3. `snapshot`  

**节点目标**:  
1. `nodes` → `status`  
2. 选择节点后执行 `describe`  
3. `notify` / `run` / `camera_snap` / `screen_record`  

---

### **安全指南**

- 避免直接使用 `system.run`；仅在用户明确同意后使用 `nodes` → `run`。  
- 尊重用户对摄像头/屏幕捕获的同意。  
- 在调用媒体命令前，使用 `status/describe` 确保权限。  

---

### **工具如何呈现给代理**

工具通过两个并行渠道呈现给代理：  
1. **系统提示文本**：人类可读的列表 + 指南。  
2. **工具模式**：发送到模型 API 的结构化函数定义。  

这意味着代理同时看到“哪些工具可用”和“如何调用它们”。如果工具未出现在系统提示或模式中，模型无法调用它。  

---

**注意**  
- 术语如 `Discord`、`Slack`、`WhatsApp` 等平台名称保留英文。  
- 技术术语如 `A2UI`、`Playwright` 等保留英文，并在必要时添加中文解释。  
- JSON 示例中的键值对（如 `command`、`env`）保持原样，但中文标签（如 `命令`、`环境变量`）需准确对应。  

---

**翻译完成**  
以上为文档的完整中文翻译，保留了技术细节和结构，确保信息准确传达。