#!/bin/bash
# 环境检查脚本
# 用法: bash check-env.sh

echo "=== 环境检查 ==="
echo

# 检查 Python 版本
echo "1. Python 版本："
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "   ✓ $PYTHON_VERSION"

    # 检查是否 >= 3.11
    MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
    MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 11 ]; then
        echo "   ✓ Python 版本符合要求 (>= 3.11)"
    else
        echo "   ✗ Python 版本过低，需要 >= 3.11"
    fi
else
    echo "   ✗ Python3 未安装"
fi

echo

# 检查 pip
echo "2. pip："
if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
    PIP_VERSION=$(python3 -m pip --version 2>&1)
    echo "   ✓ $PIP_VERSION"
else
    echo "   ✗ pip 未安装"
fi

echo

# 检查 venv
echo "3. venv 模块："
if python3 -m venv --help &> /dev/null; then
    echo "   ✓ venv 模块可用"
else
    echo "   ✗ venv 模块不可用"
    echo "   提示: Ubuntu/Debian 运行: sudo apt install python3-venv"
fi

echo

# 检查常用命令
echo "4. 常用工具："
for cmd in curl git jq; do
    if command -v $cmd &> /dev/null; then
        echo "   ✓ $cmd 已安装"
    else
        echo "   ⚠ $cmd 未安装（某些 Skill 可能需要）"
    fi
done

echo

# 检查 nanobot
echo "5. nanobot："
if command -v nanobot &> /dev/null; then
    NANOBOT_VERSION=$(nanobot --version 2>&1)
    echo "   ✓ $NANOBOT_VERSION"
else
    echo "   ✗ nanobot 未安装"
    echo "   提示: 运行 pip install nanobot-ai"
fi

echo
echo "=== 检查完成 ==="
