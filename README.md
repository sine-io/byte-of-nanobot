# 从零打造你的 AI Bot

> 一份面向零基础用户的 nanobot 教程，带你从"能跑"到"懂原理"。

## Part 1：使用 nanobot

学会使用 nanobot，理解它的配置和扩展机制。

| 章节 | 内容 | 你将学到 |
|------|------|----------|
| [第 1 章：5 分钟跑起来](01-quick-start.md) | 安装、配置、第一次对话 | nanobot 的三段启动流程 |
| [第 2 章：给 Bot 一个灵魂](02-soul.md) | 编辑人格、行为、用户画像 | System Prompt 的组装原理 |
| [第 3 章：教 Bot 新技能](03-skills.md) | 创建自定义 Skill | 渐进式加载与上下文管理 |
| [第 4 章：部署到聊天平台](04-deploy.md) | 连接 Telegram、Discord 等 | 消息总线与 Channel 架构 |

## Part 2：[从零复刻 nanobot](build/README.md)

用 Python 从零手写一个 AI Agent 框架，在实践中理解每一层架构。

| 章节 | 代码量 | 你将构建 | 对应 nanobot 模块 |
|------|--------|---------|------------------|
| [第 1 章：最简 Agent](build/01-simplest-agent.md) | ~40 行 | 能对话的 LLM 客户端 | `providers/` |
| [第 2 章：工具系统](build/02-tool-system.md) | ~200 行 | 能执行命令的 Agent | `agent/tools/`, `agent/loop.py` |
| [第 3 章：记忆与上下文](build/03-memory-and-context.md) | ~300 行 | 有记忆、有个性的 Agent | `agent/context.py`, `session/` |
| [第 4 章：消息总线](build/04-message-bus.md) | ~400 行 | 能接入多平台的 Agent | `bus/`, `channels/` |
| [第 5 章：技能与扩展](build/05-skills-and-beyond.md) | ~500 行 | 可动态扩展的完整 Agent | `agent/skills.py` |

## 适合谁

- 没有 AI Agent 开发经验，想拥有一个自己的 AI 助手
- 有一定编程基础（会用命令行、编辑 JSON），但不需要精通 Python
- 想知道 nanobot 内部是怎么工作的，而不只是照搬配置

## 前置准备

- Python >= 3.11
- 一个 LLM API Key
- 终端 / 命令行工具

## 约定

- `~/.nanobot/` — nanobot 的默认数据目录
- `~/.nanobot/config.json` — 配置文件
- `~/.nanobot/workspace/` — 工作区（Bot 的"大脑"所在）
- 代码引用优先使用模块路径，如 `nanobot/agent/loop.py`；如果出现行号，只把它当作阅读时的辅助定位，因为实现会随版本变化

## 如何阅读这套文档

这套教程分成两层：

- Part 1 关注“先用起来”，帮助你配置、定制、部署 nanobot
- Part 2 关注“为什么这样设计”，用教学版实现帮助你理解架构

阅读时有一个重要约定：文档里的架构图、伪代码和简化代码，优先服务于理解主干机制，不保证和当前仓库逐行完全一致。想核对真实实现时，请回到对应模块源码查看。
