#!/bin/bash

# 自動接続スクリプト - tmux attach後に自動でメッセージング機能を有効化

echo "🔄 自動接続システム実行中..."

# 引数チェック (ceo または team)
if [ $# -ne 1 ]; then
    echo "使用方法: $0 [ceo|team]"
    echo "  ceo  - CEOセッションに接続"
    echo "  team - チームセッションに接続"
    exit 1
fi

TARGET=$1

# セッション存在確認
case $TARGET in
    ceo)
        if ! tmux has-session -t ceo 2>/dev/null; then
            echo "❌ CEOセッションが見つかりません"
            echo "先にシステムを起動してください: ./start-system-auto.sh"
            exit 1
        fi
        ;;
    team)
        if ! tmux has-session -t team 2>/dev/null; then
            echo "❌ チームセッションが見つかりません"
            echo "先にシステムを起動してください: ./start-system-auto.sh"
            exit 1
        fi
        ;;
    *)
        echo "❌ 不明なセッション名: $TARGET"
        echo "利用可能: ceo, team"
        exit 1
        ;;
esac

echo "✅ セッション '$TARGET' を確認しました"
echo ""
echo "💬 エージェント間通信機能:"
echo "  ./send-message.sh [エージェント名] \"[メッセージ]\""
echo "  ./send-message.sh --list     エージェント一覧表示"
echo ""
echo "🔧 tmux操作:"
echo "  Ctrl+B → ↑↓←→   画面移動 (team セッションのみ)"
echo "  Ctrl+B → d       デタッチ"
echo ""
echo "📋 接続中... (デタッチするには Ctrl+B → d)"
echo ""

# セッションに接続
tmux attach -t $TARGET