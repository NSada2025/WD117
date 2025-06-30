#!/bin/bash

# Enhanced Message Sending System - Phase 1 (基本自動化)
# 使用方法: ./enhanced-send-message.sh [エージェント名] "[メッセージ]" [オプション]
# オプション: --auto-execute (default: true), --manual, --test-mode

# バージョン情報
VERSION="1.0.0-phase1"
BUILD_DATE="$(date '+%Y-%m-%d')"

# カラー定義（UI/UX向上）
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 設定
LOG_FILE="logs/enhanced_communication.log"
ERROR_LOG="logs/enhanced_errors.log"
METRICS_FILE="logs/messaging_metrics.log"
PERFORMANCE_LOG="logs/performance_monitoring.log"

# エラーハンドリング設定
MAX_RETRY_ATTEMPTS=3
RETRY_DELAY=1
TIMEOUT_SECONDS=30

# エラーコード定義
ERROR_CODES=(
    [1]="INVALID_ARGUMENTS"
    [2]="SESSION_NOT_FOUND"
    [3]="TMUX_COMMAND_FAILED"
    [4]="TIMEOUT_ERROR"
    [5]="PERMISSION_DENIED"
    [6]="NETWORK_ERROR"
    [7]="SYSTEM_RESOURCE_ERROR"
)

# オプション解析
AUTO_EXECUTE=true
TEST_MODE=false
VERBOSE=false
RETRY_ENABLED=true
MONITORING_ENABLED=true

# インタラクティブメニュー表示
show_interactive_menu() {
    echo -e "${CYAN}🎯 Enhanced Message System - インタラクティブモード${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "エージェントを選択してください:"
    echo "  ${GREEN}1${NC}) ceo     - 最高経営責任者"
    echo "  ${GREEN}2${NC}) manager - プロジェクトマネージャー" 
    echo "  ${GREEN}3${NC}) dev1    - UI/UX・フロントエンド"
    echo "  ${GREEN}4${NC}) dev2    - バックエンド・データ分析"
    echo "  ${GREEN}5${NC}) dev3    - 品質管理・テスト"
    echo "  ${RED}q${NC}) 終了"
    echo ""
    read -p "選択 [1-5/q]: " choice
    
    case $choice in
        1) AGENT="ceo" ;;
        2) AGENT="manager" ;;
        3) AGENT="dev1" ;;
        4) AGENT="dev2" ;;
        5) AGENT="dev3" ;;
        q|Q) echo "終了します"; exit 0 ;;
        *) echo -e "${RED}無効な選択です${NC}"; show_interactive_menu ;;
    esac
    
    echo ""
    echo -e "${YELLOW}選択されたエージェント: ${CYAN}$AGENT${NC}"
    echo ""
    read -p "メッセージを入力してください: " MESSAGE
    
    if [ -z "$MESSAGE" ]; then
        echo -e "${RED}メッセージが空です${NC}"
        show_interactive_menu
    fi
}

# 引数チェック
show_help() {
    echo -e "${CYAN}Enhanced Message Sending System v${VERSION}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "使用方法: $0 [エージェント名] \"[メッセージ]\" [オプション]"
    echo ""
    echo "📋 簡略化コマンド:"
    echo "  $0 -i              インタラクティブメニュー"
    echo "  $0 -c \"message\"     ceoに送信"
    echo "  $0 -m \"message\"     managerに送信"
    echo "  $0 -d1 \"message\"    dev1に送信"
    echo "  $0 -d2 \"message\"    dev2に送信"
    echo "  $0 -d3 \"message\"    dev3に送信"
    echo ""
    echo "エージェント:"
    echo "  ceo     - 最高経営責任者"
    echo "  manager - プロジェクトマネージャー"
    echo "  dev1    - 実行エージェント1 (UI/UX・フロントエンド)"
    echo "  dev2    - 実行エージェント2 (バックエンド・データ分析)"
    echo "  dev3    - 実行エージェント3 (品質管理・テスト)"
    echo ""
    echo "オプション:"
    echo "  --auto-execute    自動でEnterキーを送信 (デフォルト)"
    echo "  --manual         手動でEnterキーを押すモード"
    echo "  --test-mode      テストモード（実際に送信しない）"
    echo "  --verbose        詳細ログ出力"
    echo "  --help           このヘルプを表示"
    echo "  -i, --interactive インタラクティブメニュー"
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# 引数解析
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --manual)
                AUTO_EXECUTE=false
                shift
                ;;
            --auto-execute)
                AUTO_EXECUTE=true
                shift
                ;;
            --test-mode)
                TEST_MODE=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            --list)
                show_help
                exit 0
                ;;
            *)
                if [ -z "$AGENT" ]; then
                    AGENT=$1
                elif [ -z "$MESSAGE" ]; then
                    MESSAGE=$1
                fi
                shift
                ;;
        esac
    done
}

# 引数をパース
parse_args "$@"

# 必要な引数チェック
if [ -z "$AGENT" ] || [ -z "$MESSAGE" ]; then
    echo -e "${RED}❌ エラー: エージェント名とメッセージが必要です${NC}"
    show_help
    exit 1
fi

# ログディレクトリ作成と初期化
mkdir -p logs

# ログローテーション実行
rotate_logs

# システムパフォーマンス監視開始
monitor_system_performance

# タイムスタンプとセッションID
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
SESSION_ID=$(date +%s)_$$

# 高度なメトリクス記録システム
log_metrics() {
    local status=$1
    local duration=$2
    local additional_info="${3:-}"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local iso_timestamp=$(date -Iseconds)
    
    # JSON式メトリクスログ
    local metrics_json="{
        \"timestamp\": \"$iso_timestamp\",
        \"session_id\": \"$SESSION_ID\",
        \"agent\": \"$AGENT\",
        \"status\": \"$status\",
        \"duration_ms\": $duration,
        \"auto_execute\": $AUTO_EXECUTE,
        \"test_mode\": $TEST_MODE,
        \"message_length\": ${#MESSAGE},
        \"system_info\": {
            \"pid\": $$,
            \"ppid\": $PPID,
            \"user\": \"$USER\"
        }
        $([ -n "$additional_info" ] && echo ",\"additional_info\": \"$additional_info\"")
    }"
    
    echo "$metrics_json" >> "$METRICS_FILE"
    
    # 簡易フォーマットでも記録
    echo "[$timestamp] SESSION:$SESSION_ID AGENT:$AGENT STATUS:$status DURATION:${duration}ms AUTO:$AUTO_EXECUTE" >> "${METRICS_FILE}.simple"
}

# ログローテーション機能
rotate_logs() {
    local max_size_mb=10
    local max_files=5
    
    for log_file in "$LOG_FILE" "$ERROR_LOG" "$METRICS_FILE" "$PERFORMANCE_LOG"; do
        if [ -f "$log_file" ]; then
            local file_size_mb=$(du -m "$log_file" | cut -f1)
            
            if [ "$file_size_mb" -gt "$max_size_mb" ]; then
                verbose_log "ログファイルローテーション: $log_file (${file_size_mb}MB)"
                
                # 古いファイルをシフト
                for i in $(seq $((max_files-1)) -1 1); do
                    if [ -f "${log_file}.$i" ]; then
                        mv "${log_file}.$i" "${log_file}.$((i+1))"
                    fi
                done
                
                # 現在のファイルをリネーム
                mv "$log_file" "${log_file}.1"
                
                # 古いファイルを削除
                [ -f "${log_file}.$max_files" ] && rm -f "${log_file}.$max_files"
            fi
        fi
    done
}

# ログ集約・分析機能
analyze_logs() {
    local analysis_file="logs/log_analysis_$(date +%Y%m%d).txt"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    {
        echo "=== ログ分析レポート ($timestamp) ==="
        echo ""
        
        # 成功率統計
        if [ -f "$METRICS_FILE" ]; then
            local total_attempts=$(grep -c "STATUS:" "$METRICS_FILE" 2>/dev/null || echo "0")
            local successful_attempts=$(grep -c "STATUS:SUCCESS" "$METRICS_FILE" 2>/dev/null || echo "0")
            local success_rate=0
            
            if [ "$total_attempts" -gt 0 ]; then
                success_rate=$(echo "scale=2; $successful_attempts * 100 / $total_attempts" | bc -l 2>/dev/null || echo "0")
            fi
            
            echo "成功率: ${success_rate}% ($successful_attempts/$total_attempts)"
        fi
        
        # エラー統計
        if [ -f "$ERROR_LOG" ]; then
            echo ""
            echo "=== エラー統計 ==="
            grep "ERROR_TYPE:" "$ERROR_LOG" 2>/dev/null | awk -F'ERROR_TYPE:' '{print $2}' | awk '{print $1}' | sort | uniq -c | sort -nr
        fi
        
        # パフォーマンス統計
        if [ -f "$PERFORMANCE_LOG" ]; then
            echo ""
            echo "=== パフォーマンスサマリ ==="
            local avg_cpu=$(awk -F'CPU:' '{if(NF>1) print $2}' "$PERFORMANCE_LOG" | awk -F'%' '{sum+=$1; n++} END {if(n>0) printf "%.1f", sum/n}')
            local avg_mem=$(awk -F'MEM:' '{if(NF>1) print $2}' "$PERFORMANCE_LOG" | awk -F'%' '{sum+=$1; n++} END {if(n>0) printf "%.1f", sum/n}')
            echo "CPU平均使用率: ${avg_cpu}%"
            echo "メモリ平均使用率: ${avg_mem}%"
        fi
    } > "$analysis_file"
    
    verbose_log "ログ分析レポート作成: $analysis_file"
}

# 構造化ログ出力
structured_log() {
    local level="$1"
    local component="$2"
    local message="$3"
    local context="${4:-}"
    local timestamp=$(date -Iseconds)
    
    local log_entry="{\"timestamp\": \"$timestamp\", \"level\": \"$level\", \"component\": \"$component\", \"message\": \"$message\", \"session_id\": \"$SESSION_ID\"$([ -n "$context" ] && echo ", \"context\": \"$context\"")}"
    
    echo "$log_entry" >> "logs/structured_${level}.log"
    
    # コンソール出力 (レベルに応じて色分け)
    case $level in
        "ERROR")
            echo -e "${RED}[$level]${NC} $component: $message" >&2
            ;;
        "WARN")
            echo -e "${YELLOW}[$level]${NC} $component: $message"
            ;;
        "INFO")
            echo -e "${BLUE}[$level]${NC} $component: $message"
            ;;
        "DEBUG")
            if [ "$VERBOSE" = true ]; then
                echo -e "${CYAN}[$level]${NC} $component: $message"
            fi
            ;;
    esac
}

# 詳細ログ出力
verbose_log() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}[VERBOSE]${NC} $1"
    fi
}

# エラーハンドリング関数
handle_error() {
    local error_code=$1
    local error_message=$2
    local context=$3
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # エラーログに詳細記録
    echo "[$timestamp] ERROR_CODE:$error_code ERROR_TYPE:${ERROR_CODES[$error_code]} MESSAGE:$error_message CONTEXT:$context SESSION:$SESSION_ID" >> "$ERROR_LOG"
    
    # コンソール出力
    echo -e "${RED}❌ エラー発生 [${ERROR_CODES[$error_code]}]${NC}"
    echo -e "   🔍 詳細: $error_message"
    echo -e "   📍 コンテキスト: $context"
    echo -e "   🕐 発生時刻: $timestamp"
    
    return $error_code
}

# リトライ機能付きコマンド実行
execute_with_retry() {
    local command="$1"
    local max_attempts=$MAX_RETRY_ATTEMPTS
    local delay=$RETRY_DELAY
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        verbose_log "実行試行 $attempt/$max_attempts: $command"
        
        if eval "$command"; then
            verbose_log "コマンド実行成功 (試行回数: $attempt)"
            return 0
        else
            local exit_code=$?
            verbose_log "コマンド実行失敗 (試行回数: $attempt, 終了コード: $exit_code)"
            
            if [ $attempt -lt $max_attempts ]; then
                verbose_log "${delay}秒待機後、再試行します..."
                sleep $delay
                delay=$((delay * 2))  # 指数バックオフ
            fi
        fi
        
        attempt=$((attempt + 1))
    done
    
    handle_error 3 "コマンド実行が$max_attempts回失敗しました" "$command"
    return 3
}

# システムリソース・パフォーマンス監視
monitor_system_performance() {
    if [ "$MONITORING_ENABLED" = true ]; then
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
        local memory_usage=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
        local disk_usage=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
        
        echo "[$timestamp] SESSION:$SESSION_ID CPU:${cpu_usage}% MEM:${memory_usage}% DISK:${disk_usage}%" >> "$PERFORMANCE_LOG"
        
        # リソース不足警告
        if (( $(echo "$memory_usage > 90" | bc -l) )); then
            handle_error 7 "メモリ使用率が危険レベル (${memory_usage}%)" "システムリソース監視"
        fi
    fi
}

# タイムアウト付きコマンド実行
execute_with_timeout() {
    local command="$1"
    local timeout=$TIMEOUT_SECONDS
    
    timeout $timeout bash -c "$command"
    local exit_code=$?
    
    if [ $exit_code -eq 124 ]; then
        handle_error 4 "コマンドがタイムアウトしました (${timeout}秒)" "$command"
        return 4
    fi
    
    return $exit_code
}

echo -e "${CYAN}🚀 Enhanced Message System v${VERSION}${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# エージェント名の検証
case $AGENT in
    ceo|manager|dev1|dev2|dev3)
        verbose_log "エージェント '$AGENT' を検証しました"
        ;;
    *)
        echo -e "${RED}❌ エラー: 不明なエージェント名 '$AGENT'${NC}"
        echo -e "${YELLOW}利用可能なエージェント: ceo, manager, dev1, dev2, dev3${NC}"
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

verbose_log "tmuxセッション: $SESSION, ペイン: $PANE"

# セッション存在確認とパフォーマンス監視
structured_log "INFO" "SESSION_CHECK" "セッション確認開始: $SESSION"

if ! execute_with_timeout "tmux has-session -t $SESSION 2>/dev/null"; then
    handle_error 2 "tmuxセッション '$SESSION' が見つかりません" "セッション存在確認"
    echo -e "${YELLOW}💡 先にシステムを起動してください: ./start-system.sh${NC}"
    log_metrics "SESSION_NOT_FOUND" 0 "session=$SESSION"
    exit 2
fi

structured_log "INFO" "SESSION_CHECK" "セッション確認成功: $SESSION"

# テストモードの場合
if [ "$TEST_MODE" = true ]; then
    echo -e "${YELLOW}🧪 テストモード: 実際には送信しません${NC}"
    echo -e "${GREEN}✅ 送信シミュレーション完了${NC}"
    echo -e "   📨 対象: $AGENT"
    echo -e "   💬 内容: $MESSAGE"
    echo -e "   ⚡ 自動実行: $AUTO_EXECUTE"
    log_metrics "TEST_SUCCESS" 0
    exit 0
fi

# 送信開始時刻
START_TIME=$(date +%s.%N)

echo -e "${YELLOW}📨 メッセージ送信中...${NC}"
verbose_log "開始時刻: $START_TIME"

# Phase 1: 基本自動化機能 - Enterキー自動送信 (パフォーマンス監視付き)
SEND_SUCCESS=false

if [ "$AUTO_EXECUTE" = true ]; then
    # 自動実行モード
    structured_log "INFO" "MESSAGE_SEND" "自動実行モードでメッセージ送信開始" "agent=$AGENT, auto=true"
    
    if [ "$RETRY_ENABLED" = true ]; then
        if execute_with_retry "tmux send-keys -t $SESSION:$PANE \"$MESSAGE\" Enter 2>/dev/null"; then
            SEND_SUCCESS=true
            structured_log "INFO" "MESSAGE_SEND" "tmux send-keys実行成功"
        else
            structured_log "ERROR" "MESSAGE_SEND" "tmux send-keys実行失敗 (リトライ後)"
        fi
    else
        if execute_with_timeout "tmux send-keys -t $SESSION:$PANE \"$MESSAGE\" Enter 2>/dev/null"; then
            SEND_SUCCESS=true
            structured_log "INFO" "MESSAGE_SEND" "tmux send-keys実行成功"
        else
            structured_log "ERROR" "MESSAGE_SEND" "tmux send-keys実行失敗"
        fi
    fi
else
    # 手動実行モード
    structured_log "INFO" "MESSAGE_SEND" "手動実行モードでメッセージ送信開始" "agent=$AGENT, auto=false"
    
    if [ "$RETRY_ENABLED" = true ]; then
        if execute_with_retry "tmux send-keys -t $SESSION:$PANE \"$MESSAGE\" 2>/dev/null"; then
            SEND_SUCCESS=true
            structured_log "INFO" "MESSAGE_SEND" "tmux send-keys実行成功 (手動Enter待ち)"
        else
            structured_log "ERROR" "MESSAGE_SEND" "tmux send-keys実行失敗 (リトライ後)"
        fi
    else
        if execute_with_timeout "tmux send-keys -t $SESSION:$PANE \"$MESSAGE\" 2>/dev/null"; then
            SEND_SUCCESS=true
            structured_log "INFO" "MESSAGE_SEND" "tmux send-keys実行成功 (手動Enter待ち)"
        else
            structured_log "ERROR" "MESSAGE_SEND" "tmux send-keys実行失敗"
        fi
    fi
fi

# パフォーマンス監視更新
monitor_system_performance

# 終了時刻と処理時間計算
END_TIME=$(date +%s.%N)
DURATION=$(echo "($END_TIME - $START_TIME) * 1000" | bc 2>/dev/null | cut -d. -f1)

# 結果の表示と高度ログ記録
if [ "$SEND_SUCCESS" = true ]; then
    echo -e "${GREEN}✅ メッセージ送信成功！${NC}"
    echo -e "   🎯 対象: ${CYAN}$AGENT${NC}"
    echo -e "   💬 内容: $MESSAGE"
    echo -e "   ⚡ 自動実行: $(if [ "$AUTO_EXECUTE" = true ]; then echo "${GREEN}ON${NC}"; else echo "${YELLOW}OFF${NC}"; fi)"
    echo -e "   ⏱️  処理時間: ${DURATION}ms"
    echo -e "   📊 パフォーマンス: メモリ使用率監視中"
    
    # 高度ログ記録
    structured_log "INFO" "MESSAGE_SUCCESS" "メッセージ送信成功" "agent=$AGENT, duration=${DURATION}ms, auto=$AUTO_EXECUTE"
    echo "[$TIMESTAMP] SUCCESS → $AGENT: $MESSAGE (auto:$AUTO_EXECUTE, duration:${DURATION}ms)" >> "$LOG_FILE"
    log_metrics "SUCCESS" "$DURATION" "message_length=${#MESSAGE}"
    
    if [ "$AUTO_EXECUTE" = false ]; then
        echo -e "${YELLOW}💡 手動モード: 対象ペインでEnterキーを押してください${NC}"
    fi
    
    # ログ分析実行 (結果が成功した場合のみ)
    analyze_logs
else
    echo -e "${RED}❌ メッセージ送信失敗${NC}"
    echo -e "   🎯 対象: ${CYAN}$AGENT${NC}"
    echo -e "   💬 内容: $MESSAGE"
    echo -e "   ⏱️  処理時間: ${DURATION}ms"
    
    # エラーログ記録
    structured_log "ERROR" "MESSAGE_FAILURE" "メッセージ送信失敗" "agent=$AGENT, duration=${DURATION}ms, auto=$AUTO_EXECUTE"
    echo "[$TIMESTAMP] ERROR → $AGENT: $MESSAGE (auto:$AUTO_EXECUTE)" >> "$ERROR_LOG"
    log_metrics "ERROR" "$DURATION" "message_length=${#MESSAGE}"
    
    exit 1
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 最終パフォーマンス監視更新
monitor_system_performance

# Phase 1完了 (高度バックエンド機能付き)
structured_log "INFO" "SYSTEM" "Phase 1基本自動化処理完了 (バックエンド機能強化版)" "session=$SESSION_ID, duration=${DURATION}ms"
verbose_log "Phase 1基本自動化処理完了 - バックエンド機能強化版"
exit 0