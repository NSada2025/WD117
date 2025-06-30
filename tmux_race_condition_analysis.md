# tmux競合状態詳細分析

## 概要
マルチエージェントシステムにおけるtmux使用時の競合状態を詳細に分析し、再現可能なシナリオと対策を提示する。

## 1. 競合状態の分類

### タイプA: リソース競合
**定義**: 複数のプロセスが同一リソースに同時アクセス

#### 具体例1: ペイン番号の不整合
```bash
# プロセス1: レイアウト変更中
tmux split-window -t team:dev1 -h  # ペイン番号が変更される

# プロセス2: 同時にメッセージ送信
tmux send-keys -t team:dev1.2 "message"  # 古いペイン番号を使用
# 結果: 意図しないペインへメッセージ送信または失敗
```

#### 具体例2: セッション状態の不整合
```bash
# プロセス1: セッション確認
if tmux has-session -t multiagent; then  # この時点で存在

# プロセス2: セッション削除
tmux kill-session -t multiagent

# プロセス1: 続き
    tmux send-keys -t multiagent "message"  # セッション不在でエラー
fi
```

### タイプB: タイミング競合
**定義**: 処理順序に依存する操作の競合

#### 具体例1: 初期化競合
```bash
# start-system-auto.sh の問題
# ほぼ同時に4つのClaudeインスタンスが起動
for pane in 0 1 2 3; do
    tmux send-keys -t team:dev1.$pane "claude-code --profile dev$pane" C-m &
done
# 結果: API制限、メモリ不足、起動失敗の可能性
```

#### 具体例2: メッセージ順序の逆転
```bash
# 3つのdevエージェントが完了報告
dev1: ./send-message.sh manager "タスク1完了" &  # 時刻T
dev2: ./send-message.sh manager "タスク2完了" &  # 時刻T+1ms
dev3: ./send-message.sh manager "タスク3完了" &  # 時刻T+2ms

# 実際の到着順序: 予測不可能（タスク3→タスク1→タスク2など）
```

### タイプC: デッドロック
**定義**: 相互に待機して進行不能

#### 具体例1: レイアウト変更のデッドロック
```bash
# スクリプトA
flock -x /tmp/tmux-layout.lock
tmux select-pane -t team:0
# スクリプトBの完了を待つ処理

# スクリプトB
flock -x /tmp/tmux-pane.lock
tmux select-layout -t team tiled
# スクリプトAの完了を待つ処理
```

## 2. 実際の障害シナリオ

### シナリオ1: カスケード障害
```bash
1. dev1がメッセージ送信（エラーチェックなし）
2. tmuxサーバーが高負荷で応答遅延
3. dev2, dev3も同時にメッセージ送信
4. tmuxバッファオーバーフロー
5. tmuxサーバークラッシュ
6. 全エージェント切断
```

### シナリオ2: サイレント障害
```bash
1. manager-layout-update.sh実行
2. ペイン番号変更
3. 既存のsend-message処理が古いペイン番号使用
4. メッセージが違うペインに送信される
5. エラーチェックなしのため検出されない
6. システムは正常に見えるが、通信が破綻
```

## 3. 再現テストコード

### 競合状態再現スクリプト
```bash
#!/bin/bash
# race-condition-test.sh

# テスト1: ペイン番号競合
test_pane_race() {
    tmux new-session -d -s race-test
    tmux split-window -t race-test -h
    
    # 並行してレイアウト変更とメッセージ送信
    for i in {1..100}; do
        tmux select-layout -t race-test tiled &
        tmux send-keys -t race-test.1 "test $i" C-m &
    done
    
    wait
    echo "テスト1完了: ペイン番号競合"
}

# テスト2: 高負荷メッセージング
test_message_flood() {
    # 1000メッセージを10プロセスから同時送信
    for proc in {1..10}; do
        (
            for msg in {1..100}; do
                tmux send-keys -t race-test "Process $proc Message $msg" C-m
            done
        ) &
    done
    
    wait
    echo "テスト2完了: メッセージフラッド"
}

# テスト3: セッション操作競合
test_session_race() {
    for i in {1..50}; do
        tmux new-session -d -s "temp-$i" &
        tmux kill-session -t "temp-$i" &
    done
    
    wait
    echo "テスト3完了: セッション操作競合"
}
```

## 4. 検出方法

### 監視スクリプト
```bash
#!/bin/bash
# tmux-race-detector.sh

detect_pane_inconsistency() {
    local session=$1
    local expected_panes=$2
    
    actual_panes=$(tmux list-panes -t $session 2>/dev/null | wc -l)
    
    if [[ $actual_panes -ne $expected_panes ]]; then
        echo "警告: ペイン数不整合 - 期待: $expected_panes, 実際: $actual_panes"
        return 1
    fi
    return 0
}

detect_message_order() {
    # タイムスタンプ付きメッセージログから順序逆転を検出
    grep "タスク.*完了" message.log | \
    awk '{print $1, $NF}' | \
    sort -k2 -n | \
    awk 'NR>1 && $2<prev {print "順序逆転検出:", prev_line, "→", $0} {prev=$2; prev_line=$0}'
}

monitor_tmux_load() {
    while true; do
        sessions=$(tmux list-sessions 2>/dev/null | wc -l)
        panes=$(tmux list-panes -a 2>/dev/null | wc -l)
        cpu=$(ps aux | grep tmux | grep -v grep | awk '{sum+=$3} END {print sum}')
        
        echo "$(date): Sessions=$sessions, Panes=$panes, CPU=$cpu%"
        
        # 閾値チェック
        if (( $(echo "$cpu > 80" | bc -l) )); then
            echo "警告: tmux CPU使用率が高い: $cpu%"
        fi
        
        sleep 5
    done
}
```

## 5. 対策実装

### ミューテックスを使用した排他制御
```bash
#!/bin/bash
# safe-tmux-operation.sh

LOCK_DIR="/var/lock/tmux-operations"
mkdir -p "$LOCK_DIR"

safe_layout_change() {
    local session=$1
    local layout=$2
    local lock_file="$LOCK_DIR/${session}-layout.lock"
    
    exec 200>"$lock_file"
    
    if flock -n 200; then
        tmux select-layout -t "$session" "$layout"
        flock -u 200
    else
        echo "警告: レイアウト変更が競合しています。スキップします。"
        return 1
    fi
}

safe_send_message() {
    local target=$1
    local message=$2
    local lock_file="$LOCK_DIR/${target//:/}-send.lock"
    
    exec 201>"$lock_file"
    
    # 短時間のロック取得を試行
    if flock -w 1 201; then
        if tmux send-keys -t "$target" "$message" C-m 2>/dev/null; then
            echo "メッセージ送信成功: $target"
        else
            echo "エラー: メッセージ送信失敗: $target" >&2
            return 1
        fi
        flock -u 201
    else
        echo "警告: メッセージ送信がタイムアウトしました: $target"
        return 1
    fi
}
```

### セマフォを使用した同時実行制限
```bash
#!/bin/bash
# semaphore-tmux.sh

MAX_CONCURRENT=3
SEMAPHORE="/tmp/tmux-semaphore"

# セマフォ初期化
init_semaphore() {
    rm -f "$SEMAPHORE"
    mkfifo "$SEMAPHORE"
    exec 3<>"$SEMAPHORE"
    
    # トークン発行
    for i in $(seq $MAX_CONCURRENT); do
        echo "$i" >&3
    done
}

acquire_token() {
    local token
    read -u 3 token
    echo "$token"
}

release_token() {
    local token=$1
    echo "$token" >&3
}

# 使用例
run_with_limit() {
    local token=$(acquire_token)
    
    # tmux操作実行
    tmux send-keys -t team "operation"
    
    release_token "$token"
}
```

## 6. 推奨アーキテクチャ

### メッセージキューベースの設計
```
[Agent] → [Message Queue] → [Dispatcher] → [tmux]
                ↑                 ↓
            [Error Handler] ← [Monitor]
```

### 実装例
```bash
#!/bin/bash
# message-queue-system.sh

QUEUE_DIR="/tmp/tmux-message-queue"
mkdir -p "$QUEUE_DIR"

# メッセージをキューに追加
enqueue_message() {
    local target=$1
    local message=$2
    local timestamp=$(date +%s%N)
    local msg_file="$QUEUE_DIR/${timestamp}-${target//:/}"
    
    echo "$message" > "$msg_file"
}

# ディスパッチャー（単一プロセス）
message_dispatcher() {
    while true; do
        for msg_file in "$QUEUE_DIR"/*; do
            [[ -f "$msg_file" ]] || continue
            
            # ファイル名からターゲット抽出
            basename=$(basename "$msg_file")
            target=${basename#*-}
            target=${target//_/:}
            
            # メッセージ送信
            if message=$(cat "$msg_file" 2>/dev/null); then
                if tmux send-keys -t "$target" "$message" C-m 2>/dev/null; then
                    rm -f "$msg_file"
                    echo "送信成功: $target <- $message"
                else
                    # エラー時は再試行のため残す
                    echo "送信失敗: $target <- $message"
                fi
            fi
            
            # レート制限
            sleep 0.1
        done
        
        sleep 0.5
    done
}
```

## 結論

tmuxの競合状態は、エラーハンドリングの欠如と組み合わさることで、システム全体の信頼性を著しく低下させる。適切な排他制御、エラーハンドリング、アーキテクチャの見直しが必要である。