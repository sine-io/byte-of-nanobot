# 贡献指南

本仓库只维护中文 nanobot 教程。普通修订应保持“小白路线 + Hero 路线”的渐进结构；版本同步必须同时保护稳定版操作边界和 main 差异标记。

## 普通文档变更

提交前确认：

1. 命令、配置字段和源码说明有可核对的版本依据。
2. 稳定版步骤可直接跟做；尚未发布的行为放在明确的 main 差异提示中。
3. 源码链接使用 40 位提交 SHA，不使用可移动分支、标签或固定行号。
4. 示例不包含真实密钥，不在自动化测试中访问模型、公共 API 或真实 Channel。
5. Docker 命令按仓库约定使用 `sudo docker ...`。
6. 只修改当前 Issue 定义的范围，额外问题另开 Issue。

## 升级 nanobot 基线

升级稳定版或重新审计 main 时，先在独立 Issue 和分支中完成以下流程。

### 1. 固定两个提交

在本地上游 clone 中获取目标稳定标签和准备审计的 main，然后记录完整 SHA：

```bash
git fetch origin --tags
git rev-parse <stable-tag>^{commit}
git rev-parse origin/main^{commit}
```

不要先改教程正文。先把候选版本与当前 `scripts/upstream-baseline.json` 做源码和 CLI 差异审计。

### 2. 审查关键模块

`key_modules` 是最低审查面，不是完整上游模块清单。至少逐项核对：

| 领域 | 重点 |
|---|---|
| Agent 执行 | Provider 流、工具循环、Session 与出站编排的责任边界 |
| 上下文与状态 | Bootstrap 来源、项目/Agent 工作区、Memory、Consolidator、Dream |
| 模型 | preset、fallback、单次覆盖和运行时解析 |
| 自动化 | cron、Heartbeat、会话绑定任务、触发器和投递语义 |
| Goals/Subagents | 工具名、授权边界、生命周期与并发 |
| MCP | transport、白名单、超时、重连、SSRF 与结果处理 |
| Channel | registry、包结构、manifest、第三方扩展和 WebUI 资源 |
| API/SDK | 启动方式、鉴权、流式响应和每次运行覆盖 |

确认路径存在时使用本地 Git 对象，不依赖网页是否恰好可访问：

```bash
git cat-file -e '<full-sha>:<path>'
```

### 3. 审查命令契约

在目标源码对应的隔离环境里查看帮助，不调用模型：

```bash
nanobot --help
nanobot onboard --help
nanobot agent --help
nanobot gateway --help
nanobot channels --help
nanobot serve --help
```

把仍需出现在教程中的命令写入 `command_assertions.required`，把确认失效的形式写入 `command_assertions.forbidden`。不要为了让检查通过而降低最低出现次数；先判断正文是否遗漏了必要入口。

### 4. 更新源码链接清单

每个 GitHub 源码链接都必须满足：

- revision 是 `upstream.stable.sha` 或 `upstream.main.sha` 的完整值；
- `blob:<path>` 或 `tree:<path>` 已在对应 `audited_sources` 中；
- 路径已经在目标上游 clone 中用 `git cat-file -e` 人工确认；
- 核心行为对应的路径同时登记在 `key_modules`。

CI 的漂移检查完全离线。它能证明链接仍符合上次审计过的 SHA/路径清单，不能证明远端仓库后来发生了什么；更新清单前的人工上游核对不能省略。

### 5. 更新正文与差异附录

先更新稳定版操作正文，再更新“稳定版与 main 架构差异”附录。特别复查：

- main 独有命令是否错误进入稳定版步骤；
- Bootstrap 所有权是否与目标版本一致；
- `TOOLS.md` 是否仍被明确说明为**不是**自动 Bootstrap 文件；
- 旧目录、旧附录路径、旧日志入口和过期模型名是否重新出现；
- 示例是否仍限制文件、命令和网络边界。

### 6. 运行离线验收

```bash
python3 scripts/check_upstream_drift.py --report
python3 -m unittest discover -s tests -v
python3 -m compileall -q docs/zh-cn/examples/hero
bash -n scripts/*.sh
python3 -m mkdocs build --strict
```

`--report` 把基线、扫描数量、命令断言和发现项输出为 Markdown，并在发现漂移时返回非零状态。PR 正文应记录报告结果和人工核对的上游提交。

真实模型、公共 API、WebUI 和 Channel 只做独立人工冒烟，不进入 CI，也不把测试凭据提交到仓库。

## PR 要求

- 一个 Issue 对应一个分支和一个 PR。
- PR 正文说明上游依据、用户可见变化和验证结果，并包含 `Closes #<number>`。
- CI 失败只在当前分支修复。
- 合并使用 squash，并删除远端分支。
