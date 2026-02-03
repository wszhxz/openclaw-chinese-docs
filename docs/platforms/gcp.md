---
summary: "Run OpenClaw Gateway 24/7 on a GCP Compute Engine VM (Docker) with durable state"
read_when:
  - You want OpenClaw running 24/7 on GCP
  - You want a production-grade, always-on Gateway on your own VM
  - You want full control over persistence, binaries, and restart behavior
title: "GCP"
---
# 在GCP计算引擎上运行OpenClaw（Docker，生产VPS指南）

## 目标

使用Docker在GCP计算引擎虚拟机上运行持久化的OpenClaw网关，具备持久化状态、内置二进制文件和安全重启行为。

如果您想要“约5-12美元/月的OpenClaw 24/7服务”，这是Google Cloud上的可靠选择。

## 我们将执行什么操作

* 通过Docker在GCP计算引擎上部署OpenClaw网关
* 配置持久化状态和安全重启机制
* 设置必要的服务和权限
* 验证部署并访问网关

## 快速路径

1. 安装和配置gcloud CLI
2. 创建和启动计算引擎实例
3. 配置Docker环境
4. 部署OpenClaw网关
5. 验证部署并访问网关

## 您需要什么

* gcloud CLI
* Google Cloud项目
* Docker环境
* OpenClaw源代码
* 可选：提供方凭证（如WhatsApp QR、Telegram机器人令牌等）

## 详细步骤

### 安装和配置gcloud CLI

1. 下载并安装gcloud CLI
2. 初始化gcloud CLI
3. 设置默认项目和区域

### 创建和启动计算引擎实例

1. 创建计算引擎实例
2. 启动实例
3. 配置实例的防火墙规则

### 配置Docker环境

1. 安装Docker
2. 配置Docker守护进程
3. 设置Docker网络

### 部署OpenClaw网关

1. 克隆OpenClaw源代码
2. 配置Dockerfile
3. 构建Docker镜像
4. 启动Docker容器

### 验证部署并访问网关

1. 检查Docker日志
2. 创建SSH隧道
3. 访问网关界面

## 持久化位置（真实来源）

| 组件 | 位置 | 持久化机制 | 备注 |
|------|------|------------|------|
| 网关配置 | /home/node/.openclaw/ | 主机卷挂载 | 包括openclaw.json和令牌 |
| 模型认证配置 | /home/node/.openclaw/ | 主机卷挂载 | OAuth令牌、API密钥 |
| 技能配置 | /home/node/.openclaw/skills/ | 主机卷挂载 | 技能级别状态 |
| 代理工作区 | /home/node/.openclaw/workspace/ | 主机卷挂载 | 代码和代理工件 |
| WhatsApp会话 | /home/node/.openclaw/ | 主机卷挂载 | 保留QR登录 |
| Gmail密钥环 | /home/node/.openclaw/ | 主机卷+密码 | 需要GOG_KEYRING_PASSWORD |
| 外部二进制文件 | /usr/local/bin/ | Docker镜像 | 必须在构建时烘焙 |
| Node运行时 | 容器文件系统 | Docker镜像 | 每次镜像构建都会重建 |
| 操作系统包 | 容器文件系统 | Docker镜像 | 不要在运行时安装 |
| Docker容器 | 临时 | 可重启 | 可以安全销毁 |

## 更新

要更新VM上的OpenClaw：

1. 进入openclaw目录
2. 拉取最新代码
3. 重新构建Docker镜像
4. 重新启动Docker容器

## 故障排除

**SSH连接被拒绝**

SSH密钥传播可能需要创建虚拟机后1-2分钟。等待并重试。

**操作系统登录问题**

检查您的操作系统登录配置文件：

```bash
gcloud compute os-login describe-profile
```

确保您的账户具有所需的IAM权限（Compute OS登录或Compute OS管理员登录）。

**内存不足（OOM）**

如果使用e2-micro并遇到OOM，升级到e2-small或e2-medium：

```bash
# 首先停止虚拟机
gcloud compute instances stop openclaw-gateway --zone=us-central1-a

# 更改机器类型
gcloud compute instances set-machine-type openclaw-gateway \
  --zone=us-central1-a \
  --machine-type=e2-small

# 启动虚拟机
gcloud compute instances start openclaw-gateway --zone=us-central1-a
```

## 服务账户（安全最佳实践）

对于个人使用，默认用户账户即可。

对于自动化或CI/CD流水线，创建一个具有最小权限的专用服务账户：

1. 创建服务账户：

   ```bash
   gcloud iam service-accounts create openclaw-deploy \
     --display-name="OpenClaw部署"
   ```

2. 授予Compute实例管理员角色（或更窄的自定义角色）：
   ```bash
   gcloud projects add-iam-policy-binding my-openclaw-project \
     --member="serviceAccount:openclaw-deploy@my-openclaw-project.iam.gserviceaccount.com" \
     --role="roles/compute.instanceAdmin.v1"
   ```

避免为自动化使用所有者角色。使用最小特权原则。

查看 https://cloud.google.com/iam/docs/understanding-roles 获取IAM角色详细信息。

## 下一步

- 设置消息渠道：[消息渠道](/channels)
- 将本地设备配对为节点：[节点](/nodes)
- 配置网关：[网关配置](/gateway/configuration)