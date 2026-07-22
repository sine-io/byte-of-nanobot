#!/usr/bin/env bash
# nanobot 教程环境检查：只做本地、只读检查，不调用模型或外部 API。

set -u

echo "=== nanobot 教程环境检查 ==="
echo

echo "1. Python 版本"
if command -v python3 >/dev/null 2>&1; then
    TUTORIAL_PYTHON_VERSION=$(python3 --version 2>&1)
    echo "   ✓ ${TUTORIAL_PYTHON_VERSION}"
    if python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
        echo "   ✓ 符合要求（>= 3.11）"
    else
        echo "   ✗ 需要 Python 3.11 或更高版本"
    fi
else
    echo "   ✗ 未找到 python3"
fi

echo
echo "2. pip 与 venv"
if command -v python3 >/dev/null 2>&1 && python3 -m pip --version >/dev/null 2>&1; then
    echo "   ✓ $(python3 -m pip --version)"
else
    echo "   ✗ python3 -m pip 不可用"
fi
if command -v python3 >/dev/null 2>&1 && python3 -m venv --help >/dev/null 2>&1; then
    echo "   ✓ venv 模块可用"
else
    echo "   ✗ venv 模块不可用"
    echo "   提示：Debian/Ubuntu 可安装 python3-venv"
fi

echo
echo "3. 可选本地工具"
for TUTORIAL_COMMAND in curl git jq; do
    if command -v "${TUTORIAL_COMMAND}" >/dev/null 2>&1; then
        echo "   ✓ ${TUTORIAL_COMMAND}"
    else
        echo "   ⚠ ${TUTORIAL_COMMAND} 未安装（部分教程步骤可能需要）"
    fi
done

echo
echo "4. nanobot"
if command -v nanobot >/dev/null 2>&1; then
    TUTORIAL_NANOBOT_VERSION=$(nanobot --version 2>&1)
    echo "   ✓ ${TUTORIAL_NANOBOT_VERSION}"
    echo
    echo "5. 默认配置状态（不调用模型）"
    if nanobot status; then
        echo "   ✓ nanobot status 成功"
    else
        echo "   ⚠ status 未通过；安装后可运行 nanobot onboard --wizard"
    fi
else
    echo "   ⚠ nanobot 尚未安装"
    echo "   教程基线安装：python -m pip install \"nanobot-ai==0.2.2\""
fi

echo
echo "=== 检查完成：本脚本未读取或打印 API Key ==="
