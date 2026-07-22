# 第 5 章：连接 Telegram、Discord 与 Slack

> 目标：把已经在本地验收过的 Bot 接到聊天平台，并用明确的身份策略控制谁能访问它。

!!! warning "先完成本地验收"
    如果 `nanobot agent -m "你好"` 还不能稳定回复，请先完成[第 4 章：本地完整验收](04-local-integration.md)。Channel 会额外引入平台凭据、事件权限、网络连接和群聊策略，不能替代本地排错。

---

## 5.1 从 CLI 到 Gateway 和 Channel 插件

前面使用的 `nanobot agent` 是一次性的终端入口；`nanobot gateway` 则持续运行并承载 Telegram、Discord、Slack 和 WebUI 等 Channel。

| | CLI 模式 | Gateway 模式 |
|---|---|---|
| 命令 | `nanobot agent` | `nanobot gateway` |
| 用户入口 | 当前终端 | 聊天平台或 WebUI |
| 生命周期 | 单次消息或交互会话 | 持续接收和发送消息 |
| 主要用途 | 配置与模型排错 | 长期运行多个 Channel |

```mermaid
flowchart LR
    platform[Telegram / Discord / Slack] --> channel[Channel 插件]
    channel --> gateway[nanobot gateway]
    gateway --> bus[MessageBus]
    bus --> agent[AgentLoop]
    agent --> bus
    bus --> channel
    channel --> platform
```

v0.2.2 会同时发现内置 Channel 和通过 Python entry point 安装的第三方 Channel。发现插件不等于启用插件：配置项中的 `enabled: true` 才会让 Gateway 启动它。

```bash
# 查看内置与第三方 Channel，以及各自是否启用
nanobot plugins list

# 查看当前配置中的 Channel 状态
nanobot channels status
```

`nanobot plugins list` 的 `Source` 列会显示 `builtin` 或 `plugin`。Telegram、Discord 和 Slack 随 v0.2.2 提供，无需另装 Channel 包。

!!! info "WebUI 也是一个 Channel"
    WebUI 由 `channels.websocket` 提供，默认地址是 `http://127.0.0.1:8765`。它与 Telegram 可以同时启用并共用一个 Gateway；端口 `18790` 是 Gateway 健康检查端口，不是 WebUI。

---

## 5.2 接平台前的最后确认

- [ ] `nanobot agent -m "你好"` 能返回正常回复
- [ ] `SOUL.md` 中的行为策略已经生效
- [ ] 至少有一个 Skill 在本地成功触发过
- [ ] `tools.restrictToWorkspace` 已按第 4 章设为 `true`
- [ ] Channel Token 和模型密钥都只通过环境变量注入

本章以 nanobot v0.2.2 的 [`Channel registry`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/nanobot/channels/registry.py) 和 [`BaseChannel`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/nanobot/channels/base.py) 为准。先接通一个私聊入口，再考虑群聊和长期运行。

---

## 5.3 实操：连接 Telegram

Telegram 默认使用 long polling，因此本地试用不需要域名或公网 webhook。

### 步骤 1：创建 Bot 并保存 Token

1. 在 Telegram 搜索 `@BotFather`。
2. 发送 `/newbot`，按提示设置名称和以 `bot` 结尾的用户名。
3. 把生成的 Bot Token 保存为当前终端的环境变量：

```bash
export TELEGRAM_BOT_TOKEN='从 BotFather 获得的 Token'
```

Token 等同于 Bot 密码。不要把真实值写进教程、Git 提交、截图或聊天消息。

### 步骤 2：选择访问控制方式

Telegram 支持两种适合首次上线的方式。

#### 方式 A：显式 `allowFrom`

`allowFrom` 接受以下精确标识：

- 数字用户 ID，例如 `"123456789"`；这是更稳定的选择。
- Telegram 用户名，例如 `"alice"`；不要带 `@`，且用户改名后要同步修改配置。

数字 ID 可通过 Telegram 客户端或可信的 ID 查询 Bot 获取。v0.2.2 会把数字 ID 和当前用户名一起带入消息，并分别尝试精确匹配；因此“只能填数字”或“任何用户名格式都可以”都不准确。

#### 方式 B：只使用配对码

省略 `allowFrom`。未批准的用户第一次给 Bot 发私信时会收到形如 `ABCD-EFGH` 的配对码，管理员批准后才能继续使用。配对码 10 分钟过期；未批准的群聊消息不会收到配对码。

不要为了获取 ID 临时设置 `"allowFrom": ["*"]`。该值会允许任何能找到 Bot 的人调用它。

### 步骤 3：写入 Channel 配置

可以运行 `nanobot onboard`，进入 **Chat Channels → Telegram** 让终端向导写入配置；也可以把下面片段合并到 `~/.nanobot/config.json`：

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "token": "${TELEGRAM_BOT_TOKEN}",
      "allowFrom": ["123456789"]
    }
  }
}
```

如果选择配对码方式，删除整个 `allowFrom` 行。不要把代码块覆盖到已有配置之上；应保留已经配置好的 `modelPresets`、Provider、工具和其他 Channel。

| 字段 | 作用 | 首次上线建议 |
|---|---|---|
| `enabled` | 让 Gateway 启动 Telegram Channel | `true` |
| `token` | BotFather Token | 使用 `${TELEGRAM_BOT_TOKEN}` |
| `allowFrom` | 显式白名单 | 填自己的数字 ID，或省略并使用配对 |
| `groupPolicy` | 群聊响应策略 | 保持默认 `mention` |

#### 可选：同时启用 WebUI

如果第 1 章的向导尚未启用 WebUI，可在同一个 `channels` 对象中再合并：

```json
{
  "channels": {
    "websocket": {
      "enabled": true,
      "tokenIssueSecret": "${NANOBOT_WEBUI_PASSWORD}",
      "websocketRequiresToken": true
    }
  }
}
```

这不是把 Telegram 凭据交给 WebUI；它只是增加一个受密码保护的本地管理入口。设置 `NANOBOT_WEBUI_PASSWORD` 后，Gateway 启动时可在 `http://127.0.0.1:8765` 打开它。

### 步骤 4：先检查，再启动

```bash
nanobot plugins list
nanobot channels status
nanobot gateway
```

继续之前，确认 Telegram 在前两个命令中都显示为已发现且已启用。保持 Gateway 终端运行，并在需要详细连接日志时使用 `nanobot gateway --verbose`。

### 步骤 5：完成首次对话或配对

在 Telegram 找到 Bot，点击 **Start**，然后发送：

```text
你好，请用一句话介绍你自己
```

- 如果你的标识已在 `allowFrom` 中，Bot 应直接回复。
- 如果省略了 `allowFrom`，Bot 会先返回配对码。把配对码交给管理员，不要公开发送。

管理员可在本机终端审批：

```bash
nanobot agent -m "/pairing list"
nanobot agent -m "/pairing approve ABCD-EFGH"
```

也可以在已经通过密码登录的 WebUI 聊天中发送 `/pairing approve ABCD-EFGH`。审批立即生效，无需重启 Gateway。其余管理命令如下：

| 命令 | 作用 |
|---|---|
| `/pairing` 或 `/pairing list` | 查看尚未过期的请求 |
| `/pairing approve <code>` | 批准请求 |
| `/pairing deny <code>` | 拒绝请求 |
| `/pairing revoke <user_id>` | 撤销当前 Channel 中的用户 |
| `/pairing revoke <channel> <user_id>` | 撤销指定 Channel 中的用户 |

批准记录保存在 `~/.nanobot/pairing.json`。不要手工改这个文件，也不要把它提交到版本库。

---

## 5.4 验证部署是否成功

用这三轮对话验证完整功能：

### 第 1 轮：基本对话

**在 Telegram 中发送：**
```
你好，请用一句话介绍你自己
```

**检查点：**
- [ ] Bot 在 10 秒内回复
- [ ] 回复风格符合 `SOUL.md` 的定义
- [ ] 终端显示了消息处理日志

---

### 第 2 轮：验证人格和规则

**在 Telegram 中发送：**
```
我每个月能存 5000 元，应该先做什么理财准备？
```

**检查点：**
- [ ] 回复开头先复述了问题
- [ ] 有结构化的分段（问题理解、分析、建议等）
- [ ] 没有激进的投资建议
- [ ] 符合第 4 章本地验收时的表现

---

### 第 3 轮：验证 Skill

**在 Telegram 中发送：**
```
1000 美元等于多少人民币？请说明数据来源。
```

**检查点：**
- [ ] Bot 给出了查询时刻、币种、换算结果和数据来源
- [ ] 没有把教程里的旧汇率当作固定答案
- [ ] Gateway 日志显示了对应的工具调用
- [ ] 符合第 4 章本地验收时的表现

---

## 5.5 遇到问题了？快速诊断

如果 Telegram 没有回复，按“发现 → 启用 → 连接 → 授权 → 模型”的顺序排查：

```mermaid
flowchart TD
    start[Telegram 不回复] --> q1{plugins list 能发现 Telegram?}
    q1 -- 否 --> fix1[确认安装的是 nanobot v0.2.2]
    q1 -- 是 --> q2{channels status 显示 enabled?}
    q2 -- 否 --> fix2[检查 channels.telegram.enabled 和配置文件]
    q2 -- 是 --> q3{Gateway 已连接 Telegram?}
    q3 -- 否 --> fix3[检查 Token 环境变量和网络]
    q3 -- 是 --> q4{私聊收到回复或配对码?}
    q4 -- 否 --> fix4[检查 allowFrom 精确值并重启 Gateway]
    q4 -- 是 --> q5{模型调用成功?}
    q5 -- 否 --> fix5[回到 CLI 检查模型预设和 Provider]
    q5 -- 是 --> ok[部署路径正常]
```

### 常见问题速查表

| 症状 | 最可能的原因 | 快速排查 |
|---|---|---|
| `channels status` 显示未启用 | 配置路径或 `enabled` 错误 | 重新运行 `nanobot onboard`，或检查 `~/.nanobot/config.json` |
| Gateway 报认证失败 | Token 为空、过期或复制错误 | 重新导出环境变量并重启 Gateway |
| 私聊只返回配对码 | 当前用户尚未批准 | 在本地终端或已登录 WebUI 执行 `/pairing approve` |
| `allowFrom` 已配置但仍被拒绝 | 标识带了 `@`、用户名已变化或值不精确 | 改用数字 ID，重启 Gateway |
| 群聊不回复但私聊正常 | 默认只响应提及 | 在群里 `@Bot`，不要急着改为 `open` |
| Bot 返回模型错误 | Channel 已通，Provider 或模型配置失败 | 用同一环境运行 `nanobot agent -m "测试"` |
| 工具调用失败 | 工作区或依赖问题 | 先在 CLI 使用同一输入复现 |

### 详细排查步骤

#### 1. 确认插件和配置状态

```bash
nanobot plugins list
nanobot channels status
```

如果 Telegram 未启用，先修配置；此时重试消息或排查模型都不会有帮助。

#### 2. 确认环境变量存在，但不要打印 Token

```bash
test -n "${TELEGRAM_BOT_TOKEN:-}" && echo "Telegram Token 已设置" || echo "Telegram Token 未设置"
nanobot gateway --verbose
```

认证错误时从 BotFather 重新生成 Token，然后在启动 Gateway 的同一环境中重新导出。不要使用 `cat`、`grep` 或调试日志把完整配置和 Token 打到终端记录里。

#### 3. 区分白名单与配对问题

- 显式白名单：优先使用数字 ID；用户名必须去掉 `@` 并保持与当前用户名完全一致。
- 配对模式：从私聊获取新配对码，再用 `/pairing list` 确认它仍未过期。
- 修改 `config.json` 或环境变量后要重启 Gateway；批准配对码则无需重启。
- 群聊不会向未批准用户发送配对码，先回到私聊完成配对。

#### 4. Bot 回复了，但内容不对

这说明平台连接和访问控制已经通过，应回到更小的 CLI 路径复现：

```bash
nanobot agent -m "测试消息"
```

如果 CLI 也失败，检查命名 `modelPresets`、Provider 环境变量和工作区；如果只有 Telegram 失败，再比较两个入口使用的会话和工作区。

---

## 5.6 保持 Gateway 持续运行

前台运行适合首次连接；确认功能正常后，再从下面三种方式中选择一种。不要同时启动前台、后台和系统服务，否则会争用同一个 Channel 或端口。

### 方案 A：内置后台进程

这是从终端切换到后台的最短路径，Linux、macOS 和 Windows 都可用：

```bash
nanobot gateway --background
nanobot gateway status
nanobot gateway logs --no-follow
nanobot gateway logs
nanobot gateway restart
nanobot gateway stop
```

`logs` 默认持续跟随，按 `Ctrl+C` 只会退出日志查看，不会停止 Gateway。自定义实例必须在每条管理命令中使用相同的 `--config` 和 `--workspace`，否则会查看或停止另一个实例。

后台子进程继承启动命令当时的环境。配置使用 `${TELEGRAM_BOT_TOKEN}` 等占位符时，执行 `--background` 或 `restart` 的终端必须已经导出对应变量。

### 方案 B：安装系统用户服务

需要登录后自动启动和失败重启时，优先使用 v0.2.2 的内置安装器。Linux 自动生成 systemd **用户服务**，macOS 自动生成 LaunchAgent：

```bash
# 先预览文件路径、内容和将执行的命令
nanobot gateway install-service --dry-run

# 安装、启用并立即启动
nanobot gateway install-service

# 不再需要时卸载
nanobot gateway uninstall-service
```

安装器使用当前 Python 解释器，并让系统监督前台 Gateway；不要在 service 中再加 `--background`。自定义实例可以固定名称和路径：

```bash
nanobot gateway install-service \
  --name nanobot-telegram \
  --config ~/.nanobot/config.json \
  --workspace ~/.nanobot/workspace
```

!!! warning "系统服务需要单独注入密钥"
    生成的 systemd unit 或 LaunchAgent 不会把当前 shell 中的 Token 自动写进去。应使用操作系统的凭据管理或仅当前用户可读的环境文件，并在安装前通过 `--dry-run` 检查最终服务；不要把真实 Token 直接写进公开 unit、命令历史或仓库。

Linux 用户服务通常随登录会话运行。服务器需要注销后继续运行时，可由系统管理员评估是否启用 user lingering：

```bash
loginctl enable-linger "$USER"
```

<details>
<summary>高级回退：手工维护 systemd</summary>

只有内置 `install-service` 无法满足发行版或运维规范时，才手工维护 unit。先用 `nanobot gateway install-service --manager systemd --dry-run` 取得与当前版本一致的模板，再在 `~/.config/systemd/user/` 中审查和扩展；不要从教程复制到 `/etc/systemd/system/` 后以 root 运行。

至少保留非 root 用户、前台 `python -m nanobot gateway --foreground`、`NoNewPrivileges=yes`、明确的工作目录和受限权限。手工 unit 属于高级运维回退，本教程不再把它作为默认安装路径。

</details>

### 方案 C：从源码构建 Docker 镜像

<details>
<summary>点击展开：Docker 部署</summary>

官方 v0.2.2 没有要求信任第三方镜像命名空间；在 nanobot v0.2.2 源码检出目录中，用仓库自带 `Dockerfile` 构建：

```bash
git checkout e2e75c913f3524d4bc5b23487a4eed5329eef182
sudo docker build --pull -t nanobot:v0.2.2 .
```

镜像内进程默认使用非 root 用户 `nanobot`（UID 1000），配置和状态目录是 `/home/nanobot/.nanobot`。在宿主机准备私有目录和不进 Git 的环境文件：

```bash
mkdir -p ~/.nanobot ~/.config/nanobot
chmod 700 ~/.nanobot ~/.config/nanobot
test -e ~/.config/nanobot/nanobot.env || install -m 600 /dev/null ~/.config/nanobot/nanobot.env
chmod 600 ~/.config/nanobot/nanobot.env
nano ~/.config/nanobot/nanobot.env
```

环境文件使用 `NAME=value`，不要写 `export`：

```text
PROVIDER_API_KEY=替换为真实值
TELEGRAM_BOT_TOKEN=替换为真实值
NANOBOT_WEBUI_PASSWORD=替换为高强度随机值
```

容器端口转发无法访问容器自身的 `127.0.0.1`。因此容器内的 Gateway 和 WebSocket 需要监听 `0.0.0.0`，同时在宿主机侧只发布到 `127.0.0.1`：

```json
{
  "gateway": {
    "host": "0.0.0.0"
  },
  "channels": {
    "websocket": {
      "enabled": true,
      "host": "0.0.0.0",
      "port": 8765,
      "tokenIssueSecret": "${NANOBOT_WEBUI_PASSWORD}",
      "websocketRequiresToken": true
    }
  },
  "tools": {
    "restrictToWorkspace": true,
    "exec": {
      "sandbox": "bwrap"
    },
    "ssrfWhitelist": []
  }
}
```

WebUI 是 `8765`，Gateway 健康检查是 `18790`。以后台容器启动：

```bash
sudo docker run -d \
  --name nanobot-gateway \
  --restart unless-stopped \
  --env-file ~/.config/nanobot/nanobot.env \
  --cap-drop ALL \
  --cap-add SYS_ADMIN \
  --security-opt apparmor=unconfined \
  --security-opt seccomp=unconfined \
  -v ~/.nanobot:/home/nanobot/.nanobot \
  -p 127.0.0.1:18790:18790 \
  -p 127.0.0.1:8765:8765 \
  nanobot:v0.2.2 gateway

sudo docker logs -f nanobot-gateway
sudo docker stop nanobot-gateway
```

`SYS_ADMIN` 与两个 unconfined 选项用于让容器内的 bubblewrap 创建命名空间，但也扩大了容器权限。如果禁用 shell 工具或不使用 `tools.exec.sandbox: "bwrap"`，不要照抄这些三项；保留 `--cap-drop ALL`，并按实际功能做一次离线验证。不要用 `--user root` 绕过挂载权限，应让宿主机挂载目录对 UID 1000 可读写，或经过评估后用 `--user "$(id -u):$(id -g)"` 显式映射。

如果使用仓库自带 Compose 文件，也要给 Gateway 配置环境文件，并把宿主机发布地址限制为 `127.0.0.1`。随后使用：

```bash
sudo docker compose up -d nanobot-gateway
sudo docker compose logs -f nanobot-gateway
sudo docker compose down
```

只有需要从其他设备访问 WebUI 时，才把宿主机的 `127.0.0.1:8765` 改成局域网监听地址；此时必须保留 Token 认证，并在不可信网络前增加 TLS 反向代理和防火墙规则。

固定实现可对照 v0.2.2 的 [`Dockerfile`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/Dockerfile) 与 [`docker-compose.yml`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/docker-compose.yml)。

</details>

---

## 5.7 安全建议

`SOUL.md` 或对话中的“不要执行危险命令”只是模型可见的行为约束，不是硬安全边界。把来自 Channel 的任何输入都视为不可信，并叠加身份、文件、进程、网络和操作系统控制。

| 层次 | v0.2.2 控制 | 边界 |
|---|---|---|
| 身份 | `allowFrom`、配对、群组策略、WebSocket Token | 决定谁能发起请求，不限制已授权用户要求 Bot 做什么 |
| 文件 | `tools.restrictToWorkspace: true` | 对工作区感知工具做应用级路径限制，不是 OS 沙箱 |
| 命令 | `tools.exec.sandbox: "bwrap"`，或关闭 `exec` | bubblewrap 仅支持 Linux；容器内还需要相应内核能力 |
| 网络 | 默认 SSRF 检查和最小化 `ssrfWhitelist` | 保护内网、回环和 metadata 目标，不等于完整出站防火墙 |
| 凭据 | `${ENV_NAME}`、权限为 `600` 的环境文件、定期轮换 | 避免写入 Git，但仍需防止日志、进程环境和备份泄露 |

Linux 主机或已按上一节配置 bubblewrap 的容器可使用：

```json
{
  "tools": {
    "restrictToWorkspace": true,
    "exec": {
      "enable": true,
      "sandbox": "bwrap",
      "timeout": 60
    },
    "ssrfWhitelist": []
  }
}
```

不需要执行 shell 时，更小的攻击面是直接关闭工具：

```json
{
  "tools": {
    "restrictToWorkspace": true,
    "exec": {
      "enable": false
    },
    "ssrfWhitelist": []
  }
}
```

上线前逐项确认：

- `allowFrom` 没有无意设置为 `["*"]`，群聊仍是 `mention` 或更严格策略。
- Agent 与项目工作区只挂载必需目录；不要把整个宿主机主目录挂进容器。
- `ssrfWhitelist` 默认为空。确需访问内网服务时只放行精确 CIDR，并同时限制目标服务身份和权限。
- SSRF 检查不是通用防火墙；允许执行的 shell、第三方 MCP 或插件仍可能产生其他网络流量，应在主机或容器层限制出站访问。
- Token 不出现在 Git、命令参数、截图和日志中；泄露后立即到平台撤销并重新生成。
- Gateway、WebUI 和 API 只监听需要的接口；公网访问使用认证、TLS、反向代理和防火墙。
- 容器保持非 root 运行，挂载目录、状态文件和备份只对运行账号开放。

实现边界可对照固定版本的 [`workspace_policy.py`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/nanobot/security/workspace_policy.py)、[`network.py`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/nanobot/security/network.py) 和 [`gateway/service.py`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/nanobot/gateway/service.py)。

---

## 5.8 进阶：接入其他平台

nanobot 可以在同一个 Gateway 中同时运行多个 Channel。每增加一个平台，都重复执行“环境变量 → 配置 → `channels status` → 私聊验证”，不要一次开放所有群组。

### Discord

<details>
<summary>点击展开：Discord 配置</summary>

#### 1. 创建应用并启用 Intent

1. 打开 [Discord Developer Portal](https://discord.com/developers/applications)，创建应用并添加 Bot。
2. 在 **Bot → Privileged Gateway Intents** 中启用 **Message Content Intent**。否则 Bot 能连上 Gateway，却读不到普通消息正文。
3. 开启 Discord 的开发者模式，复制自己的 User ID；需要限制服务器频道时也复制 Channel ID。
4. 保存 Bot Token：

```bash
export DISCORD_BOT_TOKEN='从 Discord Developer Portal 获得的 Token'
```

#### 2. 配置 nanobot

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "${DISCORD_BOT_TOKEN}",
      "allowFrom": ["123456789012345678"],
      "allowChannels": [],
      "groupPolicy": "mention",
      "streaming": true
    }
  }
}
```

- `allowFrom` 使用 Discord User ID，并同时约束私聊和服务器消息。
- `allowChannels` 为空时表示不过滤频道，便于先完成私聊验证。共享服务器上线前应改成测试频道 ID 清单；该过滤也作用于私聊，因此若仍需私聊，还要包含对应 DM Channel ID。允许父频道也会允许其 Thread 或 Forum 帖子。
- `groupPolicy: "mention"` 只在被 `@` 时响应；`"open"` 会处理频道内的每条可见消息，只适合明确隔离的服务器。

#### 3. 邀请并验证

在 OAuth2 URL Generator 中选择 `bot`，至少授予发送消息和读取历史所需权限，再把 Bot 邀请到测试服务器。然后运行：

```bash
nanobot channels status
nanobot gateway
```

先私聊测试，再到测试频道 `@Bot`。确认路径正常后收紧 `allowChannels`；若连接成功但消息内容为空，首先复查 Message Content Intent，而不是修改模型配置。

配置字段可对照固定版本的 [`DiscordConfig`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/nanobot/channels/discord.py)；Intent 的平台定义见 [Discord 官方 Gateway 文档](https://docs.discord.com/developers/events/gateway#message-content-intent)。

</details>

---

### Slack

<details>
<summary>点击展开：Slack 配置</summary>

Slack Channel 使用 Socket Mode，不要求公网回调地址，但需要两种不同的 Token：

- `botToken`：安装到 Workspace 后得到的 `xoxb-...` Token，用来调用 Web API。
- `appToken`：启用 Socket Mode 后得到的 `xapp-...` App-Level Token，需要 `connections:write` scope。

#### 1. 创建并配置 Slack App

1. 在 [Slack App 管理页](https://api.slack.com/apps)创建 App。
2. 开启 Socket Mode，生成 App-Level Token。
3. 添加 Bot scopes：至少包括 `chat:write`、`app_mentions:read`，并为实际订阅的私聊或频道消息添加相应 history scope；需要文件能力时再增加 `files:read` 或 `files:write`。
4. 在 Event Subscriptions 中按场景订阅 `message.im`、`message.channels` 和 `app_mention`，然后重新安装 App 到 Workspace。
5. 分别保存两个 Token：

```bash
export SLACK_BOT_TOKEN='xoxb-...'
export SLACK_APP_TOKEN='xapp-...'
```

#### 2. 配置 nanobot

```json
{
  "channels": {
    "slack": {
      "enabled": true,
      "botToken": "${SLACK_BOT_TOKEN}",
      "appToken": "${SLACK_APP_TOKEN}",
      "dm": {
        "enabled": true,
        "policy": "allowlist",
        "allowFrom": ["U0123456789"]
      },
      "groupPolicy": "mention"
    }
  }
}
```

Slack 的私聊和群组策略是分开的：

- `dm.policy` 默认为 `open`。教程改为 `allowlist`，并在嵌套的 `dm.allowFrom` 中填写 Slack User ID。
- `groupPolicy: "mention"` 只响应 `@Bot`。
- 若使用 `groupPolicy: "allowlist"`，还要配置 `groupAllowFrom`；设置 `groupRequireMention: true` 可同时要求频道在清单中且消息提及 Bot。

最后运行 `nanobot channels status`，确认 Slack 已启用，再启动 Gateway。若 REST 认证成功但 Socket Mode 连接失败，应检查到 Slack WebSocket 的出站网络，而不是把 `appToken` 填进 `botToken`。

配置字段可对照固定版本的 [`SlackConfig`](https://github.com/HKUDS/nanobot/blob/e2e75c913f3524d4bc5b23487a4eed5329eef182/nanobot/channels/slack.py)，平台连接方式见 [Slack 官方 Socket Mode 文档](https://docs.slack.dev/apis/events-api/using-socket-mode/)。

</details>

---

## 小结

完成这一章后，你应该能：

| 能力 | 状态 |
|------|------|
| 在 Telegram 上和 Bot 对话 | ✅ |
| 能检查 Channel 插件和启用状态 | ✅ |
| 能审批和撤销 Telegram 配对 | ✅ |
| 理解 Discord 与 Slack 的群组策略 | ✅ |
| Bot 风格符合配置文件定义 | ✅ |
| Skill 能正常触发 | ✅ |
| 理解 Gateway 和 MessageBus 的作用 | ✅ |
| 知道如何排查"不回复"问题 | ✅ |

---

## 下一步

✅ **如果 Telegram 部署成功** → 继续 [第 6 章：多场景案例库](06-use-cases.md)

⚠️ **如果 Bot 不回复** → 按照本章的诊断树逐步排查

🤔 **如果想理解 MessageBus 原理** → 去 [进阶营第 4 章：消息总线](../hero/04-message-bus.md)
