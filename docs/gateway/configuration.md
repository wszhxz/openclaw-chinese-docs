---
summary: "All configuration options for ~/.openclaw/openclaw.json with examples"
read_when:
  - Adding or modifying config fields
title: "Configuration"
---

# 配置 🔧

OpenClaw 从 `~/.openclaw/openclaw.json` 读取一个可选的 **JSON5** 配置（允许注释 + 尾随逗号）。

如果文件缺失，OpenClaw 使用安全的默认值（嵌入式 Pi 代理 + 每发送者会话 + 工作区 `~/.openclaw/workspace`）。通常您只需要配置来：

- 限制谁能触发机器人（`channels.whatsapp.allowFrom`、`channels.telegram.allowFrom` 等）
- 控制群组允许列表 + 提及行为（`channels.whatsapp.groups`、`channels.telegram.groups`、`channels.discord.guilds`、`agents.list[].groupChat`）
- 自定义消息前缀（`messages`）
- 设置代理的工作区（`agents.defaults.workspace` 或 `agents.list[].workspace`）
- 调整嵌入式代理默认值（`agents.defaults`）和会话行为（`session`）
- 设置每个代理的身份（`agents.list[].identity`）

> **初次配置？** 查看 [配置示例](/gateway/configuration-examples) 指南，了解带有详细说明的完整示例！

## 严格的配置验证

OpenClaw 只接受完全匹配模式的配置。
未知键、格式错误的类型或无效值会导致网关**拒绝启动**以确保安全。

当验证失败时：

- 网关不会启动。
- 会显示验证错误消息。
- 您需要修复配置文件中的问题后才能启动网关。

验证失败的常见原因：

- 拼写错误的配置键
- 错误的数据类型（例如字符串而非数字）
- 无效的值
- 缺少必需的配置项

要修复验证错误：

1. 检查错误消息以了解具体问题
2. 验证配置文件的语法（JSON5 格式）
3. 检查键名拼写
4. 确认值的数据类型

## 配置文件位置

配置文件位于 `~/.openclaw/openclaw.json`。如果文件不存在，OpenClaw 将使用默认值。

您可以通过以下方式创建配置文件：

```json
{
  // 您的配置选项
}
```

## 配置热重载

大多数配置更改需要重启 OpenClaw 才能生效。
某些配置（如日志级别）支持热重载。

## 安全注意事项

配置文件可能包含敏感信息，如 API 密钥。
确保配置文件的权限设置适当，防止未授权访问。

## 常见配置示例

基本配置：

```json
{
  "logging": {
    "level": "info"
  }
}
```

通道配置：

```json
{
  "channels": {
    "whatsapp": {
      "allowFrom": ["+1234567890"]
    }
  }
}
```

代理配置：

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.openclaw/workspace"
    }
  }
}
```

## 故障排除

如果配置无效：

1. 检查 JSON 语法
2. 验证键名拼写
3. 确认值的数据类型
4. 参考文档中的有效选项

更多配置示例，请参阅 [配置示例](/gateway/configuration-examples) 页面。