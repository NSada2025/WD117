# 休憩後の再開ガイドライン

## 🔄 状況別の最適な再開手順

### ☕ 軽い休憩後（1-2時間）

**状況**: tmuxセッション維持、文脈も新鮮
```bash
# 1. セッション確認
tmux ls

# 2. CEOタブに接続
./connect-tab1.sh

# 3. 現状確認のみ
./send-message.sh manager "現在の進捗を報告してください"
```

**ポイント**:
- instructionsは不要（まだ記憶に新しい）
- 軽い確認で作業継続可能
- auto-compactの心配は少ない

---

### 🍽️ 長い休憩後（3時間以上）

**状況**: tmuxセッション維持、文脈が薄れ始め、auto-compact可能性あり

```bash
# 1. 全セッション健全性確認
tmux list-panes -a -F "#{session_name}:#{window_index}.#{pane_index} #{pane_current_command}"

# 2. 各エージェントに軽い ping
./send-message.sh ceo "状態確認: 応答してください"
./send-message.sh manager "状態確認: 現在のタスク状況は？"
./send-message.sh dev1 "状態確認: 作業中ですか？"
./send-message.sh dev2 "状態確認: 作業中ですか？"
./send-message.sh dev3 "状態確認: 作業中ですか？"

# 3. 応答遅延やエラーがあれば
# 該当エージェントのみ再起動を検討
```

**auto-compact対策**:
```bash
# dev3が特に心配な場合
./send-message.sh dev3 "出力を最小限にして現状を報告してください"
```

---

### 🌅 翌日再開

**状況**: 長時間経過、文脈リセット必要、auto-compact確実

```bash
# 1. システム状態の完全確認
echo "=== AI Team 健康診断 ==="
tmux ls
df -h /mnt/d/  # ディスク容量確認
free -h        # メモリ状況確認

# 2. 前日の作業ログ確認
ls -la logs/
tail -20 logs/send-message.log

# 3. 軽いウォームアップ
./send-message.sh ceo "おはようございます。昨日の作業内容を簡潔に要約してください"

# 4. 必要に応じてinstructions再確認
# （新しいプロジェクトの場合）
for agent in ceo manager dev1 dev2 dev3; do
    echo "=== $agent instructions確認 ==="
    ./send-message.sh $agent "あなたの役割を簡潔に説明してください"
done

# 5. 本格始動
./send-message.sh manager "本日の作業を開始します。優先タスクを確認してください"
```

---

## 📊 再開チェックリスト

### 🟢 問題なく再開できるサイン
- [ ] 全エージェントが5秒以内に応答
- [ ] エラーメッセージなし
- [ ] 作業内容を正確に把握している

### 🟡 注意が必要なサイン
- [ ] 一部エージェントの応答遅延（10秒以上）
- [ ] "context too long"エラー
- [ ] 作業内容の認識にズレ

### 🔴 再起動推奨のサイン
- [ ] 複数エージェントが無応答
- [ ] API errorの頻発
- [ ] tmuxペインがフリーズ

---

## 🛠️ トラブルシューティング

### エージェント個別再起動
```bash
# 特定エージェントのみ再起動（例: dev3）
tmux send-keys -t team:0.3 C-c  # 現在のプロセス終了
tmux send-keys -t team:0.3 "claude instructions/developer.md" C-m
```

### 完全再起動が必要な場合
```bash
# 1. 現在の状態を保存
./save-current-state.sh

# 2. セッション終了
tmux kill-session -t ceo
tmux kill-session -t team

# 3. 段階的再起動
./start-system-staggered.sh
```

---

## 💡 実用的なヒント

### 朝のルーティン化
```bash
# morning-check.sh として保存
#!/bin/bash
echo "☀️ Good morning! AI Team健康チェック開始..."
tmux ls
echo ""
echo "📋 昨日の最終ログ:"
tail -5 logs/send-message.log
echo ""
echo "🔄 エージェント応答確認:"
./send-message.sh manager "おはようございます。準備はできていますか？"
```

### 昼休み後の軽い確認
```bash
alias lunch-back='./send-message.sh manager "午後の作業を再開します"'
```

### 長期プロジェクトでの定期保存
```bash
# 2時間ごとに自動実行（crontab）
0 */2 * * * /mnt/d/multiagent-system/save-progress.sh
```

---

## 📝 まとめ

**基本原則**:
1. **短時間なら軽い確認**で十分
2. **長時間なら健康診断**から開始
3. **エラーが出たら個別対応**を優先
4. **完全再起動は最終手段**

**最重要**: dev3のauto-compact状態を常に意識する

この手順により、効率的で安定した作業再開が可能になります。