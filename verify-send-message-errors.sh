#!/bin/bash

# send-message関連エラー検証ツール
# dev1が発見した問題の実証テスト

# カラー定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# テスト結果保存
TEST_LOG="./logs/send-message-verification-$(date +%Y%m%d_%H%M%S).log"
mkdir -p ./logs

echo -e "${BLUE}=== send-message.sh エラー検証ツール ===${NC}" | tee "$TEST_LOG"
echo "実行時刻: $(date)" | tee -a "$TEST_LOG"
echo "" | tee -a "$TEST_LOG"

# テスト1: send-message.sh のエラーチェック検証
echo -e "${CYAN}[テスト1] send-message.sh エラーチェック欠如の検証${NC}" | tee -a "$TEST_LOG"
echo "========================================" | tee -a "$TEST_LOG"

# 74行目のコードを抽出
echo -e "${YELLOW}問題箇所（send-message.sh:74）:${NC}" | tee -a "$TEST_LOG"
sed -n '73,75p' ./send-message.sh | tee -a "$TEST_LOG"

# エラーハンドリングの有無を確認
echo -e "\n${YELLOW}エラーハンドリング分析:${NC}" | tee -a "$TEST_LOG"
if grep -A 2 "tmux send-keys" ./send-message.sh | grep -q "if\|then\|\$?"; then
    echo -e "${GREEN}✓ エラーハンドリングあり${NC}" | tee -a "$TEST_LOG"
else
    echo -e "${RED}✗ エラーハンドリングなし - tmux send-keys の結果をチェックしていません${NC}" | tee -a "$TEST_LOG"
fi

# テスト2: enhanced-send-message.sh の未定義関数
echo -e "\n${CYAN}[テスト2] enhanced-send-message.sh 未定義関数の検証${NC}" | tee -a "$TEST_LOG"
echo "========================================" | tee -a "$TEST_LOG"

# 169行目の問題を検証
echo -e "${YELLOW}問題箇所（enhanced-send-message.sh:169）:${NC}" | tee -a "$TEST_LOG"
sed -n '168,170p' ./enhanced-send-message.sh 2>/dev/null | tee -a "$TEST_LOG"

# rotate_logs関数の定義位置を確認
echo -e "\n${YELLOW}rotate_logs関数の定義位置:${NC}" | tee -a "$TEST_LOG"
FUNC_DEF_LINE=$(grep -n "^rotate_logs()" ./enhanced-send-message.sh 2>/dev/null | cut -d: -f1)
FUNC_CALL_LINE=$(grep -n "rotate_logs$" ./enhanced-send-message.sh 2>/dev/null | head -1 | cut -d: -f1)

if [ -n "$FUNC_DEF_LINE" ] && [ -n "$FUNC_CALL_LINE" ]; then
    echo "関数定義: $FUNC_DEF_LINE 行目" | tee -a "$TEST_LOG"
    echo "関数呼び出し: $FUNC_CALL_LINE 行目" | tee -a "$TEST_LOG"
    
    if [ "$FUNC_CALL_LINE" -lt "$FUNC_DEF_LINE" ]; then
        echo -e "${RED}✗ エラー: 関数定義前に呼び出されています！${NC}" | tee -a "$TEST_LOG"
    else
        echo -e "${GREEN}✓ 正常: 関数定義後に呼び出されています${NC}" | tee -a "$TEST_LOG"
    fi
fi

# monitor_system_performance関数も確認
echo -e "\n${YELLOW}monitor_system_performance関数の検証:${NC}" | tee -a "$TEST_LOG"
MONITOR_DEF_LINE=$(grep -n "^monitor_system_performance()" ./enhanced-send-message.sh 2>/dev/null | cut -d: -f1)
MONITOR_CALL_LINE=$(grep -n "monitor_system_performance$" ./enhanced-send-message.sh 2>/dev/null | head -1 | cut -d: -f1)

if [ -n "$MONITOR_DEF_LINE" ] && [ -n "$MONITOR_CALL_LINE" ]; then
    echo "関数定義: $MONITOR_DEF_LINE 行目" | tee -a "$TEST_LOG"
    echo "関数呼び出し: $MONITOR_CALL_LINE 行目" | tee -a "$TEST_LOG"
    
    if [ "$MONITOR_CALL_LINE" -lt "$MONITOR_DEF_LINE" ]; then
        echo -e "${RED}✗ エラー: 関数定義前に呼び出されています！${NC}" | tee -a "$TEST_LOG"
    fi
fi

# テスト3: ペイン存在確認の欠如
echo -e "\n${CYAN}[テスト3] ペイン存在確認の検証${NC}" | tee -a "$TEST_LOG"
echo "========================================" | tee -a "$TEST_LOG"

# send-message.sh のペイン確認
echo -e "${YELLOW}send-message.sh のペイン確認:${NC}" | tee -a "$TEST_LOG"
if grep -q "list-panes.*-t.*PANE" ./send-message.sh; then
    echo -e "${GREEN}✓ ペイン存在確認あり${NC}" | tee -a "$TEST_LOG"
else
    echo -e "${RED}✗ ペイン存在確認なし${NC}" | tee -a "$TEST_LOG"
    echo "  セッション確認のみ実施、個別ペインの確認がありません" | tee -a "$TEST_LOG"
fi

# enhanced-send-message.sh のペイン確認
echo -e "\n${YELLOW}enhanced-send-message.sh のペイン確認:${NC}" | tee -a "$TEST_LOG"
if grep -q "list-panes.*-t.*pane" ./enhanced-send-message.sh 2>/dev/null; then
    echo -e "${GREEN}✓ ペイン存在確認あり${NC}" | tee -a "$TEST_LOG"
else
    echo -e "${RED}✗ ペイン存在確認なし${NC}" | tee -a "$TEST_LOG"
fi

# テスト4: 実際のエラー再現テスト
echo -e "\n${CYAN}[テスト4] エラー再現テスト${NC}" | tee -a "$TEST_LOG"
echo "========================================" | tee -a "$TEST_LOG"

# テスト用セッション作成
TEST_SESSION="error_test_$$"
echo "テスト用セッション作成: $TEST_SESSION" | tee -a "$TEST_LOG"

if tmux new-session -d -s "$TEST_SESSION" 2>/dev/null; then
    # 存在しないペインへの送信テスト
    echo -e "\n${YELLOW}存在しないペイン(99)への送信テスト:${NC}" | tee -a "$TEST_LOG"
    
    # send-message.sh でテスト
    echo "コマンド: ./send-message.sh manager 'テストメッセージ'" | tee -a "$TEST_LOG"
    
    # 一時的にPANE変数を変更してテスト
    cp send-message.sh send-message-test.sh
    sed -i 's/PANE=1/PANE=99/' send-message-test.sh
    
    OUTPUT=$(./send-message-test.sh manager "テストメッセージ" 2>&1)
    EXIT_CODE=$?
    
    echo "出力: $OUTPUT" | tee -a "$TEST_LOG"
    echo "終了コード: $EXIT_CODE" | tee -a "$TEST_LOG"
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${RED}✗ 問題: エラーにもかかわらず正常終了しています${NC}" | tee -a "$TEST_LOG"
    else
        echo -e "${GREEN}✓ 正常: エラーを検出しました${NC}" | tee -a "$TEST_LOG"
    fi
    
    # クリーンアップ
    rm -f send-message-test.sh
    tmux kill-session -t "$TEST_SESSION" 2>/dev/null
fi

# サマリー
echo -e "\n${BLUE}=== 検証結果サマリー ===${NC}" | tee -a "$TEST_LOG"
echo "========================================" | tee -a "$TEST_LOG"

ISSUES_FOUND=0

# 問題をカウント
if ! grep -A 2 "tmux send-keys" ./send-message.sh | grep -q "if\|then\|\$?"; then
    echo -e "${RED}1. send-message.sh: エラーハンドリング欠如${NC}" | tee -a "$TEST_LOG"
    ((ISSUES_FOUND++))
fi

if [ -n "$FUNC_CALL_LINE" ] && [ -n "$FUNC_DEF_LINE" ] && [ "$FUNC_CALL_LINE" -lt "$FUNC_DEF_LINE" ]; then
    echo -e "${RED}2. enhanced-send-message.sh: 未定義関数呼び出し${NC}" | tee -a "$TEST_LOG"
    ((ISSUES_FOUND++))
fi

if ! grep -q "list-panes.*-t.*PANE" ./send-message.sh; then
    echo -e "${RED}3. ペイン存在確認の欠如${NC}" | tee -a "$TEST_LOG"
    ((ISSUES_FOUND++))
fi

echo -e "\n${YELLOW}検出された問題: $ISSUES_FOUND 件${NC}" | tee -a "$TEST_LOG"
echo -e "${CYAN}詳細ログ: $TEST_LOG${NC}" | tee -a "$TEST_LOG"

# 修正提案
if [ $ISSUES_FOUND -gt 0 ]; then
    echo -e "\n${BLUE}=== 推奨される修正 ===${NC}" | tee -a "$TEST_LOG"
    echo "1. send-message.sh の74行目にエラーチェックを追加" | tee -a "$TEST_LOG"
    echo "2. enhanced-send-message.sh の関数定義順序を修正" | tee -a "$TEST_LOG"
    echo "3. 両スクリプトにペイン存在確認を追加" | tee -a "$TEST_LOG"
fi