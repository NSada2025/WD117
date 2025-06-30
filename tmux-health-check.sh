#!/bin/bash

# tmux健康診断・状態確認ツール
# セッション異常終了の原因究明用

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ログディレクトリ
LOG_DIR="./logs/tmux-health"
mkdir -p "$LOG_DIR"

# タイムスタンプ
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
HEALTH_LOG="$LOG_DIR/health_check_${TIMESTAMP}.log"

# ヘッダー表示
function display_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                 tmux 健康診断ツール v1.0                      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo -e "実行時刻: $(date)"
    echo -e "────────────────────────────────────────────────────────────────\n"
}

# tmuxサーバー情報取得
function check_tmux_server() {
    echo -e "${CYAN}[1] tmux サーバー情報${NC}" | tee -a "$HEALTH_LOG"
    echo "=============================" | tee -a "$HEALTH_LOG"
    
    if tmux info &>/dev/null; then
        echo -e "${GREEN}✓ tmuxサーバーは実行中${NC}" | tee -a "$HEALTH_LOG"
        
        # サーバー詳細情報
        echo -e "\n${YELLOW}サーバー詳細:${NC}" | tee -a "$HEALTH_LOG"
        tmux server-info 2>&1 | head -20 | tee -a "$HEALTH_LOG"
        
        # プロセス情報
        echo -e "\n${YELLOW}tmuxプロセス:${NC}" | tee -a "$HEALTH_LOG"
        ps aux | grep -E "[t]mux" | tee -a "$HEALTH_LOG"
        
        # ソケット情報
        echo -e "\n${YELLOW}tmuxソケット:${NC}" | tee -a "$HEALTH_LOG"
        ls -la /tmp/tmux-*/ 2>/dev/null | tee -a "$HEALTH_LOG"
    else
        echo -e "${RED}✗ tmuxサーバーが起動していません${NC}" | tee -a "$HEALTH_LOG"
    fi
    echo ""
}

# セッション一覧と詳細
function check_sessions() {
    echo -e "${CYAN}[2] アクティブセッション${NC}" | tee -a "$HEALTH_LOG"
    echo "=============================" | tee -a "$HEALTH_LOG"
    
    if tmux list-sessions &>/dev/null; then
        # セッション一覧（詳細フォーマット）
        echo -e "${YELLOW}セッション一覧:${NC}" | tee -a "$HEALTH_LOG"
        tmux list-sessions -F "Session: #{session_name} | Created: #{session_created} | Attached: #{session_attached} | Windows: #{session_windows}" | tee -a "$HEALTH_LOG"
        
        # 各セッションの詳細
        echo -e "\n${YELLOW}セッション詳細:${NC}" | tee -a "$HEALTH_LOG"
        for session in $(tmux list-sessions -F "#{session_name}"); do
            echo -e "\n${GREEN}>>> セッション: $session${NC}" | tee -a "$HEALTH_LOG"
            tmux list-windows -t "$session" -F "  Window: #{window_index}:#{window_name} | Panes: #{window_panes} | Active: #{window_active}" | tee -a "$HEALTH_LOG"
            
            # ペイン情報
            tmux list-panes -t "$session" -F "    Pane: #{pane_index} | PID: #{pane_pid} | Command: #{pane_current_command} | Dead: #{pane_dead}" | tee -a "$HEALTH_LOG"
        done
    else
        echo -e "${RED}アクティブなセッションがありません${NC}" | tee -a "$HEALTH_LOG"
    fi
    echo ""
}

# システムリソース確認
function check_system_resources() {
    echo -e "${CYAN}[3] システムリソース${NC}" | tee -a "$HEALTH_LOG"
    echo "=============================" | tee -a "$HEALTH_LOG"
    
    # メモリ使用状況
    echo -e "${YELLOW}メモリ使用状況:${NC}" | tee -a "$HEALTH_LOG"
    free -h | tee -a "$HEALTH_LOG"
    
    # tmuxプロセスのメモリ使用量
    echo -e "\n${YELLOW}tmuxプロセスメモリ:${NC}" | tee -a "$HEALTH_LOG"
    ps aux | grep -E "[t]mux" | awk '{print $2, $3, $4, $11}' | column -t | tee -a "$HEALTH_LOG"
    
    # ファイルディスクリプタ
    echo -e "\n${YELLOW}オープンファイル数:${NC}" | tee -a "$HEALTH_LOG"
    for pid in $(pgrep tmux); do
        echo "PID $pid: $(ls /proc/$pid/fd 2>/dev/null | wc -l) files" | tee -a "$HEALTH_LOG"
    done
    echo ""
}

# エラーログ確認
function check_error_logs() {
    echo -e "${CYAN}[4] エラーログ確認${NC}" | tee -a "$HEALTH_LOG"
    echo "=============================" | tee -a "$HEALTH_LOG"
    
    # システムログから tmux 関連エラー
    echo -e "${YELLOW}最近のシステムログ (tmux関連):${NC}" | tee -a "$HEALTH_LOG"
    if [ -f /var/log/syslog ]; then
        grep -i tmux /var/log/syslog | tail -20 | tee -a "$HEALTH_LOG"
    elif journalctl --version &>/dev/null; then
        journalctl -u tmux -n 20 --no-pager 2>/dev/null | tee -a "$HEALTH_LOG"
    fi
    
    # dmesg確認
    echo -e "\n${YELLOW}カーネルメッセージ (tmux関連):${NC}" | tee -a "$HEALTH_LOG"
    dmesg | grep -i tmux | tail -10 | tee -a "$HEALTH_LOG"
    echo ""
}

# 異常パターン検出
function detect_anomalies() {
    echo -e "${CYAN}[5] 異常パターン検出${NC}" | tee -a "$HEALTH_LOG"
    echo "=============================" | tee -a "$HEALTH_LOG"
    
    local warnings=0
    
    # デッドペイン確認
    if tmux list-panes -a -F "#{pane_dead}" 2>/dev/null | grep -q "1"; then
        echo -e "${RED}⚠ デッドペインが検出されました${NC}" | tee -a "$HEALTH_LOG"
        tmux list-panes -a -F "#{session_name}:#{window_index}.#{pane_index} dead=#{pane_dead}" | grep "dead=1" | tee -a "$HEALTH_LOG"
        ((warnings++))
    fi
    
    # ゾンビプロセス確認
    local zombies=$(ps aux | grep -c "[t]mux.*<defunct>")
    if [ "$zombies" -gt 0 ]; then
        echo -e "${RED}⚠ ゾンビプロセスが検出されました: $zombies 個${NC}" | tee -a "$HEALTH_LOG"
        ((warnings++))
    fi
    
    # 大量のセッション確認
    local session_count=$(tmux list-sessions 2>/dev/null | wc -l)
    if [ "$session_count" -gt 10 ]; then
        echo -e "${YELLOW}⚠ 多数のセッションが実行中: $session_count 個${NC}" | tee -a "$HEALTH_LOG"
        ((warnings++))
    fi
    
    # ソケットファイルの異常
    local socket_count=$(find /tmp -name "tmux-*" -type s 2>/dev/null | wc -l)
    local actual_sessions=$(tmux list-sessions 2>/dev/null | wc -l)
    if [ "$socket_count" -gt "$actual_sessions" ]; then
        echo -e "${YELLOW}⚠ 孤立したソケットファイルの可能性${NC}" | tee -a "$HEALTH_LOG"
        ((warnings++))
    fi
    
    if [ "$warnings" -eq 0 ]; then
        echo -e "${GREEN}✓ 異常パターンは検出されませんでした${NC}" | tee -a "$HEALTH_LOG"
    else
        echo -e "${RED}検出された警告: $warnings 件${NC}" | tee -a "$HEALTH_LOG"
    fi
    echo ""
}

# 推奨事項
function show_recommendations() {
    echo -e "${CYAN}[6] 推奨事項${NC}" | tee -a "$HEALTH_LOG"
    echo "=============================" | tee -a "$HEALTH_LOG"
    
    # セッション数に基づく推奨
    local session_count=$(tmux list-sessions 2>/dev/null | wc -l)
    if [ "$session_count" -gt 5 ]; then
        echo -e "${YELLOW}• 不要なセッションを終了することを推奨します${NC}" | tee -a "$HEALTH_LOG"
        echo "  実行: tmux kill-session -t <session-name>" | tee -a "$HEALTH_LOG"
    fi
    
    # メモリ使用量に基づく推奨
    local mem_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    if [ "$mem_usage" -gt 80 ]; then
        echo -e "${YELLOW}• メモリ使用率が高い状態です ($mem_usage%)${NC}" | tee -a "$HEALTH_LOG"
        echo "  大きなバッファを持つセッションの確認を推奨" | tee -a "$HEALTH_LOG"
    fi
    
    echo -e "\n${GREEN}定期的な健康診断の実行を推奨します${NC}" | tee -a "$HEALTH_LOG"
    echo ""
}

# レポート生成
function generate_report() {
    local report_file="$LOG_DIR/health_report_${TIMESTAMP}.json"
    
    cat > "$report_file" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "server_status": $(tmux info &>/dev/null && echo "\"running\"" || echo "\"stopped\""),
  "session_count": $(tmux list-sessions 2>/dev/null | wc -l),
  "total_panes": $(tmux list-panes -a 2>/dev/null | wc -l),
  "dead_panes": $(tmux list-panes -a -F "#{pane_dead}" 2>/dev/null | grep -c "1"),
  "memory_usage_percent": $(free | grep Mem | awk '{print int($3/$2 * 100)}'),
  "log_file": "$HEALTH_LOG"
}
EOF
    
    echo -e "${GREEN}レポート生成完了: $report_file${NC}"
}

# メイン処理
display_header | tee "$HEALTH_LOG"

check_tmux_server
check_sessions
check_system_resources
check_error_logs
detect_anomalies
show_recommendations

generate_report

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}健康診断完了${NC}"
echo -e "詳細ログ: ${CYAN}$HEALTH_LOG${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"