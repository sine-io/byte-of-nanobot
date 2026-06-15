# 项目目录结构说明

本文档说明项目的目录组织方式，以便维护者理解各目录的用途。

## 目录结构

```
byte-of-nanobot/
├── *.md                      # 教程源文件（被 MkDocs 引用）
├── docs-site/                # MkDocs 文档目录
│   ├── *.md                 # 包装文件（使用 --8<-- 语法引用根目录源文件）
│   ├── build/               # 进阶教程
│   ├── examples/            # 示例代码
│   ├── scripts/             # 脚本文档
│   └── stylesheets/         # 自定义样式
├── build/                    # 进阶教程源文件
├── examples/                 # 示例代码源文件
├── scripts/                  # 诊断脚本
├── .dev-notes/              # 开发笔记和设计文档
├── .archive/                # 归档的临时文件和旧版本
├── .github/workflows/       # GitHub Actions 工作流
└── site/                     # MkDocs 构建输出（git ignored）
```

## 设计原理

### 为什么教程源文件在根目录？

使用 MkDocs 的 `pymdownx.snippets` 插件：
- 根目录的 `README.md` 既能在 GitHub 首页显示，又能被 MkDocs 使用
- 教程文件在根目录便于直接浏览和编辑
- `docs-site/` 中的包装文件使用 `--8<-- "filename.md"` 语法引用源文件
- MkDocs 构建时自动展开引用

### 工作流程

1. **编辑教程**：修改根目录的 `.md` 源文件
2. **本地预览**：`mkdocs serve` （可选）
3. **提交更改**：推送到 main 分支
4. **自动部署**：GitHub Actions 自动构建并部署到 GitHub Pages

### GitHub Pages 配置

- **Workflow**：`.github/workflows/pages.yml`
- **MkDocs 配置**：`mkdocs.yml`
- **文档目录**：`docs_dir: docs-site`
- **构建目录**：`site_dir: site`
- **部署 URL**：https://sine-io.github.io/byte-of-nanobot/

## 维护指南

### 添加新教程

1. 在根目录创建源文件：`07-new-chapter.md`
2. 在 `docs-site/` 创建包装文件：
   ```markdown
   --8<-- "07-new-chapter.md"
   ```
3. 更新 `mkdocs.yml` 的 `nav` 部分

### 更新现有教程

直接编辑根目录的源文件即可，无需修改 `docs-site/` 中的包装文件。

### 清理临时文件

临时文件和旧版本应移到 `.archive/` 目录，而不是直接删除。
