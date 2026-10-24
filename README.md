# Aegis AI（神盾 AI）

**面向个人用户、AI Agent 与服务器的可审计安全防御平台。**

Aegis AI 希望把安全事件收集、风险研判、受控响应和审计报告整合到一个清晰、可扩展的工作流中。项目处于早期 MVP 阶段，欢迎安全研究者、开发者和产品贡献者参与讨论。

> 当前版本是开发原型，不是可直接用于生产环境的安全产品。风险评分仅用于演示，不代表专业安全结论。

## 设计目标

- **一个事件视图：** 统一记录来自主机、服务、网络和 AI Agent 的安全事件。
- **可解释研判：** 输出风险等级、触发规则、建议动作和理由。
- **默认安全：** 响应器默认使用 dry-run，不执行真实封禁、删除或系统命令。
- **全程可审计：** 记录事件、研判和响应尝试，便于复盘。
- **个人优先：** 未来支持本地优先处理，减少敏感数据外传。
- **工具协作而非重复造轮子：** 逐步集成成熟的日志、网络检测和终端安全工具。

## 当前 MVP

- FastAPI REST API
- SQLite 事件与审计记录
- 基于规则的初步风险评估
- dry-run 防御响应
- 基础 API 测试

## 快速开始

需要 Python 3.11 或更新版本。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

打开 API 文档： http://127.0.0.1:8000/docs

默认仅监听本机回环地址。**不要未经身份认证、授权与网络加固，就把服务暴露到公网。**

运行测试：

```bash
pytest
```

环境变量：
- `AEGIS_DB_PATH`：SQLite 文件路径，默认 `./data/aegis.db`。
- `AEGIS_DRY_RUN`：当前版本只模拟响应；真实系统操作尚未实现，无法通过环境变量启用。

## API 示例

创建事件：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/events \
  -H 'Content-Type: application/json' \
  -d '{"source":"demo","event_type":"repeated_login_failure","severity":"high","description":"多次登录失败，疑似暴力破解","asset":"my-test-host","metadata":{}}'
```

然后把返回的事件 `id` 用于研判：

```bash
curl -X POST http://127.0.0.1:8000/api/v1/events/EVENT_ID/assess
```

## 安全边界

- 不执行模型输出中的任意 shell 命令。
- 不把日志、事件描述或外部网页内容当作可信指令。
- 不自动封禁真实 IP，不修改防火墙，不删除文件。
- 生产部署前必须补齐身份认证、授权、速率限制、秘密管理、加密传输、备份与安全测试。

## 路线图

1. [x] 事件 API、规则研判、dry-run 响应、审计日志
2. [ ] 事件来源适配器与标准化 schema
3. [ ] 规则配置、去重与事件关联
4. [ ] 本地 Web 控制台
5. [ ] AI 研判适配器（结构化输出、超时、数据脱敏与提示注入防护）
6. [ ] Wazuh / Suricata 等工具集成
7. [ ] 权限模型、身份认证与生产部署安全基线
8. [ ] 经人工审批的可回滚响应插件

## 参与贡献

请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [SECURITY.md](SECURITY.md)。当前仓库尚未授予通用开源许可证，商业使用和外部分发权限尚未开放；请勿把“公开可见”理解为“可任意复制、修改或商用”。项目方会在确定商业授权与贡献者协议后更新相关条款。

## 免责声明

本项目仅用于合法授权环境中的防御性安全监测与研究。使用者需确保拥有相关系统和数据的授权。软件按“现状”提供，不保证适用于特定用途。
