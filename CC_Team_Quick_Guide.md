# Claude Code AI Team クイックガイド

## 🎯 4つの基本パターンだけ覚えればOK

---

## 1️⃣ 朝の起動

```bash
# PowerShell
cd d:
wsl

# GitHub確認
gh auth status

# チーム起動（推奨: 段階起動）
./start-system-staggered.sh

# 作業開始
./send-message.sh manager "本日の作業を開始します"
```

---

## 2️⃣ 休憩後の再開

### ☕ 短時間（1-2時間）
```bash
./send-message.sh manager "進捗確認"
```

### 🍽️ 長時間（3時間以上）
```bash
# 健康チェック
./morning-check.sh

# または個別確認
for a in ceo manager dev1 dev2 dev3; do
  ./send-message.sh $a "状態確認"
done
```

---

## 3️⃣ 終業時の締め

```bash
# 進捗要約を依頼
./send-message.sh manager "本日の進捗を要約してください"

# 進捗保存
./save-progress.sh

# 適切な終了（セッション維持でもOK）
# 完全終了する場合のみ：
tmux kill-session -t ceo
tmux kill-session -t team
```

---

## 4️⃣ 困った時

### 🚨 症状別クイック対処

| 症状 | 対処法 |
|------|--------|
| **API Error頻発** | `./send-message-with-retry.sh [対象] "メッセージ"` |
| **画面暴走（dev3）** | `./send-message.sh dev3 "出力を最小限にして状態報告"` |
| **反応なし** | 該当エージェントのみ再起動 → `tmux send-keys -t [位置] C-c` |
| **文脈喪失** | `./send-message.sh [対象] "役割を確認してください"` |

### それでもダメなら
```bash
# 完全再起動（最終手段）
tmux kill-server
./start-system-staggered.sh
```

---

**以上！これだけで日常運用は完璧です。**

詳細情報が必要な場合は → [CC_Team_Construction_v2.md](./CC_Team_Construction_v2.md)