---
summary: "SOUL Evil hook (swap SOUL.md with SOUL_EVIL.md)"
read_when:
  - You want to enable or tune the SOUL Evil hook
  - You want a purge window or random-chance persona swap
title: "SOUL Evil Hook"
---
# SOUL 恶意钩子

SOUL 恶意钩子在清除窗口期间或以随机概率替换 **注入** 的 `SOUL.md` 内容为 `SOUL_EVIL.md`。它 **不** 修改磁盘上的文件。

## 工作原理

当 `agent:bootstrap` 运行时，钩子可以在系统提示组装之前替换内存中的 `SOUL.md` 内容。如果 `SOUL_EVIL.md` 缺失或为空，OpenClaw 记录警告并保持正常的 `SOUL.md`。

子代理运行时不包含 `SOUL.md` 在其引导文件中，因此此钩子对子代理没有影响。

## 启用

```bash
openclaw hooks enable soul-evil
```

然后设置配置：

```json
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "soul-evil": {
          "enabled": true,
          "file": "SOUL_EVIL.md",
          "chance": 0.1,
          "purge": { "at": "21:00", "duration": "15m" }
        }
      }
    }
  }
}
```

在代理工作区根目录（与 `SOUL.md` 并列）创建 `SOUL_EVIL.md`。

## 选项

- `file` (字符串): 替代的 SOUL 文件名（默认: `SOUL_EVIL.md`）
- `chance` (数字 0–1): 每次运行使用 `SOUL_EVIL.md` 的随机概率
- `purge.at` (HH:mm): 每日清除开始时间（24小时制）
- `purge.duration` (持续时间): 窗口长度（例如 `30s`, `10m`, `1h`）

**优先级:** 清除窗口优先于概率。

**时区:** 当设置时使用 `agents.defaults.userTimezone`; 否则使用主机时区。

## 注意事项

- 不会在磁盘上写入或修改文件。
- 如果 `SOUL.md` 不在引导列表中，钩子不会执行任何操作。

## 参见

- [Hooks](/hooks)