# tmux自動メッセージ送信システム テスト計画

## 1. テスト概要

### 1.1 テスト目的
- send-message.shスクリプトの機能性・信頼性・パフォーマンスの検証
- tmux自動メッセージ送信システムの品質保証
- 本番環境での安定運用の確保

### 1.2 テスト範囲
- 機能テスト（正常系・異常系）
- パフォーマンステスト
- セキュリティテスト
- 統合テスト

## 2. テスト環境

### 2.1 環境要件
- OS: Linux (WSL2)
- tmux: 最新版
- Bash: 4.0以上
- ディスク容量: 1GB以上（ログ用）

### 2.2 テストデータ
- 正常なエージェント名: ceo, manager, dev1, dev2, dev3
- 異常なエージェント名: invalid, test, ""
- テストメッセージ: 短文、長文、特殊文字、空文字列

## 3. 機能テスト

### 3.1 正常系テスト
#### TC001: 正常なメッセージ送信
- **テスト内容**: 各エージェントへの正常なメッセージ送信
- **期待結果**: メッセージが正常に送信され、ログに記録される
- **テストケース**:
  ```bash
  ./send-message.sh manager "テストメッセージ"
  ./send-message.sh dev1 "Hello World"
  ./send-message.sh ceo "重要な報告"
  ```

#### TC002: --listオプション
- **テスト内容**: エージェント一覧の表示
- **期待結果**: 5つのエージェントが正しく表示される
- **テストケース**:
  ```bash
  ./send-message.sh --list
  ```

#### TC003: ログ機能
- **テスト内容**: メッセージ送信後のログ記録確認
- **期待結果**: タイムスタンプ付きでログファイルに記録される
- **テストケース**:
  ```bash
  ./send-message.sh manager "ログテスト"
  cat logs/communication.log | tail -1
  ```

### 3.2 異常系テスト
#### TC004: 引数不足
- **テスト内容**: 引数が不足している場合のエラー処理
- **期待結果**: 使用方法が表示され、エラー終了する
- **テストケース**:
  ```bash
  ./send-message.sh
  ./send-message.sh manager
  ```

#### TC005: 不正なエージェント名
- **テスト内容**: 存在しないエージェント名の指定
- **期待結果**: エラーメッセージが表示され、処理が停止する
- **テストケース**:
  ```bash
  ./send-message.sh invalid "テストメッセージ"
  ./send-message.sh "" "空文字テスト"
  ```

#### TC006: tmuxセッション未起動
- **テスト内容**: tmuxセッションが存在しない状態での実行
- **期待結果**: セッション未検出エラーが表示される
- **テストケース**:
  ```bash
  # tmuxセッションを一時停止してテスト
  tmux kill-session -t team
  ./send-message.sh dev1 "セッションテスト"
  ```

## 4. パフォーマンステスト

### 4.1 応答時間テスト
#### TC007: メッセージ送信時間
- **テスト内容**: メッセージ送信の応答時間測定
- **期待結果**: 1秒以内で完了する
- **テストケース**:
  ```bash
  time ./send-message.sh manager "パフォーマンステスト"
  ```

### 4.2 負荷テスト
#### TC008: 連続メッセージ送信
- **テスト内容**: 短時間での連続メッセージ送信
- **期待結果**: 全メッセージが正常に送信される
- **テストケース**:
  ```bash
  for i in {1..50}; do
    ./send-message.sh manager "負荷テスト$i"
  done
  ```

## 5. セキュリティテスト

### 5.1 入力検証テスト
#### TC009: 特殊文字テスト
- **テスト内容**: 特殊文字を含むメッセージの送信
- **期待結果**: 特殊文字が適切に処理される
- **テストケース**:
  ```bash
  ./send-message.sh manager "特殊文字テスト: !@#$%^&*()"
  ./send-message.sh dev1 "改行\nテスト"
  ```

#### TC010: インジェクション攻撃テスト
- **テスト内容**: コマンドインジェクション攻撃の検証
- **期待結果**: 悪意のあるコマンドが実行されない
- **テストケース**:
  ```bash
  ./send-message.sh manager "; rm -rf /tmp/test"
  ./send-message.sh dev1 "\$(whoami)"
  ```

## 6. 統合テスト

### 6.1 システム統合テスト
#### TC011: エージェント間通信テスト
- **テスト内容**: 複数エージェント間での通信確認
- **期待結果**: 全エージェントが正常に通信できる
- **テストケース**:
  ```bash
  ./send-message.sh ceo "統合テスト開始"
  ./send-message.sh manager "ceoからの指示を受信"
  ./send-message.sh dev1 "タスクを実行中"
  ./send-message.sh dev2 "バックエンド処理完了"
  ./send-message.sh dev3 "品質検証完了"
  ```

## 7. 自動テストスクリプト

### 7.1 テスト自動化
```bash
#!/bin/bash
# test-send-message.sh

SCRIPT_DIR=$(dirname "$0")
TEST_LOG="$SCRIPT_DIR/test_results.log"
PASSED=0
FAILED=0

# テスト関数
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_exit_code="$3"
    
    echo "[$test_name] 実行中..." >> "$TEST_LOG"
    
    if eval "$test_command"; then
        if [ "$?" -eq "$expected_exit_code" ]; then
            echo "[$test_name] PASSED" >> "$TEST_LOG"
            ((PASSED++))
        else
            echo "[$test_name] FAILED - 予期しない終了コード" >> "$TEST_LOG"
            ((FAILED++))
        fi
    else
        echo "[$test_name] FAILED - 実行エラー" >> "$TEST_LOG"
        ((FAILED++))
    fi
}

# テスト実行
echo "=== テスト開始 $(date) ===" > "$TEST_LOG"

run_test "TC001-正常送信" "./send-message.sh manager 'テスト'" 0
run_test "TC002-リスト表示" "./send-message.sh --list" 0
run_test "TC004-引数不足" "./send-message.sh" 1
run_test "TC005-不正エージェント" "./send-message.sh invalid 'テスト'" 1

echo "=== テスト結果 ===" >> "$TEST_LOG"
echo "PASSED: $PASSED" >> "$TEST_LOG"
echo "FAILED: $FAILED" >> "$TEST_LOG"
echo "=== テスト終了 $(date) ===" >> "$TEST_LOG"

cat "$TEST_LOG"
```

## 8. テスト実行スケジュール

### 8.1 開発段階
- 機能テスト: 機能追加・修正後
- パフォーマンステスト: 週1回
- セキュリティテスト: 月1回

### 8.2 本番前
- 全テストケースの実行
- 統合テストの実行
- パフォーマンステストの実行

### 8.3 本番後
- 定期監視テスト: 日次
- 機能テスト: 週次
- 包括的テスト: 月次

## 9. テスト完了条件

### 9.1 合格基準
- 全機能テストのPASS率: 100%
- パフォーマンステストの合格: 応答時間1秒以内
- セキュリティテストの合格: 脆弱性なし
- 統合テストの合格: エージェント間通信正常

### 9.2 不合格時の対応
- 機能不良の修正
- パフォーマンス改善
- セキュリティ脆弱性の対策
- 再テストの実施