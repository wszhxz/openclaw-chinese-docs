---
summary: "All configuration options for ~/.openclaw/openclaw.json with examples"
read_when:
  - Adding or modifying config fields
title: "Configuration"
---
以下是您提供的技术文档的中文翻译，保持了原文的结构和术语准确性：

---

# 翻译设置

## `translation`（翻译设置）

- `enabled`: 启用翻译功能（默认为 `true`）
- `targetLanguage`: 目标语言（例如 `zh` 表示中文）
- `fallbackLanguage`: 默认语言（若目标语言不可用时使用）
- `preserveFormatting`: 保留原始格式（如代码块、表格等）

```json
{
  "translation": {
    "enabled": true,
    "targetLanguage": "zh",
    "fallbackLanguage": "en",
    "preserveFormatting": true
  }
}
```

---

## `canvasHost`（LAN/尾网 Canvas 文件服务器 + 实时重载）

Gateway 通过 HTTP 提供 HTML/CSS/JS 目录，使 iOS/Android 节点可通过 `canvas.navigate` 访问。

默认根目录：`~/.openclaw/workspace/canvas`  
默认端口：`18793`（避开 openclaw 浏览器 CDP 端口 `18792`）  
服务器监听 **网关绑定主机**（LAN 或 Tailnet），以便节点访问。

服务器功能：
- 提供 `canvasHost.root` 下的文件
- 向服务的 HTML 注入微型实时重载客户端
- 监控目录并在 `/__openclaw__/ws` WebSocket 端点广播重载
- 若目录为空，自动创建初始 `index.html`（立即显示内容）
- 同时提供 A2UI 于 `/__openclaw__/a2ui/`，并作为 `canvasHostUrl` 广告给节点（始终用于 Canvas/A2UI）

若目录过大或遇到 `EMFILE` 错误，禁用实时重载（及文件监控）：
- 配置：`canvasHost: { liveReload: false }`

```json
{
  "canvasHost": {
    "root": "~/.openclaw/workspace/canvas",
    "port": 18793,
    "liveReload": true
  }
}
```

更改 `canvasHost.*` 需重启网关（配置重载将重启）。

禁用方法：
- 配置：`canvasHost: { enabled: false }`
- 环境变量：`OPENCLAW_SKIP_CANVAS_HOST=1`

---

## `bridge`（旧版 TCP 桥接，已移除）

当前构建不再包含 TCP 桥接监听器；`bridge.*` 配置键被忽略。节点通过网关 WebSocket 连接。此部分仅保留历史参考。

旧版行为：
- 网关可为节点（iOS/Android）提供简单 TCP 桥接，通常在端口 `18790`。

默认设置：
- 启用：`true`
- 端口：`18790`
- 绑定：`lan`（绑定到 `0.0.0.0`）

绑定模式：
- `lan`: `0.0.0.0`（任何接口均可访问，包括 LAN/Wi-Fi 和 Tailscale）
- `tailnet`: 仅绑定到机器的 Tailscale IP（推荐用于维也纳 ⇄ 伦敦）
- `loopback`: `12.7.0.1`（仅本地）
- `auto`: 优先使用 Tailnet IP（若存在），否则使用 `lan`

TLS：
- `bridge.tls.enabled`: 启用桥接连接的 TLS（启用时仅 TLS）
- `bridge.tls.autoGenerate`: 无证书/密钥时生成自签名证书（默认：true）
- `bridge.tls.certPath` / `bridge.tls.keyPath`: 桥接证书及私钥的 PEM 路径
- `bridge.tls.caPath`: 可选 PEM CA 捆绑包（自定义根证书或未来 mTLS）

启用 TLS 时，网关在发现 TXT 记录中广告 `bridgeTls=1` 和 `bridgeTlsSha256`，以便节点固定证书。手动连接若无指纹存储则使用首次信任。自动生成证书需 `openssl` 在 PATH 中；若生成失败，桥接将无法启动。

```json
{
  "bridge": {
    "enabled": true,
    "port": 18790,
    "bind": "tailnet",
    "tls": {
      "enabled": true,
      // 未指定时使用 ~/.openclaw/bridge/tls/bridge-{cert,key}.pem
      // "certPath": "~/.openclaw/bridge/tls/bridge-cert.pem",
      // "keyPath": "~/.openclaw/bridge/tls/bridge-key.pem"
    }
  }
}
```

---

## `discovery.mdns`（Bonjour / mDNS 广播模式）

控制 LAN mDNS 发现广播（`_openclaw-gw._tcp`）。

- `minimal`（默认）：从 TXT 记录中省略 `cliPath` + `sshPort`
- `full`: 在 TXT 记录中包含 `cliPath` + `sshPort`
- `off`: 完全禁用 mDNS 广播
- 主机名：默认为 `openclaw`（广告 `openclaw.local`）。通过 `OPENCLAW_MDNS_HOSTNAME` 覆盖。

```json
{
  "discovery": { "mdns": { "mode": "minimal" } }
}
```

---

## `discovery.wideArea`（广域 Bonjour / 单播 DNS-SD）

启用时，网关在 `~/.openclaw/dns/` 下为 `_openclaw-gw._tcp` 写入单播 DNS-SD 区域，使用配置的发现域（示例：`openclaw.internal.`）。

为使 iOS/Android 跨网络发现（维也纳 ⇄ 伦敦），需配合：
- 网关主机上的 DNS 服务器提供您选择的域（推荐 CoreDNS）
- Tailscale **分割 DNS** 使客户端通过网关 DNS 服务器解析该域

一次性设置辅助（网关主机）：

```bash
openclaw dns setup --apply
```

```json
{
  "discovery": { "wideArea": { "enabled": true } }
}
```

---

## 模板变量

模板占位符在 `tools.media.*.models[].args` 和 `tools.media.models[].args`（及未来所有模板化参数字段）中展开。

| 变量           | 描述                                                                     |
|------------------|------------------------------------------------------------------------------- | -------- | ------- | ---------- | ----- | ------ | -------- | ------- | ------- | --- |
| `{{Body}}`         | 全部入站消息正文                                                       |
| `{{RawBody}}`      | 原始入站消息正文（无历史/发送者包装；适合命令解析）                     |
| `{{BodyStripped}}` |