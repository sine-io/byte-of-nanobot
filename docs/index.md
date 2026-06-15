# 简明 NanoBot 教程

> 一套面向 AI Agent 初学者的 nanobot 教程，带你从"先跑起来"到"理解架构"，再到"自己写一个 bot"。

本项目在整理内容、迭代结构和补充示例时，使用了 Codex 结合 Superpowers 进行辅助开发。它主要用于提升文档编写和工程协作效率，最终内容仍以教程的可读性、教学性和可验证性为准。

---

## 🚀 从这里开始

如果你现在只想知道"这套教程值不值得读"，先看这 3 句：

- ✅ 你可以在 **5 分钟**内跑通 nanobot 的 CLI，拿到第一次正常回复
- ✅ 你可以在 **1 小时**左右做出一个带人格、规则和 Skill 的 Bot 原型
- ✅ 你可以继续读进阶营，理解 Skill、Memory、MessageBus 这些主干机制为什么这样设计

### 最适合从这里开始的人

- 会命令行、会编辑 JSON / Markdown，但还没有 AI Agent 开发经验的人
- 想先把 nanobot 用起来，再逐步理解它为什么这样设计的人
- 想从零手写一个教学版 Agent，理解 nanobot 核心架构的程序员

### 不太适合的人

- 完全没有命令行基础的绝对新手
- 想直接得到生产级 bot 脚手架的人

---

## 📖 你现在该走哪条路线

| 你现在最想要的结果 | 从哪里开始 | 读完后你会得到什么 |
|------|------|------|
| 先把 Bot 跑起来 | [第一次阅读请只走这一条](#first-read) | 一条从 CLI 到 Skill 再到 Telegram 的最短闭环 |
| 理解 nanobot 的主干机制 | [路线 B：知其然，也知其所以然](#path-b) | 对 Provider、AgentLoop、Skill、MessageBus 的整体心智模型 |
| 自己手写一个教学版 Agent | [路线 C：自己写一个 Bot](#path-c) | 一套从最简 Agent 到工程化边界的增量实现路径 |

---

<a id="first-read"></a>

## ⚡ 第一次阅读请只走这一条

如果这是你第一次接触 nanobot，不要一上来就自己改路线。先按这个顺序完成一遍：

```mermaid
flowchart LR
    A[第0章<br/>开始之前] --> B[第1章<br/>5分钟跑起来]
    B --> C[第2章<br/>定制性格]
    C --> D[第3章<br/>添加技能]
    D --> E[第4章<br/>本地验收]
    E --> F[第5章<br/>部署Telegram]
    F --> G[第6章<br/>多场景案例]
```

1. 读 [第 0 章：开始之前](00-before-you-start.md)，确认环境准备好
2. 读 [第 1 章：5 分钟跑起来](01-quick-start.md)，把 CLI 跑通
3. 读 [第 2 章：让 Bot 有个性](02-soul.md) 和 [第 3 章：教 Bot 新技能](03-skills.md)，完成"人格 + 规则 + Skill"闭环
4. 读 [第 4 章：本地完整验收](04-local-integration.md)，在本地完成端到端测试
5. 读 [第 5 章：部署到 Telegram](05-deploy-telegram.md)，接入真实聊天平台
6. 读 [第 6 章：多场景案例库](06-use-cases.md)，找到适合你的配置模板

**预计时间：** 2-3 小时

---

## 三条阅读路径

### 路线 A：先把 Bot 用起来

适合想尽快上手的人。按顺序阅读：

| 章节 | 内容 | 你将学到 |
|------|------|----------|
| [第 0 章](00-before-you-start.md) | 开始之前 | 判断适合性、环境检查、用户画像 |
| [第 1 章](01-quick-start.md) | 5 分钟跑起来 | 安装、配置、第一次对话 |
| [第 2 章](02-soul.md) | 让 Bot 有个性 | 编辑人格、行为、用户画像 |
| [第 3 章](03-skills.md) | 教 Bot 新技能 | 创建自定义 Skill，理解触发机制 |
| [第 4 章](04-local-integration.md) | 本地完整验收 | 端到端测试，分层排查问题 |
| [第 5 章](05-deploy-telegram.md) | 部署到 Telegram | Gateway 模式，接入真实平台 |
| [第 6 章](06-use-cases.md) | 多场景案例库 | 文件管理/代码助手/知识管理模板 |

**学完后你应该能：**
- 跑通 nanobot
- 改人格、规则、用户画像
- 写一个自己的 Skill
- 把 Bot 部署到 Telegram

---

<a id="path-b"></a>

### 路线 B：知其然，也知其所以然

适合想理解 nanobot 主干机制的人。推荐读法：

1. 先读新手村（第 0-6 章），知道功能入口
2. 再对照读 `build/` 中对应章节，理解实现原理

| 新手村章节 | 对应进阶营章节 | 核心概念 |
|-----------|--------------|---------|
| 第 1 章 | [build/第 1 章](build/01-simplest-agent.md) | Provider、Session |
| 第 3 章 | [build/第 5 章](build/05-skills-and-beyond.md) | Skill 渐进式加载 |
| 第 5 章 | [build/第 4 章](build/04-message-bus.md) | MessageBus、多平台 |

**学完后你应该能解释：**
- Provider 是什么
- AgentLoop 怎么工作
- Skill 为什么能按需加载
- Memory / Dream 如何把长对话沉淀成长期记忆
- MessageBus 为什么能支持多平台

---

<a id="path-c"></a>

### 路线 C：自己写一个 Bot

适合程序员。按顺序阅读：

| 章节 | 代码量 | 你将构建 | 对应 nanobot 模块 |
|------|--------|---------|------------------|
| [导读](build/README.md) | 0 | 理解教学目标 | 整体架构 |
| [第 1 章](build/01-simplest-agent.md) | ~40 行 | 能对话的 LLM 客户端 | `providers/` |
| [第 2 章](build/02-tool-system.md) | ~200 行 | 能执行命令的 Agent | `agent/tools/`, `agent/loop.py` |
| [第 3 章](build/03-memory-and-context.md) | ~300 行 | 有记忆、有个性的 Agent | `agent/context.py`, `session/` |
| [第 4 章](build/04-message-bus.md) | ~400 行 | 能接入多平台的 Agent | `bus/`, `channels/` |
| [第 5 章](build/05-skills-and-beyond.md) | ~500 行 | 可动态扩展的完整 Agent | `agent/skills.py` |
| [第 6 章](build/06-from-mini-agent-to-real-bot.md) | 架构桥接 | 从教学版走向可维护项目 | 工程化边界 |

**学完后你应该能：**
- 写出一个教学版多轮 Agent
- 给它加工具、记忆、技能和多平台入口
- 理解它距离工程化产品还差什么

---

## 🎯 第一次成功的最低标准

如果你是第一次跟做，不要一开始就追求"全都懂了"或"已经上线"。先把下面 4 项做出来：

- [ ] 在 CLI 中成功得到一次正常回复
- [ ] 修改 `SOUL.md` 或 `AGENTS.md` 后，下一次回复出现明显变化
- [ ] 至少有一个自定义 Skill 成功触发一次
- [ ] 能分清"Bot 本身是否正常"和"聊天平台是否接通"是两层不同问题

**这 4 项都成立后，再继续做 Telegram、Docker、systemd、多实例这些内容，效率会高很多。**

---

## 📚 附录与配套材料

- [附录：环境预检](appendix-environment-precheck.md) — 适合在"还没开始跟做，但不确定本机和账号是否准备好"时先看
- [附录：统一排障手册](appendix-troubleshooting-guide.md) — 按层级组织的系统化诊断方案（环境/配置/行为/部署）
- [附录：常见坑与排障](appendix-troubleshooting.md) — 适合在"哪里不对劲，但还不知道是哪一层出问题"时查
- [附录：术语表](appendix-glossary.md) — 核心概念和技术术语速查
- [诊断脚本集合](scripts/README.md) — 自动化环境检查、配置验证、Skill 诊断工具
- [进阶营配套示例](examples/part2/README.md) — 给程序员的章节快照代码，方便对照 `build/` 边读边跑

---

## 🛠️ 前置准备

- Python >= 3.11
- 一个 LLM API Key（OpenRouter / OpenAI / Claude / DeepSeek / 智谱 / 通义千问等任意一个）
- 终端 / 命令行工具
- 如果你要跟做新手村里的 Skill 示例，建议本机已安装 `curl` 和 `python3`

**不确定环境是否准备好？** 先看 [第 0 章：开始之前](00-before-you-start.md)

---

## 📝 约定

- `~/.nanobot/` — nanobot 的默认数据目录
- `~/.nanobot/config.json` — 配置文件
- `~/.nanobot/workspace/` — 工作区（Bot 的"大脑"所在）
- 代码引用优先使用模块路径，如 `nanobot/agent/loop.py`
- 如果出现行号，只把它当作阅读时的辅助定位，因为实现会随版本变化

---

## 🎓 学完后你能做到什么

- **对使用者**：你可以定制自己的 nanobot，并把它部署到真实聊天平台
- **对学习者**：你可以解释 Prompt、Skill、Memory / Dream、MessageBus 这些主干设计
- **对程序员**：你可以写出一个属于自己的教学版 Agent，并知道下一步该补哪些工程能力

---

## ⚙️ 本教程的边界

这套教程解决的是"理解主干机制"和"做出自己的 bot 原型"。

它不会直接替你解决所有生产问题，例如：
- 并发控制
- 错误恢复与重试
- 平台边界情况处理
- ACL 与安全沙箱
- 完整测试与部署体系

这些会在进阶营的最后一章集中说明。想核对真实实现时，请回到对应源码模块查看。

---

## 🤝 贡献与反馈

如果你发现教程中的错误、不清楚的地方，或者有改进建议：
- 提交 Issue：https://github.com/HKUDS/nanobot/issues
- 提交 Pull Request：https://github.com/HKUDS/nanobot/pulls

---

## 📖 本地阅读

如果你只是想快速读 Markdown，直接用编辑器打开即可。

如果你希望它像一个带目录、搜索和上下页导航的文档站来阅读，仓库已经提供了 MkDocs 配置。clone 到本地后，在仓库根目录执行：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-docs.txt
python -m mkdocs serve
```

然后打开 `http://127.0.0.1:8000`。

如果 `python3 -m venv .venv` 报 `ensurepip is not available`，通常说明系统没装 `venv` 组件；在 Debian / Ubuntu 上先安装 `python3-venv` 再重试。

---

## 🌐 GitHub Pages

仓库已经补上 `GitHub Pages` 发布工作流，使用 `MkDocs` 构建静态站点，再由 GitHub Actions 自动部署。

- 工作流文件：`.github/workflows/pages.yml`
- 目标地址：`https://sine-io.github.io/byte-of-nanobot/`

第一次启用时，到仓库的 `Settings -> Pages` 中确认发布来源使用 `GitHub Actions`。之后只要向 `main` 分支推送，文档站就会自动重新发布。

---

## 📋 完整章节概览

### 新手村：使用 nanobot

| 章节 | 内容 | 你将学到 |
|------|------|----------|
| [第 0 章](00-before-you-start.md) | 开始之前 | 判断适合性、环境检查、用户画像、快速诊断 |
| [第 1 章](01-quick-start.md) | 5 分钟跑起来 | 安装、配置、第一次对话、错误诊断树 |
| [第 2 章](02-soul.md) | 让 Bot 有个性 | 编辑人格、行为、用户画像、三个配置模板 |
| [第 3 章](03-skills.md) | 教 Bot 新技能 | 创建 Skill、理解触发机制、分级难度示例 |
| [第 4 章](04-local-integration.md) | 本地完整验收 | 端到端测试、分层排查、验收记录模板 |
| [第 5 章](05-deploy-telegram.md) | 部署到 Telegram | Gateway 模式、MessageBus、持续运行方案 |
| [第 6 章](06-use-cases.md) | 多场景案例库 | 文件管理/代码助手/知识管理完整配置 |

### 进阶营：从零复刻 nanobot

| 章节 | 代码量 | 你将构建 | 对应 nanobot 模块 |
|------|--------|---------|------------------|
| [导读](build/README.md) | - | 理解教学目标和架构演进 | 整体架构 |
| [第 1 章](build/01-simplest-agent.md) | ~40 行 | 能对话的 LLM 客户端 | `providers/` |
| [第 2 章](build/02-tool-system.md) | ~200 行 | 能执行命令的 Agent | `agent/tools/`, `agent/loop.py` |
| [第 3 章](build/03-memory-and-context.md) | ~300 行 | 有记忆、有个性的 Agent | `agent/context.py`, `session/` |
| [第 4 章](build/04-message-bus.md) | ~400 行 | 能接入多平台的 Agent | `bus/`, `channels/` |
| [第 5 章](build/05-skills-and-beyond.md) | ~500 行 | 可动态扩展的完整 Agent | `agent/skills.py` |
| [第 6 章](build/06-from-mini-agent-to-real-bot.md) | 架构桥接 | 从教学版走向可维护项目 | 工程化边界 |

---

## 🆘 遇到问题？

1. **环境问题（安装、依赖）** → [附录：环境预检](appendix-environment-precheck.md)
2. **系统化排障** → [附录：统一排障手册](appendix-troubleshooting-guide.md)
3. **常见坑速查** → [附录：常见坑与排障](appendix-troubleshooting.md)
4. **GitHub Issues** → https://github.com/HKUDS/nanobot/issues

---

**现在开始吧！** → [第 0 章：开始之前](00-before-you-start.md)
