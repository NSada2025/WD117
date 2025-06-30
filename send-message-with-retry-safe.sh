#!/bin/bash

# エラー時自動リトライ機能付きメッセージ送信スクリプト（安全版）

TARGET=$1
MESSAGE=$2
MAX_RETRIES=3
RETRY_DELAY=5

# ログディレクトリ作成
mkdir -p logs

# 使用方法チェック
if [ -z "$TARGET" ] || [ -z "$MESSAGE" ]; then
    echo "使用方法: ./send-message-with-retry-safe.sh [ceo|manager|dev1|dev2|dev3] \"メッセージ\""
    exit 1
fi

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ペイン存在確認関数
check_target_pane() {
    local target=$1
    local session=""
    local pane=""
    
    # ターゲットに応じたセッション・ペイン設定
    case $target in
        ceo)
            session="ceo"
            pane="0"
            ;;
        manager)
            session="team"
            pane="0.0"
            ;;
        dev1)
            session="team"
            pane="0.1"
            ;;
        dev2)
            session="team"
            pane="0.2"
            ;;
        dev3)
            session="team"
            pane="0.3"
            ;;
        *)
            echo -e "${RED}エラー: 不明なターゲット '$target'${NC}"
            return 1
            ;;
    esac
    
    # tmuxサーバー確認
    if ! tmux list-sessions &>/dev/null; then
        echo -e "${RED}エラー: tmuxサーバーが応答しません${NC}"
        return 1
    fi
    
    # セッション存在確認
    if ! tmux has-session -t "$session" 2>/dev/null; then
        echo -e "${RED}エラー: セッション '$session' が見つかりません${NC}"
        return 1
    fi
    
    # ペイン存在確認
    local pane_index="${pane#*.}"
    if ! tmux list-panes -t "$session" -F "#{pane_index}" 2>/dev/null | grep -q "^${pane_index}$"; then
        echo -e "${RED}エラー: ペイン '$session:$pane' が見つかりません${NC}"
        return 1
    fi
    
    return 0
}

echo -e "${YELLOW}📨 メッセージ送信: $TARGET${NC}"
echo -e "${BLUE}内容: $MESSAGE${NC}"

# 事前チェック
if ! check_target_pane "$TARGET"; then
    echo -e "${RED}❌ 送信先の確認に失敗しました${NC}"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pre-check failed for $TARGET" >> logs/send-errors.log
    echo -e "${YELLOW}ヒント: システムを起動してください: ./start-system-auto-safe.sh${NC}"
    exit 1
fi

# リトライループ
for i in $(seq 1 $MAX_RETRIES); do
    echo -e "試行 $i/$MAX_RETRIES..."
    
    # 各試行前に再度ペイン存在確認
    if ! check_target_pane "$TARGET"; then
        echo -e "${RED}❌ ペインが見つかりません（試行 $i）${NC}"
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pane check failed for $TARGET (attempt $i)" >> logs/send-errors.log
    else
        # send-message-safe.sh実行（存在する場合）
        if [ -f "./send-message-safe.sh" ]; then
            if ./send-message-safe.sh "$TARGET" "$MESSAGE" 2>/dev/null; then
                echo -e "${GREEN}✅ メッセージ送信成功！${NC}"
                exit 0
            fi
        # フォールバック: 通常のsend-message.sh
        elif [ -f "./send-message.sh" ]; then
            if ./send-message.sh "$TARGET" "$MESSAGE" 2>/dev/null; then
                echo -e "${GREEN}✅ メッセージ送信成功！${NC}"
                exit 0
            fi
        else
            echo -e "${RED}❌ 送信スクリプトが見つかりません${NC}"
            exit 1
        fi
    fi
    
    echo -e "${RED}❌ 送信失敗${NC}"
    
    # エラーログ記録
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Failed to send to $TARGET (attempt $i)" >> logs/send-errors.log
    
    if [ $i -lt $MAX_RETRIES ]; then
        echo -e "${YELLOW}⏳ ${RETRY_DELAY}秒後にリトライします...${NC}"
        
        # プログレスバー表示
        for j in $(seq 1 $RETRY_DELAY); do
            printf "\r待機中: ["
            printf "%${j}s" | tr ' ' '='
            printf "%$((RETRY_DELAY-j))s" | tr ' ' '-'
            printf "]"
            sleep 1
        done
        echo ""
    fi
done

# 最終失敗
echo -e "${RED}❌ 送信失敗: 最大リトライ回数に達しました${NC}"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] CRITICAL: Failed to send to $TARGET after $MAX_RETRIES attempts" >> logs/send-errors.log

# エラー通知（オプション）
if [ -f "./notify-error.sh" ]; then
    ./notify-error.sh "メッセージ送信失敗: $TARGET"
fi

exit 1