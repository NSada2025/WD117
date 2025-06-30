#!/bin/bash

# PowerShell再起動後の簡単起動スクリプト (自動化統合版)

echo "🔍 既存セッション確認中..."

# 既存セッションがあるか確認
if tmux has-session -t ceo 2>/dev/null && tmux has-session -t team 2>/dev/null; then
    echo "✅ 既存セッション発見！接続方法："
    echo ""
    echo "📋 自動接続スクリプト使用 (推奨):"
    echo "  ./auto-attach.sh ceo   # CEO画面"
    echo "  ./auto-attach.sh team  # チーム画面"
    echo ""
    echo "📋 従来の接続方法:"
    echo "  tmux attach -t ceo"
    echo "  tmux attach -t team"
    echo ""
    echo "💡 ヒント: 自動接続スクリプトでメッセージング機能も有効化されます"
else
    echo "⚠️  セッションが見つかりません。新規起動しますか？"
    echo ""
    echo "🚀 起動オプション:"
    echo "  [1] 統合自動化システム (推奨): ./start-system-auto.sh"
    echo "  [2] 従来システム: ./start-system.sh + ./initialize-agents.sh"
    echo ""
    read -p "どちらを実行しますか？ (1/2): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[1]$ ]]; then
        echo "🚀 統合自動化システム起動中..."
        ./start-system-auto.sh
        echo ""
        echo "✅ 起動完了！自動接続してください："
        echo ""
        echo "📋 ./auto-attach.sh ceo   # CEO画面"
        echo "📋 ./auto-attach.sh team  # チーム画面"
    elif [[ $REPLY =~ ^[2]$ ]]; then
        echo "🔧 従来システム起動中..."
        ./start-system.sh
        ./initialize-agents.sh
        echo ""
        echo "✅ 起動完了！接続してください："
        echo ""
        echo "📋 tmux attach -t ceo"
        echo "📋 tmux attach -t team"
    else
        echo "❌ キャンセルされました"
    fi
fi