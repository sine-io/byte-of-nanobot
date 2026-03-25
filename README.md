# 从零打造你的 AI Bot

> 一套面向 AI Agent 初学者的 nanobot 教程，带你从“先跑起来”到“理解架构”，再到“自己写一个 bot”。

本项目在整理内容、迭代结构和补充示例时，使用了 Codex 结合 Superpowers 进行辅助开发。它主要用于提升文档编写和工程协作效率，最终内容仍以教程的可读性、教学性和可验证性为准。

## 本地阅读

如果你只是想快速读 Markdown，直接用编辑器打开 [README.md](README.md) 即可。

如果你希望它像一个带目录、搜索和上下页导航的文档站来阅读，仓库已经提供了 MkDocs 配置。clone 到本地后，在仓库根目录执行：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-docs.txt
python -m mkdocs serve
```

然后打开 `http://127.0.0.1:8000`。

如果 `python3 -m venv .venv` 报 `ensurepip is not available`，通常说明系统没装 `venv` 组件；在 Debian / Ubuntu 上先安装 `python3-venv` 再重试。

如果你只想检查站点能不能正常构建，可以运行：

```bash
python -m mkdocs build --strict
```

## GitHub Pages

仓库已经补上 `GitHub Pages` 发布工作流，使用 `MkDocs` 构建静态站点，再由 GitHub Actions 自动部署。

- 工作流文件：`.github/workflows/pages.yml`
- 目标地址：`https://sine-io.github.io/nanobot-playbook/`

第一次启用时，到仓库的 `Settings -> Pages` 中确认发布来源使用 `GitHub Actions`。之后只要向 `main` 分支推送，文档站就会自动重新发布。

## 这套教程适合谁

- 想先把 nanobot 用起来，再逐步理解它为什么这样设计的人
- 会命令行、会编辑配置文件，但没有 AI Agent 开发经验的人
- 想从零手写一个教学版 Agent，理解 nanobot 核心架构的程序员

不太适合：

- 完全没有命令行基础的绝对新手
- 想直接得到生产级 bot 脚手架的人

## 三条阅读路径

### 路线 A：先把 Bot 用起来

适合想尽快上手的人。按顺序阅读：

1. [第 1 章：5 分钟跑起来](01-quick-start.md)
2. [第 2 章：用 Markdown 定义 Bot](02-soul.md)
3. [第 3 章：教 Bot 新技能](03-skills.md)
4. [第 4 章：先部署到 Telegram](04-deploy.md)
5. [第 5 章：做一个真实可用的 Bot](05-first-real-bot.md)

学完后你应该能：

- 跑通 nanobot
- 改人格、规则、用户画像
- 写一个自己的 Skill
- 把 Bot 部署到 Telegram

### 路线 B：知其然，也知其所以然

适合想理解 nanobot 主干机制的人。推荐读法：

1. 先读 Part 1，知道功能入口
2. 再对照读 `build/` 中对应章节，理解实现原理

学完后你应该能解释：

- Provider 是什么
- AgentLoop 怎么工作
- Skill 为什么能按需加载
- MessageBus 为什么能支持多平台

### 路线 C：自己写一个 Bot

适合程序员。按顺序阅读：

1. [Part 2 导读](build/README.md)
2. [第 1 章：最简 Agent](build/01-simplest-agent.md)
3. [第 2 章：工具系统](build/02-tool-system.md)
4. [第 3 章：记忆与上下文](build/03-memory-and-context.md)
5. [第 4 章：消息总线](build/04-message-bus.md)
6. [第 5 章：技能与扩展](build/05-skills-and-beyond.md)
7. [第 6 章：从 Mini Agent 到真实项目](build/06-from-mini-agent-to-real-bot.md)

学完后你应该能：

- 写出一个教学版多轮 Agent
- 给它加工具、记忆、技能和多平台入口
- 理解它距离工程化产品还差什么

## Part 1：使用 nanobot

这一部分关注“先用起来”，帮助你配置、定制、扩展并部署自己的 Bot。

| 章节 | 内容 | 你将学到 |
|------|------|----------|
| [第 1 章：5 分钟跑起来](01-quick-start.md) | 安装、配置、第一次对话 | nanobot 的三段启动流程 |
| [第 2 章：用 Markdown 定义 Bot](02-soul.md) | 编辑人格、行为、用户画像和工具规则 | Bootstrap 文件如何影响 Bot 行为 |
| [第 3 章：教 Bot 新技能](03-skills.md) | 创建自定义 Skill | 渐进式加载与上下文管理 |
| [第 4 章：先部署到 Telegram](04-deploy.md) | 把 Bot 接到真实聊天平台 | Gateway 模式与 MessageBus 架构 |
| [第 5 章：做一个真实可用的 Bot](05-first-real-bot.md) | 把前四章串成完整项目 | 从配置到上线的完整闭环 |

## Part 2：[从零复刻 nanobot](build/README.md)

这一部分关注“为什么这样设计”，用 Python 从零手写一个教学版 AI Agent 框架。

| 章节 | 代码量 | 你将构建 | 对应 nanobot 模块 / 重点 |
|------|--------|---------|---------------------------|
| [第 1 章：最简 Agent](build/01-simplest-agent.md) | ~40 行 | 能对话的 LLM 客户端 | `providers/` |
| [第 2 章：工具系统](build/02-tool-system.md) | ~200 行 | 能执行命令的 Agent | `agent/tools/`, `agent/loop.py` |
| [第 3 章：记忆与上下文](build/03-memory-and-context.md) | ~300 行 | 有记忆、有个性的 Agent | `agent/context.py`, `agent/memory.py`, `session/` |
| [第 4 章：消息总线](build/04-message-bus.md) | ~400 行 | 能接入多平台的 Agent | `bus/`, `channels/` |
| [第 5 章：技能与扩展](build/05-skills-and-beyond.md) | ~500 行 | 可动态扩展的完整 Agent | `agent/skills.py` |
| [第 6 章：从 Mini Agent 到真实项目](build/06-from-mini-agent-to-real-bot.md) | 架构桥接 | 从教学版走向可维护项目 | 工程化边界、安全、并发、重试 |

## 学完后你能做到什么

- 对使用者：你可以定制自己的 nanobot，并把它部署到真实聊天平台
- 对学习者：你可以解释 Prompt、Skill、Memory、MessageBus 这些主干设计
- 对程序员：你可以写出一个属于自己的教学版 Agent，并知道下一步该补哪些工程能力

## 前置准备

- Python >= 3.11
- 一个 LLM API Key
- 终端 / 命令行工具
- 如果你要跟做 Part 1 里的 Skill 示例，建议本机已安装 `curl` 和 `python3`

## 约定

- `~/.nanobot/` — nanobot 的默认数据目录
- `~/.nanobot/config.json` — 配置文件
- `~/.nanobot/workspace/` — 工作区（Bot 的“大脑”所在）
- 代码引用优先使用模块路径，如 `nanobot/agent/loop.py`
- 如果出现行号，只把它当作阅读时的辅助定位，因为实现会随版本变化

## 本教程的边界

这套教程解决的是“理解主干机制”和“做出自己的 bot 原型”。

它不会直接替你解决所有生产问题，例如：

- 并发控制
- 错误恢复与重试
- 平台边界情况处理
- ACL 与安全沙箱
- 完整测试与部署体系

这些会在 Part 2 的最后一章集中说明。想核对真实实现时，请回到对应源码模块查看。
