#!/bin/bash
# 配置验证脚本
# 用法: bash verify-config.sh

CONFIG_FILE=~/.nanobot/config.json

echo "=== 配置验证 ==="
echo

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "✗ 配置文件不存在: $CONFIG_FILE"
    echo "  提示: 运行 nanobot onboard 初始化配置"
    exit 1
fi

echo "✓ 配置文件存在: $CONFIG_FILE"
echo

# 检查 JSON 格式
if ! jq empty "$CONFIG_FILE" 2>/dev/null; then
    echo "✗ JSON 格式错误"
    echo "  请检查配置文件格式"
    exit 1
fi

echo "✓ JSON 格式正确"
echo

# 检查 providers
if jq -e '.providers' "$CONFIG_FILE" > /dev/null 2>&1; then
    echo "✓ providers 配置存在"

    # 列出配置的 providers
    PROVIDERS=$(jq -r '.providers | keys[]' "$CONFIG_FILE" 2>/dev/null)
    if [ -n "$PROVIDERS" ]; then
        echo "  已配置的 providers:"
        echo "$PROVIDERS" | while read -r p; do
            echo "    - $p"
        done
    fi
else
    echo "⚠ providers 配置缺失"
fi

echo

# 检查 agents.defaults
if jq -e '.agents.defaults' "$CONFIG_FILE" > /dev/null 2>&1; then
    echo "✓ agents.defaults 配置存在"

    PROVIDER=$(jq -r '.agents.defaults.provider' "$CONFIG_FILE" 2>/dev/null)
    MODEL=$(jq -r '.agents.defaults.model' "$CONFIG_FILE" 2>/dev/null)

    echo "  provider: $PROVIDER"
    echo "  model: $MODEL"
else
    echo "⚠ agents.defaults 配置缺失"
fi

echo

# 检查工作区
WORKSPACE=~/.nanobot/workspace
if [ -d "$WORKSPACE" ]; then
    echo "✓ 工作区存在: $WORKSPACE"

    # 检查关键文件
    for file in SOUL.md AGENTS.md USER.md TOOLS.md; do
        if [ -f "$WORKSPACE/$file" ]; then
            echo "  ✓ $file"
        else
            echo "  ⚠ $file 缺失"
        fi
    done
else
    echo "✗ 工作区不存在: $WORKSPACE"
    echo "  提示: 运行 nanobot onboard 初始化工作区"
fi

echo
echo "=== 验证完成 ==="
