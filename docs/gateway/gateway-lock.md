---
summary: "Gateway singleton guard using the WebSocket listener bind"
read_when:
  - Running or debugging the gateway process
  - Investigating single-instance enforcement
title: "Gateway Lock"
---
-<think>
Okay, I need to translate this technical document from English to Chinese. Let me start by reading through the entire text to understand the context. The main topic is about a gateway lock mechanism, so the translation needs to be precise, especially for technical terms.

First, the title "Gateway lock" should be translated as "网关锁" to maintain the technical term. The date format is okay as is, but I'll check if it's commonly used in Chinese technical documents. The section headings like "Why" and "Mechanism" should be straightforward: "为什么" and "机制".

Looking at the bullet points under "Why", I need to ensure that terms like "base port", "isolated profiles", and "unique ports" are accurately translated. For example, "base port" could be "基础端口", "isolated profiles" might be "隔离的配置文件", and "unique ports" as "唯一端口". 

In the "Mechanism" section, phrases like "exclusive TCP listener" should be "独占的TCP监听器". The error messages need to be translated carefully to retain their meaning. For instance, "GatewayLockError" remains as "GatewayLockError" since it's a specific error name, but the message inside should be translated. 

The part about the OS releasing the listener automatically on process exit is important. I'll make sure to convey that the operating system automatically releases the listener when the process exits, including crashes and SIGKILL. Terms like "SIGKILL" might not need translation as they are technical terms.

In the "Error surface" section, the error messages should be translated to reflect the same conditions. For example, "another gateway instance is already listening" becomes "另一个网关实例已经在监听".

The "Operational notes" section mentions macOS and PID guard. "PID guard" is a technical term, so I'll keep it as "PID防护" or find an equivalent term. Also, ensuring that commands like "openclaw gateway --port <port>" are kept as is since they are commands.

I need to check for consistency in terminology throughout the translation. Words like "bind" in the context of network ports should be translated as "绑定". Also, ensuring that the structure of the document remains the same, with sections and bullet points properly formatted.

Finally, I'll review the entire translation to make sure it's clear, accurate, and maintains the technical precision required for such a document. Making sure that all error messages and instructions are correctly translated without losing their original intent.
</think>

# 网关锁

最后更新时间：2025-12-11

## 为什么

- 确保同一主机上的每个基础端口仅运行一个网关实例；其他网关必须使用隔离的配置文件和唯一端口。
- 在崩溃/SIGKILL情况下避免留下陈旧的锁文件。
- 控制端口已被占用时快速失败并显示明确错误。

## 机制

- 网关在启动时立即使用独占的TCP监听器绑定WebSocket监听器（默认 `ws://127.0.0.1:18789`）。
- 如果绑定失败并返回 `EADDRINUSE`，启动将抛出 `GatewayLockError("另一个网关实例已经在 ws://127.0.0.1:<port> 上监听")`。
- 任何进程退出（包括崩溃和SIGKILL）时，操作系统会自动释放监听器——无需单独的锁文件或清理步骤。
- 关闭网关时，会关闭WebSocket服务器和底层HTTP服务器，以及时释放端口。

## 错误场景

- 如果其他进程占用了端口，启动时将抛出 `GatewayLockError("另一个网关实例已经在 ws://127.0.0.1:<port> 上监听")`。
- 其他绑定失败会显示为 `GatewayLockError("无法在 ws://127.0.0.1:<port> 绑定网关套接字: …")`。

## 操作说明

- 如果端口被其他进程占用，错误信息相同；请释放端口或通过 `openclaw gateway --port <port>` 选择另一个端口。
- macOS 应用程序在启动网关前仍会维护自己的轻量级 PID 防护；运行时锁通过 WebSocket 绑定强制执行。