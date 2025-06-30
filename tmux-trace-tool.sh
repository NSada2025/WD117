#!/bin/bash

# tmux実行トレースツール
# tmux実行時に呼び出される.shファイルの数をカウント

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログディレクトリ設定
LOG_DIR="./logs/tmux-trace"
mkdir -p "$LOG_DIR"

# タイムスタンプ
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# トレースモード選択
echo -e "${BLUE}=== tmux実行トレースツール ===${NC}"
echo "トレース方法を選択してください:"
echo "1) Bash Debug Mode (推奨 - より詳細)"
echo "2) strace (システムコール)"
echo "3) 両方 (最も包括的)"
read -p "選択 [1-3]: " choice

# 実行対象のコマンド指定
echo -e "\n${YELLOW}トレースする tmux コマンドを入力してください:${NC}"
echo "例: tmux new-session -s test"
echo "例: ./start-system.sh"
read -p "コマンド: " TRACE_COMMAND

# 結果ファイル名
RESULT_FILE="$LOG_DIR/trace_result_${TIMESTAMP}.txt"
DEBUG_LOG="$LOG_DIR/debug_${TIMESTAMP}.log"
STRACE_LOG="$LOG_DIR/strace_${TIMESTAMP}.log"

# トレース関数
function trace_with_bash_debug() {
    echo -e "\n${GREEN}Bash Debug Mode でトレース開始...${NC}"
    
    # デバッグトレース用の一時スクリプト作成
    cat > "$LOG_DIR/trace_wrapper.sh" << 'EOF'
#!/bin/bash
set -x  # デバッグモード有効化
export PS4='+ $(date "+%Y-%m-%d %H:%M:%S") [${BASH_SOURCE}:${LINENO}]: '

# 実行されるシェルスクリプトを記録
TRACE_LOG="/tmp/bash_trace_$$.log"
exec 4>&2
exec 2> >(tee -a "$TRACE_LOG" | grep -E '\.(sh|bash)' | tee -a "/tmp/sh_files_$$.txt")

# コマンド実行
eval "$@"

# 結果を標準エラー出力に戻す
exec 2>&4

# 呼び出されたシェルファイルの統計
echo "=== シェルスクリプト呼び出し統計 ==="
if [ -f "/tmp/sh_files_$$.txt" ]; then
    sort "/tmp/sh_files_$$.txt" | uniq -c | sort -nr
    echo ""
    echo "総呼び出し数: $(wc -l < "/tmp/sh_files_$$.txt")"
    echo "ユニークファイル数: $(sort "/tmp/sh_files_$$.txt" | uniq | wc -l)"
fi

# クリーンアップ
rm -f "/tmp/bash_trace_$$.log" "/tmp/sh_files_$$.txt"
EOF
    
    chmod +x "$LOG_DIR/trace_wrapper.sh"
    
    # トレース実行
    bash -x "$LOG_DIR/trace_wrapper.sh" "$TRACE_COMMAND" 2>&1 | tee "$DEBUG_LOG"
    
    # .shファイルの呼び出しを抽出してカウント
    echo -e "\n${YELLOW}=== Bash Debug 結果分析 ===${NC}" | tee -a "$RESULT_FILE"
    grep -E '\+.*\.(sh|bash)' "$DEBUG_LOG" | sed 's/^.*\///' | sort | uniq -c | sort -nr | tee -a "$RESULT_FILE"
    
    local total_calls=$(grep -E '\+.*\.(sh|bash)' "$DEBUG_LOG" | wc -l)
    local unique_files=$(grep -E '\+.*\.(sh|bash)' "$DEBUG_LOG" | sed 's/^.*\///' | sort | uniq | wc -l)
    
    echo -e "\n総呼び出し回数: ${GREEN}${total_calls}${NC}" | tee -a "$RESULT_FILE"
    echo -e "ユニークファイル数: ${GREEN}${unique_files}${NC}" | tee -a "$RESULT_FILE"
}

function trace_with_strace() {
    echo -e "\n${GREEN}strace でトレース開始...${NC}"
    
    # straceでexecveシステムコールを追跡
    strace -f -e trace=execve -o "$STRACE_LOG" $TRACE_COMMAND 2>&1
    
    # .shファイルの実行を抽出
    echo -e "\n${YELLOW}=== strace 結果分析 ===${NC}" | tee -a "$RESULT_FILE"
    grep -E 'execve.*\.(sh|bash)' "$STRACE_LOG" | sed 's/.*"\([^"]*\.sh\)".*/\1/' | sed 's/^.*\///' | sort | uniq -c | sort -nr | tee -a "$RESULT_FILE"
    
    local total_execs=$(grep -E 'execve.*\.(sh|bash)' "$STRACE_LOG" | wc -l)
    local unique_execs=$(grep -E 'execve.*\.(sh|bash)' "$STRACE_LOG" | sed 's/.*"\([^"]*\.sh\)".*/\1/' | sed 's/^.*\///' | sort | uniq | wc -l)
    
    echo -e "\n総実行回数: ${GREEN}${total_execs}${NC}" | tee -a "$RESULT_FILE"
    echo -e "ユニーク実行ファイル数: ${GREEN}${unique_execs}${NC}" | tee -a "$RESULT_FILE"
}

# メイン処理
echo -e "\n${BLUE}トレース開始: $TRACE_COMMAND${NC}"
echo "結果は $RESULT_FILE に保存されます"
echo "==================================" | tee "$RESULT_FILE"
echo "tmux実行トレース結果" | tee -a "$RESULT_FILE"
echo "実行時刻: $(date)" | tee -a "$RESULT_FILE"
echo "対象コマンド: $TRACE_COMMAND" | tee -a "$RESULT_FILE"
echo "==================================" | tee -a "$RESULT_FILE"

case $choice in
    1)
        trace_with_bash_debug
        ;;
    2)
        trace_with_strace
        ;;
    3)
        trace_with_bash_debug
        trace_with_strace
        ;;
    *)
        echo -e "${RED}無効な選択です${NC}"
        exit 1
        ;;
esac

# サマリー表示
echo -e "\n${BLUE}=== トレース完了 ===${NC}"
echo -e "詳細結果: ${GREEN}$RESULT_FILE${NC}"
echo -e "デバッグログ: ${GREEN}$DEBUG_LOG${NC}"
if [ "$choice" = "2" ] || [ "$choice" = "3" ]; then
    echo -e "straceログ: ${GREEN}$STRACE_LOG${NC}"
fi

# 簡易的な可視化
echo -e "\n${YELLOW}=== 呼び出し頻度グラフ (上位5件) ===${NC}"
head -5 "$RESULT_FILE" | while read count file; do
    if [[ "$count" =~ ^[0-9]+$ ]]; then
        printf "%-30s " "$file"
        for ((i=0; i<$count; i++)); do
            echo -n "█"
        done
        echo " ($count)"
    fi
done