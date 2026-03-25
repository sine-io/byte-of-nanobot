# 第 5 章：技能与扩展

> 让 Agent 的能力可以动态扩展，不改代码就能学会新技能。

## 问题

前四章的 Agent 能力是硬编码的——exec、read_file、write_file。想加"查天气"？改代码。想加"操作 GitHub"？改代码。

但 nanobot 的用户只需要往 `workspace/skills/` 放一个 Markdown 文件，Agent 就自动学会了新技能。这是怎么做到的？

## 核心原理：技能 = 动态 Prompt

技能并不是新的工具（Tool），而是**注入到 System Prompt 中的领域知识**。

Agent 已经有 `exec` 工具，能执行任何命令。它缺的不是执行能力，而是**知识**——不知道用什么命令查天气、用什么 API 查汇率。

Skill 就是把这些知识教给它：

```markdown
# Weather Skill

用 curl 查天气（不需要 API Key）：
\```bash
curl -s "wttr.in/Beijing?format=3"
\```
```

Agent 读到这个 Skill 后，下次用户问"北京天气怎么样"，它就知道该用 `exec` 执行 `curl` 命令了。

### 为什么 Skill 不是 Tool

这里一定要把边界掰开：

- `Tool` 解决的是“Agent **能不能做** 这件事”
- `Skill` 解决的是“Agent **知不知道什么时候该做、该怎么做** 这件事”

比如 `exec` 这个工具早就已经给了 Agent“执行命令”的能力；`weather` Skill 做的，是补上“查天气时应该执行什么命令”这部分知识。

如果你把两者混为一谈，系统就会越来越臃肿：每新增一个场景，都要往底层代码里塞一个新工具。

## 实现 SkillsLoader

对应 `nanobot/agent/skills.py`（229 行）：

```python
import re
from pathlib import Path

class SkillsLoader:
    """技能加载器——对应 nanobot/agent/skills.py"""

    def __init__(self, workspace: Path, builtin_dir: Path | None = None):
        self.workspace_skills = workspace / "skills"
        self.builtin_skills = builtin_dir

    def list_skills(self) -> list[dict]:
        """扫描所有可用技能，返回名字+描述+路径"""
        skills = []
        # 工作区技能优先
        if self.workspace_skills.exists():
            for d in self.workspace_skills.iterdir():
                skill_file = d / "SKILL.md"
                if d.is_dir() and skill_file.exists():
                    skills.append({
                        "name": d.name,
                        "path": str(skill_file),
                        "description": self._get_description(skill_file),
                    })
        # 然后加载内置技能（不覆盖同名的工作区技能）
        if self.builtin_skills and self.builtin_skills.exists():
            existing = {s["name"] for s in skills}
            for d in self.builtin_skills.iterdir():
                skill_file = d / "SKILL.md"
                if d.is_dir() and skill_file.exists() and d.name not in existing:
                    skills.append({
                        "name": d.name,
                        "path": str(skill_file),
                        "description": self._get_description(skill_file),
                    })
        return skills

    def build_skills_summary(self) -> str:
        """构建技能摘要（始终注入 System Prompt）"""
        skills = self.list_skills()
        if not skills:
            return ""
        lines = ["<skills>"]
        for s in skills:
            lines.append(f'  <skill>')
            lines.append(f'    <name>{s["name"]}</name>')
            lines.append(f'    <description>{s["description"]}</description>')
            lines.append(f'    <location>{s["path"]}</location>')
            lines.append(f'  </skill>')
        lines.append("</skills>")
        return "\n".join(lines)

    def _get_description(self, path: Path) -> str:
        """从 frontmatter 提取 description"""
        content = path.read_text(encoding="utf-8")
        if content.startswith("---"):
            match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if match:
                for line in match.group(1).split("\n"):
                    if line.startswith("description:"):
                        return line.split(":", 1)[1].strip().strip("\"'")
        return path.parent.name
```

> 这个 `_get_description` 是故意写小的教学版，只解析**单行** `description:`。它足够说明“先扫元信息，再按需加载正文”的原理，但不等于生产实现。真实项目应使用完整的 frontmatter/YAML 解析，并把 `description` 视为技能匹配的主要线索，而不是唯一决定因素。

### 渐进式加载的三层设计

nanobot 不会把所有 Skill 的完整内容都塞进 System Prompt。它用**三层加载**：

```
第 1 层（始终加载）：Skill 名字 + 描述    → ~50 tokens / Skill
第 2 层（按需加载）：Skill 的完整内容      → Agent 用 read_file 自行读取
第 3 层（按需加载）：scripts / references  → Agent 按需读取
```

这意味着 100 个 Skill 只多占 ~5000 tokens 的 System Prompt 空间。Agent 只在需要时才读取具体 Skill 的完整内容。

在 ContextBuilder 中集成：

```python
class ContextBuilder:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.skills = SkillsLoader(workspace)

    def build_system_prompt(self) -> str:
        parts = [self._get_identity()]

        # ... bootstrap files, memory (同第 3 章) ...

        # 技能摘要
        summary = self.skills.build_skills_summary()
        if summary:
            parts.append(
                "# Skills\n\n"
                "以下技能扩展了你的能力。需要时用 read_file 读取 SKILL.md 获取详情。\n\n"
                + summary
            )

        return "\n\n---\n\n".join(parts)
```

## 创建你的第一个 Skill

```bash
mkdir -p ~/.mini-agent/workspace/skills/weather
```

创建 `~/.mini-agent/workspace/skills/weather/SKILL.md`：

```markdown
---
name: weather
description: Get current weather and forecasts. Use when user asks about weather.
---

# Weather

Free weather via wttr.in (no API key):

\```bash
# 简洁格式
curl -s "wttr.in/CityName?format=3"

# 详细格式
curl -s "wttr.in/CityName?format=%l:+%c+%t+%h+%w"
\```

URL-encode spaces: `wttr.in/New+York`
```

现在当用户问天气时，Agent 会：

1. 看到 Skills 摘要中有 `weather`（描述匹配"weather"）
2. 用 `read_file` 读取 `SKILL.md` 全文
3. 学到用 `curl` 查天气的方法
4. 用 `exec` 执行 `curl` 命令
5. 把结果转述给用户

**没有任何代码改动。**

### 什么时候该用 `scripts/`

第一次教学时，直接把命令写进 `SKILL.md` 很方便。但当某段逻辑开始变长、变脆弱、需要重复使用时，就应该考虑把它下沉成 `scripts/`：

- 命令特别长
- 解析逻辑开始依赖多步转换
- 你希望同样操作每次都更稳定
- 你不希望模型在执行前随意改写关键步骤

Skill 负责告诉 Agent“什么时候调用这个脚本”；脚本负责把事情稳定做对。

## 架构全景

经过五章的构建，我们的 Agent 已经拥有了 nanobot 的核心架构：

```
┌─────────────────────────────────────────────────┐
│                  config.json                     │
│          (providers, channels, tools)            │
└────────────────────┬────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    ↓                ↓                ↓
Provider        AgentLoop         Channels
(LLM 连接)    (核心引擎)       (平台集成)
    │                │                │
    │     ┌──────────┼──────────┐     │
    │     ↓          ↓          ↓     │
    │  Context    ToolReg    Session   │
    │  Builder    istry      Manager  │
    │     │          │                │
    │  ┌──┼──┐    ┌──┼──┐            │
    │  ↓  ↓  ↓    ↓  ↓  ↓            │
    │ SOUL mem skills exec read write │
    │ .md  ory       file  file      │
    │                                 │
    └─────────── MessageBus ──────────┘
```

## 对照 nanobot 源码

下面这些代码量和能力数量只用于帮助你建立规模感，具体以你查看仓库时的 nanobot 版本为准。

| 我们构建的 | 代码量 | nanobot 对应 | nanobot 代码量 |
|-----------|--------|-------------|---------------|
| LLM 调用 | ~10 行 | `providers/` | ~800 行（多 provider 支持） |
| Tool 基类 + Registry | ~50 行 | `agent/tools/base.py` + `registry.py` | ~250 行（含校验） |
| 3 个工具 | ~80 行 | `agent/tools/*.py` | ~1000 行（6 个工具 + MCP） |
| ReAct 循环 | ~30 行 | `agent/loop.py` | ~500 行（含并发、进度、整合） |
| Session 管理 | ~40 行 | `session/manager.py` | ~214 行（含迁移、元数据） |
| Context Builder | ~30 行 | `agent/context.py` | ~194 行（含多模态） |
| Memory 系统 | ~30 行 | `agent/memory.py` | ~158 行（含 function calling 整合） |
| MessageBus | ~15 行 | `bus/queue.py` | ~45 行 |
| Channel 基类 | ~20 行 | `channels/base.py` | ~117 行（含 ACL） |
| Skills 加载 | ~50 行 | `agent/skills.py` | ~229 行（含 frontmatter 解析、依赖检查） |
| **总计** | **~350 行** | **核心代码** | **数千行级别** |

我们用 350 行实现了 nanobot 数千行级别核心骨架的教学版。差距在哪里？在**生产级的健壮性**：
- 参数校验与类型转换
- 错误恢复与重试
- 多平台的边界情况处理
- 安全防护（ACL、路径限制、命令过滤）
- 并发控制（多个用户同时对话）
- 记忆整合（上下文窗口管理）

这些是从"能跑"到"能用"的距离。

## nanobot 还有什么我们没做的？

| 功能 | nanobot 模块 | 作用 |
|------|-------------|------|
| 定时任务 | `cron/service.py` | 让 Agent 定时执行任务 |
| 心跳服务 | `heartbeat/service.py` | 定期检查 HEARTBEAT.md 并执行 |
| 子 Agent | `agent/subagent.py` | 后台派生子任务 |
| MCP 协议 | `agent/tools/mcp.py` | 连接外部工具服务器 |
| 多个 Channel | `channels/*.py` | Telegram / Discord / Slack / 飞书 / 钉钉 / QQ / Email / WhatsApp / Matrix / Mochat |
| Provider 注册表 | `providers/registry.py` | 声明式配置多种 LLM 提供商 |

但它们的底层原理和我们构建的完全一样——都是在这个骨架上增加模块。

## 你接下来可以做什么？

1. **先读下一章**：如果你准备把教学版继续发展成自己的项目，先看第 6 章，明确工程化边界
2. **读 nanobot 源码**：现在你已经理解了架构，读源码会非常顺畅
3. **给你的 Mini Agent 加功能**：
   - 加一个 `web_search` 工具（用 Brave Search API）
   - 实现记忆整合（第 3 章的 `consolidate_memory`）
   - 接入 Telegram（第 4 章的 TelegramChannel）
4. **创建你自己的 Skills**：查天气、查汇率、操作 GitHub...
5. **贡献 nanobot**：项目欢迎 PR，代码库刻意保持精简

## 本章你真正学到的抽象

这一章最核心的抽象是：很多“新能力”并不需要新增代码级工具，而是可以作为“按需加载的领域知识”接入系统。

也就是说，你现在手里有两种扩展手段：

- `Tool`：给 Agent 新的执行能力
- `Skill`：给 Agent 新的使用知识和工作方法

把两者分开，系统才不会每加一种场景能力就膨胀一层底层代码。

## 最小验证步骤

建议至少做下面 4 个验证：

1. 创建一个最简单的 Skill，确认它能出现在 skills summary 中
2. 提一个与 `description` 强相关的问题，确认 Agent 会读取 `SKILL.md`
3. 让 Skill 指导 Agent 调用现有工具，确认“知识”确实能转化成行动
4. 再创建一个同名 workspace skill 覆盖内置 skill，确认优先级符合预期

## 常见失败点

- Skill 存在但不触发：首先怀疑 `description` 写法，而不是怀疑加载器本身
- Skill 很长但效果很差：通常是写成了文档，而不是写成了 Agent 可执行的操作说明
- 什么都往 Skill 里塞：如果需要稳定的输入输出、确定性执行和强校验，应该下沉成 Tool 或脚本，而不是只靠提示词
- workspace skill 没覆盖 builtin：先检查目录名，再检查扫描顺序，不要只看 frontmatter 的 `name`

## 配套示例

- 对应代码快照：[examples/part2/ch05-skills-loader.py](../examples/part2/ch05-skills-loader.py)
- 配套目录说明：[examples/part2/README.md](../examples/part2/README.md)

这个示例聚焦在 `SkillsLoader` 和技能摘要构建上，因为第 5 章真正新增的抽象核心就在这里。

---

## 回顾：五章走过的路

```
第 1 章  →  第 2 章  →  第 3 章  →  第 4 章  →  第 5 章
40 行       200 行      300 行      400 行      500 行
聊天       能做事      有记忆      多平台    可扩展
Chatbot     Agent      有个性     Gateway    Skills
```

每一步都是一个关键概念的引入：

| 章节 | 引入的概念 | 一句话总结 |
|------|-----------|-----------|
| 1 | LLM API | 调 API 就能对话 |
| 2 | Function Calling + ReAct | 让 LLM 能调用工具，循环直到完成 |
| 3 | Session + Context + Memory | 记住对话、组装 Prompt、持久化记忆 |
| 4 | MessageBus + Channel | 解耦 I/O，一个 Agent 服务多平台 |
| 5 | Skills | 动态注入领域知识，不改代码扩展能力 |

这就是一个 AI Agent 框架的全部核心。nanobot 用数千行级别的工程实现把它做稳，我们用 350 行教学代码把它讲清楚。

---

[← 上一章：消息总线](04-message-bus.md) | [下一章：从 Mini Agent 到真实项目 →](06-from-mini-agent-to-real-bot.md) | [回到目录](README.md)
