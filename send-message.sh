#!/bin/bash

# エージェント間通信スクリプト
# 使用方法: ./send-message.sh [エージェント名] "[メッセージ]"

# ログファイル
LOG_FILE="logs/communication.log"

# 引数チェック
if [ "$1" = "--list" ]; then
    echo "利用可能なエージェント:"
    echo "  ceo     - 最高経営責任者"
    echo "  manager - プロジェクトマネージャー"
    echo "  dev1    - 実行エージェント1 (UI/UX・フロントエンド)"
    echo "  dev2    - 実行エージェント2 (バックエンド・データ分析)"
    echo "  dev3    - 実行エージェント3 (品質管理・テスト)"
    exit 0
fi

if [ $# -ne 2 ]; then
    echo "使用方法: $0 [エージェント名] \"[メッセージ]\""
    echo "エージェント一覧: $0 --list"
    exit 1
fi

AGENT=$1
MESSAGE=$2
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# エージェント名の検証
case $AGENT in
    ceo|manager|dev1|dev2|dev3)
        ;;
    *)
        echo "エラー: 不明なエージェント名 '$AGENT'"
        echo "利用可能なエージェント: ceo, manager, dev1, dev2, dev3"
        exit 1
        ;;
esac

# tmuxセッション・ペインの特定
case $AGENT in
    ceo)
        SESSION="ceo"
        PANE="0"
        ;;
    manager)
        SESSION="team"
        PANE="0.0"
        ;;
    dev1)
        SESSION="team"
        PANE="0.1"
        ;;
    dev2)
        SESSION="team"
        PANE="0.2"
        ;;
    dev3)
        SESSION="team"
        PANE="0.3"
        ;;
esac

# セッション存在確認
if ! tmux has-session -t $SESSION 2>/dev/null; then
    echo "エラー: tmuxセッション '$SESSION' が見つかりません"
    echo "先にシステムを起動してください: ./start-system.sh"
    exit 1
fi

# メッセージ送信
echo "[$TIMESTAMP] → $AGENT: $MESSAGE" >> $LOG_FILE
tmux send-keys -t $SESSION:$PANE "$MESSAGE" C-m

echo "メッセージを送信しました: $AGENT"
echo "内容: $MESSAGE"