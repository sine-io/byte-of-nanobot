# 项目目录结构说明

本文档说明项目的目录组织方式，以便维护者理解各目录的用途。

## 目录结构

```
byte-of-nanobot/
├── docs/                         # MkDocs 文档目录
│   ├── index.md                 # 首页
│   ├── zh-cn/                   # 中文文档
│   │   ├── README.md           # 阅读指南
│   │   ├── zero/               # 新手村教程
│   │   ├── hero/               # 进阶营教程
│   │   ├── appendix/           # 附录
│   │   ├── examples/           # 示例代码
│   │   └── scripts/            # 脚本文档
│   ├── stylesheets/            # 自定义样式
│   └── superpowers/            # 开发笔记（excluded）
├── scripts/                      # 实际脚本
├── .archive/                    # 归档文件
├── .github/workflows/           # GitHub Actions
├── mkdocs.yml                   # MkDocs 配置
├── requirements.txt             # 文档构建依赖
└── README.md                    # GitHub 仓库首页
```

## 设计原理

### 文档组织方式

参考 [byte-of-vdbench](https://github.com/sine-io/byte-of-vdbench) 的目录结构：

- **所有文档在 `docs/` 下**：直接存放，不使用包装文件或 snippets 插件
- **按语言组织**：`docs/zh-cn/` 存放中文内容，便于未来扩展其他语言
- **按类型分类**：
  - `zero/` - 新手村（快速上手）
  - `hero/` - 进阶营（深入理解）
  - `appendix/` - 附录（参考资料）
  - `examples/` - 示例代码
  - `scripts/` - 脚本文档

### 工作流程

1. **编辑教程**：直接修改 `docs/zh-cn/` 下的 `.md` 文件
2. **本地预览**：`mkdocs serve`（可选）
3. **提交更改**：推送到 main 分支
4. **自动部署**：GitHub Actions 自动构建并部署到 GitHub Pages

### GitHub Pages 配置

- **Workflow**：`.github/workflows/pages.yml`
- **MkDocs 配置**：`mkdocs.yml`
- **文档目录**：`docs_dir: docs`
- **构建目录**：`site_dir: site`
- **部署 URL**：https://sine-io.github.io/byte-of-nanobot/

## 维护指南

### 添加新教程

1. 在对应目录创建源文件：
   - 新手村：`docs/zh-cn/zero/XX-new-chapter.md`
   - 进阶营：`docs/zh-cn/hero/XX-new-chapter.md`
2. 更新 `mkdocs.yml` 的 `nav` 部分

### 更新现有教程

直接编辑 `docs/zh-cn/` 下的源文件即可。

### 添加示例代码

将代码文件放在 `docs/zh-cn/examples/` 对应目录下，MkDocs 会自动处理。

### 清理临时文件

临时文件和旧版本应移到 `.archive/` 目录，而不是直接删除。

## 与旧版本的差异

### 旧结构（已废弃）
```
byte-of-nanobot/
├── *.md                      # 教程源文件（根目录）
├── docs-site/                # 包装文件（使用 --8<-- 语法）
├── build/                    # 进阶教程源文件
└── examples/                 # 示例代码源文件
```

### 新结构（当前）
```
byte-of-nanobot/
└── docs/                     # 所有文档在这里
    └── zh-cn/
        ├── zero/            # 新手村
        ├── hero/            # 进阶营
        ├── appendix/        # 附录
        └── examples/        # 示例
```

### 改进点

1. **更清晰**：所有文档在 `docs/` 下，按类型组织
2. **更简单**：不再使用 snippets 插件和包装文件
3. **国际化友好**：`zh-cn/` 结构便于扩展
4. **一致性**：与 byte-of-vdbench 风格统一

## 参考

- [byte-of-vdbench](https://github.com/sine-io/byte-of-vdbench) - 参考项目
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) - 主题文档
