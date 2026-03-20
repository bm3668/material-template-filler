#!/bin/bash
# 材料模板填充 Web 应用启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"
WORKSPACE="$SKILL_ROOT/workspace"

echo "🚀 材料模板填充 Web 应用"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查依赖
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  检测到未安装 Flask，正在安装..."
    pip3 install --user flask python-docx
    echo "✅ Flask 安装完成"
fi

# 检查工作目录
if [ ! -d "$WORKSPACE" ]; then
    echo "📁 创建工作目录：$WORKSPACE"
    mkdir -p "$WORKSPACE"/{templates,inputs,filled}
fi

echo ""
echo "📂 工作目录：$WORKSPACE"
echo "📁 模板目录：$WORKSPACE/templates"
echo "📁 项目说明：$WORKSPACE/inputs"
echo "📁 输出目录：$WORKSPACE/filled"
echo ""
echo "🌐 访问地址：http://localhost:5000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动应用
cd "$SCRIPT_DIR"
python3 app.py
