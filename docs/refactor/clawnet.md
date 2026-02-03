---
summary: "Clawnet refactor: unify network protocol, roles, auth, approvals, identity"
read_when:
  - Planning a unified network protocol for nodes + operator clients
  - Reworking approvals, pairing, TLS, and presence across devices
title: "Clawnet Refactor"
---
# Clawnet重构（协议+认证统一）

## 你好

你好Peter——很好的方向；这将解锁更简单的用户体验+更强的安全性。

## 目的

单一、严谨的文档用于：

- 当前状态：协议、流程、信任边界。
- 痛点：审批、多跳路由、UI重复。
- 提议的新状态：单一协议、范围角色、统一认证/配对、TLS固定。
- 身份模型：稳定ID + 可爱slug。
- 迁移计划、风险、开放问题。

## 目标（讨论中）

- 为所有客户端（mac应用、CLI、iOS、Android、无头节点）使用单一协议。
- 每个网络参与者均需认证+配对。
- 角色清晰：节点 vs 操作者。
- 中央审批路由至用户所在位置。
- 所有远程流量均使用TLS加密+可选固定。
- 最小化代码重复。
- 单一机器应仅出现一次（无UI/节点重复条目）。

## 非目标（明确）

- 移除能力分离（仍需最小权限）。
- 暴露完整网关控制平面而无范围检查。
- 认证依赖人类标签（slug保持非安全）。

---

# 当前状态（原样）

## 两个协议

### 1) 网关WebSocket（控制平面）

- 完整API表面积：配置、通道、模型、会话、代理运行、日志、节点等。
- 默认绑定：环回。远程访问通过SSH/Tailscale。
- 认证：通过`connect`使用令牌/密码。
- 无TLS固定（依赖环回/隧道）。
- 代码：
  - `src/gateway/server/ws-connection/message-handler.ts`
  - `src/gateway/client.ts`
  - `docs/gateway/protocol.md`

### 2) 桥接（节点传输）

- 狭窄允许列表表面积，节点身份+配对。
- TCP上的JSONL；可选TLS+证书指纹固定。
- TLS在发现TXT中广播指纹。
- 代码：
  - `src/infra/bridge/server/connection.ts`
  - `src/gateway/server-bridge.ts`
  - `src/node-host/bridge-client.ts`
  - `docs/gateway/bridge-protocol.md`

## 当前控制平面客户端

- CLI → 网关WS通过`callGateway`（`src/gateway/call.ts`）。
- macOS应用UI → 网关WS（`GatewayConnection`）。
- Web控制UI → 网关WS。
- ACP → 网关WS。
- 浏览器控制使用其自身的HTTP控制服务器。

## 当前节点

- macOS应用在节点模式连接到网关桥接（`MacNodeBridgeSession`）。
- iOS/Android应用连接到网关桥接。
- 配对+每节点令牌存储在网关。

## 当前审批流程（执行）

- 代理通过`system.run`使用网关。
- 网关通过桥接调用节点。
- 节点运行时决定审批。
- macOS应用显示UI提示（当节点==mac应用时）。
- 节点返回`invoke-res`给网关。
- 多跳，UI绑定到节点主机。

## 存在性+身份（当前）

- 网关存在性条目来自WS客户端。
- 节点存在性条目来自桥接。
- macOS应用可显示同一机器的两个条目（UI+节点）。
- 节点身份存储在配对存储中；UI身份独立。

---

# 问题/痛点

- 维护两个协议栈（WS+桥接）。
- 远程节点审批：提示出现在节点主机，而非用户所在位置。
- TLS固定仅存在于桥接；WS依赖SSH/Tailscale。
- 身份重复：同一机器显示为多个实例。
- 角色模糊：UI+节点+CLI能力未明确分离。

---

# 提议的新状态（Clawnet）

## 单一协议，两个角色

单一WS协议，带角色+范围。

- **角色：节点**（能力主机）
- **角色：操作者**
- **范围：明确的权限范围**
- **统一配对+TLS固定**

## 审批流程

- 所有连接均需配对。
- TLS+固定降低移动端MITM风险。
- SSH静默审批为便利性，仍记录+可撤销。
- 发现永不作为信任锚点。
- 能力声明通过平台/类型验证服务器允许列表。

---

# 流媒体+大负载（节点媒体）

WS控制平面适用于小消息，但节点也执行：

- 摄像头片段
- 屏幕录制
- 音频流

选项：

1. WS二进制帧+分块+背压规则。
2. 分离流媒体端点（仍TLS+认证）。
3. 为媒体密集型命令保留桥接更久，最后迁移。

实施前选择一个以避免漂移。

---

# 能力+命令策略

- 节点报告的caps/commands视为**声明**。
- 网关强制平台允许列表。
- 任何新命令需操作者审批或显式允许列表更改。
- 审计更改并记录时间戳。

---

# 审计+速率限制

- 日志：配对请求、审批/拒绝、令牌发放/轮换/撤销。
- 限制配对垃圾邮件和审批提示。

---

# 协议卫生

- 显式协议版本+错误代码。
- 重连规则+心跳策略。
- 存在性TTL和最后看到语义。

---

# 开放问题

1. 单设备运行两个角色：令牌模型
   - 建议每个角色使用独立令牌（节点 vs 操作者）。
   - 相同deviceId；不同范围；更清晰的撤销。

2. 操作者范围粒度
   - 读/写/管理员+审批+配对（最小可行）。
   - 后续考虑按功能范围。

3. 令牌轮换+撤销UX
   - 角色变更时自动轮换。
   - 通过deviceId+角色撤销的UI。

4. 发现
   - 扩展当前Bonjour TXT以包含WS TLS指纹+角色提示。
   - 仅作为定位提示。

5. 跨网络审批
   - 广播至所有操作者客户端；活跃UI显示模态。
   - 首个响应胜出；网关强制原子性。

---

# 总结（TL;DR）

- 当前：WS控制平面+桥接节点传输。
- 痛点：审批+重复+两个栈。
- 提议：单一WS协议带明确角色+范围、统一配对+TLS固定、网关托管审批、稳定设备ID+可爱slug。
- 结果：更简单的用户体验、更强的安全性、更少重复、更好的移动路由。