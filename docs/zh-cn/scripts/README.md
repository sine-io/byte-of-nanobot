# 诊断脚本集合

这个目录包含用于诊断 nanobot 环境和配置的实用脚本。

## 📋 可用脚本

### 1. check-env.sh - 环境检查

检查 Python、pip、venv 和常用工具是否正确安装。

**用法：**
```bash
bash scripts/check-env.sh
```

**检查项目：**
- Python 版本 (>= 3.11)
- pip 是否可用
- venv 模块是否可用
- curl、git、jq 等工具
- nanobot 是否已安装

---

### 2. verify-config.sh - 配置验证

验证 `~/.nanobot/config.json` 的格式和内容。

**用法：**
```bash
bash scripts/verify-config.sh
```

**检查项目：**
- 配置文件是否存在
- JSON 格式是否正确
- providers 配置
- agents.defaults 配置
- 工作区目录和关键文件

---

### 3. check-skill.sh - Skill 检查

检查指定 Skill 的配置是否正确。

**用法：**
```bash
bash scripts/check-skill.sh <skill-name>

# 示例
bash scripts/check-skill.sh exchange-rate
```

**检查项目：**
- Skill 目录是否存在
- SKILL.md 文件是否存在
- frontmatter 格式是否正确
- name 和 description 字段是否存在

---

## 🚀 快速诊断流程

### 第一次安装时

```bash
# 1. 检查环境
bash scripts/check-env.sh

# 2. 安装 nanobot（如果未安装）
pip install nanobot-ai

# 3. 初始化配置
nanobot onboard

# 4. 验证配置
bash scripts/verify-config.sh
```

---

### 遇到问题时

```bash
# 1. 如果命令不存在 → 检查环境
bash scripts/check-env.sh

# 2. 如果无法连接 LLM → 验证配置
bash scripts/verify-config.sh

# 3. 如果 Skill 不触发 → 检查 Skill
bash scripts/check-skill.sh <skill-name>
```

---

## 📝 注意事项

1. **Windows 用户：** 使用 Git Bash 或 WSL 运行这些脚本
2. **权限问题：** 如果遇到权限错误，确保脚本有执行权限
   ```bash
   chmod +x scripts/*.sh
   ```
3. **依赖工具：** `verify-config.sh` 需要 `jq` 工具
   ```bash
   # macOS
   brew install jq

   # Ubuntu/Debian
   sudo apt install jq

   # Windows (Git Bash)
   # 从 https://stedolan.github.io/jq/download/ 下载
   ```

---

## 🔗 相关文档

- [第 0 章：开始之前](../zero/00-before-you-start.md) - 环境准备
- [第 1 章：5 分钟跑起来](../zero/01-quick-start.md) - 快速开始
- [附录：统一排障手册](../appendix/troubleshooting-guide.md) - 系统化排障

---

## 🤝 贡献

如果你发现问题或有改进建议，欢迎提交 Issue 或 Pull Request。
