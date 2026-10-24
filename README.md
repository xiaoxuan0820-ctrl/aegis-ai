# Aegis AI（神盾 AI）

[简体中文](#简体中文) · [English](#english) · [日本語](#日本語)

> An auditable security-defense platform for individuals, AI agents, and servers.  
> 面向个人用户、AI Agent 与服务器的可审计安全防御平台。

## 简体中文

Aegis AI 是一个正在开发中的安全防御项目，目标是把安全事件收集、风险研判、受控响应与审计记录整合到统一工作流中。项目面向个人设备、AI Agent、网站和服务器等场景，优先采用本地处理、透明规则与可审计操作。

### 当前状态
- FastAPI + SQLite 的早期 MVP
- 安全事件录入与查询
- 基于规则的初步风险研判
- 默认 dry-run 的模拟响应
- 审计记录与基础测试

当前是开发原型，尚未达到生产环境安全要求。它不会自动封禁真实 IP、修改防火墙或执行系统命令。

### 快速开始
需要 Python 3.11+：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API 文档： http://127.0.0.1:8000/docs  
运行测试：`pytest`

### 授权与商业使用
当前代码采用 **PolyForm Noncommercial License 1.0.0**。该许可证允许符合条款的非商业使用、修改和分发；商业用途需要另行取得书面商业授权。请阅读 [LICENSE](LICENSE) 与 [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md)。

社区贡献者在 PR 合并前需要同意 [CLA.md](CLA.md)，以便项目能在保留贡献者版权的前提下，依法维护、分发并为项目提供商业授权。不要提交你无权授权的代码。

## English

Aegis AI is an early-stage security-defense project that aims to bring security-event intake, risk triage, controlled response, and audit records into one workflow. It is intended for personal devices, AI agents, websites, and servers, with an emphasis on local-first processing, transparent rules, and auditable actions.

### Current status
- Early MVP built with FastAPI and SQLite
- Security-event intake and listing
- Starter rule-based risk triage
- Simulated response actions (dry-run by default)
- Audit records and basic tests

This is a development prototype, not production-ready security software. It does not automatically block real IPs, change firewall rules, or execute system commands.

### Quick start
Python 3.11+ is required:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs  
Run tests: `pytest`

### Licensing and commercial use
The current code is licensed under the **PolyForm Noncommercial License 1.0.0**. Qualifying noncommercial use, modification, and distribution are permitted under its terms. Commercial use requires a separate written commercial license. See [LICENSE](LICENSE) and [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md).

Contributors must agree to [CLA.md](CLA.md) before their pull requests are merged. The CLA is intended to let the project maintain and distribute contributions and offer commercial licensing while contributors retain copyright. Do not submit code you are not authorized to contribute.

## 日本語

Aegis AI は、セキュリティイベントの収集、リスク評価、制御された対応、監査記録を一つのワークフローに統合することを目指す初期開発段階のプロジェクトです。個人端末、AI エージェント、Web サイト、サーバーを対象とし、ローカル優先の処理、透明性のあるルール、監査可能な操作を重視します。

### 現在の状態
- FastAPI と SQLite による初期 MVP
- セキュリティイベントの登録と一覧表示
- ルールベースの初期リスク評価
- dry-run による対応シミュレーション
- 監査記録と基本テスト

本ソフトウェアは開発用プロトタイプであり、本番環境向けの安全性は保証されていません。実際の IP ブロック、ファイアウォール変更、システムコマンドの実行は行いません。

### セットアップ
Python 3.11 以降が必要です。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API ドキュメント: http://127.0.0.1:8000/docs  
テスト: `pytest`

### ライセンスと商用利用
現在のコードは **PolyForm Noncommercial License 1.0.0** に基づいて提供されます。ライセンス条件を満たす非商用利用、改変、再配布が認められます。商用利用には別途、書面による商用ライセンスが必要です。[LICENSE](LICENSE) と [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md) を参照してください。

プルリクエストのマージ前に [CLA.md](CLA.md) への同意が必要です。寄稿者は著作権を保持しつつ、プロジェクトが寄稿を保守・配布し、商用ライセンスを提供できるようにすることを目的としています。権利を有しないコードは投稿しないでください。

## Project principles / 项目原则 / プロジェクト方針

- Defensive security only; test only systems you are authorized to assess.
- Default to dry-run; no model-generated arbitrary shell commands.
- Keep security decisions explainable and auditable.
- Never upload secrets or production logs to public issues.
- 本项目仅用于有授权的防御性安全用途。
- 許可された環境での防御的なセキュリティ用途に限定してください。

## Links
- [Contribution guide](CONTRIBUTING.md)
- [Security reporting](SECURITY.md)
- [Commercial licensing overview](COMMERCIAL-LICENSE.md)
- [Contributor License Agreement](CLA.md)
- [License policy](LICENSE_POLICY.md)

## Disclaimer
This project is provided “as is” for defensive research and development. It is not a substitute for professional security controls and must not be deployed in production without independent security review.
