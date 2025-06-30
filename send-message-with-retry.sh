#!/bin/bash

# エラー時自動リトライ機能付きメッセージ送信スクリプト

TARGET=$1
MESSAGE=$2
MAX_RETRIES=3
RETRY_DELAY=5

# 使用方法チェック
if [ -z "$TARGET" ] || [ -z "$MESSAGE" ]; then
    echo "使用方法: ./send-message-with-retry.sh [ceo|manager|dev1|dev2|dev3] \"メッセージ\""
    exit 1
fi

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📨 メッセージ送信: $TARGET${NC}"

# リトライループ
for i in $(seq 1 $MAX_RETRIES); do
    echo -e "試行 $i/$MAX_RETRIES..."
    
    # send-message.sh実行
    if ./send-message.sh "$TARGET" "$MESSAGE" 2>/dev/null; then
        echo -e "${GREEN}✅ メッセージ送信成功！${NC}"
        exit 0
    else
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