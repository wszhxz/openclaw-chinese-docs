---
summary: "Use Amazon Bedrock (Converse API) models with OpenClaw"
read_when:
  - You want to use Amazon Bedrock models with OpenClaw
  - You need AWS credential/region setup for model calls
title: "Amazon Bedrock"
---
# Amazon Bedrock

OpenClaw 可通过 pi‑ai 的 **Bedrock Converse** 流式传输提供程序，使用 **Amazon Bedrock** 模型。Bedrock 身份验证采用 **AWS SDK 默认凭证链**，而非 API 密钥。

## pi‑ai 支持的功能

- 提供程序：`amazon-bedrock`
- API：`bedrock-converse-stream`
- 身份验证：AWS 凭证（环境变量、共享配置文件或实例角色）
- 区域：`AWS_REGION` 或 `AWS_DEFAULT_REGION`（默认：`us-east-1`）

## 自动模型发现

若检测到 AWS 凭证，OpenClaw 可自动发现支持 **流式传输** 和 **文本输出** 的 Bedrock 模型。该发现过程使用 `bedrock:ListFoundationModels`，并进行缓存（默认：1 小时）。

配置选项位于 `models.bedrockDiscovery` 下：

```json5
{
  models: {
    bedrockDiscovery: {
      enabled: true,
      region: "us-east-1",
      providerFilter: ["anthropic", "amazon"],
      refreshInterval: 3600,
      defaultContextWindow: 32000,
      defaultMaxTokens: 4096,
    },
  },
}
```

注意事项：

- 当存在 AWS 凭证时，`enabled` 默认为 `true`。
- `region` 默认为 `AWS_REGION` 或 `AWS_DEFAULT_REGION`，随后为 `us-east-1`。
- `providerFilter` 与 Bedrock 提供程序名称匹配（例如 `anthropic`）。
- `refreshInterval` 单位为秒；设为 `0` 可禁用缓存。
- `defaultContextWindow`（默认：`32000`）和 `defaultMaxTokens`（默认：`4096`）用于已发现的模型（若您了解模型限制，可手动覆盖）。

## 入门指南

1. 确保 AWS 凭证在 **网关主机** 上可用：

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
# Optional:
export AWS_SESSION_TOKEN="..."
export AWS_PROFILE="your-profile"
# Optional (Bedrock API key/bearer token):
export AWS_BEARER_TOKEN_BEDROCK="..."
```

2. 在配置中添加 Bedrock 提供程序及模型（无需 `apiKey`）：

```json5
{
  models: {
    providers: {
      "amazon-bedrock": {
        baseUrl: "https://bedrock-runtime.us-east-1.amazonaws.com",
        api: "bedrock-converse-stream",
        auth: "aws-sdk",
        models: [
          {
            id: "us.anthropic.claude-opus-4-6-v1:0",
            name: "Claude Opus 4.6 (Bedrock)",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "amazon-bedrock/us.anthropic.claude-opus-4-6-v1:0" },
    },
  },
}
```

## EC2 实例角色

当 OpenClaw 运行于附加了 IAM 角色的 EC2 实例上时，AWS SDK 将自动通过实例元数据服务（IMDS）进行身份验证。但目前 OpenClaw 的凭证检测仅检查环境变量，不检查 IMDS 凭证。

**临时解决方案：** 设置 `AWS_PROFILE=default`，以表明 AWS 凭证可用。实际身份验证仍通过 IMDS 使用实例角色完成。

```bash
# Add to ~/.bashrc or your shell profile
export AWS_PROFILE=default
export AWS_REGION=us-east-1
```

**EC2 实例角色所需的 IAM 权限：**

- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`
- `bedrock:ListFoundationModels`（用于自动发现）

或附加托管策略 `AmazonBedrockFullAccess`。

## 快速设置（AWS 路径）

```bash
# 1. Create IAM role and instance profile
aws iam create-role --role-name EC2-Bedrock-Access \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy --role-name EC2-Bedrock-Access \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam create-instance-profile --instance-profile-name EC2-Bedrock-Access
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-Bedrock-Access \
  --role-name EC2-Bedrock-Access

# 2. Attach to your EC2 instance
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Access

# 3. On the EC2 instance, enable discovery
openclaw config set models.bedrockDiscovery.enabled true
openclaw config set models.bedrockDiscovery.region us-east-1

# 4. Set the workaround env vars
echo 'export AWS_PROFILE=default' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# 5. Verify models are discovered
openclaw models list
```

## 注意事项

- Bedrock 要求您的 AWS 账户/区域中已启用 **模型访问权限**。
- 自动发现需要 `bedrock:ListFoundationModels` 权限。
- 若使用配置文件，请在网关主机上设置 `AWS_PROFILE`。
- OpenClaw 按如下顺序识别凭证来源：`AWS_BEARER_TOKEN_BEDROCK`，然后是 `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`，接着是 `AWS_PROFILE`，最后是默认的 AWS SDK 凭证链。
- 推理支持取决于具体模型；请查阅 Bedrock 模型卡片以了解当前能力。
- 若您更倾向使用受管密钥流程，也可在 Bedrock 前部署一个兼容 OpenAI 的代理，并将其配置为 OpenAI 提供程序。