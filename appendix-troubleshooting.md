# 附录：常见坑与排障

> 这份附录不讲新概念，只解决跟做时最容易卡住的问题。建议在“哪里不对劲，但还不知道是哪一层出了问题”时来这里查。

## 先判断：问题到底在哪一层

很多排障之所以越查越乱，不是因为问题太复杂，而是因为一开始就没有分层。

先用这张表定位：

| 现象 | 优先怀疑哪一层 |
|------|------|
| `nanobot` 命令找不到 | Python 环境 / 安装 |
| `401`、模型不存在、请求失败 | provider / model / API Key |
| 能回复，但人格和流程没变化 | `SOUL.md` / `AGENTS.md` / `USER.md` / `TOOLS.md` |
| 能回复，但 Skill 没触发 | `skills/` 路径、frontmatter、依赖命令、提问方式 |
| CLI 正常，Telegram 不回复 | `gateway`、`allowFrom`、token、channel 配置 |
| 文档站构建失败 | MkDocs 环境、导航配置、相对链接 |

先判断在哪一层，再改对应文件，会比“每个地方都改一点”高效很多。

## 1. 安装与环境

### 现象：`nanobot: command not found`

优先检查：

1. 你当前 shell 是否还在安装 nanobot 的那个虚拟环境里
2. `python` / `pip` / `nanobot` 是否来自同一套环境
3. 你是否在新的 shell 窗口里忘了重新激活 `.venv`

最小检查：

```bash
which python
which pip
which nanobot
nanobot --version
```

### 现象：`python` 存在，但 `mkdocs` 不存在

这通常不是教程内容的问题，而是本地文档环境还没装好。

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-docs.txt
python -m mkdocs build --strict
```

如果这里失败，再去看依赖安装日志，而不是先改文档内容。

## 2. Provider、模型与 API Key

### 现象：`401` / `Unauthorized`

优先怀疑：

1. API Key 填错
2. provider 选对了，但 key 属于另一个 provider
3. model 和 provider 不匹配

第一次跟做时，最稳的做法是：**只改 `apiKey` 和 `model` 两处，先让一次请求成功。**

### 现象：模型不存在 / 模型不可用

先去 provider 控制台确认两件事：

- 模型名是不是当前 provider 真支持的名字
- 你的账号是否真的有调用权限

不要一开始就假设是 nanobot 配置有 bug。

## 3. Markdown 文件改了，但行为没变化

### 现象：改了 `SOUL.md`，回复还是老样子

优先检查：

1. 改动是否足够明显
2. 你提的问题是否真的能触发这种人格差异
3. 你改的是不是当前工作区里的那份文件

建议测试问法：

```bash
nanobot agent -m "请用一句话介绍你自己"
```

### 现象：Bot 没按 `AGENTS.md` 的流程回答

优先检查：

1. 规则是否冲突
2. 规则是否过长、过抽象
3. 你问的问题是否真的需要那套流程

一个好规则通常比“很长的规则集合”更稳定。

## 4. Skill 不触发

### 现象：Skill 在目录里，但回复像完全没用到它

按这个顺序查：

1. 路径：`~/.nanobot/workspace/skills/<skill>/SKILL.md`
2. frontmatter：是否至少有 `name` 和清晰的 `description`
3. 依赖：`curl`、`python3`、`gh` 之类的命令是否存在
4. 提问：是否真的覆盖了 `description` 描述的场景

最小检查：

```bash
ls ~/.nanobot/workspace/skills
sed -n '1,80p' ~/.nanobot/workspace/skills/<skill>/SKILL.md
which curl
which python3
```

更强触发问法：

```bash
nanobot agent -m "请使用 <skill-name> skill 完成这件事，并说明你使用了什么数据来源"
```

### 现象：Skill 很长，但效果反而更差

通常说明你写成了“文档”，而不是“Agent 可执行的操作说明”。

优先改成：

- 短步骤
- 明确命令
- 明确输入输出
- 少背景，多动作

## 5. Telegram 不回复

### 现象：`nanobot gateway` 能启动，但 Telegram 上没反应

优先顺序：

1. 先确认 CLI 模式本来就能回复
2. 再确认 `gateway` 进程持续存活
3. 再确认日志里显示 Telegram channel 已启用
4. 再确认 `allowFrom` 里放的是你的 **数字用户 ID**
5. 最后再确认 token、provider 和 model

### 现象：Bot 在线，但只有你发消息它不回

最常见原因不是程序挂了，而是：

- `allowFrom` 填了用户名而不是数字 ID
- `allowFrom` 是空数组 `[]`
- 临时调试后忘了把白名单改回自己

第一次部署时，建议前台运行：

```bash
nanobot gateway
```

先把最短收发链路跑通，再考虑 `systemd` 或 Docker。

## 6. Docs 站点构建问题

### 现象：MkDocs 构建失败

先看是不是下面几类：

- `mkdocs` 没安装
- 新增页面没加入导航
- 相对链接写错
- `docs-site/` 和根目录文档内容分叉

建议检查：

```bash
python -m mkdocs build --strict
```

如果你同时维护根目录 Markdown 和 `docs-site/` 副本，改完后要确认两边是同步的。

## 7. 什么时候该停下来，不要继续乱改

出现下面这些情况时，最好的动作通常不是继续改文档或配置，而是先缩小范围：

- 你同时改了 provider、model、Skill、Telegram 配置
- 你已经不知道自己刚才改的是哪一份文件
- 你在 CLI 和 Telegram 两条链路上同时排查
- 你为了让 Skill 触发，把 prompt 和 Skill 一起大改了一轮

最稳的回退方式是：

1. 先只验证 CLI 是否正常
2. 再只验证 Markdown 行为是否生效
3. 再只验证 Skill 是否触发
4. 最后才验证 Telegram

把问题一层一层拆开，几乎总会比“全链路一起猜”更快。
