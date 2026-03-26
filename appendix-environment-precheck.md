# 附录：环境预检

> 这份附录不讲 nanobot 的新概念，只帮你在正式跟做前确认：你的本机环境、账号信息和平台前置条件是不是已经准备好。

## 先判断：你准备走到哪一步

不是每个前置条件都要一次准备齐。先看你这次的目标：

| 你的目标 | 最少需要准备什么 |
|------|------|
| 只跑通 Part 1 的 CLI | 终端、Python、`venv`、一个可用的 API Key、一个可调用的模型名 |
| 跟做 Skill 示例 | 在 CLI 基础上，再确认本机有 `curl` 和 `python3` |
| 接 Telegram | 在 CLI 基础上，再准备 Telegram 账号、Bot Token、数字用户 ID |
| 跟做 Part 2 代码 | 在 CLI 基础上，再确认你有基础 Python 知识（函数、类、`async/await`） |

如果你这次的目标只是“先跑起来”，不要一开始就把 Telegram、Docker、systemd 和 Part 2 一起准备。

## 1. 终端与基础命令

先确认你能做到下面这些最小动作：

- 打开终端
- 知道当前目录是什么
- 能执行 `cd`、`ls`、`pwd` 这类基础命令
- 能用一个文本编辑器修改 JSON 和 Markdown 文件

如果这里已经卡住了，建议先补一点命令行基础，再继续本教程。

## 2. Python 与虚拟环境

先确认本机真的有可用的 Python 3：

```bash
python3 --version
```

你应该看到一个可用的 Python 版本号，而不是 `command not found`。

然后确认 `venv` 组件是可用的：

```bash
python3 -m venv .venv-check
```

如果创建成功，可以删掉这个临时目录：

```bash
rm -rf .venv-check
```

如果这里报 `ensurepip is not available`，通常说明系统没装 `venv` 组件；在 Debian / Ubuntu 上先安装 `python3-venv` 再重试。

## 3. Provider、API Key 与模型名

这一步最容易被低估。第一次跟做前，至少确认下面 3 件事：

1. 你已经有一个真实可用的 LLM API Key
2. 你知道这个 Key 对应哪个 provider
3. 你手里有一个该 provider 当前账号可调用的聊天模型名

第一次成功最需要的不是“最优模型”，而是“一个你已经验证能调通的 key + model 组合”。

如果你现在还说不清这 3 件事，建议先不要开始配 `config.json`。

## 4. Skill 示例会用到的本机命令

如果你准备跟做第 3 章的 Skill 示例，建议提前确认：

```bash
which curl
which python3
```

这一步不是所有章节都必须做，但它能提前暴露很多“Skill 没触发，其实是命令不存在”的问题。

## 5. Telegram 前置条件

如果你后面准备接 Telegram，再额外确认下面几件事：

- 你有一个可正常登录的 Telegram 账号
- 你知道怎么通过 `@BotFather` 创建 Bot
- 你能拿到一个 Bot Token
- 你知道 `allowFrom` 需要的是 **数字用户 ID**，不是用户名，也不带 `@`

如果你暂时只想先做本地 CLI，不必现在就准备 Telegram。

## 6. 自检清单

开始前，至少确认下面 6 项里你已经满足大部分：

- 我会打开终端，并执行基础命令
- 我本机有可用的 `python3`
- `python3 -m venv` 能正常创建虚拟环境
- 我能编辑 JSON 和 Markdown 文件
- 我已经有一个可用的 API Key
- 我已经知道这次要用哪个 provider 和哪个 model

如果这 6 条里有 2 条以上做不到，建议先补基础环境；否则你大概率会把“教程问题”和“本机没准备好”混在一起。

## 7. 通过后从哪里开始

- 如果你要先跑通 CLI：回到 [第 1 章：5 分钟跑起来](01-quick-start.md)
- 如果你已经能在 CLI 正常对话：继续 [第 2 章：用 Markdown 定义 Bot](02-soul.md) 和 [第 3 章：教 Bot 新技能](03-skills.md)
- 如果你已经完成本地闭环，准备接平台：再读 [第 4 章：先部署到 Telegram](04-deploy.md)
