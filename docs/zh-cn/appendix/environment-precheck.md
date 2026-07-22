# 附录：环境预检

> 这份附录不引入新概念，只用于确认本机、账号、凭据和部署边界已经准备好。按本次目标检查即可，不必一次安装所有组件。

## 先判断：你准备走到哪一步

| 目标 | 最少需要准备 |
|---|---|
| 跑通本地 CLI | 终端、Python 3、虚拟环境、一个可用 Provider、环境变量中的凭据、可调用的模型 |
| 跟做 Skill | 在 CLI 基础上，准备示例实际使用的 `curl`、`python3` 等命令 |
| 接 Telegram | 在 CLI 基础上，准备账号、Bot Token，以及显式 `allowFrom` 或配对方案 |
| 长期运行 Gateway | 确认状态目录持久化、服务管理器、密钥注入和日志位置 |
| 使用 Docker | 可用的 Docker Engine/Compose、v0.2.2 源码、两个端口和持久化挂载目录 |
| 跟做进阶营 | 在 CLI 基础上，具备函数、类和 `async`/`await` 等 Python 基础 |

只想先跑起来时，不要同时调试 Telegram、Docker、systemd 和 Hero 示例。

## 1. 终端与基础命令

先确认你能：

- 打开终端并识别当前目录。
- 执行 `cd`、`ls`、`pwd` 和 `command -v`。
- 使用文本编辑器修改 JSON 与 Markdown。
- 区分项目工作区、Agent 工作区和 `~/.nanobot/config.json`。

## 2. Python 与虚拟环境

```bash
python3 --version
python3 -c 'import venv; print("venv 模块可用")'
```

如果第二条命令报错，在 Debian/Ubuntu 上安装与当前 Python 对应的 `python3-venv` 后再继续。不要为了测试创建一个随后用递归删除命令清理的目录；第 1 章会直接创建教程真正使用的虚拟环境。

## 3. Provider、凭据与模型预设

第一次配置前确认：

1. 账号下有一个真实可用的 Provider 凭据。
2. 该 Provider 的 API 地址和模型 ID 已从官方控制台确认。
3. 计划把它写入一个命名 `modelPresets`，并知道哪个预设是默认值。
4. `config.json` 使用 `${ENV_NAME}`，真实值不进入 Git。

检查环境变量是否存在时只判断长度，不打印值。把示例变量名替换为自己的名字：

```bash
test -n "${PROVIDER_API_KEY:-}" && echo "Provider 凭据已设置" || echo "Provider 凭据未设置"
```

## 4. Skill 所需的本机命令

只检查准备跟做的 Skill 实际声明的依赖：

```bash
command -v curl
command -v python3
```

命令存在不代表网络 API 一定可用。真实天气、汇率和模型调用属于人工冒烟测试，不应放进 CI。

## 5. Telegram 前置条件

- 有可正常登录的 Telegram 账号。
- 能通过 `@BotFather` 创建 Bot 并撤销泄露的 Token。
- 选择显式白名单或配对模式。
- 显式 `allowFrom` 优先使用数字用户 ID；v0.2.2 也接受不带 `@` 的用户名，但用户名变化后配置会失效。
- 配对码只从私聊产生，由本机 CLI 或已认证的 WebUI 管理员批准。

不要临时使用 `["*"]` 来寻找自己的 ID。接平台前应先通过：

```bash
nanobot agent -m "本地预检"
nanobot plugins list
nanobot channels status
```

## 6. 后台服务前置条件

长期运行前确认 `nanobot status` 显示的是预期配置与工作区，并选择一种托管方式：

- `nanobot gateway --background`：轻量后台进程，继承启动终端的环境。
- `nanobot gateway install-service`：systemd 用户服务或 macOS LaunchAgent，适合登录启动和失败重启。
- Docker：独立容器，需要显式环境文件、挂载和端口映射。

安装系统服务前必须先预览：

```bash
nanobot gateway install-service --dry-run
```

确认生成内容使用当前 Python、前台 Gateway、正确工作区和非 root 用户。系统服务不会自动保存当前 shell 的 Token；先设计操作系统级的密钥注入方式。

## 7. Docker 前置条件

本仓库约定所有 Docker 命令都通过 `sudo` 执行：

```bash
sudo docker version
sudo docker compose version
```

继续前确认：

- 从固定提交 `e2e75c913f3524d4bc5b23487a4eed5329eef182` 的源码和 `Dockerfile` 构建，而不是默认信任第三方镜像。
- 宿主机 `~/.nanobot` 挂载到容器 `/home/nanobot/.nanobot`，使配置、工作区、会话和日志持久化。
- 官方镜像以 `nanobot`（UID 1000）运行；挂载目录可由该用户读写，但不把容器改成 root。
- 容器内 Gateway/WebSocket 监听 `0.0.0.0` 才能接受端口转发；宿主机默认只发布到 `127.0.0.1`。
- `18790` 是健康检查端口，`8765` 才是 WebUI；WebUI 使用 `tokenIssueSecret` 或 Token 认证。
- 环境文件权限为 `600`，且不在项目目录或镜像构建上下文中。

完整命令见[第 5 章的 Docker 部署](../zero/05-deploy-telegram.md#c-docker)。

## 8. 安全边界预检

- Prompt、`SOUL.md` 和 `AGENTS.md` 是模型指令，不是硬隔离。
- `tools.restrictToWorkspace: true` 是应用级路径控制，不等于操作系统沙箱。
- Linux 上需要命令执行时评估 `tools.exec.sandbox: "bwrap"`；不需要时关闭 `tools.exec.enable`。
- 保持 `tools.ssrfWhitelist` 为空，除非确实需要精确放行某个 CIDR。
- SSRF 检查不代替宿主机或容器的出站防火墙。
- Channel Token、模型密钥、WebUI 密码和 OAuth 状态都按凭据保护并可轮换。

## 9. 自检清单

- [ ] Python、虚拟环境模块和文本编辑器可用。
- [ ] Provider、模型和命名预设已经确定。
- [ ] 真实凭据只存在于环境变量或受保护的凭据文件。
- [ ] 本地 `nanobot agent` 已通过，再接 Channel。
- [ ] 长期运行方式只有一种，配置和工作区路径明确。
- [ ] Docker 部署已确认非 root 用户、持久挂载、监听地址、认证与端口。
- [ ] 工作区限制、执行隔离和 SSRF 边界符合使用场景。

## 10. 通过后从哪里开始

- 本地 CLI：回到[第 1 章：5 分钟跑起来](../zero/01-quick-start.md)。
- 已能在 CLI 对话：继续[第 2 章：用 Markdown 定义 Bot](../zero/02-soul.md)和[第 3 章：教 Bot 新技能](../zero/03-skills.md)。
- 已完成本地闭环：阅读[第 5 章：连接 Telegram、Discord 与 Slack](../zero/05-deploy-telegram.md)。
