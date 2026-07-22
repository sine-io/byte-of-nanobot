#!/usr/bin/env bash
# 验证默认 nanobot 配置结构；不输出任何凭据值。

set -u

NANOBOT_TUTORIAL_CONFIG="${HOME}/.nanobot/config.json"
NANOBOT_TUTORIAL_WORKSPACE="${HOME}/.nanobot/workspace"

echo "=== nanobot 配置验证 ==="
echo

if ! command -v jq >/dev/null 2>&1; then
    echo "✗ 需要 jq 才能运行此脚本"
    exit 1
fi

if [ ! -f "${NANOBOT_TUTORIAL_CONFIG}" ]; then
    echo "✗ 配置文件不存在：${NANOBOT_TUTORIAL_CONFIG}"
    echo "  运行 nanobot onboard --wizard 初始化"
    exit 1
fi

if ! jq empty "${NANOBOT_TUTORIAL_CONFIG}" >/dev/null 2>&1; then
    echo "✗ config.json 不是合法 JSON"
    exit 1
fi
echo "✓ config.json 语法正确"

if jq -e '.providers | type == "object"' "${NANOBOT_TUTORIAL_CONFIG}" >/dev/null 2>&1; then
    NANOBOT_TUTORIAL_PROVIDER_COUNT=$(jq '.providers | length' "${NANOBOT_TUTORIAL_CONFIG}")
    echo "✓ providers 对象存在（${NANOBOT_TUTORIAL_PROVIDER_COUNT} 项；未读取凭据值）"
else
    echo "⚠ providers 对象缺失"
fi

NANOBOT_TUTORIAL_PRESET=$(jq -r '.agents.defaults.modelPreset // empty' "${NANOBOT_TUTORIAL_CONFIG}")
if [ -n "${NANOBOT_TUTORIAL_PRESET}" ]; then
    if jq -e --arg preset "${NANOBOT_TUTORIAL_PRESET}" '.modelPresets[$preset] | type == "object"' "${NANOBOT_TUTORIAL_CONFIG}" >/dev/null 2>&1; then
        echo "✓ 活动 modelPreset 存在：${NANOBOT_TUTORIAL_PRESET}"
    else
        echo "✗ agents.defaults.modelPreset 未在 modelPresets 中定义：${NANOBOT_TUTORIAL_PRESET}"
    fi
elif jq -e '.agents.defaults.provider and .agents.defaults.model' "${NANOBOT_TUTORIAL_CONFIG}" >/dev/null 2>&1; then
    echo "⚠ 使用兼容的 agents.defaults.provider/model；新配置推荐命名 modelPresets"
else
    echo "✗ 未找到活动 modelPreset，也没有兼容 provider/model 配置"
fi

if [ -d "${NANOBOT_TUTORIAL_WORKSPACE}" ]; then
    echo "✓ 默认 Agent 工作区存在：${NANOBOT_TUTORIAL_WORKSPACE}"
    for NANOBOT_TUTORIAL_BOOTSTRAP in AGENTS.md SOUL.md USER.md; do
        if [ -f "${NANOBOT_TUTORIAL_WORKSPACE}/${NANOBOT_TUTORIAL_BOOTSTRAP}" ]; then
            echo "  ✓ ${NANOBOT_TUTORIAL_BOOTSTRAP}"
        else
            echo "  ⚠ ${NANOBOT_TUTORIAL_BOOTSTRAP} 缺失"
        fi
    done
else
    echo "✗ 默认 Agent 工作区不存在：${NANOBOT_TUTORIAL_WORKSPACE}"
fi

echo
if command -v nanobot >/dev/null 2>&1; then
    echo "--- nanobot status（不调用模型）---"
    nanobot status || true
else
    echo "⚠ nanobot 命令不可用，跳过 status"
fi

echo
echo "=== 验证完成：未输出 API Key ==="
