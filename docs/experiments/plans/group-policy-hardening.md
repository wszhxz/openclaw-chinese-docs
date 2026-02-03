---
summary: "Telegram allowlist hardening: prefix + whitespace normalization"
read_when:
  - Reviewing historical Telegram allowlist changes
title: "Telegram Allowlist Hardening"
---
# Telegram 允许列表强化

**日期**: 2026-01-05  
**状态**: 已完成  
**PR**: #216

## 概述

Telegram 允许列表现在以不区分大小写的方式接受 `telegram:` 和 `tg:` 前缀，并容忍意外的空格。这使入站允许列表检查与出站发送规范化保持一致。

## 变更内容

- `telegram:` 和 `tg:` 前缀被视为相同（不区分大小写）。
- 允许列表条目会进行修剪；空条目将被忽略。

## 示例

以下所有示例均对应相同的 ID：

- `telegram:123456`
- `TG:123456`
- `tg:123456`

## 为何重要

从日志或聊天 ID 复制粘贴时通常包含前缀和空格。规范化可避免在决定是否在私聊或群组中回复时出现误判（假阴性）。

## 相关文档

- [群组聊天](/concepts/groups)
- [Telegram 提供商](/channels/telegram)