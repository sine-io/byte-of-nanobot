# 排障快速索引

> 这里不再维护第二份重复正文。按症状选择入口，再到[统一排障手册](troubleshooting-guide.md)执行完整步骤。

## 按症状进入

| 现象 | 完整步骤 |
|---|---|
| `nanobot`、Python 或 MkDocs 命令找不到 | [安装与 Python 环境](troubleshooting-guide.md#install) |
| `401`、模型不可用、配置解析失败 | [配置、Provider 与模型](troubleshooting-guide.md#config) |
| 人格、规则、工作区或文件边界不对 | [Bootstrap 与工作区](troubleshooting-guide.md#workspace) |
| Skill 不触发或依赖执行失败 | [Skill 排障](troubleshooting-guide.md#skills) |
| Telegram、Discord、Slack 不回复或等待配对 | [Channel、配对与 Gateway](troubleshooting-guide.md#channels) |
| WebUI 打不开、认证或端口异常 | [WebUI、端口与认证](troubleshooting-guide.md#webui) |
| 容器挂载、权限、监听地址或日志异常 | [Docker 部署](troubleshooting-guide.md#docker) |
| Session、Memory、Consolidator 或 Dream 异常 | [记忆生命周期](troubleshooting-guide.md#memory) |
| 严格构建、内部链接或 Hero 示例语法失败 | [文档与示例构建](troubleshooting-guide.md#docs-build) |
| 准备向上游报告问题 | [提交 Issue 前的最小信息](troubleshooting-guide.md#report) |

## 不确定从哪里开始

先运行四个本地、只读检查：

```bash
nanobot --version
nanobot status
bash scripts/check-env.sh
bash scripts/verify-config.sh
```

不要打印或提交完整配置、环境文件、Token、配对码、Session 或 Memory。仍无法归类时，从[统一排障手册的一分钟定位表](troubleshooting-guide.md#quick-triage)开始。
