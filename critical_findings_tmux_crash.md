# 緊急：tmux異常終了の重大な発見事項

## 最重要発見事項

### 1. send-message.sh - エラーチェック完全欠如
**ファイル**: send-message.sh  
**行番号**: 74行目  
**問題のコード**:
```bash
tmux send-keys -t $SESSION:$PANE "$MESSAGE" C-m
echo "メッセージを送信しました: $SESSION:$PANE"
```

**重大性**: ★★★★★（最重要）  
**詳細**: tmux send-keysコマンドが失敗してもエラーとして検出されず、常に「送信成功」と表示される。

### 2. enhanced-send-message.sh - 未定義関数呼び出し
**ファイル**: enhanced-send-message.sh  
**行番号**: 169行目  
**問題のコード**:
```bash
rotate_logs
```

**重大性**: ★★★★☆（重要）  
**詳細**: rotate_logs関数が定義されていないため、実行時エラーが発生。

### 3. システム全体の構造的欠陥

#### ペイン存在確認の欠如
すべてのメッセージングスクリプトで、セッション確認は行うがペインの存在確認が行われていない。

#### tmuxプロセス健全性チェックの欠如
tmuxデーモン自体の状態確認が一切行われていない。

## 緊急修正が必要なコード

### 修正1: send-message.sh（74行目付近）
```bash
# 現在のコード（問題あり）
tmux send-keys -t $SESSION:$PANE "$MESSAGE" C-m
echo "メッセージを送信しました: $SESSION:$PANE"

# 修正後のコード
if ! tmux send-keys -t $SESSION:$PANE "$MESSAGE" C-m 2>/dev/null; then
    echo "エラー: メッセージ送信に失敗しました: $SESSION:$PANE" >&2
    exit 1
fi
echo "メッセージを送信しました: $SESSION:$PANE"
```

### 修正2: ペイン存在確認の追加（66行目付近）
```bash
# セッション確認後に追加
if ! tmux list-panes -t $SESSION 2>/dev/null | grep -q "^$PANE:"; then
    echo "エラー: ペイン $SESSION:$PANE が存在しません" >&2
    exit 1
fi
```

## 依存関係と影響範囲

```
影響を受けるスクリプト:
├── send-message.sh （中核）
│   ├── send-message-with-retry.sh
│   ├── reply-to-manager.sh
│   ├── initialize-agents.sh
│   └── start-system-auto.sh
└── enhanced-send-message.sh （独立系統）
    └── test_enhanced_send_message.sh
```

## 今すぐ実施すべきアクション

1. **send-message.sh の緊急修正**
   - tmux send-keysのエラーチェック追加
   - ペイン存在確認の追加

2. **enhanced-send-message.sh の修正**
   - rotate_logs関数の定義追加または呼び出し削除

3. **全システムの再テスト**
   - 修正後の動作確認
   - エラーケースのテスト追加

## 結論

現在のシステムは、tmuxコマンドの失敗を一切検出できない状態にあり、
これがtmux異常終了の検出を困難にしている主要因である。
即座の修正が必要。