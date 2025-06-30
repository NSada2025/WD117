#!/bin/bash
# tmux-safe-session-manager.sh - 安全なtmuxセッション管理ユーティリティ

# 色付き出力用の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ログファイル
LOG_FILE="logs/tmux-session-manager.log"
mkdir -p logs

# ログ出力関数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# セッションの存在確認
has_session() {
    local session_name=$1
    tmux has-session -t "$session_name" 2>/dev/null
}

# 安全なセッション終了
safe_kill_session() {
    local session_name=$1
    local timeout=${2:-5}  # デフォルト5秒のタイムアウト
    
    if ! has_session "$session_name"; then
        log "INFO: セッション '$session_name' は存在しません"
        return 0
    fi
    
    log "INFO: セッション '$session_name' の安全な終了を開始"
    
    # ステップ1: 実行中のコマンドを中断
    tmux send-keys -t "$session_name" C-c 2>/dev/null
    sleep 0.5
    
    # ステップ2: 各ペインにexitコマンドを送信
    local panes=$(tmux list-panes -t "$session_name" -F '#P' 2>/dev/null)
    for pane in $panes; do
        tmux send-keys -t "$session_name:.$pane" "exit" C-m 2>/dev/null
    done
    
    # ステップ3: タイムアウトまで待機
    local count=0
    while [ $count -lt $timeout ] && has_session "$session_name"; do
        sleep 1
        ((count++))
    done
    
    # ステップ4: まだ存在する場合は強制終了
    if has_session "$session_name"; then
        log "WARN: 通常の終了がタイムアウト。強制終了します。"
        tmux kill-session -t "$session_name" 2>/dev/null
        sleep 0.5
        
        if has_session "$session_name"; then
            log "ERROR: セッション '$session_name' の終了に失敗"
            return 1
        fi
    fi
    
    log "INFO: セッション '$session_name' を正常に終了"
    return 0
}

# セッションの作成または再利用
create_or_reuse_session() {
    local session_name=$1
    local reuse=${2:-false}  # デフォルトは再利用しない
    
    if has_session "$session_name"; then
        if [ "$reuse" = true ]; then
            log "INFO: 既存のセッション '$session_name' を再利用"
            return 0
        else
            log "INFO: 既存のセッション '$session_name' を終了"
            safe_kill_session "$session_name"
        fi
    fi
    
    log "INFO: 新しいセッション '$session_name' を作成"
    tmux new-session -d -s "$session_name"
    return $?
}

# すべてのプロジェクトセッションを安全に終了
cleanup_all_sessions() {
    local sessions=("ceo" "team")
    
    echo -e "${YELLOW}すべてのプロジェクトセッションをクリーンアップします${NC}"
    
    for session in "${sessions[@]}"; do
        safe_kill_session "$session"
    done
    
    # tmpディレクトリのクリーンアップ
    if [ -d "tmp" ]; then
        rm -rf tmp/*
        log "INFO: tmpディレクトリをクリーンアップ"
    fi
}

# ヘルスチェック
check_session_health() {
    local session_name=$1
    
    if ! has_session "$session_name"; then
        echo -e "${RED}✗ セッション '$session_name' は存在しません${NC}"
        return 1
    fi
    
    # ペイン数を確認
    local pane_count=$(tmux list-panes -t "$session_name" 2>/dev/null | wc -l)
    
    # セッションの稼働時間を取得
    local session_info=$(tmux list-sessions -F '#{session_name} #{session_created}' | grep "^$session_name ")
    
    echo -e "${GREEN}✓ セッション '$session_name' は正常です${NC}"
    echo "  - ペイン数: $pane_count"
    
    return 0
}

# メイン処理（直接実行された場合）
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    case "${1:-}" in
        "kill")
            safe_kill_session "${2:-}"
            ;;
        "create")
            create_or_reuse_session "${2:-}" "${3:-false}"
            ;;
        "cleanup")
            cleanup_all_sessions
            ;;
        "health")
            check_session_health "${2:-}"
            ;;
        *)
            echo "使用方法:"
            echo "  $0 kill <session-name>     - セッションを安全に終了"
            echo "  $0 create <session-name> [true|false] - セッションを作成（trueで再利用）"
            echo "  $0 cleanup                 - すべてのセッションをクリーンアップ"
            echo "  $0 health <session-name>   - セッションのヘルスチェック"
            exit 1
            ;;
    esac
fi