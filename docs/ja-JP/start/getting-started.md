---
read_when:
  - ゼロからの初回セットアップ
  - 動作するチャットへの最短ルートを知りたい
summary: OpenClawをインストールし、数分で最初のチャットを実行しましょう。
title: はじめに
x-i18n:
  generated_at: "2026-02-08T17:15:16Z"
  model: claude-opus-4-6
  provider: pi
  source_hash: 27aeeb3d18c495380e94e6b011b0df3def518535c9f1eee504f04871d8a32269
  source_path: start/getting-started.md
  workflow: 15
---
# 简介

目标：从零开始，通过最少的设置实现第一个可运行的聊天功能。

<Info>
最速のチャット方法：Control UIを開く（チャンネル設定は不要）。__CODE_BLOCK_0__を実行してブラウザでチャットするか、<Tooltip headline="Gatewayホスト" tip="OpenClaw Gatewayサービスを実行しているマシン。">Gatewayホスト</Tooltip>で__CODE_BLOCK_1__を開きます。
ドキュメント：[Dashboard](/web/dashboard)と[Control UI](/web/control-ui)。
</Info>

## 前提条件

- Node 22 及以上

<Tip>
不明な場合は__CODE_BLOCK_2__でNodeのバージョンを確認してください。
</Tip>

## 快速设置（CLI）

<Steps>
  <Step title="OpenClawをインストール（推奨）">
    <Tabs>
      <Tab title="macOS/Linux">
        __CODE_BLOCK_3__
      </Tab>
      <Tab title="Windows (PowerShell)">
        __CODE_BLOCK_4__
      </Tab>
    </Tabs>

    <Note>
    その他のインストール方法と要件：[インストール](/install)。
    </Note>

  </Step>
  <Step title="オンボーディングウィザードを実行">
    __CODE_BLOCK_5__

    ウィザードは認証、Gateway設定、およびオプションのチャンネルを構成します。
    詳細は[オンボーディングウィザード](/start/wizard)を参照してください。

  </Step>
  <Step title="Gatewayを確認">
    サービスをインストールした場合、すでに実行されているはずです：

    __CODE_BLOCK_6__

  </Step>
  <Step title="Control UIを開く">
    __CODE_BLOCK_7__
  </Step>
</Steps>

<Check>
Control UIが読み込まれれば、Gatewayは使用可能な状態です。
</Check>

## 选项确认与附加功能

<AccordionGroup>
  <Accordion title="Gatewayをフォアグラウンドで実行">
    クイックテストやトラブルシューティングに便利です。

    __CODE_BLOCK_8__

  </Accordion>
  <Accordion title="テストメッセージを送信">
    構成済みのチャンネルが必要です。

    __CODE_BLOCK_9__

  </Accordion>
</AccordionGroup>

## 了解更多

<Columns>
  <Card title="オンボーディングウィザード（詳細）" href="/start/wizard">
    完全なCLIウィザードリファレンスと高度なオプション。
  </Card>
  <Card title="macOSアプリのオンボーディング" href="/start/onboarding">
    macOSアプリの初回実行フロー。
  </Card>
</Columns>

## 完成后的状态

- 运行中的 Gateway
- 已配置的认证
- Control UI 访问或已连接的频道

## 下一步

- DM 的安全性与授权：[配对](/channels/pairing)
- 连接更多频道：[频道](/channels)
- 高级工作流及从源码构建：[设置](/start/setup)