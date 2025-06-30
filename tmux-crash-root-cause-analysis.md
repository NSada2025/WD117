# tmux異常終了 根本原因分析レポート

## エグゼクティブサマリー
dev1の発見とdev2のログ分析により、tmux異常終了の根本原因が特定されました。
主要因は`send-message.sh`および`enhanced-send-message.sh`のエラーハンドリング不足です。

## 検証された問題箇所

### 1. send-message.sh のエラーチェック欠如（74行目）

```bash
# 問題のコード
tmux send-keys -t $SESSION:$PANE "$MESSAGE" C-m
echo "メッセージを $AGENT_NAME ($SESSION ペイン $PANE) に送信しました: $MESSAGE"
```

**問題点**:
- `tmux send-keys`の実行結果をチェックしていない
- ペインが存在しない場合でも「送信しました」と表示
- エラーが発生してもスクリプトは正常終了（exit code 0）

**クラッシュへの影響**:
- 存在しないペインへのメッセージ送信を繰り返すことで、tmuxサーバーに負荷
- エラーの蓄積により、メモリリークやファイルディスクリプタの枯渇を引き起こす可能性

### 2. enhanced-send-message.sh の未定義関数呼び出し（169行目）

```bash
# 問題のコード（169行目）
rotate_logs  # この時点で関数が未定義

# 関数定義は211行目以降
rotate_logs() {
    # ...
}
```

**問題点**:
- 関数定義前に呼び出しているため、初回実行時にエラー
- `monitor_system_performance`（172行目）も同様の問題
- bashの`set -e`が設定されていれば即座にスクリプト終了

**クラッシュへの影響**:
- スクリプトの異常終了により、tmuxセッション内で予期しない状態が発生
- エラー時のクリーンアップ処理が実行されない

### 3. ペイン存在確認の欠如

**両スクリプト共通の問題**:
```bash
# 現状：セッション確認のみ
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "エラー: セッション '$SESSION' が見つかりません"
    exit 1
fi

# 欠如：ペイン確認がない
# 正しくは以下のような確認が必要
if ! tmux list-panes -t "$SESSION:$PANE" &>/dev/null; then
    echo "エラー: ペイン '$PANE' が見つかりません"
    exit 1
fi
```

## 3回連続クラッシュパターンとの関連性

### 再現シナリオ
1. **初回実行**: enhanced-send-message.shが未定義関数エラーで異常終了
2. **フォールバック**: send-message.shに切り替え
3. **ペインエラー**: 存在しないペインへの送信を繰り返す
4. **リソース枯渇**: エラーの蓄積によりtmuxサーバーがクラッシュ

### ログ分析による裏付け
```bash
# 典型的なエラーパターン
./enhanced-send-message.sh: line 169: rotate_logs: command not found
can't find pane %3
failed to connect to server: Connection refused
```

## 推奨される修正

### 1. 即座に実施すべき修正

#### send-message.sh
```bash
# 74行目を以下に修正
if tmux send-keys -t "$SESSION:$PANE" "$MESSAGE" C-m 2>/dev/null; then
    echo "メッセージを $AGENT_NAME ($SESSION ペイン $PANE) に送信しました: $MESSAGE"
else
    echo "エラー: メッセージ送信に失敗しました" >&2
    exit 1
fi
```

#### enhanced-send-message.sh
```bash
# 関数定義を使用前に移動
# または、メイン処理を関数化して最後に実行
main() {
    # 現在のメイン処理
}

# 全ての関数定義後に
main "$@"
```

### 2. ペイン存在確認の追加
```bash
# 両スクリプトに追加
check_pane_exists() {
    local session=$1
    local pane=$2
    
    if ! tmux list-panes -t "$session" -F "#{pane_index}" | grep -q "^${pane}$"; then
        echo "エラー: ペイン $pane がセッション $session に存在しません" >&2
        echo "利用可能なペイン:"
        tmux list-panes -t "$session" -F "  #{pane_index}: #{pane_current_command}"
        return 1
    fi
    return 0
}
```

## 結論

tmuxの3回連続クラッシュは、メッセージ送信スクリプトの以下の問題の組み合わせによって発生：

1. **エラーハンドリング不足**: 失敗を検知できずに繰り返し実行
2. **関数定義順序の誤り**: スクリプトが異常終了
3. **ペイン存在確認の欠如**: 存在しないペインへのアクセス

これらの修正により、tmuxの安定性が大幅に向上することが期待されます。