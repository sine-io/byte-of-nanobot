# 阅读指南

本教程提供三条阅读路线，选择最适合你的开始：

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

1. 读 [第 0 章：开始之前](zero/00-before-you-start.md)，确认环境准备好
2. 读 [第 1 章：5 分钟跑起来](zero/01-quick-start.md)，把 CLI 跑通
3. 读 [第 2 章：让 Bot 有个性](zero/02-soul.md) 和 [第 3 章：教 Bot 新技能](zero/03-skills.md)，完成"人格 + 规则 + Skill"闭环
4. 读 [第 4 章：本地完整验收](zero/04-local-integration.md)，在本地完成端到端测试
5. 读 [第 5 章：部署到 Telegram](zero/05-deploy-telegram.md)，接入真实聊天平台
6. 读 [第 6 章：多场景案例库](zero/06-use-cases.md)，找到适合你的配置模板

**预计时间：** 2-3 小时

---

## 三条阅读路径

### 路线 A：先把 Bot 用起来

适合想尽快上手的人。按顺序阅读：

| 章节 | 内容 | 你将学到 |
|------|------|----------|
| [第 0 章](zero/00-before-you-start.md) | 开始之前 | 判断适合性、环境检查、用户画像 |
| [第 1 章](zero/01-quick-start.md) | 5 分钟跑起来 | 安装、配置、第一次对话 |
| [第 2 章](zero/02-soul.md) | 让 Bot 有个性 | 编辑人格、行为、用户画像 |
| [第 3 章](zero/03-skills.md) | 教 Bot 新技能 | 创建自定义 Skill，理解触发机制 |
| [第 4 章](zero/04-local-integration.md) | 本地完整验收 | 端到端测试，分层排查问题 |
| [第 5 章](zero/05-deploy-telegram.md) | 部署到 Telegram | Gateway 模式，接入真实平台 |
| [第 6 章](zero/06-use-cases.md) | 多场景案例库 | 文件管理/代码助手/知识管理模板 |

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
2. 再对照读进阶营中对应章节，理解实现原理

| 新手村章节 | 对应进阶营章节 | 核心概念 |
|-----------|--------------|---------|
| 第 1 章 | [进阶营第 1 章](hero/01-simplest-agent.md) | Provider、Session |
| 第 3 章 | [进阶营第 5 章](hero/05-skills-and-beyond.md) | Skill 渐进式加载 |
| 第 5 章 | [进阶营第 4 章](hero/04-message-bus.md) | MessageBus、多平台 |

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
| [导读](hero/README.md) | 0 | 理解教学目标 | 整体架构 |
| [第 1 章](hero/01-simplest-agent.md) | ~40 行 | 能对话的 LLM 客户端 | `providers/` |
| [第 2 章](hero/02-tool-system.md) | ~200 行 | 能执行命令的 Agent | `agent/tools/`, `agent/loop.py` |
| [第 3 章](hero/03-memory-and-context.md) | ~300 行 | 有记忆、有个性的 Agent | `agent/context.py`, `session/` |
| [第 4 章](hero/04-message-bus.md) | ~400 行 | 能接入多平台的 Agent | `bus/`, `channels/` |
| [第 5 章](hero/05-skills-and-beyond.md) | ~500 行 | 可动态扩展的完整 Agent | `agent/skills.py` |
| [第 6 章](hero/06-from-mini-agent-to-real-bot.md) | 架构桥接 | 从教学版走向可维护项目 | 工程化边界 |

**配套资料：**
- [进阶营配套示例代码](examples/part2/README.md)
- [诊断脚本](scripts/README.md)

---

## 附录资源

- [环境预检](appendix/environment-precheck.md) - 安装前的系统检查
- [统一排障手册](appendix/troubleshooting-guide.md) - 常见问题解决方案
- [常见坑与排障](appendix/troubleshooting.md) - 典型问题案例
- [术语表](appendix/glossary.md) - 关键概念速查

---

## 开始学习

👉 如果是第一次学习，从 [第 0 章：开始之前](zero/00-before-you-start.md) 开始
