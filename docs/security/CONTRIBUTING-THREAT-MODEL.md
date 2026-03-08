# 为 OpenClaw 威胁模型做贡献

感谢帮助 OpenClaw 变得更安全。此威胁模型是一份动态文档，我们欢迎任何人的贡献——您不需要成为安全专家。

## 贡献方式

### 添加威胁

发现了我们未涵盖的攻击向量或风险？在 [openclaw/trust](https://github.com/openclaw/trust/issues) 上开启一个 issue 并用您自己的话描述它。您不需要了解任何框架或填写每个字段——只需描述场景即可。

**建议包含（但不是必需的）：**

- 攻击场景以及它如何被利用
- OpenClaw 的哪些部分受到影响（CLI, gateway, channels, ClawHub, MCP servers 等）
- 您认为它的严重程度如何（low / medium / high / critical）
- 任何相关研究、CVEs 或现实世界示例的链接

我们将在审查期间处理 ATLAS 映射、威胁 ID 和风险评估。如果您想包含这些细节，很好——但这不是预期的。

> **这是用于添加到威胁模型，而不是报告实时漏洞。** 如果您发现了可利用的漏洞，请参阅我们的 [Trust 页面](https://trust.openclaw.ai) 获取负责任的披露说明。

### 建议缓解措施

有关于如何解决现有威胁的想法？开启一个 issue 或 PR 引用该威胁。有用的缓解措施是具体且可操作的——例如，"gateway 处每个发送者 10 条消息/分钟的速率限制" 比 "实施速率限制" 更好。

### 提出攻击链

攻击链展示多个威胁如何结合成现实的攻击场景。如果您看到危险的组合，描述步骤以及攻击者如何将它们链接在一起。关于攻击在实际中如何展开的简短叙述比正式模板更有价值。

### 修复或改进现有内容

拼写错误、澄清、过时信息、更好的示例——欢迎 PR，无需 issue。

## 我们使用什么

### MITRE ATLAS

此威胁模型基于 [MITRE ATLAS](https://atlas.mitre.org/)（Adversarial Threat Landscape for AI Systems）构建，这是一个专门为 AI/ML 威胁设计的框架，如 prompt injection, tool misuse 和 agent exploitation。您不需要了解 ATLAS 即可贡献——我们在审查期间将提交内容映射到框架。

### 威胁 ID

每个威胁获得一个像 `T-EXEC-003` 这样的 ID。类别如下：

| 代码    | 类别                                   |
| ------- | ------------------------------------------ |
| RECON   | Reconnaissance - 信息收集     |
| ACCESS  | Initial access - 获取入口             |
| EXEC    | Execution - 运行恶意操作      |
| PERSIST | Persistence - 维持访问           |
| EVADE   | Defense evasion - 避免检测       |
| DISC    | Discovery - 了解环境 |
| EXFIL   | Exfiltration - 窃取数据               |
| IMPACT  | Impact - 损害或 disruption              |

ID 由维护者在审查期间分配。您不需要选择一个。

### 风险级别

| 级别        | 含义                                                           |
| ------------ | ----------------------------------------------------------------- |
| **Critical** | 完全系统妥协，或高可能性 + 关键影响      |
| **High**     | 可能造成重大损害，或中等可能性 + 关键影响 |
| **Medium**   | 中等风险，或低可能性 + 高影响                    |
| **Low**      | 可能性低且影响有限                                       |

如果您不确定风险级别，只需描述影响，我们将进行评估。

## 审查流程

1. **Triage** - 我们在 48 小时内审查新提交
2. **Assessment** - 我们验证可行性，分配 ATLAS 映射和威胁 ID，验证风险级别
3. **Documentation** - 我们确保所有内容格式正确且完整
4. **Merge** - 添加到威胁模型和可视化中

## 资源

- [ATLAS 网站](https://atlas.mitre.org/)
- [ATLAS 技术](https://atlas.mitre.org/techniques/)
- [ATLAS 案例研究](https://atlas.mitre.org/studies/)
- [OpenClaw 威胁模型](/security/THREAT-MODEL-ATLAS)

## 联系

- **安全漏洞：** 请参阅我们的 [Trust 页面](https://trust.openclaw.ai) 获取报告说明
- **威胁模型问题：** 在 [openclaw/trust](https://github.com/openclaw/trust/issues) 上开启 issue
- **一般聊天：** Discord #security 频道

## 认可

威胁模型的贡献者将在威胁模型致谢、发布说明和 OpenClaw 安全名人堂中获得认可，以表彰重大贡献。