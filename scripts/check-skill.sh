#!/bin/bash
# Skill 诊断脚本
# 用法: bash check-skill.sh <skill-name>

SKILL_NAME=$1
SKILL_PATH=~/.nanobot/workspace/skills/$SKILL_NAME

echo "=== Skill 诊断 ==="
echo "Skill名称: $SKILL_NAME"
echo

# 检查1：路径
if [ -d "$SKILL_PATH" ]; then
    echo "✓ 目录存在: $SKILL_PATH"
else
    echo "✗ 目录不存在: $SKILL_PATH"
    exit 1
fi

# 检查2：SKILL.md
if [ -f "$SKILL_PATH/SKILL.md" ]; then
    echo "✓ SKILL.md 存在"
else
    echo "✗ SKILL.md 不存在"
    exit 1
fi

# 检查3：frontmatter
if head -n 1 "$SKILL_PATH/SKILL.md" | grep -q "^---$"; then
    echo "✓ frontmatter 格式正确"
else
    echo "✗ frontmatter 格式错误（应该以 --- 开头）"
fi

# 检查4：name 和 description
if grep -q "^name:" "$SKILL_PATH/SKILL.md"; then
    echo "✓ 包含 name 字段"
else
    echo "✗ 缺少 name 字段"
fi

if grep -q "^description:" "$SKILL_PATH/SKILL.md"; then
    echo "✓ 包含 description 字段"
else
    echo "✗ 缺少 description 字段"
fi

echo
echo "=== Skill 内容预览 ==="
head -n 10 "$SKILL_PATH/SKILL.md"
