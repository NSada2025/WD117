#!/bin/bash

# PowerShell再起動後の簡単起動スクリプト

echo "🔍 既存セッション確認中..."

# 既存セッションがあるか確認
if tmux has-session -t ceo 2>/dev/null && tmux has-session -t team 2>/dev/null; then
    echo "✅ 既存セッション発見！接続方法："
    echo ""
    echo "📋 タブ1 (CEO):"
    echo "  wsl"
    echo "  tmux attach -t ceo"
    echo ""
    echo "📋 タブ2 (チーム):"
    echo "  wsl"
    echo "  tmux attach -t team"
    echo ""
    echo "💡 ヒント: tmuxセッションは既に実行中です"
else
    echo "⚠️  セッションが見つかりません。新規起動しますか？"
    echo ""
    echo "実行するコマンド:"
    echo "  ./start-system.sh"
    echo "  ./initialize-agents.sh"
    read -p "続行しますか？ (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./start-system.sh
        ./initialize-agents.sh
        echo ""
        echo "✅ 起動完了！接続してください："
        echo ""
        echo "📋 タブ1: tmux attach -t ceo"
        echo "📋 タブ2: tmux attach -t team"
    fi
fi