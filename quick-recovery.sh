#!/bin/bash

# Quick Recovery Script - 再起動後の素早い環境復旧
# 使用方法: ./quick-recovery.sh

set -e

echo "🚀 Multi-Agent System Quick Recovery"
echo "===================================="

# 現在のディレクトリ確認
CURRENT_DIR=$(pwd)
echo "📍 Current directory: $CURRENT_DIR"

# 実行権限の設定
echo "🔧 Setting execute permissions..."
chmod +x *.sh *.py 2>/dev/null || true

# 必要ディレクトリの作成
echo "📁 Creating required directories..."
mkdir -p managed-outputs output-summaries output-archives
mkdir -p progress-states session-configs session-states  
mkdir -p tmux-backups tmp logs
mkdir -p organized/scripts organized/analysis organized/reports

# 基本ファイルの存在確認
echo "✅ Checking critical files..."
CRITICAL_FILES=(
    "workflow-launcher.sh"
    "repo-selector.py"
    "tmux-session-manager.py"
    "tmux-health-monitor.py"
    "output-management-system.py"
    "progress-state-saver.py"
    "start-system.sh"
    "send-message.sh"
)

MISSING_FILES=0
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file (MISSING)"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -gt 0 ]; then
    echo "⚠️  Warning: $MISSING_FILES critical files are missing"
    echo "   Please restore from backup"
fi

# 環境設定の表示
echo ""
echo "📋 Environment Setup Commands:"
echo "================================"
echo "# Add to ~/.bashrc or ~/.zshrc:"
echo 'export MULTIAGENT_HOME="'$CURRENT_DIR'"'
echo 'export PATH="$MULTIAGENT_HOME:$PATH"'
echo ""
echo "# Useful aliases:"
echo 'alias workflow="cd $MULTIAGENT_HOME && ./workflow-launcher.sh"'
echo 'alias tmux-health="python3 $MULTIAGENT_HOME/tmux-health-monitor.py"'
echo 'alias dashboard="python3 $MULTIAGENT_HOME/realtime-status-dashboard.py"'
echo 'alias clearb="tmux clear-history"'

# tmux設定の確認
echo ""
echo "⚙️  Recommended tmux configuration:"
echo "=================================="
echo "# Add to ~/.tmux.conf:"
echo "set-option -g history-limit 10000"
echo "set-option -g status-interval 5"
echo "set-option -g display-time 4000"

# システムテスト
echo ""
echo "🧪 Running system tests..."
echo "========================="

# Python環境確認
if command -v python3 &> /dev/null; then
    echo "✓ Python3 is available"
    python3 --version
else
    echo "✗ Python3 is not available"
fi

# tmux確認
if command -v tmux &> /dev/null; then
    echo "✓ tmux is available"
    tmux -V
else
    echo "✗ tmux is not available"
fi

# GitHub CLI確認
if command -v gh &> /dev/null; then
    echo "✓ GitHub CLI is available"
    gh --version | head -1
else
    echo "✗ GitHub CLI is not available"
fi

# Claude Code確認
if command -v claude &> /dev/null; then
    echo "✓ Claude Code CLI is available"
else
    echo "✗ Claude Code CLI is not available"
fi

# Quick start commands
echo ""
echo "🎯 Quick Start Commands:"
echo "======================="
echo "1. Start tmux health monitor:"
echo "   python3 tmux-health-monitor.py 30 &"
echo ""
echo "2. Start realtime dashboard:"
echo "   python3 realtime-status-dashboard.py 5"
echo ""
echo "3. Launch workflow system:"
echo "   ./workflow-launcher.sh"
echo ""
echo "4. Start 5-agent system:"
echo "   ./start-system.sh"
echo ""
echo "5. View system help:"
echo "   ./workflow-launcher.sh help"

echo ""
echo "✨ Recovery preparation complete!"
echo "================================"
echo ""
echo "💡 Next steps:"
echo "1. Source your shell configuration file"
echo "2. Start the tmux health monitor"
echo "3. Launch the workflow system"
echo ""
echo "📚 Documentation:"
echo "- System design: workflow_automation_design.md"
echo "- Optimization guide: dev3-optimized-workflow.md"
echo "- Backup info: SYSTEM_RESTART_BACKUP.md"