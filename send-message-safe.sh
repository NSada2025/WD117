#!/bin/bash

# エージェント間通信スクリプト（安全版）
# 使用方法: ./send-message-safe.sh [エージェント名] "[メッセージ]"

# ログファイル
LOG_FILE="logs/communication.log"
ERROR_LOG="logs/send-errors.log"

# ディレクトリ作成
mkdir -p logs

# エラーハンドリング関数
log_error() {
    local error_msg=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] ERROR: $error_msg" | tee -a "$ERROR_LOG" >&2
}

# ペイン存在確認関数
check_pane_exists() {
    local session=$1
    local pane=$2
    
    # セッション存在確認
    if ! tmux has-session -t "$session" 2>/dev/null; then
        log_error "tmuxセッション '$session' が見つかりません"
        return 1
    fi
    
    # ペイン存在確認
    if ! tmux list-panes -t "$session" -F "#{pane_index}" 2>/dev/null | grep -q "^${pane#*.}$"; then
        log_error "ペイン '$session:$pane' が見つかりません"
        return 1
    fi
    
    return 0
}

# tmuxサーバー状態確認
check_tmux_server() {
    if ! tmux list-sessions &>/dev/null; then
        log_error "tmuxサーバーが応答しません"
        return 1
    fi
    return 0
}

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
        log_error "不明なエージェント名 '$AGENT'"
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

# tmuxサーバー状態確認
if ! check_tmux_server; then
    exit 1
fi

# ペイン存在確認
if ! check_pane_exists "$SESSION" "$PANE"; then
    echo "ヒント: システムを起動してください: ./start-system-auto-safe.sh"
    exit 1
fi

# メッセージ送信（エラーチェック付き）
if tmux send-keys -t "$SESSION:$PANE" "$MESSAGE" C-m 2>/dev/null; then
    echo "[$TIMESTAMP] → $AGENT: $MESSAGE" >> "$LOG_FILE"
    echo "✓ メッセージを送信しました: $AGENT"
    echo "  内容: $MESSAGE"
else
    log_error "メッセージ送信に失敗しました: $AGENT"
    exit 1
fi