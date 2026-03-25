# 第 5 章：做一个真实可用的 Bot

> 目标：把前四章真正串起来，做出一个能在 Telegram 上工作的财务顾问 Bot。
>
> 边界先说清楚：这一章是**教学示例**，不是投资建议模板。凡是涉及汇率、利率、市场价格这类时效性信息，都应该查证并在回复里标注数据来源或查询时间。

## 5.1 这章要完成什么

前四章分别解决了四件事：

- 第 1 章：让 nanobot 跑起来
- 第 2 章：让 Bot 有人格、规则和用户画像
- 第 3 章：让 Bot 学会一个新技能
- 第 4 章：让 Bot 接入 Telegram

这一章不再新增新概念，而是把这些部分拼成一个完整项目。做完后，你会得到一个真正能用的 `FinBot`：

- 在 Telegram 上和你聊天
- 用你定义的风格回答问题
- 遵守你写在 `AGENTS.md` 里的分析流程
- 在需要时调用汇率 Skill

## 5.2 先定清楚：这个 Bot 是干什么的

我们这次做一个**个人财务顾问 Bot**。它的职责很具体：

- 回答基础财务规划问题
- 根据你的风险偏好调整建议
- 需要汇率时调用 `exchange-rate` Skill
- 不给出激进的投机建议

这里有一个重要原则：**先把职责收窄，再谈能力扩展。** 一个“什么都能做”的 Bot 往往最难调好；一个边界明确的 Bot 反而更稳定。

## 5.3 配好工作区文件

先准备 4 个文件。

### `SOUL.md`

编辑 `~/.nanobot/workspace/SOUL.md`：

```markdown
# Soul

我是 FinBot，一个专业、谨慎、结构化的个人财务顾问。

## Personality

- 严谨、克制、清晰
- 不夸大收益，不故作确定
- 面对不完整信息时先补充假设

## Values

- 用户的财务安全优先于“听起来厉害”
- 不推荐自己无法解释清楚的产品
- 尊重风险承受能力差异

## Communication Style

- 先总结问题，再分析，再给建议
- 涉及金额时注明币种
- 重要风险单独列出
```

### `AGENTS.md`

编辑 `~/.nanobot/workspace/AGENTS.md`：

```markdown
# Agent Instructions

你是一个个人财务顾问 Bot。

## 回答流程

1. 先复述问题，确认理解
2. 列出关键假设和已知信息
3. 再给建议，不要直接跳结论
4. 涉及不确定数据时优先查证

## 禁止事项

- 不给出具体股票买卖时机建议
- 不承诺收益
- 不把教育性信息说成个性化投资建议
```

### `USER.md`

编辑 `~/.nanobot/workspace/USER.md`：

```markdown
# User Profile

## Basic Information

- **Name**: 小明
- **Language**: 中文
- **Timezone**: UTC+8

## Preferences

- 风险偏好：稳健型
- 关注领域：储蓄、指数基金、保险
- 输出偏好：喜欢表格和分点说明

## Special Instructions

- 默认用人民币
- 涉及汇率时说明数据来源
```

### `TOOLS.md`

编辑 `~/.nanobot/workspace/TOOLS.md`：

```markdown
# Tool Usage Notes

## exec

- 优先执行短命令
- 如果是外部数据查询，说明所用来源

## web_search / web_fetch

- 只在问题需要最新信息时使用
- 不要复制整篇文章
```

## 5.4 给它一个真正有用的 Skill

延续第 3 章，直接复用已经创建好的 `exchange-rate` Skill。如果你还没做过那一章，先按[第 3 章：教 Bot 新技能](03-skills.md)里的完整示例创建它，这里不再重复贴全文。目录结构仍然是：

```text
~/.nanobot/workspace/
└── skills/
    └── exchange-rate/
        └── SKILL.md
```

这个 Skill 的价值不在于“多一个文件”，而在于它把“汇率怎么查”这件事从 Bot 主体里剥离了出去。Bot 本身不需要硬编码汇率逻辑，只需要在合适的时候读取 Skill 并调用已有工具。

本章只要求它满足两点：

- 能返回明确的汇率或换算结果
- 回复里能说明数据来源，最好顺手带上查询时间

## 5.5 接到 Telegram

在第 1 章已经跑通、且第 4 章已经接入 Telegram 的 `~/.nanobot/config.json` 基础上，至少补齐下面两段；如果 provider 或 model 还没配置好，先回到前两章完成：

```json
{
  "tools": {
    "restrictToWorkspace": true
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "你的Bot Token",
      "allowFrom": ["你的Telegram数字用户ID"]
    }
  }
}
```

这里的 `allowFrom` 要填的是 Telegram 的**数字用户 ID**，不是用户名，也不带 `@`。第一次对外运行前，先把它只设成你自己的 ID，并保持 `restrictToWorkspace: true`。

然后启动：

```bash
nanobot gateway
```

如果日志里看到了 Telegram channel 已启用，就去 Telegram 给 Bot 发第一条消息。

如果没有回复，先回到[第 4 章：先部署到 Telegram](04-deploy.md)里的排障清单，优先检查 `allowFrom`、token 和 `gateway` 日志。

## 5.6 做一次完整对话

你可以用下面三轮来验证它是不是真的“串起来了”。

### 第 1 轮：看人格和流程

```text
我每个月能存 5000 元，应该先做什么理财准备？
```

最低通过标准：

- 回复开头先复述你的问题，而不是直接给结论
- 回复里能看出“已知信息 / 假设 / 建议”这类结构化分段
- 不出现“梭哈”“保证收益”这类激进表述

### 第 2 轮：看用户画像

```text
按我的风险偏好，你会先关注哪些方向？
```

最低通过标准：

- 回复里明确提到“稳健型”或等价表述
- 涉及金额时默认用人民币
- 输出形式符合你在 `USER.md` 中写的偏好，比如表格或分点

### 第 3 轮：看 Skill 是否真的被用到

```text
1000 美元大概等于多少人民币？请说明你使用了什么数据来源。
```

最低通过标准：

- 回复里有明确的换算结果
- 回复里有数据来源，例如 `open.er-api.com` 或 ExchangeRate API
- 回复里出现“按当前查询结果”一类时间性表述，而不是只给一个裸数字

## 5.7 回头解释：为什么它能工作

这一整套链路可以压缩成一张图：

```text
Telegram 消息
   ↓
gateway / MessageBus
   ↓
AgentLoop
   ↓
System Prompt
  ├── SOUL.md
  ├── AGENTS.md
  ├── USER.md
  ├── TOOLS.md
  └── Skills Summary
   ↓
需要汇率时读取 exchange-rate/SKILL.md
   ↓
调用工具获取结果
   ↓
回到 Telegram
```

也就是说：

- `SOUL.md` 决定它像谁
- `AGENTS.md` 决定它怎么做事
- `USER.md` 决定它如何理解你
- `SKILL.md` 决定它在特定领域里知道怎么行动
- `gateway` 决定它能不能出现在真实聊天平台里

## 5.8 最终检查清单

做完这一章，至少确认下面 7 项：

1. `nanobot gateway` 能持续运行
2. Telegram 上能正常收到回复
3. 回复风格明显受 `SOUL.md` 影响
4. 回答流程明显受 `AGENTS.md` 影响
5. 个性化内容明显受 `USER.md` 影响
6. 涉及汇率时能触发 `exchange-rate` Skill
7. 涉及外部数据时，回复会给出来源或查询时间

如果这 7 项都成立，你就不是“学完四篇文档”而已，而是真的做出了一个自己的 Bot。

## 5.9 到这里你已经会了什么

现在你已经能：

- 用配置和 Markdown 文件定制一个 Bot
- 用 Skill 扩展一个 Bot
- 把 Bot 部署到真实聊天平台
- 解释这套行为背后的主干架构

如果你更关心“它为什么能这样工作”，下一步就去读 Part 2。那里会从 40 行代码开始，一步一步把教学版 Agent 搭出来。

---

[← 上一章：先部署到 Telegram](04-deploy.md) | [回到目录](README.md) | [继续：从零复刻 nanobot →](build/README.md)
