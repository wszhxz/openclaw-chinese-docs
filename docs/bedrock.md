---
summary: "Use Amazon Bedrock (Converse API) models with OpenClaw"
read_when:
  - You want to use Amazon Bedrock models with OpenClaw
  - You need AWS credential/region setup for model calls
title: "Amazon Bedrock"
---
# Amazon Bedrock

OpenClaw 可以通过 pi‑ai 的 **Bedrock Converse** 流式传输提供程序使用 **Amazon Bedrock** 模型。Bedrock 认证使用 **AWS SDK 默认凭证链**，而不是 API 密钥。

## pi‑ai 支持的功能

- 提供程序：`bedrock`
- API：`converse`
- 认证：AWS 凭证（环境变量、共享配置或实例角色）
- 区域：`us-east-1` 或 `us-west-2`（默认：`us-east-1`）

## 自动模型发现

如果检测到 AWS 凭证，OpenClaw 可以自动发现支持 **流式传输** 和 **文本输出** 的 Bedrock 模型。发现功能使用 `list-foundation-models` 并进行缓存（默认：1 小时）。

配置选项位于 `providers.bedrock` 下：

```yaml
providers:
  bedrock:
    # 启用自动发现（需要有效的 AWS 凭证）
    auto_discover: true
    
    # 发现的模型名称过滤器（正则表达式）
    # 例如："anthropic|meta|amazon" 
    filter: ""
    
    # 缓存持续时间（秒）
    cache_duration: 3600
    
    # 模型上下文长度限制
    max_context: 30720
    
    # 最大输出令牌数
    max_output: 4096
```

注意事项：

- `auto_discover` 在存在 AWS 凭证时默认为 `true`。
- `region` 默认为 `us-east-1` 或 `us-west-2`，然后是 `us-east-1`。
- `filter` 匹配 Bedrock 提供程序名称（例如 `anthropic`）。
- `cache_duration` 以秒为单位；设置为 `0` 以禁用缓存。
- `max_context`（默认：`30720`）和 `max_output`（默认：`4096`）
  用于发现的模型（如果您知道模型限制，可以覆盖）。

## 手动设置

1. 确保 AWS 凭证在 **网关主机** 上可用：

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

2. 向您的配置中添加 Bedrock 提供程序和模型（不需要 `api_key`）：

```yaml
providers:
  - id: bedrock/gateway
    model: anthropic.claude-3-sonnet-20240229-v1:0
    base_url: https://bedrock.us-east-1.amazonaws.com
```

## EC2 实例角色

当在附加了 IAM 角色的 EC2 实例上运行 OpenClaw 时，AWS SDK 将自动使用实例元数据服务（IMDS）进行认证。
然而，OpenClaw 的凭证检测目前只检查环境变量，而不检查 IMDS 凭证。

**解决方法：** 设置 `AWS_ACCESS_KEY_ID=dummy` 以表示 AWS 凭证可用。实际认证仍通过 IMDS 使用实例角色。

```bash
export AWS_ACCESS_KEY_ID=dummy
export AWS_SECRET_ACCESS_KEY=dummy  
export AWS_DEFAULT_REGION=us-east-1
```

EC2 实例角色的 **必需 IAM 权限**：

- `bedrock:Converse`
- `bedrock:InvokeModel`
- `bedrock:ListFoundationModels`（用于自动发现）

或者附加托管策略 `AmazonBedrockFullAccess`。

**快速设置：**

```bash
# 创建具有必要权限的角色
aws iam create-role --role-name OpenClawBedrockRole \
  --assume-role-policy-document file://trust-policy.json

# 附加托管策略
aws iam attach-role-policy --role-name OpenClawBedrockRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
```

## 注意事项

- Bedrock 需要在您的 AWS 账户/区域中启用 **模型访问**。
- 自动发现需要 `bedrock:ListFoundationModels` 权限。
- 如果您使用配置文件，请在网关主机上设置 `AWS_PROFILE`。
- OpenClaw 按此顺序显示凭证源：`AWS_*` 环境变量，
  然后是 `~/.aws/credentials` + `~/.aws/config`，然后是 `instance_role`，然后是
  默认 AWS SDK 链。
- 推理支持取决于模型；查看 Bedrock 模型卡片了解
  当前功能。
- 如果您更喜欢托管密钥流程，也可以在 Bedrock 前面放置一个与 OpenAI 兼容的
  代理并将其配置为 OpenAI 提供程序。