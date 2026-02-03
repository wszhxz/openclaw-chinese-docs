---
summary: "Integrated browser control service + action commands"
read_when:
  - Adding agent-controlled browser automation
  - Debugging why openclaw is interfering with your own Chrome
  - Implementing browser settings + lifecycle in the macOS app
title: "Browser (OpenClaw-managed)"
---
以下是您提供的技术文档的中文翻译：

---

**翻译**

**AI 快照（数字引用）**：`openclaw browser snapshot`（默认；`--format ai`）  
- 输出：包含数字引用的文本快照。  
- 操作：`openclaw browser click 12`、`openclaw browser type 23 "hello"`。  
- 内部，引用通过 Playwright 的 `aria-ref` 解析。

**角色快照（角色引用如 `e12`）**：`openclaw browser snapshot --interactive`（或 `--compact`、`--depth`、`--selector`、`--frame`）  
- 输出：基于角色的列表/树，包含 `[ref=e12]`（可选 `[nth=1]`）。  
- 操作：`openclaw browser click e12`、`openclaw browser highlight e12`。  
- 内部，引用通过 `getByRole(...)`（加上 `nth()` 处理重复项）解析。  
- 添加 `--labels` 以包含视口截图并叠加 `e12` 标签。

**引用行为**：  
- 引用在导航后**不稳定**；如果操作失败，请重新运行 `snapshot` 并使用新鲜引用。  
- 如果角色快照使用了 `--frame`，角色引用将仅限于该 iframe，直到下次角色快照。

**等待增强功能**  
您可以等待的不仅仅是时间或文本：  
- 等待 URL（支持 Playwright 的通配符）：  
  - `openclaw browser wait --url "**/dash"`  
- 等待加载状态：  
  - `openclaw browser wait --load networkidle`  
- 等待 JS 条件：  
  - `openclaw browser wait --fn "window.ready===true"`  
- 等待选择器可见：  
  - `openclaw browser wait "#main"`

这些可以组合使用：  
```bash
openclaw browser wait "#main" \
  --url "**/dash" \
  --load networkidle \
  --fn "window.ready===true" \
  --timeout-ms 15000
```

**调试工作流**  
当操作失败（例如“不可见”、“严格模式违规”、“被覆盖”）：  
1. `openclaw browser snapshot --interactive`  
2. 使用 `click <ref>` / `type <ref>`（优先使用交互模式的角色引用）  
3. 如果仍失败：`openclaw browser highlight <ref>` 查看 Playwright 目标  
4. 如果页面行为异常：  
   - `openclaw browser errors --clear`  
   - `openclaw browser requests --filter api --clear`  
5. 深度调试：记录跟踪  
   - `openclaw browser trace start`  
   - 复现问题  
   - `openclaw browser trace stop`（输出 `TRACE:<路径>`）

**JSON 输出**  
`--json` 用于脚本和结构化工具：  
示例：  
```bash
openclaw browser status --json  
openclaw browser snapshot --interactive --json  
openclaw browser requests --filter api --json  
openclaw browser cookies --json  
```  
角色快照的 JSON 包含 `refs` 和小型 `stats` 块（行数/字符数/引用数/交互元素），以便工具判断负载大小和密度。

**状态和环境控制**  
这些对“让网站像 X 行为”的工作流很有用：  
- Cookies：`cookies`、`cookies set`、`cookies clear`  
- 存储：`storage local|session get|set|clear`  
- 离线：`set offline on|off`  
- 请求头：`set headers --json '{"X-Debug":"1"}'`（或 `--clear`）  
- HTTP 基本认证：`set credentials user pass`（或 `--clear`）  
- 地理位置：`set geo <纬度> <经度> --origin "https://example.com"`（或 `--clear`）  
- 媒体：`set media dark|light|no-preference|none`  
- 时区/语言：`set timezone ...`、`set locale ...`  
- 设备/视口：  
  - `set device "iPhone 14"`（Playwright 设备预设）  
  - `set viewport 1280 720`

**安全与隐私**  
- openclaw 浏览器配置文件可能包含登录会话；视为敏感数据。  
- `browser act kind=evaluate` / `openclaw browser evaluate` 和 `wait --fn` 会在页面上下文中执行任意 JavaScript。提示注入可能引导此行为。若不需要，禁用 `browser.evaluateEnabled=false`。  
- 登录和反爬虫注意事项（如 X/Twitter 等），请参见 [浏览器登录 + X/Twitter 发布](/tools/browser-login)。  
- 保持网关/节点主机私有（仅限回环或 tailnet）。  
- 远程 CDP 端点功能强大；请隧道化并保护它们。

**故障排除**  
针对 Linux 特定问题（尤其是 snap Chromium），请参见 [浏览器故障排除](/tools/browser-linux-troubleshooting)。

**代理工具 + 控制方式**  
代理获得 **一个浏览器自动化工具**：  
- `browser` — 状态/启动/停止/标签/打开/聚焦/关闭/快照/截图/导航/操作

映射关系：  
- `browser snapshot` 返回稳定的 UI 树（AI 或 ARIA）。  
- `browser act` 使用快照 `ref` ID 进行点击/输入/拖拽/选择。  
- `browser screenshot` 捕获像素（全页或元素）。  
- `browser` 支持：  
  - `profile` 选择命名的浏览器配置文件（openclaw、chrome 或远程 CDP）。  
  - `target`（`sandbox` | `host` | `node`）选择浏览器所在位置。  
  - 在沙箱会话中，`target: "host"` 需要 `agents.defaults.sandbox.browser.allowHostControl=true`。  
  - 如果未指定 `target`：沙箱会话默认为 `sandbox`，非沙箱会话默认为 `host`。  
  - 如果连接了浏览器节点，工具可能自动路由到它，除非您固定 `target="host"` 或 `target="node"`。

这保持代理的确定性，避免脆弱的选择器。

--- 

**注**