# 文件清理指南

## 需要归档的过时文件

以下文件是旧版本章节，已被新文件替代，建议重命名以避免混淆：

### 1. 04-deploy.md → 04-deploy.old.md

**原因：** 该文件是旧版第4章（部署到Telegram），现已被以下文件替代：
- `04-local-integration.md` - 本地完整验收
- `05-deploy-telegram.md` - 部署到Telegram

**手动操作：**
```bash
# Windows PowerShell
Rename-Item "04-deploy.md" "04-deploy.old.md"

# Git Bash / Linux / macOS
mv 04-deploy.md 04-deploy.old.md
```

---

### 2. 05-first-real-bot.md → 05-first-real-bot.old.md

**原因：** 该文件是旧版第5章，内容已重组并拆分到：
- `04-local-integration.md` - 本地验收部分
- `06-use-cases.md` - 案例库部分

**手动操作：**
```bash
# Windows PowerShell
Rename-Item "05-first-real-bot.md" "05-first-real-bot.old.md"

# Git Bash / Linux / macOS
mv 05-first-real-bot.md 05-first-real-bot.old.md
```

---

## 快速执行脚本

### Windows (PowerShell)
```powershell
cd G:\sineio-projects\byte-of-nanobot
Rename-Item "04-deploy.md" "04-deploy.old.md" -ErrorAction SilentlyContinue
Rename-Item "05-first-real-bot.md" "05-first-real-bot.old.md" -ErrorAction SilentlyContinue
Write-Host "✓ 旧文件已归档"
```

### Linux / macOS / Git Bash
```bash
cd /path/to/byte-of-nanobot
mv 04-deploy.md 04-deploy.old.md 2>/dev/null || true
mv 05-first-real-bot.md 05-first-real-bot.old.md 2>/dev/null || true
echo "✓ 旧文件已归档"
```

---

## Git 提交建议

```bash
git add -A
git commit -m "chore: archive obsolete chapter files (04-deploy, 05-first-real-bot)"
```

---

## 新章节结构

| 旧编号 | 旧文件 | 新编号 | 新文件 |
|-------|--------|-------|--------|
| - | - | 00 | 00-before-you-start.md |
| 01 | 01-quick-start.md | 01 | 01-quick-start.md |
| 02 | 02-soul.md | 02 | 02-soul.md |
| 03 | 03-skills.md | 03 | 03-skills.md |
| 04 | 04-deploy.md | 04 | 04-local-integration.md ⭐ |
| 05 | 05-first-real-bot.md | 05 | 05-deploy-telegram.md ⭐ |
| - | - | 06 | 06-use-cases.md ⭐ |

⭐ 表示新增或重组的文件

---

## 验证清单

归档完成后，检查：

- [ ] `04-deploy.old.md` 文件存在
- [ ] `05-first-real-bot.old.md` 文件存在
- [ ] 没有意外删除其他文件
- [ ] Git 状态正常（`git status`）

---

**注意：** 由于 Claude 在 Windows 环境下无法直接重命名文件，请您手动执行上述命令。
