#!/bin/bash

# tmux 3回連続終了パターン再現テストツール
# 異常終了パターンを意図的に再現して原因を特定

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# テスト設定
TEST_LOG_DIR="./logs/tmux-crash-tests"
TEST_SESSION_PREFIX="crash_test"
REPRODUCTION_SCENARIOS=(
    "memory_exhaustion"
    "rapid_pane_creation"
    "file_descriptor_leak"
    "config_reload_loop"
    "large_buffer_overflow"
    "nested_sessions"
    "signal_storm"
    "race_condition"
)

mkdir -p "$TEST_LOG_DIR"

# ヘッダー表示
function display_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║          tmux クラッシュ再現テストツール v1.0                 ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo -e "${RED}警告: このツールは意図的にtmuxをクラッシュさせます${NC}"
    echo -e "${YELLOW}テスト環境でのみ使用してください${NC}\n"
}

# テストシナリオ1: メモリ枯渇
function test_memory_exhaustion() {
    local session_name="${TEST_SESSION_PREFIX}_memory"
    echo -e "${CYAN}[テスト1] メモリ枯渇シナリオ${NC}"
    
    tmux new-session -d -s "$session_name" 2>/dev/null
    
    # 大量のバッファを作成
    for i in {1..3}; do
        echo -e "  試行 $i/3: 大量データ生成..."
        tmux send-keys -t "$session_name" "seq 1 10000000 | tee /tmp/tmux_test_$i.txt" Enter
        sleep 2
        
        # セッション存在確認
        if ! tmux has-session -t "$session_name" 2>/dev/null; then
            echo -e "${RED}  → クラッシュ検出！ (試行 $i)${NC}"
            return 0
        fi
    done
    
    tmux kill-session -t "$session_name" 2>/dev/null
    return 1
}

# テストシナリオ2: 急速なペイン作成
function test_rapid_pane_creation() {
    local session_name="${TEST_SESSION_PREFIX}_panes"
    echo -e "${CYAN}[テスト2] 急速ペイン作成シナリオ${NC}"
    
    tmux new-session -d -s "$session_name" 2>/dev/null
    
    for attempt in {1..3}; do
        echo -e "  試行 $attempt/3: 高速ペイン作成..."
        
        # 短時間で大量のペインを作成
        for i in {1..50}; do
            tmux split-window -t "$session_name" -h 2>/dev/null || break
            tmux split-window -t "$session_name" -v 2>/dev/null || break
        done
        
        sleep 1
        
        if ! tmux has-session -t "$session_name" 2>/dev/null; then
            echo -e "${RED}  → クラッシュ検出！ (試行 $attempt)${NC}"
            return 0
        fi
    done
    
    tmux kill-session -t "$session_name" 2>/dev/null
    return 1
}

# テストシナリオ3: ファイルディスクリプタリーク
function test_file_descriptor_leak() {
    local session_name="${TEST_SESSION_PREFIX}_fd"
    echo -e "${CYAN}[テスト3] ファイルディスクリプタリークシナリオ${NC}"
    
    tmux new-session -d -s "$session_name" 2>/dev/null
    
    for attempt in {1..3}; do
        echo -e "  試行 $attempt/3: 大量ファイルオープン..."
        
        # 大量のファイルを開く
        tmux send-keys -t "$session_name" '
for i in {1..1000}; do
    exec {fd}<>/tmp/test_fd_$i.txt
done
' Enter
        
        sleep 2
        
        if ! tmux has-session -t "$session_name" 2>/dev/null; then
            echo -e "${RED}  → クラッシュ検出！ (試行 $attempt)${NC}"
            return 0
        fi
    done
    
    tmux kill-session -t "$session_name" 2>/dev/null
    return 1
}

# テストシナリオ4: 設定リロードループ
function test_config_reload_loop() {
    local session_name="${TEST_SESSION_PREFIX}_config"
    echo -e "${CYAN}[テスト4] 設定リロードループシナリオ${NC}"
    
    # 一時的な設定ファイル作成
    local temp_config="/tmp/tmux_test_config.conf"
    echo "set -g status-interval 1" > "$temp_config"
    
    tmux -f "$temp_config" new-session -d -s "$session_name" 2>/dev/null
    
    for attempt in {1..3}; do
        echo -e "  試行 $attempt/3: 高速設定リロード..."
        
        # 高速で設定をリロード
        for i in {1..20}; do
            echo "set -g status-bg colour$((i % 256))" >> "$temp_config"
            tmux source-file "$temp_config" 2>/dev/null
        done
        
        sleep 1
        
        if ! tmux has-session -t "$session_name" 2>/dev/null; then
            echo -e "${RED}  → クラッシュ検出！ (試行 $attempt)${NC}"
            rm -f "$temp_config"
            return 0
        fi
    done
    
    tmux kill-session -t "$session_name" 2>/dev/null
    rm -f "$temp_config"
    return 1
}

# テストシナリオ5: バッファオーバーフロー
function test_large_buffer_overflow() {
    local session_name="${TEST_SESSION_PREFIX}_buffer"
    echo -e "${CYAN}[テスト5] 大量バッファシナリオ${NC}"
    
    tmux new-session -d -s "$session_name" 2>/dev/null
    
    for attempt in {1..3}; do
        echo -e "  試行 $attempt/3: 巨大出力生成..."
        
        # 巨大な出力を生成
        tmux send-keys -t "$session_name" "yes '$(printf '=%.0s' {1..1000})' | head -100000" Enter
        
        sleep 3
        
        if ! tmux has-session -t "$session_name" 2>/dev/null; then
            echo -e "${RED}  → クラッシュ検出！ (試行 $attempt)${NC}"
            return 0
        fi
    done
    
    tmux kill-session -t "$session_name" 2>/dev/null
    return 1
}

# テストシナリオ6: ネストセッション
function test_nested_sessions() {
    local session_name="${TEST_SESSION_PREFIX}_nested"
    echo -e "${CYAN}[テスト6] ネストセッションシナリオ${NC}"
    
    tmux new-session -d -s "$session_name" 2>/dev/null
    
    for attempt in {1..3}; do
        echo -e "  試行 $attempt/3: ネストセッション作成..."
        
        # ネストされたtmuxセッションを作成
        for i in {1..5}; do
            tmux send-keys -t "$session_name" "tmux new-session -d -s nested_$i" Enter
            sleep 0.5
        done
        
        if ! tmux has-session -t "$session_name" 2>/dev/null; then
            echo -e "${RED}  → クラッシュ検出！ (試行 $attempt)${NC}"
            return 0
        fi
    done
    
    tmux kill-session -t "$session_name" 2>/dev/null
    return 1
}

# テストシナリオ7: シグナルストーム
function test_signal_storm() {
    local session_name="${TEST_SESSION_PREFIX}_signal"
    echo -e "${CYAN}[テスト7] シグナルストームシナリオ${NC}"
    
    tmux new-session -d -s "$session_name" 2>/dev/null
    local tmux_pid=$(tmux list-sessions -F "#{session_name} #{session_pid}" | grep "^$session_name" | awk '{print $2}')
    
    for attempt in {1..3}; do
        echo -e "  試行 $attempt/3: 大量シグナル送信..."
        
        # 様々なシグナルを高速送信
        for sig in HUP INT TERM USR1 USR2; do
            for i in {1..10}; do
                kill -$sig $tmux_pid 2>/dev/null || break
                sleep 0.01
            done
        done
        
        sleep 1
        
        if ! tmux has-session -t "$session_name" 2>/dev/null; then
            echo -e "${RED}  → クラッシュ検出！ (試行 $attempt)${NC}"
            return 0
        fi
    done
    
    tmux kill-session -t "$session_name" 2>/dev/null
    return 1
}

# テストシナリオ8: レース条件
function test_race_condition() {
    local session_name="${TEST_SESSION_PREFIX}_race"
    echo -e "${CYAN}[テスト8] レース条件シナリオ${NC}"
    
    tmux new-session -d -s "$session_name" 2>/dev/null
    
    for attempt in {1..3}; do
        echo -e "  試行 $attempt/3: 同時操作実行..."
        
        # 複数の操作を同時に実行
        (
            for i in {1..10}; do
                tmux split-window -t "$session_name" 2>/dev/null
                tmux select-pane -t "$session_name" -R 2>/dev/null
            done
        ) &
        
        (
            for i in {1..10}; do
                tmux resize-pane -t "$session_name" -x 80 -y 24 2>/dev/null
                tmux select-layout -t "$session_name" tiled 2>/dev/null
            done
        ) &
        
        wait
        
        if ! tmux has-session -t "$session_name" 2>/dev/null; then
            echo -e "${RED}  → クラッシュ検出！ (試行 $attempt)${NC}"
            return 0
        fi
    done
    
    tmux kill-session -t "$session_name" 2>/dev/null
    return 1
}

# テスト結果レポート生成
function generate_test_report() {
    local report_file="$TEST_LOG_DIR/crash_test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
════════════════════════════════════════════════════════════
              tmuxクラッシュ再現テスト結果
════════════════════════════════════════════════════════════

実行日時: $(date)
tmuxバージョン: $(tmux -V)
システム: $(uname -a)

テスト結果:
EOF
    
    for scenario in "${!TEST_RESULTS[@]}"; do
        local result="${TEST_RESULTS[$scenario]}"
        if [ "$result" = "CRASH" ]; then
            echo "  ✗ $scenario: ${RED}クラッシュ再現成功${NC}" >> "$report_file"
        else
            echo "  ✓ $scenario: クラッシュなし" >> "$report_file"
        fi
    done
    
    echo -e "\n${GREEN}テストレポート生成: $report_file${NC}"
}

# メイン処理
display_header

echo "実行するテストシナリオを選択してください:"
echo "1) すべてのテストを実行"
echo "2) 個別テストを選択"
echo "3) クイックテスト（最も可能性の高い3つ）"
read -p "選択 [1-3]: " choice

declare -A TEST_RESULTS

case $choice in
    1)
        echo -e "\n${YELLOW}すべてのテストを実行します...${NC}\n"
        for test_func in test_memory_exhaustion test_rapid_pane_creation test_file_descriptor_leak test_config_reload_loop test_large_buffer_overflow test_nested_sessions test_signal_storm test_race_condition; do
            $test_func && TEST_RESULTS[$test_func]="CRASH" || TEST_RESULTS[$test_func]="OK"
            echo ""
        done
        ;;
    2)
        echo -e "\nテストを選択してください:"
        select test_name in "${REPRODUCTION_SCENARIOS[@]}" "終了"; do
            [ "$test_name" = "終了" ] && break
            
            test_func="test_${test_name}"
            $test_func && TEST_RESULTS[$test_func]="CRASH" || TEST_RESULTS[$test_func]="OK"
            echo ""
        done
        ;;
    3)
        echo -e "\n${YELLOW}クイックテストを実行します...${NC}\n"
        for test_func in test_memory_exhaustion test_rapid_pane_creation test_large_buffer_overflow; do
            $test_func && TEST_RESULTS[$test_func]="CRASH" || TEST_RESULTS[$test_func]="OK"
            echo ""
        done
        ;;
    *)
        echo -e "${RED}無効な選択です${NC}"
        exit 1
        ;;
esac

# 結果サマリー
echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                        テスト完了                              ${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

generate_test_report

# クリーンアップ
echo -e "\n${YELLOW}テストセッションをクリーンアップ中...${NC}"
for session in $(tmux list-sessions -F "#{session_name}" | grep "^${TEST_SESSION_PREFIX}"); do
    tmux kill-session -t "$session" 2>/dev/null
done

echo -e "${GREEN}完了${NC}"