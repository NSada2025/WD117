# tmux異常終了予防ガイドライン

## エグゼクティブサマリー
本調査により、tmux異常終了の根本原因は以下の3点に集約される：
1. エラーハンドリングの欠如（最重要）
2. 並行実行時の競合状態
3. 負荷限界を超えた使用

これらの問題に対する包括的な予防策を以下に提示する。

## 1. 開発ガイドライン

### 必須チェックリスト
```bash
# すべてのtmuxコマンドに適用すべきパターン

# ❌ 悪い例
tmux send-keys -t session "message" C-m

# ✅ 良い例
if ! tmux send-keys -t session "message" C-m 2>/dev/null; then
    echo "エラー: メッセージ送信失敗" >&2
    exit 1
fi
```

### スクリプトヘッダーテンプレート
```bash
#!/bin/bash
set -euo pipefail  # エラー時即座に終了
trap 'echo "エラーが発生しました: 行 $LINENO" >&2' ERR

# tmux健全性チェック
check_tmux_health() {
    if ! command -v tmux &>/dev/null; then
        echo "エラー: tmuxがインストールされていません" >&2
        exit 1
    fi
    
    if ! pgrep -x tmux >/dev/null; then
        echo "エラー: tmuxサーバーが実行されていません" >&2
        exit 1
    fi
}
```

## 2. 運用制限値

### 推奨パラメータ
| 項目 | 推奨値 | 限界値 | 備考 |
|------|--------|--------|------|
| 同時セッション数 | 10 | 30 | システムメモリ依存 |
| ウィンドウ/セッション | 5 | 20 | 管理性を考慮 |
| ペイン/ウィンドウ | 4 | 10 | 視認性を考慮 |
| メッセージ頻度 | 5/秒 | 20/秒 | バッファ考慮 |
| スクリプト同時実行 | 3 | 10 | CPU負荷考慮 |

### 監視閾値
```bash
# monitoring-config.sh
TMUX_CPU_THRESHOLD=50      # CPU使用率警告閾値
TMUX_MEM_THRESHOLD=1024    # メモリ使用量警告閾値(MB)
PANE_COUNT_WARNING=50      # ペイン数警告閾値
MESSAGE_RATE_WARNING=10    # メッセージ/秒警告閾値
```

## 3. 標準実装パターン

### パターン1: 安全なセッション作成
```bash
safe_create_session() {
    local session_name=$1
    local max_retries=3
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if tmux new-session -d -s "$session_name" 2>/dev/null; then
            echo "セッション作成成功: $session_name"
            return 0
        fi
        
        # 既存セッションの場合は再利用
        if tmux has-session -t "$session_name" 2>/dev/null; then
            echo "既存セッションを使用: $session_name"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        sleep 1
    done
    
    echo "エラー: セッション作成失敗: $session_name" >&2
    return 1
}
```

### パターン2: 排他制御付きレイアウト変更
```bash
safe_layout_change() {
    local session=$1
    local layout=$2
    local lockfile="/tmp/tmux-${session}-layout.lock"
    
    {
        flock -n 9 || {
            echo "警告: レイアウト変更が競合しています"
            return 1
        }
        
        if ! tmux select-layout -t "$session" "$layout" 2>/dev/null; then
            echo "エラー: レイアウト変更失敗"
            return 1
        fi
        
        echo "レイアウト変更完了: $session -> $layout"
    } 9>"$lockfile"
}
```

### パターン3: レート制限付きメッセージ送信
```bash
# グローバル変数
declare -A LAST_SEND_TIME
RATE_LIMIT=0.2  # 200ms = 5メッセージ/秒

rate_limited_send() {
    local target=$1
    local message=$2
    local current_time=$(date +%s.%N)
    local last_time=${LAST_SEND_TIME[$target]:-0}
    
    # レート制限チェック
    local elapsed=$(echo "$current_time - $last_time" | bc)
    if (( $(echo "$elapsed < $RATE_LIMIT" | bc -l) )); then
        local wait_time=$(echo "$RATE_LIMIT - $elapsed" | bc)
        sleep "$wait_time"
    fi
    
    # メッセージ送信
    if tmux send-keys -t "$target" "$message" C-m 2>/dev/null; then
        LAST_SEND_TIME[$target]=$(date +%s.%N)
        return 0
    else
        return 1
    fi
}
```

## 4. 自動化ツール

### tmux健全性監視デーモン
```bash
#!/bin/bash
# tmux-health-daemon.sh

INTERVAL=30
LOG_FILE="/var/log/tmux-health.log"

monitor_loop() {
    while true; do
        # セッション数チェック
        session_count=$(tmux list-sessions 2>/dev/null | wc -l)
        
        # ペイン総数チェック
        pane_count=$(tmux list-panes -a 2>/dev/null | wc -l)
        
        # CPU使用率チェック
        cpu_usage=$(ps aux | grep tmux | grep -v grep | awk '{sum+=$3} END {print sum}')
        
        # ログ記録
        echo "$(date '+%Y-%m-%d %H:%M:%S') Sessions=$session_count Panes=$pane_count CPU=$cpu_usage%" >> "$LOG_FILE"
        
        # 異常検知
        if (( pane_count > 100 )); then
            echo "警告: ペイン数が多すぎます: $pane_count" | logger -t tmux-health
        fi
        
        if (( $(echo "$cpu_usage > 50" | bc -l) )); then
            echo "警告: tmux CPU使用率が高い: $cpu_usage%" | logger -t tmux-health
        fi
        
        sleep $INTERVAL
    done
}

# デーモンとして実行
monitor_loop &
```

### 自動復旧スクリプト
```bash
#!/bin/bash
# tmux-auto-recovery.sh

recover_dead_sessions() {
    local config_file="/etc/tmux-sessions.conf"
    
    while IFS='|' read -r session_name window_count command; do
        if ! tmux has-session -t "$session_name" 2>/dev/null; then
            echo "セッション復旧中: $session_name"
            
            # セッション再作成
            tmux new-session -d -s "$session_name"
            
            # ウィンドウ復旧
            for ((i=2; i<=window_count; i++)); do
                tmux new-window -t "$session_name"
            done
            
            # 初期コマンド実行
            if [ -n "$command" ]; then
                tmux send-keys -t "$session_name:1" "$command" C-m
            fi
        fi
    done < "$config_file"
}
```

## 5. テストフレームワーク

### 負荷テスト
```bash
#!/bin/bash
# tmux-load-test.sh

run_stress_test() {
    local duration=$1
    local message_rate=$2
    
    echo "負荷テスト開始: ${duration}秒間、${message_rate}メッセージ/秒"
    
    local end_time=$(($(date +%s) + duration))
    local interval=$(echo "1 / $message_rate" | bc -l)
    
    while [ $(date +%s) -lt $end_time ]; do
        tmux send-keys -t test "stress test message" C-m 2>/dev/null || {
            echo "エラー: tmuxが応答しません"
            break
        }
        sleep "$interval"
    done
}
```

### 競合状態テスト
```bash
#!/bin/bash
# race-condition-test.sh

test_concurrent_operations() {
    echo "競合状態テスト開始"
    
    # 10個の並行プロセス
    for i in {1..10}; do
        (
            # ランダムな操作を実行
            case $((RANDOM % 4)) in
                0) tmux split-window -t test ;;
                1) tmux select-layout -t test tiled ;;
                2) tmux send-keys -t test "test $i" C-m ;;
                3) tmux select-pane -t test -t .+1 ;;
            esac
        ) &
    done
    
    wait
    echo "競合状態テスト完了"
}
```

## 6. 移行計画

### フェーズ1: 即時対応（24時間以内）
1. ✅ send-message.sh修正（完了）
2. enhanced-send-message.sh修正
3. 全開発者への周知

### フェーズ2: 短期対応（1週間以内）
1. start-system系スクリプトへのエラーハンドリング追加
2. 監視スクリプトの導入
3. ドキュメント整備

### フェーズ3: 中期対応（1ヶ月以内）
1. メッセージキューシステムの設計・実装
2. 包括的なテストスイートの構築
3. CI/CDパイプラインへの統合

### フェーズ4: 長期対応（3ヶ月以内）
1. アーキテクチャの根本的見直し
2. 分散システムへの移行検討
3. 高可用性の実現

## 7. チームへの提言

### 開発チーム向け
- コードレビューでtmuxコマンドのエラーチェックを必須項目に
- 新規スクリプトは必ずテンプレートを使用
- 並行実行を前提とした設計を心がける

### 運用チーム向け
- 日次での健全性チェック実施
- 負荷状況の定期的なレビュー
- インシデント発生時の迅速な原因究明体制

### 管理層向け
- tmux依存度を下げる長期戦略の検討
- 専任のインフラエンジニアの配置
- 定期的な技術的負債の棚卸し

## まとめ
tmux異常終了は予防可能な問題である。本ガイドラインに従うことで、システムの安定性を大幅に向上させることができる。特に重要なのは、エラーハンドリングの徹底と、負荷限界を意識した設計である。

全チームメンバーが本ガイドラインを理解し、実践することを強く推奨する。