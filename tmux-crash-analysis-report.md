# tmux異常終了原因分析レポート

## 1. 破壊的コマンド使用箇所の特定

### 1.1 kill-session使用箇所
以下のファイルで `tmux kill-session` が使用されています：

1. **start-system-auto.sh** (9-10行目)
   ```bash
   tmux kill-session -t ceo 2>/dev/null
   tmux kill-session -t team 2>/dev/null
   ```

2. **start-system-staggered.sh** (10-11行目)
   ```bash
   tmux kill-session -t ceo 2>/dev/null
   tmux kill-session -t team 2>/dev/null
   ```

3. **start-system.sh** (6-7行目)
   ```bash
   tmux kill-session -t ceo 2>/dev/null
   tmux kill-session -t team 2>/dev/null
   ```

4. **start-system-secure.sh** (6-7行目)
   ```bash
   tmux kill-session -t ceo 2>/dev/null
   tmux kill-session -t team 2>/dev/null
   ```

5. **integration_test_environment.sh** (44-46, 183-184行目)
   ```bash
   tmux kill-session -t "$MOCK_SESSION" 2>/dev/null || true
   tmux kill-session -t "ceo" 2>/dev/null || true
   tmux kill-session -t "team" 2>/dev/null || true
   ```

### 1.2 kill-pane使用箇所
1. **setup-manager-grid-layout.sh** (44行目)
   ```bash
   tmux kill-pane -t "$SESSION_NAME:$WINDOW_NAME.$i"
   ```

### 1.3 kill-server言及箇所（実行はされていない）
- start-system-auto.sh (111行目) - ヘルプテキストのみ
- start-system-secure.sh (69行目) - ヘルプテキストのみ
- start-system.sh (69行目) - ヘルプテキストのみ

## 2. 問題の分析

### 2.1 主な問題点
1. **無差別なセッション破棄**: 起動時に既存セッションを無条件で破棄
2. **エラーハンドリング不足**: kill-sessionの失敗を無視（2>/dev/null）
3. **競合状態の可能性**: 複数のスクリプトが同時実行された場合の競合

### 2.2 tmux異常終了の推定原因
1. **セッション破棄の連鎖反応**: アクティブなセッションを強制終了することで、関連プロセスが異常終了
2. **リソース競合**: 複数のkill-sessionが同時実行される可能性
3. **tmuxサーバーへの過負荷**: 短時間での大量のセッション操作

## 3. 安全な代替案

### 3.1 セッション存在確認の実装
```bash
# 破壊的な方法（現在）
tmux kill-session -t ceo 2>/dev/null

# 安全な方法（推奨）
if tmux has-session -t ceo 2>/dev/null; then
    echo "既存のCEOセッションを検出。再利用または安全な終了を行います。"
    # オプション1: 既存セッションに接続
    # tmux attach-session -t ceo
    
    # オプション2: 安全な終了シーケンス
    tmux send-keys -t ceo C-c C-m  # 実行中のコマンドを中断
    sleep 1
    tmux send-keys -t ceo "exit" C-m  # セッションを正常終了
    sleep 1
    
    # それでも残っている場合のみkill
    if tmux has-session -t ceo 2>/dev/null; then
        tmux kill-session -t ceo
    fi
fi
```

### 3.2 セッション再利用パターン
```bash
# セッションの再利用を優先
SESSION_NAME="ceo"
if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    # セッションが存在しない場合のみ新規作成
    tmux new-session -d -s "$SESSION_NAME"
else
    echo "既存の$SESSION_NAMEセッションを再利用します"
fi
```

### 3.3 グレースフルシャットダウン
```bash
#!/bin/bash
# graceful-shutdown.sh - 安全なセッション終了スクリプト

graceful_kill_session() {
    local session_name=$1
    
    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo "セッション '$session_name' の安全な終了を開始..."
        
        # 1. 実行中のコマンドを中断
        tmux send-keys -t "$session_name" C-c
        sleep 0.5
        
        # 2. exitコマンドを送信
        tmux send-keys -t "$session_name" "exit" C-m
        sleep 1
        
        # 3. まだ存在する場合は強制終了
        if tmux has-session -t "$session_name" 2>/dev/null; then
            echo "警告: 通常の終了に失敗。強制終了します。"
            tmux kill-session -t "$session_name"
        fi
    fi
}
```

## 4. 実装優先順位

1. **緊急度：高** - すべての起動スクリプトのkill-session部分を安全な代替案に置換
2. **緊急度：中** - セッション管理用のユーティリティ関数を作成
3. **緊急度：低** - 既存セッションの再利用オプションを追加

## 5. 次のステップ

1. 安全なセッション管理関数の実装
2. 各起動スクリプトの修正
3. テスト環境での動作確認
4. 本番環境への段階的適用