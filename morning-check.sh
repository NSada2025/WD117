#!/bin/bash

# AI Team 朝の健康チェックスクリプト

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}☀️ Good morning! AI Team健康チェック開始...${NC}"
echo ""

# 1. tmuxセッション確認
echo -e "${BLUE}📋 アクティブセッション:${NC}"
tmux ls 2>/dev/null || echo -e "${RED}セッションが見つかりません${NC}"
echo ""

# 2. ディスク・メモリ状況
echo -e "${BLUE}💾 システムリソース:${NC}"
df -h /mnt/d/ | grep -E "(Filesystem|/mnt/d)"
echo ""
free -h | grep -E "(total|Mem:|Swap:)"
echo ""

# 3. 昨日の作業ログ確認
if [ -d "logs" ]; then
    echo -e "${BLUE}📝 最新の作業ログ:${NC}"
    if [ -f "logs/send-message.log" ]; then
        tail -5 logs/send-message.log
    else
        echo "ログファイルが見つかりません"
    fi
else
    echo -e "${YELLOW}logsディレクトリが見つかりません${NC}"
fi
echo ""

# 4. エージェント応答確認
echo -e "${BLUE}🔄 エージェント応答確認:${NC}"

# 応答確認関数
check_agent() {
    local agent=$1
    local role=$2
    echo -n "  $agent ($role): "
    
    # タイムアウト付きで応答確認
    timeout 10 bash -c "
        ./send-message.sh $agent '状態確認: 準備完了していますか？（はい/いいえで応答）' >/dev/null 2>&1
    "
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 応答あり${NC}"
    else
        echo -e "${RED}✗ 応答なし/遅延${NC}"
    fi
}

# 各エージェントをチェック
check_agent "ceo" "CEO"
check_agent "manager" "Manager"
check_agent "dev1" "Dev1"
check_agent "dev2" "Dev2"
check_agent "dev3" "Dev3-注意:高出力"

echo ""

# 5. 推奨アクション
echo -e "${YELLOW}💡 推奨アクション:${NC}"

# エラーチェック
if tmux ls 2>/dev/null | grep -q "ceo\|team"; then
    echo -e "${GREEN}✓ セッション正常 - 作業継続可能${NC}"
    echo ""
    echo "次のコマンドで作業開始:"
    echo "  ./send-message.sh manager \"本日の作業を開始します\""
else
    echo -e "${RED}⚠️ セッション異常 - 再起動推奨${NC}"
    echo ""
    echo "次のコマンドで再起動:"
    echo "  ./start-system-staggered.sh"
fi

echo ""
echo -e "${BLUE}Have a productive day! 🚀${NC}"