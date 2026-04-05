---
read_when:
  - オンボーディングウィザードの実行または設定時
  - 新しいマシンのセットアップ時
sidebarTitle: Wizard (CLI)
summary: CLIオンボーディングウィザード：Gateway、ワークスペース、チャンネル、Skillsの対話式セットアップ
title: オンボーディングウィザード（CLI）
x-i18n:
  generated_at: "2026-02-08T17:15:18Z"
  model: claude-opus-4-6
  provider: pi
  source_hash: 9a650d46044a930aa4aaec30b35f1273ca3969bf676ab67bf4e1575b5c46db4c
  source_path: start/wizard.md
  workflow: 15
---
# 入门向导（CLI）

CLI 入门向导是在 macOS、Linux、Windows（通过 WSL2）上设置 OpenClaw 时的推荐方式。除本地 Gateway 或远程 Gateway 连接外，还可配置 Workspace 的默认设置、Channels 和 Skills。

```bash
openclaw onboard
```

<Info>
最速で初回チャットを開始する方法：Control UI を開きます（チャンネル設定は不要）。__CODE_BLOCK_1__ を実行してブラウザでチャットできます。ドキュメント：[Dashboard](/web/dashboard)。
</Info>

## 快速开始 vs 详细设置

向导启动时可选择**快速开始**（默认设置）或**详细设置**（完全控制）。

<Tabs>
  <Tab title="クイックスタート（デフォルト設定）">
    - loopback上のローカルGateway
    - 既存のワークスペースまたはデフォルトワークスペース
    - Gatewayポート __CODE_BLOCK_2__
    - Gateway認証トークンは自動生成（loopback上でも生成されます）
    - Tailscale公開はオフ
    - TelegramとWhatsAppのDMはデフォルトで許可リスト（電話番号の入力を求められる場合があります）
  </Tab>
  <Tab title="詳細設定（完全な制御）">
    - モード、ワークスペース、Gateway、チャンネル、デーモン、Skillsの完全なプロンプトフローを表示
  </Tab>
</Tabs>

## CLI 入门详情

<Columns>
  <Card title="CLIリファレンス" href="/start/wizard-cli-reference">
    ローカルおよびリモートフローの完全な説明、認証とモデルマトリックス、設定出力、ウィザードRPC、signal-cliの動作。
  </Card>
  <Card title="自動化とスクリプト" href="/start/wizard-cli-automation">
    非対話式オンボーディングのレシピと自動化された __CODE_BLOCK_3__ の例。
  </Card>
</Columns>

## 常用后续命令

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
__CODE_BLOCK_5__ は非対話モードを意味しません。スクリプトでは __CODE_BLOCK_6__ を使用してください。
</Note>

<Tip>
推奨：エージェントが __CODE_BLOCK_7__ を使用できるように、Brave Search APIキーを設定してください（__CODE_BLOCK_8__ はキーなしで動作します）。最も簡単な方法：__CODE_BLOCK_9__ を実行すると __CODE_BLOCK_10__ に保存されます。旧 __CODE_BLOCK_11__ パスは互換用に引き続き読み込まれますが、新しい設定では使用しないでください。ドキュメント：[Webツール](/tools/web)。
</Tip>

## 相关文档

- CLI 命令参考：[`openclaw onboard`](/cli/onboard)
- macOS 应用入门：[入门](/start/onboarding)
- Agent 首次启动步骤：[Agent 引导](/start/bootstrapping)