# 诊断脚本集合

这个目录说明仓库根 `scripts/` 下的本地诊断脚本。请从仓库根目录运行；脚本不调用模型或真实 Channel。

!!! warning "不要把诊断变成泄密"
    `check-env.sh` 和 `verify-config.sh` 不输出凭据值。`check-skill.sh` 会预览目标 `SKILL.md` 的开头，因此 Skill 文件本身也不应保存密钥、Token 或个人数据。

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

验证 `~/.nanobot/config.json` 的格式和必要结构，但不打印 Provider 或 Channel 凭据。

**用法：**
```bash
bash scripts/verify-config.sh
```

**检查项目：**
- 配置文件是否存在
- JSON 格式是否正确
- Provider 名称与活动 model preset
- 命名 `modelPresets` 或兼容 provider/model 配置
- 工作区目录和关键文件
- `nanobot status`（已安装时）

---

### 3. check-skill.sh - Skill 检查

检查指定 Skill 的配置是否正确。

**用法：**
```bash
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

# 2. 安装教程固定版本（如果未安装）
python -m pip install "nanobot-ai==0.2.2"

# 3. 用向导初始化配置
nanobot onboard --wizard

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
bash scripts/check-skill.sh exchange-rate
```

---

## 📝 注意事项

1. **Windows 用户：** 使用 Git Bash 或 WSL 运行这些脚本
2. **运行方式：** 文档统一使用 `bash scripts/<name>.sh`，不要求给文件增加可执行位
3. **依赖工具：** `verify-config.sh` 需要 `jq` 工具
   ```bash
   # macOS
   brew install jq

   # Ubuntu/Debian
   sudo apt install jq

   # Windows (Git Bash / WSL)
   # 使用系统包管理器安装 jq
   ```

4. **配置修改：** 脚本只诊断，不会重写 `config.json`。发现问题后优先回到 `nanobot onboard --wizard` 或 WebUI；不要用教程片段覆盖完整配置。

---

## 🔗 相关文档

- [第 0 章：开始之前](../zero/00-before-you-start.md) - 环境准备
- [第 1 章：5 分钟跑起来](../zero/01-quick-start.md) - 快速开始
- [附录：统一排障手册](../appendix/troubleshooting-guide.md) - 唯一完整的系统化排障正文

---

## 🤝 贡献

如果你发现问题或有改进建议，欢迎提交 Issue 或 Pull Request。
