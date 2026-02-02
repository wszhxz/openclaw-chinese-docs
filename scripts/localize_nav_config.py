#!/usr/bin/env python3

"""
导航配置本地化工具 - 将英文导航配置转换为中文
实现思维导图中提到的本地化配置保护机制
"""

import json
import yaml
import os
import sys
from pathlib import Path


def load_json_file(filepath):
    """安全加载JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"文件不存在: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"JSON解析错误: {filepath}")
        return None


def save_json_file(data, filepath):
    """保存JSON文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_yaml_file(filepath):
    """安全加载YAML文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"文件不存在: {filepath}")
        return None
    except yaml.YAMLError:
        print(f"YAML解析错误: {filepath}")
        return None


def save_yaml_file(data, filepath):
    """保存YAML文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


def translate_nav_item_title(title):
    """翻译导航项标题（简单的映射）"""
    translation_map = {
        "Start Here": "开始使用",
        "Help": "帮助",
        "Install & Updates": "安装与更新",
        "CLI": "命令行工具",
        "Core Concepts": "核心概念",
        "Gateway & Ops": "网关与运维",
        "Web & Interfaces": "网页与界面",
        "Channels": "通信渠道",
        "Providers": "服务提供商",
        "Automation & Hooks": "自动化与钩子",
        "Tools & Skills": "工具与技能",
        "Nodes & Media": "节点与媒体",
        "Platforms": "平台支持",
        "macOS Companion App": "macOS 伴侣应用",
        "Reference & Templates": "参考与模板",
        "Getting Started": "快速入门",
        "Wizard": "向导",
        "Setup": "设置",
        "Pairing": "配对",
        "Showcase": "展示",
        "Hubs": "中心",
        "Onboarding": "入门指南",
        "Lore": "背景知识",
        "Troubleshooting": "故障排除",
        "FAQ": "常见问题",
        "Installer": "安装程序",
        "Updating": "更新",
        "Development Channels": "开发频道",
        "Uninstall": "卸载",
        "Ansible": "Ansible",
        "Nix": "Nix",
        "Docker": "Docker",
        "Railway": "Railway",
        "Render": "Render",
        "Northflank": "Northflank",
        "Bun": "Bun",
        "Configuration": "配置",
        "Multiple Gateways": "多网关",
        "Authentication": "认证",
        "OpenAI HTTP API": "OpenAI HTTP API",
        "Tools Invoke HTTP API": "工具调用HTTP API",
        "CLI Backends": "CLI后端",
        "Local Models": "本地模型",
        "Background Process": "后台进程",
        "Health": "健康检查",
        "Heartbeat": "心跳",
        "Doctor": "诊断",
        "Logging": "日志",
        "Security": "安全",
        "Formal Verification": "形式化验证",
        "Sandbox vs Tool Policy vs Elevated": "沙盒vs工具策略vs提升权限",
        "Sandboxing": "沙盒",
        "Remote": "远程",
        "Discovery": "发现",
        "Bonjour": "Bonjour",
        "Tailscale": "Tailscale",
        "Control UI": "控制界面",
        "Dashboard": "仪表板",
        "WebChat": "网页聊天",
        "TUI": "终端用户界面",
        "WhatsApp": "WhatsApp",
        "Telegram": "Telegram",
        "Grammy": "Grammy",
        "Discord": "Discord",
        "Slack": "Slack",
        "Google Chat": "Google Chat",
        "Mattermost": "Mattermost",
        "Signal": "Signal",
        "iMessage": "iMessage",
        "MS Teams": "MS Teams",
        "Line": "Line",
        "Matrix": "Matrix",
        "Zalo": "Zalo",
        "Zalo User": "Zalo用户",
        "Broadcast Groups": "广播组",
        "Models": "模型",
        "Anthropic": "Anthropic",
        "Bedrock": "Bedrock",
        "Moonshot": "月球发射",
        "Minimax": "Minimax",
        "Vercel AI Gateway": "Vercel AI网关",
        "Synthetic": "合成",
        "OpenCode": "OpenCode",
        "GLM": "GLM",
        "Zai": "Zai",
        "Auth Monitoring": "认证监控",
        "Webhook": "Webhook",
        "Gmail PubSub": "Gmail PubSub",
        "Cron Jobs": "定时任务",
        "Cron vs Heartbeat": "定时任务vs心跳",
        "Poll": "轮询",
        "Lobster": "Lobster",
        "LLM Task": "LLM任务",
        "Plugin": "插件",
        "Voice Call Plugin": "语音通话插件",
        "Zalo User Plugin": "Zalo用户插件",
        "Exec": "执行",
        "Web": "网页",
        "Apply Patch": "应用补丁",
        "Elevated": "提升权限",
        "Browser": "浏览器",
        "Browser Login": "浏览器登录",
        "Chrome Extension": "Chrome扩展",
        "Browser Linux Troubleshooting": "浏览器Linux故障排除",
        "Slash Commands": "斜杠命令",
        "Thinking": "思考",
        "Agent Send": "代理发送",
        "Subagents": "子代理",
        "Multi-Agent Sandbox Tools": "多代理沙盒工具",
        "Reactions": "反应",
        "Skills": "技能",
        "Skills Config": "技能配置",
        "ClawHub": "ClawHub",
        "Camera": "摄像头",
        "Images": "图像",
        "Audio": "音频",
        "Location Command": "位置命令",
        "Voice Wake": "语音唤醒",
        "Talk": "说话",
        "macOS": "macOS",
        "macOS VM": "macOS虚拟机",
        "iOS": "iOS",
        "Android": "Android",
        "Windows": "Windows",
        "Linux": "Linux",
        "Fly": "Fly",
        "Hetzner": "Hetzner",
        "GCP": "GCP",
        "Exe Dev": "Exe开发",
        "Dev Setup": "开发设置",
        "Menu Bar": "菜单栏",
        "Voice Overlay": "语音叠加",
        "Canvas": "画布",
        "Child Process": "子进程",
        "Icon": "图标",
        "Permissions": "权限",
        "Remote Access": "远程访问",
        "Signing": "签名",
        "Release": "发布",
        "Bundled Gateway": "捆绑网关",
        "XPC": "XPC",
        "Peekaboo": "Peekaboo",
        "Session Management Compaction": "会话管理压缩",
        "RPC": "远程过程调用",
        "Device Models": "设备模型",
        "Testing": "测试",
        "Scripts": "脚本",
        "Templates": "模板",
        "Releasing": "发布",
        "AGENTS.default": "AGENTS.default",
        "System Prompt": "系统提示",
        "Context": "上下文",
        "Token Use": "令牌使用",
        "OAuth": "OAuth",
        "Agent Workspace": "代理工作空间",
        "Memory": "记忆",
        "Multi-Agent": "多代理",
        "Compaction": "压缩",
        "Sessions": "会话",
        "Session Pruning": "会话修剪",
        "Session Tool": "会话工具",
        "Presence": "存在感",
        "Channel Routing": "渠道路由",
        "Messages": "消息",
        "Streaming": "流传输",
        "Markdown Formatting": "Markdown格式化",
        "Groups": "群组",
        "Group Messages": "群组消息",
        "Typing Indicators": "输入指示器",
        "Queue": "队列",
        "Retry": "重试",
        "Model Providers": "模型提供商",
        "Model Failover": "模型故障转移",
        "Usage Tracking": "使用情况跟踪",
        "Timezone": "时区",
        "TypeBox": "TypeBox",
        "Protocol": "协议",
        "Bridge Protocol": "桥接协议",
        "Gateway Lock": "网关锁",
        "Environment": "环境",
        "Configuration Examples": "配置示例",
        "CLI Backends": "CLI后端",
        "Debugging": "调试",
        "Remote Gateway Readme": "远程网关说明",
        "Research Memory": "研究记忆",
        "Hooks": "钩子",
        "Evil Soul": "邪恶灵魂",
        "Browser Linux Troubleshooting": "浏览器Linux故障排除",
        "Application": "应用程序"
    }
    
    return translation_map.get(title, title)


def localize_docs_json(en_docs_path, zh_docs_path):
    """本地化 docs.json 文件"""
    en_config = load_json_file(en_docs_path)
    if not en_config:
        print("无法加载英文配置文件")
        return False
    
    # 翻译导航部分
    if 'navigation' in en_config and 'groups' in en_config['navigation']:
        for group in en_config['navigation']['groups']:
            if 'group' in group:
                group['group'] = translate_nav_item_title(group['group'])
    
    # 保存本地化后的配置
    save_json_file(en_config, zh_docs_path)
    print(f"已保存本地化配置到: {zh_docs_path}")
    return True


def localize_config_yml(en_config_path, zh_config_path):
    """本地化 _config.yml 文件"""
    en_config = load_yaml_file(en_config_path)
    if not en_config:
        print("无法加载英文配置文件")
        return False
    
    # 翻译导航部分
    if 'nav' in en_config:
        for item in en_config['nav']:
            if 'title' in item:
                item['title'] = translate_nav_item_title(item['title'])
            if 'children' in item:
                for child in item['children']:
                    if 'title' in child:
                        child['title'] = translate_nav_item_title(child['title'])
    
    # 保存本地化后的配置
    save_yaml_file(en_config, zh_config_path)
    print(f"已保存本地化配置到: {zh_config_path}")
    return True


def main():
    if len(sys.argv) != 3:
        print("用法: python localize_nav_config.py <英文配置路径> <中文配置路径>")
        sys.exit(1)
    
    en_path = sys.argv[1]
    zh_path = sys.argv[2]
    
    # 根据文件扩展名判断类型
    if en_path.endswith('.json'):
        success = localize_docs_json(en_path, zh_path)
    elif en_path.endswith(('.yml', '.yaml')):
        success = localize_config_yml(en_path, zh_path)
    else:
        print(f"不支持的文件类型: {en_path}")
        sys.exit(1)
    
    if success:
        print("本地化配置完成")
    else:
        print("本地化配置失败")
        sys.exit(1)


if __name__ == "__main__":
    main()