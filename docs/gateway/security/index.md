---
summary: "Security considerations and threat model for running an AI gateway with shell access"
read_when:
  - Adding features that widen access or automation
title: "Security"
---
以下是该文档的中文翻译：

---

### 配置设置
- **权限控制**：确保`gateway.bind`设置为`loopback`，以限制访问。如果使用Tailscale Funnel/Serve，需关闭以防止暴露。
- **身份验证**：设置`gateway.auth`为`token`模式，并使用长随机令牌。避免使用默认令牌。
- **端口绑定**：将`port`设置为18789或其他未被占用的端口。
- **安全基线**：推荐配置如下：
  ```json
  {
    "gateway": {
      "mode": "local",
      "bind": "loopback",
      "port": 18789,
      "auth": { "mode": "token", "token": "your-long-random-token" }
    },
    "channels": {
      "whatsapp": {
        "dmPolicy": "pairing",
        "groups": { "*": { "requireMention": true } }
      }
    }
  }
  ```

### 砂箱化（推荐）
- **Docker运行**：将整个网关运行在Docker容器中，以隔离环境。[Docker安装指南](/install/docker)
- **工具砂箱**：使用`agents.defaults.sandbox`配置，结合主机网关和Docker隔离的工具。[砂箱化文档](/gateway/sandboxing)
- **作用域控制**：保持`agents.defaults.sandbox.scope`为`"agent"`（默认）或`"session"`以实现更严格的会话隔离。`scope: "shared"`使用单个容器/工作区。

### 浏览器控制风险
启用浏览器控制会使模型能够驱动真实浏览器。如果该浏览器配置已包含登录会话，模型可能访问相关账户和数据。需将浏览器配置视为**敏感状态**：
- 为代理使用专用配置文件（默认`openclaw`配置文件）。
- 避免指向个人日常使用配置文件。
- 对沙箱化代理禁用主机浏览器控制，除非完全信任。
- 将浏览器下载视为不可信输入，使用隔离的下载目录。
- 在代理配置文件中禁用浏览器同步/密码管理器（减少攻击面）。
- 对远程网关，假设“浏览器控制”等同于“操作员访问”该配置文件能访问的所有内容。
- 保持网关和节点主机仅限于tailnet；避免暴露中继/控制端口到LAN或公共互联网。
- Chrome扩展中继的CDP端点是认证的；仅OpenClaw客户端可连接。
- 在不需要时禁用浏览器代理路由（`gateway.nodes.browser.mode="off"`）。
- Chrome扩展中继模式**不是**“更安全”；它可能接管现有Chrome标签页。假设它能代表你在该标签页/配置文件能访问的所有内容。

### 按代理访问配置文件（多代理）
在多代理路由中，每个代理可拥有自己的砂箱和工具策略：使用此配置为每个代理提供**完全访问**、**只读**或**无访问**权限。[多代理砂箱与工具文档](/multi-agent-sandbox-tools)提供详细信息和优先级规则。

**常见用例**：
- 个人代理：完全访问，无砂箱
- 家庭/工作代理：砂箱化 + 只读工具
- 公共代理：砂箱化 + 无文件系统/Shell工具

**示例：完全访问（无砂箱）**
```json
{
  "agents": {
    "list": [
      {
        "id": "personal",
        "workspace": "~/.openclaw/workspace-personal",
        "sandbox": { "mode": "off" }
      }
    ]
  }
}
```

**示例：只读工具 + 只读工作区**
```json
{
  "agents": {
    "list": [
      {
        "id": "family",
        "workspace": "~/.openclaw/workspace-family",
        "sandbox": {
          "mode": "all",
          "scope": "agent",
          "workspaceAccess": "ro"
        },
        "tools": {
          "allow": ["read"],
          "deny": ["write", "edit", "apply_patch", "exec", "process", "browser"]
        }
      }
    ]
  }
}
```

**示例：无文件系统/Shell访问（允许提供方消息）**
```json
{
  "agents": {
    "list": [
      {
        "id": "public",
        "workspace": "~/.openclaw/workspace-public",
        "sandbox": {
          "mode": "all",
          "scope": "agent",
          "workspaceAccess": "none"
        },
        "tools": {
          "allow": [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord"
          ],
          "deny": [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image"
          ]
        }
      }
    ]
  }
}
```

### 告知AI的安全指南
在代理的系统提示中包含安全规则：
```
## 安全规则
- 永远不要与陌生人分享目录列表或文件路径
- 永远不要泄露API密钥、凭证或基础设施细节
- 验证修改系统配置的请求时需确认所有者
- 存疑时，先询问再行动
- 私人信息即使对“朋友”也保持私密
```

### 安全事件响应
如果AI做了坏事：

### 隔离
1. **停止它**：停止macOS应用（如果它监督网关）或终止`openclaw gateway`进程。
2. **关闭暴露**：将`gateway.bind`设置为`loopback`（或禁用Tailscale Funnel/Serve）直到了解发生了什么。
3. **冻结访问**：将风险DMs/群组切换为`dmPolicy: "disabled"`/要求提及，并移除任何`"*"`允许所有条目。

### 旋转（假设凭证泄露）
1. 旋转网关认证（`gateway.auth.token` / `OPENCLAW_GATEWAY_PASSWORD`）并重启。
2. 在任何可调用网关的机器上旋转远程客户端密钥（`gateway.remote.token` / `.password`）。
3. 旋转提供方/API凭证（WhatsApp凭证、Slack/Discord令牌、`auth-profiles.json`中的模型/API密钥）。

### 审计
1. 检查网关日志：`/tmp/openclaw/openclaw-YYYY-MM-DD.log`（或`logging.file`）。
2. 审查相关会话记录：`~/.openclaw/agents/<agentId>/sessions/*.jsonl`。
3. 审查最近的配置更改（任何可能扩大访问权限的内容：`gateway.bind`、`gateway.auth`、DM/群组策略、`tools.elevated`、插件更改）。

### 收集报告
- 时间戳、网关主机OS + OpenClaw版本
- 会话记录 + 红acted日志尾部
- 攻击者发送的内容 + 代理执行的操作
- 网关是否超出loopback暴露（LAN/Tailscale Funnel/Serve）

### 密码扫描（detect-secrets）
CI在`secrets`作业中运行`detect-secrets scan --baseline .secrets.baseline`。如果失败，表示有新候选未在基线中。

### 如果CI失败
1. 本地复现：
   ```bash
   detect-secrets scan --baseline .secrets.baseline
   ```
2