---
summary: "macOS Skills settings UI and gateway-backed status"
read_when:
  - Updating the macOS Skills settings UI
  - Changing skills gating or install behavior
title: "Skills"
---
# 技能 (macOS)

macOS 应用通过网关展示 OpenClaw 技能；它不会在本地解析技能。

## 数据源

- `skills.status`（网关）返回所有技能以及资格和缺失的依赖项（包括捆绑技能的允许列表阻止项）。
- 依赖项来源于每个 `SKILL.md` 中的 `metadata.openclaw.requires`。

## 安装操作

- `metadata.openclaw.install` 定义安装选项（brew/node/go/uv）。
- 应用调用 `skills.install` 在网关主机上运行安装程序。
- 网关仅在提供多个安装程序时显示一个首选安装程序（优先使用 brew，否则使用 `skills.install` 中的节点管理器，默认 npm）。

## 环境/API 密钥

- 应用将密钥存储在 `~/.openclaw/openclaw.json` 的 `skills.entries.<skillKey>` 下。
- `skills.update` 修补 `enabled`、`apiKey` 和 `env`。

## 远程模式

- 安装 + 配置更新在网关主机上进行（而非本地 Mac）。