#!/bin/bash

# Enhanced Send Message System - 自動テストスクリプト
# 作成者: dev3 (品質管理・テスト担当)
# 対象: enhanced-send-message.sh

set -euo pipefail

# テスト設定
SCRIPT_PATH="./enhanced-send-message.sh"
TEST_LOG="logs/test_results.log"
ERROR_COUNT=0
SUCCESS_COUNT=0
TOTAL_TESTS=0

# カラー定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ログディレクトリ作成
mkdir -p logs

# テスト開始ログ
echo "=== Enhanced Send Message Test Suite ===" > "$TEST_LOG"
echo "実行日時: $(date)" >> "$TEST_LOG"
echo "対象スクリプト: $SCRIPT_PATH" >> "$TEST_LOG"
echo "" >> "$TEST_LOG"

# テスト実行関数
run_test() {
    local test_name="$1"
    local expected_exit_code="$2"
    shift 2
    local command="$@"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "${CYAN}[TEST $TOTAL_TESTS] $test_name${NC}"
    echo "テスト $TOTAL_TESTS: $test_name" >> "$TEST_LOG"
    echo "コマンド: $command" >> "$TEST_LOG"
    
    # テスト実行
    if eval "$command" > /tmp/test_output 2>&1; then
        actual_exit_code=0
    else
        actual_exit_code=$?
    fi
    
    # 結果確認
    if [ "$actual_exit_code" -eq "$expected_exit_code" ]; then
        echo -e "${GREEN}✅ PASS${NC}"
        echo "結果: PASS (exit code: $actual_exit_code)" >> "$TEST_LOG"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo -e "${RED}❌ FAIL (expected: $expected_exit_code, actual: $actual_exit_code)${NC}"
        echo "結果: FAIL (expected: $expected_exit_code, actual: $actual_exit_code)" >> "$TEST_LOG"
        echo "出力:" >> "$TEST_LOG"
        cat /tmp/test_output >> "$TEST_LOG"
        ERROR_COUNT=$((ERROR_COUNT + 1))
    fi
    
    echo "---" >> "$TEST_LOG"
    echo ""
}

echo -e "${BLUE}🧪 Enhanced Send Message System テストスイート開始${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# テスト1: スクリプト存在確認
run_test "スクリプト存在確認" 0 "test -f $SCRIPT_PATH"

# テスト2: 実行権限確認
run_test "実行権限確認" 0 "test -x $SCRIPT_PATH"

# テスト3: ヘルプ表示テスト
run_test "ヘルプ表示" 0 "$SCRIPT_PATH --help"

# テスト4: 引数なしエラーテスト
run_test "引数なしエラー" 1 "$SCRIPT_PATH"

# テスト5: 不正エージェント名テスト
run_test "不正エージェント名" 1 "$SCRIPT_PATH invalid_agent 'test message' --test-mode"

# テスト6: 有効エージェント名テスト（テストモード）
for agent in ceo manager dev1 dev2 dev3; do
    run_test "エージェント名テスト: $agent" 0 "$SCRIPT_PATH $agent 'テストメッセージ' --test-mode"
done

# テスト7: オプションテスト
run_test "自動実行オプション" 0 "$SCRIPT_PATH dev1 'test' --auto-execute --test-mode"
run_test "手動オプション" 0 "$SCRIPT_PATH dev1 'test' --manual --test-mode"
run_test "詳細モード" 0 "$SCRIPT_PATH dev1 'test' --verbose --test-mode"

# テスト8: メッセージ内容テスト
run_test "日本語メッセージ" 0 "$SCRIPT_PATH dev1 'こんにちは世界' --test-mode"
run_test "英語メッセージ" 0 "$SCRIPT_PATH dev1 'Hello World' --test-mode"
run_test "特殊文字メッセージ" 0 "$SCRIPT_PATH dev1 'Test @#$%^&*()' --test-mode"
run_test "長いメッセージ" 0 "$SCRIPT_PATH dev1 'これは非常に長いメッセージのテストです。複数の単語と文章が含まれています。' --test-mode"

# テスト9: 組み合わせテスト
run_test "全オプション組み合わせ" 0 "$SCRIPT_PATH dev3 'フルテスト' --test-mode --verbose --manual"

# 結果サマリー
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📊 テスト結果サマリー${NC}"
echo -e "総テスト数: $TOTAL_TESTS"
echo -e "${GREEN}成功: $SUCCESS_COUNT${NC}"
echo -e "${RED}失敗: $ERROR_COUNT${NC}"

echo "" >> "$TEST_LOG"
echo "=== テスト結果サマリー ===" >> "$TEST_LOG"
echo "総テスト数: $TOTAL_TESTS" >> "$TEST_LOG"
echo "成功: $SUCCESS_COUNT" >> "$TEST_LOG"
echo "失敗: $ERROR_COUNT" >> "$TEST_LOG"

if [ "$ERROR_COUNT" -eq 0 ]; then
    echo -e "${GREEN}🎉 全テスト PASS!${NC}"
    echo "全体結果: 全テスト PASS" >> "$TEST_LOG"
    exit 0
else
    echo -e "${RED}❌ $ERROR_COUNT 件のテストが失敗しました${NC}"
    echo "全体結果: $ERROR_COUNT 件の失敗" >> "$TEST_LOG"
    exit 1
fi