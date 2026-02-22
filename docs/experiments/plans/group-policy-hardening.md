---
summary: "Telegram allowlist hardening: prefix + whitespace normalization"
read_when:
  - Reviewing historical Telegram allowlist changes
title: "Telegram Allowlist Hardening"
---
# Telegram 允许列表强化

**日期**: 2026-01-05  
**状态**: 完成  
**PR**: #216

## 概要

Telegram 允许列表现在接受 `telegram:` 和 `tg:` 前缀（不区分大小写），并容忍意外的空白字符。这使入站允许列表检查与出站发送规范化保持一致。

## 发生了什么变化

- 前缀 `telegram:` 和 `tg:` 被视为相同（不区分大小写）。
- 允许列表条目会被修剪；空条目将被忽略。

## 示例

所有这些都被视为相同的ID：

- `telegram:123456`
- `TG:123456`
- `tg:123456`

## 为什么重要

从日志或聊天ID复制粘贴的内容通常包含前缀和空白字符。规范化可以避免在决定是否通过私信或群组响应时出现假阴性。

## 相关文档

- [群聊](/channels/groups)
- [Telegram 提供者](/channels/telegram)