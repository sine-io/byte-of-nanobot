# 统一排障手册

> 按“环境 → 配置 → Agent 状态 → Skill → Channel/Gateway → 部署”的顺序缩小问题，避免同时改多个变量。

!!! note "版本边界"
    本手册的可执行命令以 nanobot **v0.2.2** 为准。固定的 `main@b189a376` 只用于教程中的差异说明；看到 main 独有结构时，不要直接套到稳定版安装上。

## 先做三件安全的事

1. 不要把 `config.json`、环境文件、完整日志或截图原样贴到 Issue。
2. 不要用 `cat`、`grep`、`printenv` 等命令把凭据值打印出来。
3. 不要为了“回到最小配置”直接覆盖现有配置；一次只改一个字段，并保留权限受限的本地备份，且不要把备份提交到版本库。

首轮诊断只运行本地、只读命令：

```bash
nanobot --version
nanobot status
bash scripts/check-env.sh
bash scripts/verify-config.sh
```

仓库中的诊断脚本不会调用模型，也不会输出 API Key。若你不在教程仓库根目录，先切回仓库根目录再执行。

## 一分钟定位表 { #quick-triage }

| 现象 | 先查哪一层 | 第一条命令 |
|---|---|---|
| `nanobot: command not found` | Python/虚拟环境 | `command -v python3; command -v nanobot` |
| `401`、认证失败 | Provider 凭据是否进入当前进程 | `nanobot status` |
| 模型不存在或不可用 | 当前 model preset 与 Provider | `bash scripts/verify-config.sh` |
| 能回复，但人格/规则不生效 | 当前 Agent 或项目工作区 | `nanobot status` |
| Skill 不触发 | Skill 路径、frontmatter、依赖、禁用状态 | `bash scripts/check-skill.sh exchange-rate` |
| CLI 正常，Channel 不回复 | 插件、启用、授权、Gateway | `nanobot channels status` |
| WebUI 打不开 | WebSocket Channel、监听地址、认证、端口 | `nanobot gateway status` |
| 长期记忆没变化 | Consolidator 是否已有摘要、Dream 是否完成 | 在聊天中发送 `/dream-log` |
| 文档构建失败 | 依赖、导航、内部链接 | `.venv/bin/python -m mkdocs build --strict` |

只要某一层失败，就先停在这一层；不要同时修改模型、Skill 和 Channel。

## 1. 安装与 Python 环境 { #install }

### `nanobot` 命令找不到

```bash
command -v python3
python3 --version
python3 -m pip --version
command -v nanobot
```

常见原因：

- 新终端没有重新激活虚拟环境。
- `pip` 与 `python` 来自不同环境。
- 安装的是别的包或版本。

教程正文固定使用 v0.2.2：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install "nanobot-ai==0.2.2"
nanobot --version
```

不要看到安装错误就立刻换未审计的主线版本。先确认 Python 版本、虚拟环境和包索引是否正常。

### 文档依赖与 nanobot 运行依赖混在一起

构建本站只需要仓库的文档依赖：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m mkdocs build --strict
```

`requirements.txt` 服务于文档站，不代表安装了 Hero 示例所需的模型 SDK，也不代表安装了 nanobot 本体。

### 缺少系统命令

```bash
command -v curl
command -v git
command -v jq
```

缺少 `jq` 时，`verify-config.sh` 会明确退出。只安装你确实需要的依赖；Skill 自己声明的依赖留到 Skill 层再查。

## 2. 配置、Provider 与模型 { #config }

### 推荐的恢复入口

新配置优先用向导或 WebUI维护：

```bash
nanobot onboard --wizard
nanobot status
```

推荐使用命名 `modelPresets`，并让 `agents.defaults.modelPreset` 指向当前预设。直接填写 `agents.defaults.provider` / `model` 是兼容方式，不是新教程的首选路径。

### `401` 或 Provider 认证失败

只检查“有没有值”，不要回显值：

```bash
test -n "${PROVIDER_API_KEY:-}" && echo "Provider 凭据已设置" || echo "Provider 凭据未设置"
nanobot status
```

如果交互终端可用、后台 Gateway 不可用，通常是两者没有继承同一环境。重新启动后台进程或服务，让服务管理器显式加载凭据；不要把真实 Key 写进 unit、仓库或 Issue。

仍需检查配置结构时，只打印名称和键，不打印对象值：

```bash
jq '{
  activePreset: .agents.defaults.modelPreset,
  presetNames: ((.modelPresets // {}) | keys),
  providerNames: ((.providers // {}) | keys)
}' ~/.nanobot/config.json
```

### 模型不存在或拒绝访问

模型目录会变化，本手册不固定任何“推荐模型名”。按以下顺序查：

1. 在当前 Provider 控制台确认模型标识仍可用。
2. 确认账号有权限、余额或配额。
3. 确认活动 preset 指向同一个 Provider。
4. 回到 CLI 做最小请求：

```bash
nanobot agent -m "只回复：连接正常"
```

CLI 也失败时先修 Provider；CLI 成功而 Channel 失败时再进入 Channel 层。

### 手工编辑后配置损坏

先做语法检查，不要用一个教程片段覆盖整个文件：

```bash
python -m json.tool ~/.nanobot/config.json >/dev/null
bash scripts/verify-config.sh
```

配置片段只用于“合并字段”。保留现有的 Provider、`modelPresets`、工具和 Channel，再做最小修改。无法确认合并结果时，回到 `nanobot onboard --wizard` 或 WebUI。

## 3. Bootstrap、工作区与长期状态 { #workspace }

### 改了人格或规则，但回复没变化

v0.2.2 自动加载的 Bootstrap 是：

- `AGENTS.md`：项目或实例规则
- `SOUL.md`：行为策略与表达风格
- `USER.md`：用户偏好和背景

默认 CLI/Channel 使用 Agent 工作区。WebUI 选择项目后，项目根同名文件会成为当前 turn 的 Bootstrap；这时继续改默认 Agent 工作区，当前项目对话可能看不到变化。

安全地确认文件位置：

```bash
nanobot status
find ~/.nanobot/workspace -maxdepth 2 -type f -print
```

再用一个差异明显、但不影响安全边界的规则做测试。不要同时修改三份文件，也不要把工具硬权限写成 Prompt 后就认为已经隔离。

### 工作区工具越界或读不到文件

先确认当前配置是否启用了工作区限制，以及你是在 Agent 工作区还是 WebUI 项目工作区：

```bash
bash scripts/verify-config.sh
nanobot status
```

`tools.restrictToWorkspace` 是文件/命令边界的一部分；符号链接、子进程、网络访问和容器权限还需要各自的实现或系统隔离。遇到拒绝时不要把限制全局关闭，先把目标文件移入专用工作区并缩小权限。

## 4. Skill 不触发或执行失败 { #skills }

### 先检查目录和 frontmatter

工作区 Skill 的基本路径是：

```text
~/.nanobot/workspace/skills/<skill-name>/SKILL.md
```

使用仓库脚本做只读检查：

```bash
bash scripts/check-skill.sh exchange-rate
```

再确认：

1. 目录名和 `SKILL.md` 大小写正确。
2. frontmatter 至少有清晰的 `name` 与 `description`。
3. Skill 没有被当前配置禁用。
4. 所需命令、环境变量或文件存在。
5. 用户请求确实匹配描述；不要只靠在问题里硬写 Skill 名称掩盖描述问题。

### Skill 被发现，但工具失败

把“选择 Skill”和“执行步骤”分开测试：

- 模型是否读取了目标 `SKILL.md`？
- 失败发生在输入校验、命令依赖、HTTP、路径还是解析？
- 失败输出是否被截断，是否包含可行动的错误？

需要网络的天气、汇率等案例只做人工冒烟。CI 不应访问公共 API，也不应依赖实时值。

## 5. Channel、配对与 Gateway { #channels }

### 先分清发现、启用、运行

```bash
nanobot plugins list
nanobot channels status
nanobot gateway
```

- `plugins list` 看得到：实现已发现。
- `channels status` 显示启用：配置中的 `enabled` 生效。
- Gateway 日志显示连接成功：运行时真的连上平台。

三者不是一回事。Channel 没启用时，不要先排查模型；Gateway 没运行时，不要反复修改白名单。

### Telegram 不回复

按以下顺序：

1. 同一环境下 `nanobot agent -m "测试"` 能回复。
2. `nanobot channels status` 显示 Telegram 启用。
3. 只检查 Token 环境变量是否存在，不打印 Token。
4. 前台运行 `nanobot gateway --verbose`，观察连接错误。
5. 核对 `allowFrom` 的精确数字 ID 或不带 `@` 的用户名；也可省略它并走配对。

```bash
test -n "${TELEGRAM_BOT_TOKEN:-}" && echo "Telegram Token 已设置" || echo "Telegram Token 未设置"
nanobot channels status
nanobot gateway --verbose
```

如果私聊返回配对码，在本机批准：

```bash
nanobot agent -m "/pairing list"
nanobot agent -m "/pairing approve ABCD-EFGH"
```

群聊默认通常需要提及 Bot；先让私聊成功，再调群组策略。Discord 还需启用 Message Content Intent；Slack 要区分 `botToken` 与 `appToken`。完整配置见[部署到 Telegram](../zero/05-deploy-telegram.md)。

### Gateway 后台进程

优先使用内置生命周期命令：

```bash
nanobot gateway --background
nanobot gateway status
nanobot gateway logs --no-follow
nanobot gateway logs
nanobot gateway restart
nanobot gateway stop
```

长期随登录启动时使用：

```bash
nanobot gateway install-service --dry-run
nanobot gateway install-service
```

手写 systemd 只是高级回退，不是默认排障步骤。不要为了恢复运行直接复制未知 unit 到系统目录或改成 root 用户。

## 6. WebUI、端口与认证 { #webui }

WebUI 由 WebSocket Channel 提供，默认浏览器地址是 `127.0.0.1:8765`；Gateway 健康状态端口不是 WebUI 端口。

```bash
nanobot channels status
nanobot gateway status
nanobot gateway logs --no-follow
```

本机打不开时依次检查：

1. WebSocket Channel 是否启用。
2. `8765` 是否被占用。
3. Gateway 是否仍在运行。
4. WebUI 认证环境变量是否进入 Gateway 进程。

容器内服务要监听 `0.0.0.0` 才能接受端口转发，但宿主机应优先只发布到 `127.0.0.1`，并启用 Token/密码认证。不要为了快速测试把无认证 WebUI 暴露到公网。

## 7. Docker 部署 { #docker }

仓库约定所有 Docker 命令都使用 `sudo`。先检查状态和日志，不要先删容器或卷：

```bash
sudo docker ps -a
sudo docker logs --tail 200 nanobot-gateway
sudo docker compose ps
sudo docker compose logs --no-color --tail 200 nanobot-gateway
```

常见边界：

- 容器以非 root 用户运行，配置挂载到 `/home/nanobot/.nanobot`。
- 宿主目录权限必须允许容器运行用户读取和写入必要状态。
- Provider、Channel 和 WebUI 凭据通过受保护的环境文件注入。
- 不要把环境文件提交到 Git，也不要用会展开环境变量的诊断命令公开它。

完整镜像构建、挂载和端口示例见 [Docker 部署](../zero/05-deploy-telegram.md#c-docker)。

## 8. Session、Memory 与 Dream { #memory }

先区分四种状态：

| 状态 | 位置或来源 | 何时进入上下文 |
|---|---|---|
| 当前 Session | `sessions/*.jsonl` | 当前会话历史窗口 |
| Session 归档摘要 | Session metadata | 当前 Session 已压缩时 |
| Recent History | `memory/history.jsonl` 中 Dream cursor 之后的摘要 | 非临时 turn，且存在待处理摘要时 |
| 长期 Memory | `memory/MEMORY.md` | 非空且不再是初始模板时 |

### `/dream` 提示没有新内容

短对话可能还没触发 Consolidator，因此 `history.jsonl` 没有新的归档。先继续正常使用，不要为了触发 Dream 人为灌入无意义对话。

### 查看或恢复 Dream 修改

```text
/dream
/dream-log
/dream-log <sha>
/dream-restore
/dream-restore <sha>
```

`/dream-log` 没有版本时，可能是 Dream 尚未产生文件变化，或 Agent 工作区无法初始化独立版本记录。恢复前先查看目标 diff；恢复会创建新的安全提交，不要直接编辑内部游标。

## 9. 文档与示例构建 { #docs-build }

从仓库根目录执行：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python -m mkdocs build --strict
PYTHONPYCACHEPREFIX=/tmp/byte-of-nanobot-pyc python -m compileall -q docs/zh-cn/examples/hero
bash -n scripts/*.sh
```

严格构建失败时先读第一条实际错误：

- 页面不存在：检查 `mkdocs.yml` 与文件名。
- 相对链接失效：从当前 Markdown 文件所在目录重新计算。
- 锚点失效：以目标页面当前标题生成的锚点为准。
- 示例编译失败：先修语法，不要用真实 API 请求代替离线检查。

## 10. 提交 Issue 前的最小信息 { #report }

可以提供：

- 操作系统类型与 Python、nanobot 版本。
- `nanobot status` 的脱敏结果。
- 最小复现步骤和预期/实际行为。
- 去除凭据、用户消息、绝对个人路径后的相关日志片段。
- 问题发生在 CLI、WebUI、哪个 Channel 或哪类后台任务。

不要提供：

- 完整 `config.json` 或环境文件。
- API Key、Bot Token、WebUI 密码、配对码。
- 未脱敏的 Session、Memory、个人工作区文件。
- 为了复现而关闭全部安全限制的公网实例。

先搜索 [nanobot Issues](https://github.com/HKUDS/nanobot/issues)，仍无法定位时再按模板提交最小复现。

## 常用只读命令

```bash
nanobot --version
nanobot status
nanobot plugins list
nanobot channels status
nanobot gateway status
nanobot gateway logs --no-follow
bash scripts/check-env.sh
bash scripts/verify-config.sh
bash scripts/check-skill.sh exchange-rate
```

这份手册是唯一完整排障正文；[排障快速索引](troubleshooting.md)只负责按症状把你带到这里。
