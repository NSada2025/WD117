#!/bin/bash

# Enhanced Send Message System - 統合テスト環境構築スクリプト
# 作成者: dev3 (品質管理・テスト担当)
# 目的: 本格的な統合テスト環境の構築と実行

set -euo pipefail

# カラー定義
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 統合テスト設定
SCRIPT_PATH="./enhanced-send-message.sh"
TEST_ENV_DIR="test_environment"
INTEGRATION_LOG="logs/integration_test.log"
MOCK_SESSION="test_integration"

# テスト環境初期化
initialize_test_environment() {
    echo -e "${BLUE}🔧 統合テスト環境を初期化中...${NC}"
    
    # テストディレクトリ作成
    mkdir -p "$TEST_ENV_DIR/logs"
    mkdir -p logs
    
    # ログファイル初期化
    echo "=== Enhanced Send Message 統合テスト ===" > "$INTEGRATION_LOG"
    echo "開始時刻: $(date)" >> "$INTEGRATION_LOG"
    echo "" >> "$INTEGRATION_LOG"
    
    echo -e "${GREEN}✅ テスト環境初期化完了${NC}"
}

# モックtmuxセッション作成
create_mock_tmux_sessions() {
    echo -e "${BLUE}🎭 モックtmuxセッションを作成中...${NC}"
    
    # 既存のテストセッションを削除
    tmux kill-session -t "$MOCK_SESSION" 2>/dev/null || true
    tmux kill-session -t "ceo" 2>/dev/null || true
    tmux kill-session -t "team" 2>/dev/null || true
    
    # CEOセッション作成
    tmux new-session -d -s "ceo" -x 80 -y 24
    tmux send-keys -t "ceo" "echo 'CEO Session Ready'" Enter
    
    # チームセッション作成 (4ペイン)
    tmux new-session -d -s "team" -x 80 -y 24
    tmux split-window -h -t "team"
    tmux split-window -v -t "team:0.0"
    tmux split-window -v -t "team:0.2"
    
    # 各ペインにラベル設定
    tmux send-keys -t "team:0.0" "echo 'Manager Session Ready'" Enter
    tmux send-keys -t "team:0.1" "echo 'Dev1 Session Ready'" Enter
    tmux send-keys -t "team:0.2" "echo 'Dev2 Session Ready'" Enter
    tmux send-keys -t "team:0.3" "echo 'Dev3 Session Ready'" Enter
    
    sleep 2
    echo -e "${GREEN}✅ モックtmuxセッション作成完了${NC}"
}

# 統合テスト実行
run_integration_tests() {
    echo -e "${BLUE}🧪 統合テストを実行中...${NC}"
    echo "統合テスト開始: $(date)" >> "$INTEGRATION_LOG"
    
    local test_count=0
    local success_count=0
    local error_count=0
    
    # テストケース定義
    declare -a test_cases=(
        "ceo:CEO統合テスト:こんにちは、CEOです"
        "manager:Manager統合テスト:プロジェクト進捗確認"
        "dev1:Dev1統合テスト:UI/UXタスク完了報告"
        "dev2:Dev2統合テスト:バックエンド開発状況"
        "dev3:Dev3統合テスト:品質管理テスト実行中"
    )
    
    for test_case in "${test_cases[@]}"; do
        IFS=':' read -r agent test_name message <<< "$test_case"
        test_count=$((test_count + 1))
        
        echo -e "${CYAN}[統合テスト $test_count] $test_name${NC}"
        echo "統合テスト $test_count: $test_name (Agent: $agent)" >> "$INTEGRATION_LOG"
        
        # 実際のメッセージ送信テスト
        if $SCRIPT_PATH "$agent" "$message" --auto-execute 2>&1 | tee -a "$INTEGRATION_LOG"; then
            echo -e "${GREEN}✅ 統合テスト成功${NC}"
            echo "結果: SUCCESS" >> "$INTEGRATION_LOG"
            success_count=$((success_count + 1))
        else
            echo -e "${RED}❌ 統合テスト失敗${NC}"
            echo "結果: FAILED" >> "$INTEGRATION_LOG"
            error_count=$((error_count + 1))
        fi
        
        echo "---" >> "$INTEGRATION_LOG"
        sleep 1
    done
    
    # 結果サマリー
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📊 統合テスト結果${NC}"
    echo -e "総テスト数: $test_count"
    echo -e "${GREEN}成功: $success_count${NC}"
    echo -e "${RED}失敗: $error_count${NC}"
    
    echo "" >> "$INTEGRATION_LOG"
    echo "=== 統合テスト結果サマリー ===" >> "$INTEGRATION_LOG"
    echo "総テスト数: $test_count" >> "$INTEGRATION_LOG"
    echo "成功: $success_count" >> "$INTEGRATION_LOG"
    echo "失敗: $error_count" >> "$INTEGRATION_LOG"
    echo "完了時刻: $(date)" >> "$INTEGRATION_LOG"
    
    return $error_count
}

# パフォーマンステスト
run_performance_tests() {
    echo -e "${BLUE}⚡ パフォーマンステストを実行中...${NC}"
    
    local start_time
    local end_time
    local duration
    
    # 連続送信テスト
    echo -e "${YELLOW}📈 連続送信パフォーマンステスト${NC}"
    start_time=$(date +%s.%N)
    
    for i in {1..10}; do
        $SCRIPT_PATH "dev3" "パフォーマンステスト $i" --auto-execute >/dev/null 2>&1
        sleep 0.1
    done
    
    end_time=$(date +%s.%N)
    duration=$(echo "($end_time - $start_time) * 1000" | bc | cut -d. -f1)
    
    echo -e "${GREEN}✅ 10件連続送信完了: ${duration}ms${NC}"
    echo "パフォーマンステスト: 10件連続送信 ${duration}ms" >> "$INTEGRATION_LOG"
}

# ストレステスト
run_stress_tests() {
    echo -e "${BLUE}💪 ストレステストを実行中...${NC}"
    
    # 長いメッセージテスト
    local long_message="これは非常に長いメッセージのストレステストです。"
    for i in {1..10}; do
        long_message+="追加テキスト$i "
    done
    
    if $SCRIPT_PATH "dev3" "$long_message" --auto-execute --verbose >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 長いメッセージテスト成功${NC}"
        echo "ストレステスト: 長いメッセージ SUCCESS" >> "$INTEGRATION_LOG"
    else
        echo -e "${RED}❌ 長いメッセージテスト失敗${NC}"
        echo "ストレステスト: 長いメッセージ FAILED" >> "$INTEGRATION_LOG"
    fi
    
    # 特殊文字テスト
    local special_message="特殊文字テスト: @#$%^&*()[]{}|\\;':\",./<>?~\`"
    if $SCRIPT_PATH "dev3" "$special_message" --auto-execute >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 特殊文字テスト成功${NC}"
        echo "ストレステスト: 特殊文字 SUCCESS" >> "$INTEGRATION_LOG"
    else
        echo -e "${RED}❌ 特殊文字テスト失敗${NC}"
        echo "ストレステスト: 特殊文字 FAILED" >> "$INTEGRATION_LOG"
    fi
}

# テスト環境クリーンアップ
cleanup_test_environment() {
    echo -e "${BLUE}🧹 テスト環境をクリーンアップ中...${NC}"
    
    # モックセッション削除
    tmux kill-session -t "ceo" 2>/dev/null || true
    tmux kill-session -t "team" 2>/dev/null || true
    
    echo -e "${GREEN}✅ クリーンアップ完了${NC}"
}

# メイン実行フロー
main() {
    echo -e "${CYAN}🚀 Enhanced Send Message System 統合テスト環境${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # スクリプト存在確認
    if [ ! -f "$SCRIPT_PATH" ]; then
        echo -e "${RED}❌ エラー: $SCRIPT_PATH が見つかりません${NC}"
        exit 1
    fi
    
    if [ ! -x "$SCRIPT_PATH" ]; then
        echo -e "${RED}❌ エラー: $SCRIPT_PATH に実行権限がありません${NC}"
        exit 1
    fi
    
    # テスト実行
    initialize_test_environment
    create_mock_tmux_sessions
    
    local total_errors=0
    
    # 各テスト実行
    if ! run_integration_tests; then
        total_errors=$((total_errors + $?))
    fi
    
    run_performance_tests
    run_stress_tests
    
    cleanup_test_environment
    
    # 最終結果
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    if [ $total_errors -eq 0 ]; then
        echo -e "${GREEN}🎉 統合テスト環境構築・実行完了: 全テスト成功!${NC}"
        exit 0
    else
        echo -e "${RED}❌ 統合テスト環境構築・実行完了: $total_errors 件のエラー${NC}"
        exit 1
    fi
}

# スクリプト実行
main "$@"