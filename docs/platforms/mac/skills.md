---
summary: "macOS Skills settings UI and gateway-backed status"
read_when:
  - Updating the macOS Skills settings UI
  - Changing skills gating or install behavior
title: "Skills"
---
# 技能 (macOS)

macOS应用程序通过网关显示OpenClaw技能；它不会在本地解析技能。

## 数据源

- `skills.status`（网关）返回所有技能以及资格和缺失的要求
  （包括捆绑技能的允许列表块）。
- 要求从每个`SKILL.md`中的`metadata.openclaw.requires`派生。

## 安装操作

- `metadata.openclaw.install` 定义安装选项（brew/node/go/uv）。
- 应用程序调用 `skills.install` 在网关主机上运行安装程序。
- 当提供多个安装程序时，网关仅显示一个首选安装程序
  （如果可用，则为brew，否则为来自`skills.install`的节点管理器，默认npm）。

## 环境/API密钥

- 应用程序将密钥存储在`skills.entries.<skillKey>`下的`~/.openclaw/openclaw.json`中。
- `skills.update` 修改 `enabled`、`apiKey` 和 `env`。

## 远程模式

- 安装 + 配置更新发生在网关主机上（而不是本地Mac）。