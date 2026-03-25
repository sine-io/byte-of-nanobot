# Part 2 配套示例

> 这些文件是 `build/` 章节的教学快照，方便你边读边跑。它们的目标是降低复制 Markdown 代码块的成本，不是替代正文讲解。

## 怎么用

推荐顺序：

1. 先读对应章节，搞清楚这一章新增了什么
2. 再打开这里的示例文件
3. 最后运行并做正文里的“最小验证步骤”

## 文件说明

- [ch01-mini-agent.py](ch01-mini-agent.py)：对应 [第 1 章：最简 Agent](../../build/01-simplest-agent.md)
- [ch02-mini-agent-with-tools.py](ch02-mini-agent-with-tools.py)：对应 [第 2 章：工具系统](../../build/02-tool-system.md)
- [ch03-mini-agent-with-memory.py](ch03-mini-agent-with-memory.py)：对应 [第 3 章：记忆与上下文](../../build/03-memory-and-context.md)
- [ch04-mini-agent-gateway.py](ch04-mini-agent-gateway.py)：对应 [第 4 章：消息总线](../../build/04-message-bus.md)
- [ch05-skills-loader.py](ch05-skills-loader.py)：对应 [第 5 章：技能与扩展](../../build/05-skills-and-beyond.md)

## 边界说明

- 这些文件是**教学快照**，不是生产级项目结构
- 它们优先服务于“看懂主干机制”，不是“完整复刻 nanobot”
- 第 6 章主要是工程化路线图，所以没有单独的可运行脚本

## 推荐读法

如果你是第一次读 Part 2，建议：

1. 先从 `ch01` 到 `ch03`
2. `ch04` 先只跑 CLI 路径，理解总线，不必一开始就接 Telegram
3. `ch05` 先看 `SkillsLoader` 如何扫描和构建摘要，再回正文理解为什么 Skill 不等于 Tool

如果你现在想返回正文：

- 回 Part 2 导读：[build/README.md](../../build/README.md)
- 回仓库首页：[README.md](../../README.md)
- 查排障附录：[appendix-troubleshooting.md](../../appendix-troubleshooting.md)
