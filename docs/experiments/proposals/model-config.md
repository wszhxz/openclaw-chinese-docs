---
summary: "Exploration: model config, auth profiles, and fallback behavior"
read_when:
  - Exploring future model selection + auth profile ideas
title: "Model Config Exploration"
---
# 模型配置（探索）

本文档记录**未来模型配置的思路**。它并非发货规格。如需了解当前行为，请参见：

- [模型](/concepts/models)
- [模型故障转移](/concepts/model-failover)
- [OAuth + 配置文件](/concepts/oauth)

## 动机

运维人员希望：

- 每个服务提供商支持多个认证配置文件（个人 vs 工作）。
- 通过简单 `/model` 选择模型，具有可预测的回退机制。
- 明确区分文本模型与支持图像的模型。

## 可能方向（高层次）

- 保持模型选择简单：`provider/model`，支持可选别名。
- 允许服务提供商拥有多个认证配置文件，并显式指定顺序。
- 使用全局回退列表，确保所有会话一致地进行故障转移。
- 仅在显式配置时覆盖图像路由。

## 开放性问题

- 配置文件轮换应按服务提供商还是按模型进行？
- 会话的 UI 应如何展示配置文件选择？
- 从旧配置键迁移的最安全路径是什么？