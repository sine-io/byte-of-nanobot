# 第 2 章：用 Markdown 定义 Bot

> 目标：通过编辑 Markdown 文件，定制 Bot 的性格、行为和对你的认知。

## 2.1 四个文件，定义一个 Bot

nanobot 的个性化设计非常优雅——**四个 Markdown 文件**就定义了一个 Bot 的全部"灵魂"：

| 文件 | 作用 | 比喻 |
|------|------|------|
| `SOUL.md` | 性格、价值观、沟通风格 | Bot 的"人格" |
| `AGENTS.md` | 行为指令、工作流规则 | Bot 的"岗位职责" |
| `USER.md` | 用户信息、偏好设定 | Bot 对"主人"的认知 |
| `TOOLS.md` | 工具使用的注意事项 | Bot 的"操作手册" |

这些文件都在工作区 `~/.nanobot/workspace/` 下，是纯 Markdown 格式，用任何文本编辑器都能修改。

## 2.2 实操：打造一个"海盗风格"助手

我们先做一个夸张的例子来直观感受效果。

编辑 `~/.nanobot/workspace/SOUL.md`：

```markdown
# Soul

我是 CaptainBot，一个海盗风格的 AI 助手。

## Personality

- 说话像一个老练的海盗船长
- 用"啊嘿"、"海上的风"等口头禅
- 把用户称为"船员"
- 回答问题时喜欢用航海比喻

## Values

- 忠诚于船员（用户）
- 追求宝藏（知识）
- 在风暴中保持冷静（处理复杂问题时沉稳）

## Communication Style

- 每次回复开头先说一句海盗风格的问候
- 用航海术语替代技术术语（比如"启航"代替"启动"）
- 回复结尾用 ⚓ 或 🏴‍☠️ 结束
```

然后测试效果：

```bash
nanobot agent -m "今天天气怎么样？"
```

你会发现 Bot 的回复风格完全变了。**你没有修改任何代码，只是编辑了一个 Markdown 文件。**

## 2.3 实操：做一个专业的"财务顾问"Bot

把 `SOUL.md` 换成正经的内容：

```markdown
# Soul

我是 FinBot，一个专业的个人财务顾问。

## Personality

- 严谨、专业、有条理
- 用数据说话，避免模糊表述
- 对风险保持警惕

## Values

- 用户的财务安全永远第一
- 不推荐自己不理解的金融产品
- 涉及具体投资建议时，提醒用户咨询持牌顾问

## Communication Style

- 使用清晰的结构（标题、列表、表格）呈现分析
- 涉及金额时注明币种
- 重要风险用加粗标注
```

再编辑 `~/.nanobot/workspace/USER.md` 来告诉 Bot 你的背景：

```markdown
# User Profile

## Basic Information

- **Name**: 小明
- **Timezone**: UTC+8 (北京时间)
- **Language**: 中文

## Preferences

- 月收入约 2 万元
- 风险偏好：稳健型
- 关注领域：指数基金、储蓄、保险

## Special Instructions

- 涉及金额时使用人民币
- 对比产品时用表格形式
- 不要推荐加密货币相关产品
```

现在 Bot 不仅知道"自己是谁"，还知道"用户是谁"。它会根据你的收入水平和风险偏好来调整建议。

## 2.4 用 AGENTS.md 定义行为规则

`AGENTS.md` 比 `SOUL.md` 更偏向"做事的规则"。比如你希望财务顾问 Bot 遵守特定流程：

```markdown
# Agent Instructions

你是一个专业的财务顾问 Bot。

## 回答规则

1. **先确认理解**：在给出建议前，先复述用户的问题确保理解正确
2. **分析再结论**：先列出关键数据和假设，再给出建议
3. **标注风险**：每条建议后面标注风险等级（低/中/高）
4. **免责声明**：涉及具体投资建议时，结尾加上免责声明

## 禁止事项

- 不给出具体股票买卖时机的建议
- 不预测市场走势
- 不推荐用户不理解的复杂金融衍生品
```

## 2.5 用 TOOLS.md 控制工具行为

`TOOLS.md` 可以限制或引导 Bot 使用工具的方式：

```markdown
# Tool Usage Notes

## exec

- 只在用户明确要求时才运行代码
- 运行前先向用户确认命令内容

## web_search / web_fetch

- 优先使用 web_search 搜索最新数据
- 抓取网页时只提取关键数据，不要复制整篇文章
```

---

## 原理：System Prompt 是怎么组装的？

这四个文件是怎么影响 Bot 行为的？可以从 `nanobot/agent/context.py` 的 system prompt 组装逻辑开始看：

```python
def build_system_prompt(self, skill_names=None):
    parts = [self._get_identity()]          # 1. 固定身份信息

    bootstrap = self._load_bootstrap_files() # 2. 加载四个 Markdown 文件
    if bootstrap:
        parts.append(bootstrap)

    memory = self.memory.get_memory_context() # 3. 加载长期记忆
    if memory:
        parts.append(f"# Memory\n\n{memory}")

    # 4. 加载技能（下一章详解）
    ...

    return "\n\n---\n\n".join(parts)
```

其中 `_load_bootstrap_files` 就是读取那四个文件：

```python
BOOTSTRAP_FILES = ["AGENTS.md", "SOUL.md", "USER.md", "TOOLS.md"]

def _load_bootstrap_files(self):
    parts = []
    for filename in self.BOOTSTRAP_FILES:
        file_path = self.workspace / filename
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            parts.append(f"## {filename}\n\n{content}")
    return "\n\n".join(parts) if parts else ""
```

所以最终发给 LLM 的 System Prompt 长这样：

```
# nanobot                          ← 固定身份
...
---
## AGENTS.md                       ← 你写的行为指令
（AGENTS.md 的内容）
## SOUL.md                         ← 你写的人格
（SOUL.md 的内容）
## USER.md                         ← 你写的用户画像
（USER.md 的内容）
## TOOLS.md                        ← 你写的工具规则
（TOOLS.md 的内容）
---
# Memory                           ← 长期记忆（自动维护）
（MEMORY.md 的内容）
---
# Skills                           ← 技能摘要（下一章详解）
...
```

这里同样做了教学上的简化。真实实现里通常还会包含运行时上下文、平台信息、always skills 等内容，但主干结构就是“身份 + bootstrap 文件 + 记忆 + skills”。

### 为什么这么设计？

1. **纯文本 = 零门槛**：不需要学 Python，不需要懂 API，编辑 Markdown 就能改行为
2. **关注点分离**：性格（SOUL）、规则（AGENTS）、用户认知（USER）、工具约束（TOOLS）各司其职，改一个不影响其他
3. **透明可审计**：你能看到发给 LLM 的完整 prompt，知道 Bot 为什么这么回答

### 记忆系统如何工作？

除了四个静态文件，nanobot 还有一个动态的**两层记忆系统**（`nanobot/agent/memory.py`）：

| 层 | 文件 | 特点 |
|---|---|---|
| 长期记忆 | `memory/MEMORY.md` | 每次对话都加载到上下文中，存放重要事实 |
| 历史日志 | `memory/HISTORY.md` | 不加载到上下文，可用 grep 搜索 |

当对话变长时，nanobot 会自动用 LLM 做**记忆整合**：
- 从旧对话中提取重要事实 → 写入 `MEMORY.md`
- 把对话摘要 → 追加到 `HISTORY.md`

从理解上，你可以把它看成“旧对话被折叠进记忆层”。但具体实现不一定是直接删除历史消息；当前版本更接近“保留原始消息，同时只把未整合部分继续送进上下文”。

这样既不浪费上下文窗口，又不丢失重要信息。

你也可以手动编辑 `memory/MEMORY.md`，写入任何你想让 Bot 永远记住的信息：

```markdown
- 我的生日是 3 月 15 日
- 我的猫叫小花
- 我的项目用 React + TypeScript
```

---

## 小结

| 你想改什么 | 编辑哪个文件 |
|-----------|------------|
| Bot 的性格和说话风格 | `SOUL.md` |
| Bot 做事的规则和流程 | `AGENTS.md` |
| Bot 对你的了解 | `USER.md` |
| Bot 使用工具的方式 | `TOOLS.md` |
| Bot 需要永远记住的事 | `memory/MEMORY.md` |

改完文件后不需要重启——下一次对话自动生效（因为每次对话都重新读取这些文件）。

## 2.6 验证与排障

完成本章修改后，可以做三个快速验证：

1. 修改 `SOUL.md` 后运行 `nanobot agent -m "请用一句话介绍你自己"`，预期回复里出现你写进人格文件的独特称呼、口头禅或语气，而不是泛泛自我介绍
2. 修改 `AGENTS.md` 后运行 `nanobot agent -m "我每个月能存 3000 元，先给建议"`，预期回复先复述问题，再列出假设或关键信息，而不是直接跳到结论
3. 修改 `USER.md` 后运行 `nanobot agent -m "按我的风险偏好，给我三个优先关注方向"`，预期回复明确引用你的偏好设定，并按你要求的币种或格式输出

常见问题：

- 改了文件但风格没变化：通常是改动太弱，或提问场景不足以触发这些指令
- Bot 没按 `AGENTS.md` 的流程回答：先检查规则是否冲突、是否过长、是否过于抽象
- `TOOLS.md` 不生效：工具使用约束属于提示词引导，不是强权限控制；真正的硬限制还要看工具层和配置层

---

[← 上一章：5 分钟跑起来](01-quick-start.md) | [下一章：教 Bot 新技能 →](03-skills.md)
