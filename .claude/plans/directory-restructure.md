# 目录结构改造计划

## 目标

参考 byte-of-vdbench 的目录结构，将 byte-of-nanobot 改造为更清晰的文档组织方式。

## 当前结构分析

### 现状
```
byte-of-nanobot/
├── *.md                      # 教程源文件（根目录）
├── docs-site/                # 包装文件（使用 --8<-- 语法）
│   ├── *.md                 # 包装文件
│   ├── build/               # 进阶教程（包装）
│   ├── examples/            # 示例（包装）
│   └── stylesheets/         # 样式
├── build/                    # 进阶教程源文件
├── examples/part2/          # 示例代码源文件
└── scripts/                  # 诊断脚本
```

### 问题
1. 源文件和包装文件分离，使用 snippets 插件引用
2. 文件散落在根目录，不够清晰
3. 与 byte-of-vdbench 的风格不一致

## byte-of-vdbench 参考结构

```
byte-of-vdbench/
├── docs/
│   ├── index.md
│   ├── zh-cn/
│   │   ├── README.md        # 阅读指南
│   │   ├── zero/            # 新手村
│   │   └── hero/            # 进阶营
│   └── superpowers/         # 设计文档（excluded）
├── mkdocs.yml
└── .github/workflows/
```

## 改造方案

### 新结构
```
byte-of-nanobot/
├── docs/
│   ├── index.md                          # 首页（复制 README.md）
│   ├── zh-cn/
│   │   ├── README.md                    # 阅读指南（提取 README.md 路线部分）
│   │   ├── zero/                        # 新手村
│   │   │   ├── 00-before-you-start.md
│   │   │   ├── 01-quick-start.md
│   │   │   ├── 02-soul.md
│   │   │   ├── 03-skills.md
│   │   │   ├── 04-local-integration.md
│   │   │   ├── 05-deploy-telegram.md
│   │   │   └── 06-use-cases.md
│   │   ├── hero/                        # 进阶营
│   │   │   ├── README.md                # 导读（从 build/README.md）
│   │   │   ├── 01-simplest-agent.md
│   │   │   ├── 02-tool-system.md
│   │   │   ├── 03-memory-and-context.md
│   │   │   ├── 04-message-bus.md
│   │   │   ├── 05-skills-and-beyond.md
│   │   │   └── 06-from-mini-agent-to-real-bot.md
│   │   ├── appendix/                    # 附录
│   │   │   ├── environment-precheck.md
│   │   │   ├── troubleshooting-guide.md
│   │   │   ├── troubleshooting.md
│   │   │   └── glossary.md
│   │   ├── examples/                    # 示例
│   │   │   └── part2/
│   │   │       ├── README.md
│   │   │       └── *.py
│   │   └── scripts/                     # 脚本文档
│   │       └── README.md
│   ├── stylesheets/                     # 样式
│   │   └── cyber-theme.css
│   └── superpowers/                     # 设计文档（excluded）
├── scripts/                              # 实际脚本（保持不变）
├── .dev-notes/                          # 开发笔记（保持不变）
├── .archive/                            # 归档（保持不变）
├── mkdocs.yml
├── requirements.txt                     # 重命名 requirements-docs.txt
├── README.md                            # 保留（GitHub 首页）
└── .github/workflows/
```

## 实施步骤

### 1. 创建新目录结构
- 创建 `docs/` 及子目录
- 创建 `docs/zh-cn/zero/`、`docs/zh-cn/hero/`、`docs/zh-cn/appendix/`

### 2. 迁移文件

**新手村教程（根目录 → docs/zh-cn/zero/）：**
- 00-before-you-start.md
- 01-quick-start.md
- 02-soul.md
- 03-skills.md
- 04-local-integration.md
- 05-deploy-telegram.md
- 06-use-cases.md

**进阶营教程（build/ → docs/zh-cn/hero/）：**
- README.md
- 01-simplest-agent.md
- 02-tool-system.md
- 03-memory-and-context.md
- 04-message-bus.md
- 05-skills-and-beyond.md
- 06-from-mini-agent-to-real-bot.md

**附录（根目录 → docs/zh-cn/appendix/）：**
- appendix-environment-precheck.md → environment-precheck.md
- appendix-troubleshooting-guide.md → troubleshooting-guide.md
- appendix-troubleshooting.md → troubleshooting.md
- appendix-glossary.md → glossary.md

**示例（examples/part2/ → docs/zh-cn/examples/part2/）：**
- 整个 part2 目录及其内容

**脚本文档（scripts/README.md → docs/zh-cn/scripts/README.md）：**
- README.md

**样式（docs-site/stylesheets/ → docs/stylesheets/）：**
- cyber-theme.css

**设计文档（.dev-notes/superpowers/ → docs/superpowers/）：**
- 整个 superpowers 目录

### 3. 创建新文件

**docs/index.md：**
- 复制 README.md 的内容
- 作为首页

**docs/zh-cn/README.md：**
- 提取 README.md 中的路线说明部分
- 作为阅读指南

### 4. 更新配置文件

**mkdocs.yml：**
```yaml
site_name: 简明 NanoBot 教程
site_description: 一套面向 AI Agent 初学者的 nanobot 教程
site_url: https://sine-io.github.io/byte-of-nanobot/
repo_url: https://github.com/sine-io/byte-of-nanobot
repo_name: sine-io/byte-of-nanobot
docs_dir: docs
site_dir: site
exclude_docs: |
  /superpowers/**

theme:
  name: material
  language: zh
  palette:
    scheme: slate
    primary: cyan
    accent: deep purple
  features:
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.top
    - navigation.sections
    - toc.integrate
    - content.code.copy
    - content.code.annotate
    - search.suggest
    - search.highlight
    - toc.follow

plugins:
  - search

extra_css:
  - stylesheets/cyber-theme.css

markdown_extensions:
  - admonition
  - attr_list
  - def_list
  - footnotes
  - tables
  - toc:
      permalink: true
  - pymdownx.details
  - pymdownx.highlight:
      anchor_linenums: true
      linenums: true
  - pymdownx.inlinehilite
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true

nav:
  - 首页: index.md
  - 阅读指南: zh-cn/README.md
  - 新手村:
      - 第 0 章：开始之前: zh-cn/zero/00-before-you-start.md
      - 第 1 章：5 分钟跑起来: zh-cn/zero/01-quick-start.md
      - 第 2 章：让 Bot 有个性: zh-cn/zero/02-soul.md
      - 第 3 章：教 Bot 新技能: zh-cn/zero/03-skills.md
      - 第 4 章：本地完整验收: zh-cn/zero/04-local-integration.md
      - 第 5 章：部署到 Telegram: zh-cn/zero/05-deploy-telegram.md
      - 第 6 章：多场景案例库: zh-cn/zero/06-use-cases.md
  - 进阶营:
      - 导读: zh-cn/hero/README.md
      - 第 1 章：最简 Agent: zh-cn/hero/01-simplest-agent.md
      - 第 2 章：工具系统: zh-cn/hero/02-tool-system.md
      - 第 3 章：记忆与上下文: zh-cn/hero/03-memory-and-context.md
      - 第 4 章：消息总线: zh-cn/hero/04-message-bus.md
      - 第 5 章：技能与扩展: zh-cn/hero/05-skills-and-beyond.md
      - 第 6 章：从 Mini Agent 到真实项目: zh-cn/hero/06-from-mini-agent-to-real-bot.md
  - 附录:
      - 环境预检: zh-cn/appendix/environment-precheck.md
      - 统一排障手册: zh-cn/appendix/troubleshooting-guide.md
      - 常见坑与排障: zh-cn/appendix/troubleshooting.md
      - 术语表: zh-cn/appendix/glossary.md
      - 诊断脚本: zh-cn/scripts/README.md
      - 进阶营配套示例: zh-cn/examples/part2/README.md
```

**requirements-docs.txt → requirements.txt：**
- 重命名文件

**.github/workflows/pages.yml：**
- 更新依赖文件名：`requirements-docs.txt` → `requirements.txt`
- 参考 byte-of-vdbench 的 workflow 结构

### 5. 删除旧文件和目录

**删除根目录的教程源文件：**
- 00-before-you-start.md
- 01-quick-start.md
- 02-soul.md
- 03-skills.md
- 04-local-integration.md
- 05-deploy-telegram.md
- 06-use-cases.md
- appendix-*.md

**删除目录：**
- docs-site/（整个目录）
- build/（整个目录）
- examples/（整个目录）

**保留：**
- scripts/（实际脚本，不是文档）
- .dev-notes/
- .archive/
- README.md（GitHub 首页）
- CLAUDE.md
- STRUCTURE.md
- LICENSE

### 6. 更新 STRUCTURE.md

更新项目结构说明文档，反映新的目录组织方式。

## 验证步骤

1. 本地构建测试（如果可能）
2. 检查 git status 确认所有更改
3. 提交并推送
4. 验证 GitHub Pages 部署是否成功

## 注意事项

1. **不使用 snippets 插件**：所有文档直接存放在 docs/ 下
2. **保持 README.md**：作为 GitHub 仓库首页
3. **superpowers 目录排除**：使用 exclude_docs 配置
4. **保持样式**：确保 cyber-theme.css 正确迁移
5. **示例代码**：Python 代码文件也要迁移到 docs/ 下
6. **实际脚本保留**：scripts/ 目录中的 shell 脚本保持在根目录

## 优势

1. **更清晰的组织**：所有文档在 docs/ 下，按语言和类别组织
2. **国际化友好**：zh-cn/ 结构便于未来添加其他语言
3. **一致性**：与 byte-of-vdbench 风格统一
4. **简化构建**：不需要 snippets 插件
5. **易于维护**：文件位置更直观
