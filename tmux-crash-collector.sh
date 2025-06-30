#!/bin/bash

# tmux異常終了時の自動ログ収集システム
# 3回連続終了パターンの検出と詳細ログ収集

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# 設定
CRASH_LOG_DIR="./logs/tmux-crashes"
MONITOR_INTERVAL=2  # 監視間隔（秒）
CRASH_THRESHOLD=3   # 連続クラッシュ判定閾値
CRASH_TIME_WINDOW=300  # クラッシュ判定時間窓（秒）

# グローバル変数
declare -A SESSION_CRASHES  # セッション別クラッシュカウント
declare -A CRASH_TIMESTAMPS # クラッシュタイムスタンプ
MONITOR_PID=""
LAST_SESSION_COUNT=0

# 初期化
mkdir -p "$CRASH_LOG_DIR"

# クリーンアップ処理
trap cleanup EXIT INT TERM

function cleanup() {
    echo -e "\n${YELLOW}監視終了...${NC}"
    if [ -n "$MONITOR_PID" ]; then
        kill $MONITOR_PID 2>/dev/null
    fi
    save_crash_statistics
}

# クラッシュ情報収集
function collect_crash_info() {
    local crash_id="$1"
    local session_name="$2"
    local crash_dir="$CRASH_LOG_DIR/crash_${crash_id}"
    
    mkdir -p "$crash_dir"
    
    echo -e "${RED}クラッシュ検出！ 詳細情報を収集中...${NC}"
    
    # 基本情報
    cat > "$crash_dir/crash_info.txt" << EOF
クラッシュID: $crash_id
検出時刻: $(date)
セッション名: $session_name
連続クラッシュ回数: ${SESSION_CRASHES[$session_name]:-0}
EOF
    
    # システム状態
    echo -e "\n=== システム状態 ===" >> "$crash_dir/crash_info.txt"
    
    # メモリ情報
    echo -e "\n[メモリ状態]" >> "$crash_dir/crash_info.txt"
    free -h >> "$crash_dir/crash_info.txt"
    
    # CPU情報
    echo -e "\n[CPU使用率]" >> "$crash_dir/crash_info.txt"
    top -bn1 | head -20 >> "$crash_dir/crash_info.txt"
    
    # tmuxプロセス情報
    echo -e "\n[tmuxプロセス]" >> "$crash_dir/crash_info.txt"
    ps aux | grep -E "[t]mux" >> "$crash_dir/crash_info.txt"
    
    # ファイルディスクリプタ
    echo -e "\n[オープンファイル数]" >> "$crash_dir/crash_info.txt"
    for pid in $(pgrep tmux 2>/dev/null); do
        echo "PID $pid: $(ls /proc/$pid/fd 2>/dev/null | wc -l) files" >> "$crash_dir/crash_info.txt"
    done
    
    # システムログ
    echo -e "\n[システムログ (最新20行)]" >> "$crash_dir/crash_info.txt"
    if [ -f /var/log/syslog ]; then
        tail -20 /var/log/syslog >> "$crash_dir/crash_info.txt"
    fi
    
    # dmesg
    echo -e "\n[カーネルメッセージ (最新20行)]" >> "$crash_dir/crash_info.txt"
    dmesg | tail -20 >> "$crash_dir/crash_info.txt"
    
    # tmux server info (可能な場合)
    if tmux info &>/dev/null; then
        echo -e "\n[tmux server info]" >> "$crash_dir/crash_info.txt"
        tmux server-info >> "$crash_dir/crash_info.txt" 2>&1
    fi
    
    # コアダンプ確認
    echo -e "\n[コアダンプ確認]" >> "$crash_dir/crash_info.txt"
    find /tmp -name "core*" -mmin -5 2>/dev/null | head -10 >> "$crash_dir/crash_info.txt"
    
    # 環境変数
    echo -e "\n[関連環境変数]" >> "$crash_dir/crash_info.txt"
    env | grep -E "(TMUX|SHELL|TERM|DISPLAY)" | sort >> "$crash_dir/crash_info.txt"
    
    # セッション履歴（可能な場合）
    if [ -f ~/.tmux_history ]; then
        echo -e "\n[tmux履歴 (最新20行)]" >> "$crash_dir/crash_info.txt"
        tail -20 ~/.tmux_history >> "$crash_dir/crash_info.txt"
    fi
    
    echo -e "${GREEN}クラッシュ情報収集完了: $crash_dir${NC}"
}

# 3回連続クラッシュパターン検出
function detect_crash_pattern() {
    local session_name="$1"
    local current_time=$(date +%s)
    
    # セッションのクラッシュ履歴更新
    SESSION_CRASHES[$session_name]=$((${SESSION_CRASHES[$session_name]:-0} + 1))
    CRASH_TIMESTAMPS[$session_name]="$current_time ${CRASH_TIMESTAMPS[$session_name]:-}"
    
    # 時間窓内のクラッシュ回数カウント
    local crash_count=0
    for timestamp in ${CRASH_TIMESTAMPS[$session_name]}; do
        if [ $((current_time - timestamp)) -lt $CRASH_TIME_WINDOW ]; then
            ((crash_count++))
        fi
    done
    
    # 3回連続クラッシュ検出
    if [ $crash_count -ge $CRASH_THRESHOLD ]; then
        echo -e "${RED}⚠ 警告: セッション '$session_name' が${CRASH_TIME_WINDOW}秒以内に${crash_count}回クラッシュしました！${NC}"
        
        # 詳細分析レポート生成
        generate_pattern_analysis "$session_name" "$crash_count"
        
        return 0  # パターン検出
    fi
    
    return 1  # パターン未検出
}

# パターン分析レポート生成
function generate_pattern_analysis() {
    local session_name="$1"
    local crash_count="$2"
    local analysis_file="$CRASH_LOG_DIR/pattern_analysis_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$analysis_file" << EOF
════════════════════════════════════════════════════════════
           3回連続クラッシュパターン分析レポート
════════════════════════════════════════════════════════════

検出時刻: $(date)
影響セッション: $session_name
クラッシュ回数: $crash_count 回（${CRASH_TIME_WINDOW}秒以内）

【推定原因】
1. メモリ不足
   - 現在のメモリ使用率: $(free | grep Mem | awk '{print int($3/$2 * 100)}')%
   
2. リソース枯渇
   - オープンファイル数制限
   - プロセス数制限
   
3. 設定ファイルの問題
   - .tmux.conf の構文エラー
   - プラグインの競合
   
4. 外部要因
   - ネットワーク切断
   - ディスクI/Oエラー

【推奨対処法】
1. tmux server-info でサーバー状態確認
2. すべてのセッションを一度終了: tmux kill-server
3. 設定ファイルを一時的に無効化: mv ~/.tmux.conf ~/.tmux.conf.bak
4. クリーンな状態で再起動: tmux new-session -s test

【収集されたクラッシュログ】
EOF
    
    # 最新のクラッシュログをリスト
    ls -lt "$CRASH_LOG_DIR"/crash_*/crash_info.txt 2>/dev/null | head -5 >> "$analysis_file"
    
    echo -e "${MAGENTA}パターン分析レポート生成: $analysis_file${NC}"
}

# リアルタイム監視
function monitor_tmux_sessions() {
    echo -e "${BLUE}tmuxセッション監視開始...${NC}"
    echo -e "${YELLOW}Ctrl+C で終了${NC}\n"
    
    while true; do
        # 現在のセッション数取得
        local current_sessions=$(tmux list-sessions 2>/dev/null | wc -l)
        
        # セッション数の変化を検出
        if [ "$current_sessions" -lt "$LAST_SESSION_COUNT" ] && [ "$LAST_SESSION_COUNT" -gt 0 ]; then
            # セッションが減少した = クラッシュの可能性
            local crash_id=$(date +%Y%m%d_%H%M%S)_$$
            echo -e "${RED}[$(date +%H:%M:%S)] セッション数減少検出: $LAST_SESSION_COUNT → $current_sessions${NC}"
            
            # どのセッションがクラッシュしたか特定を試みる
            local crashed_session="unknown"
            
            # クラッシュ情報収集
            collect_crash_info "$crash_id" "$crashed_session"
            
            # パターン検出
            detect_crash_pattern "$crashed_session"
        fi
        
        # 現在の状態を表示
        printf "\r${CYAN}[$(date +%H:%M:%S)] アクティブセッション: $current_sessions${NC} "
        
        # セッション数更新
        LAST_SESSION_COUNT=$current_sessions
        
        sleep $MONITOR_INTERVAL
    done
}

# 統計情報保存
function save_crash_statistics() {
    local stats_file="$CRASH_LOG_DIR/crash_statistics_$(date +%Y%m%d_%H%M%S).json"
    
    echo "{" > "$stats_file"
    echo "  \"monitoring_end\": \"$(date -Iseconds)\"," >> "$stats_file"
    echo "  \"total_crashes\": $(find "$CRASH_LOG_DIR" -name "crash_*" -type d | wc -l)," >> "$stats_file"
    echo "  \"session_crashes\": {" >> "$stats_file"
    
    local first=true
    for session in "${!SESSION_CRASHES[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            echo "," >> "$stats_file"
        fi
        echo -n "    \"$session\": ${SESSION_CRASHES[$session]}" >> "$stats_file"
    done
    
    echo -e "\n  }" >> "$stats_file"
    echo "}" >> "$stats_file"
    
    echo -e "${GREEN}統計情報保存: $stats_file${NC}"
}

# メイン処理
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           tmux異常終了自動収集システム v1.0                   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}設定:${NC}"
echo -e "  • 監視間隔: ${MONITOR_INTERVAL}秒"
echo -e "  • クラッシュ判定: ${CRASH_TIME_WINDOW}秒以内に${CRASH_THRESHOLD}回"
echo -e "  • ログ保存先: $CRASH_LOG_DIR"
echo ""

# 初回のセッション数取得
LAST_SESSION_COUNT=$(tmux list-sessions 2>/dev/null | wc -l)

# 監視開始
monitor_tmux_sessions