# 进阶营配套示例

> 这些文件是进阶营章节的教学快照，方便你边读边跑。它们的目标是降低复制 Markdown 代码块的成本，不是替代正文讲解。

!!! warning "先看安全边界"
    五个入口都会先打印安全提示。它们**不是生产沙箱**：路径检查和只读命令白名单只是教学防护，不能替代容器、低权限用户、系统调用隔离和网络策略。不要在含敏感文件的目录中运行，也不要交给不受信任用户使用。

## 怎么用

推荐顺序：

1. 先读对应章节，搞清楚这一章新增了什么
2. 再打开这里的示例文件
3. 最后运行并做正文里的“最小验证步骤”

前四个示例会真实调用你配置的模型服务。密钥只从环境变量读取，不会从源码或参数读取：

```bash
python -m pip install openai
test -n "${OPENROUTER_API_KEY}" || echo "请先在当前 shell 设置 OPENROUTER_API_KEY"
export OPENROUTER_MODEL="your-provider-supported-model"
python docs/zh-cn/examples/hero/ch01-mini-agent.py
```

可选的 `OPENROUTER_BASE_URL` 用于兼容端点。不要把密钥写进命令历史、示例文件或 Git；CI 只做离线语法检查，不需要这些变量。

涉及文件和命令的示例默认用 `TemporaryDirectory` 创建本次进程专属的临时工作区，正常退出后自动清理。若要在重启后继续验证 Session，或让 `ch05` 扫描你准备的 Skill，可以显式设置 `NANOBOT_HERO_WORKSPACE`，但该目录应只放教学数据：

```bash
export NANOBOT_HERO_WORKSPACE="${PWD}/.nanobot-hero-workspace"
```

教学 `exec` 不启动 Shell，只允许 `pwd`、`ls`、`cat`、`head`、`tail`、`wc` 的有限参数；所有文件参数都必须解析到教学工作区内。文件工具也会拒绝绝对路径、`..` 或符号链接造成的越界。

## 文件说明

- [ch01-mini-agent.py](ch01-mini-agent.py)：对应 [第 1 章：最简 Agent](../../hero/01-simplest-agent.md)
- [ch02-mini-agent-with-tools.py](ch02-mini-agent-with-tools.py)：对应 [第 2 章：工具系统](../../hero/02-tool-system.md)
- [ch03-mini-agent-with-memory.py](ch03-mini-agent-with-memory.py)：对应 [第 3 章：记忆与上下文](../../hero/03-memory-and-context.md)
- [ch04-mini-agent-gateway.py](ch04-mini-agent-gateway.py)：对应 [第 4 章：消息总线](../../hero/04-message-bus.md)
- [ch05-skills-loader.py](ch05-skills-loader.py)：对应 [第 5 章：技能与扩展](../../hero/05-skills-and-beyond.md)

## 边界说明

- 这些文件是**教学快照**，不是生产级项目结构
- 它们优先服务于“看懂主干机制”，不是“完整复刻 nanobot”
- 每个文件都带齐本章所需的导入、配置与入口，可以单独阅读；重复代码是为了保持渐进式叙事
- `ch03` 和 `ch04` 的 Bootstrap 只有 `AGENTS.md`、`SOUL.md`、`USER.md`；工具约束来自代码中的 tool schema，不从 `TOOLS.md` 自动加载
- `ch03` 的同一进程内 Session 会持久化到临时目录；要验证“退出后再运行”，必须显式指定专用教学目录
- 第 6 章主要是工程化路线图，所以没有单独的可运行脚本

## 推荐读法

如果你是第一次读进阶营，建议：

1. 先从 `ch01` 到 `ch03`
2. `ch04` 先只跑 CLI 路径，理解总线，不必一开始就接 Telegram
3. `ch05` 默认扫描临时教学工作区；也可以把一个专用练习目录作为唯一参数传入，再看 `SkillsLoader` 如何扫描和构建摘要

如果你现在想返回正文：

- 回进阶营导读：[进阶营导读](../../hero/README.md)
- 回阅读指南：[阅读指南](../../README.md)
- 查排障附录：[统一排障手册](../../appendix/troubleshooting-guide.md)
