#!/bin/bash

# tmux実行リアルタイムモニタリングツール
# .shファイルの呼び出しをリアルタイムで監視・カウント

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# グローバル変数
declare -A FILE_COUNTS
TOTAL_CALLS=0
MONITOR_PID=""
TRACE_DIR="./logs/tmux-trace-monitor"
mkdir -p "$TRACE_DIR"

# タイムスタンプ
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
MONITOR_LOG="$TRACE_DIR/monitor_${TIMESTAMP}.log"
STATS_FILE="$TRACE_DIR/stats_${TIMESTAMP}.json"

# シグナルハンドラー
trap cleanup EXIT INT TERM

function cleanup() {
    echo -e "\n${YELLOW}モニタリング終了...${NC}"
    if [ -n "$MONITOR_PID" ]; then
        kill $MONITOR_PID 2>/dev/null
    fi
    save_statistics
    display_final_report
}

function save_statistics() {
    echo "{" > "$STATS_FILE"
    echo "  \"timestamp\": \"$(date -Iseconds)\"," >> "$STATS_FILE"
    echo "  \"total_calls\": $TOTAL_CALLS," >> "$STATS_FILE"
    echo "  \"unique_files\": ${#FILE_COUNTS[@]}," >> "$STATS_FILE"
    echo "  \"file_counts\": {" >> "$STATS_FILE"
    
    local first=true
    for file in "${!FILE_COUNTS[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "$STATS_FILE"
        fi
        echo -n "    \"$file\": ${FILE_COUNTS[$file]}" >> "$STATS_FILE"
    done
    
    echo -e "\n  }" >> "$STATS_FILE"
    echo "}" >> "$STATS_FILE"
}

function display_header() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║          tmux シェルスクリプト実行モニター v1.0               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo -e "${CYAN}監視開始時刻: $(date)${NC}"
    echo -e "${YELLOW}Ctrl+C で終了${NC}"
    echo -e "────────────────────────────────────────────────────────────────"
}

function display_stats() {
    # カーソル位置を保存
    tput sc
    
    # 統計表示エリアに移動
    tput cup 8 0
    
    echo -e "${GREEN}▶ 総呼び出し回数: ${TOTAL_CALLS}${NC}"
    echo -e "${GREEN}▶ ユニークファイル数: ${#FILE_COUNTS[@]}${NC}"
    echo -e "\n${YELLOW}[呼び出し頻度 TOP 10]${NC}"
    echo -e "────────────────────────────────────────────────────────────────"
    
    # ソートして上位10件表示
    for file in "${!FILE_COUNTS[@]}"; do
        echo "${FILE_COUNTS[$file]} $file"
    done | sort -rn | head -10 | while read count file; do
        printf "%-40s %4d回 " "$file" "$count"
        
        # 簡易バーグラフ
        local bar_length=$((count * 20 / (TOTAL_CALLS + 1)))
        [ $bar_length -gt 20 ] && bar_length=20
        echo -n "["
        for ((i=0; i<bar_length; i++)); do
            echo -n "█"
        done
        for ((i=bar_length; i<20; i++)); do
            echo -n " "
        done
        echo "]"
    done
    
    # カーソル位置を復元
    tput rc
}

function monitor_shell_calls() {
    echo -e "\n${GREEN}モニタリング開始...${NC}\n"
    
    # デバッグトレースを有効にしたラッパースクリプト
    cat > "$TRACE_DIR/monitor_wrapper.sh" << 'EOF'
#!/bin/bash
export BASH_XTRACEFD=3
exec 3> >(while read line; do
    if [[ "$line" =~ \+.*\.sh ]]; then
        # シェルスクリプトファイル名を抽出
        script_name=$(echo "$line" | grep -oE '[^/]+\.sh' | head -1)
        if [ -n "$script_name" ]; then
            echo "SHELL_CALL: $script_name"
        fi
    fi
done)
set -x
eval "$@"
EOF
    
    chmod +x "$TRACE_DIR/monitor_wrapper.sh"
}

function start_realtime_monitor() {
    local cmd="$1"
    
    display_header
    
    # バックグラウンドでコマンドを実行し、出力を監視
    (
        bash "$TRACE_DIR/monitor_wrapper.sh" "$cmd" 2>&1 | while read line; do
            if [[ "$line" =~ ^SHELL_CALL: ]]; then
                local file=$(echo "$line" | cut -d' ' -f2)
                ((FILE_COUNTS[$file]++))
                ((TOTAL_CALLS++))
                
                # ログに記録
                echo "[$(date +%H:%M:%S)] $file" >> "$MONITOR_LOG"
                
                # 画面更新
                display_stats
            fi
        done
    ) &
    
    MONITOR_PID=$!
    
    # プロセスが終了するまで待機
    wait $MONITOR_PID
}

function display_final_report() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                        最終レポート                            ${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    
    echo -e "\n${GREEN}📊 統計サマリー:${NC}"
    echo -e "  • 総呼び出し回数: ${YELLOW}${TOTAL_CALLS}${NC}"
    echo -e "  • ユニークファイル数: ${YELLOW}${#FILE_COUNTS[@]}${NC}"
    echo -e "  • 監視時間: ${YELLOW}$(date -d @$(($(date +%s) - $(date -d "$TIMESTAMP" +%s))) -u +%H:%M:%S)${NC}"
    
    echo -e "\n${GREEN}📈 呼び出し頻度 (全件):${NC}"
    for file in "${!FILE_COUNTS[@]}"; do
        echo "${FILE_COUNTS[$file]} $file"
    done | sort -rn | while read count file; do
        printf "  %-40s %4d回\n" "$file" "$count"
    done
    
    echo -e "\n${GREEN}💾 保存されたファイル:${NC}"
    echo -e "  • ログファイル: ${CYAN}$MONITOR_LOG${NC}"
    echo -e "  • 統計JSON: ${CYAN}$STATS_FILE${NC}"
}

# メイン処理
echo -e "${BLUE}=== tmux実行リアルタイムモニター ===${NC}"
echo -e "\n監視するコマンドを入力してください:"
echo -e "例: ${CYAN}tmux new-session -s test${NC}"
echo -e "例: ${CYAN}./start-system.sh${NC}"
read -p "コマンド: " MONITOR_COMMAND

if [ -z "$MONITOR_COMMAND" ]; then
    echo -e "${RED}エラー: コマンドが指定されていません${NC}"
    exit 1
fi

# モニタリング準備
monitor_shell_calls

# リアルタイムモニタリング開始
start_realtime_monitor "$MONITOR_COMMAND"