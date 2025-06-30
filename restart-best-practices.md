# 休憩後再開のベストプラクティス

## 🎯 基本原則

1. **tmuxの永続性を活用** - セッションは生きている
2. **段階的な確認** - 軽い ping から始める
3. **dev3への特別配慮** - auto-compact リスクが最も高い

## 📊 統計的な傾向

### 時間経過とリスクの関係
```
1時間   : リスク低（そのまま継続可能）
2-3時間 : リスク中（軽い確認推奨）
4時間以上: リスク高（全体確認必須）
翌日    : リスク最高（ウォームアップ必須）
```

### エージェント別の注意度
```
CEO     : ★☆☆☆☆（最も安定）
Manager : ★★☆☆☆（比較的安定）
Dev1    : ★★☆☆☆（安定）
Dev2    : ★★★☆☆（中程度）
Dev3    : ★★★★★（要注意！）
```

## 🚀 クイックコマンド集

### エイリアス設定（.bashrc）
```bash
# 休憩後の再開用エイリアス
alias ai-check='./morning-check.sh'
alias ai-ping='for a in ceo manager dev1 dev2 dev3; do ./send-message.sh $a "ping"; done'
alias ai-resume='./send-message.sh manager "作業を再開します"'
alias ai-dev3-check='./send-message.sh dev3 "最小出力で状態報告"'
```

### ワンライナー健康診断
```bash
# 全エージェントの生存確認（5秒タイムアウト）
for a in ceo manager dev1 dev2 dev3; do echo -n "$a: "; timeout 5 ./send-message.sh $a "生存確認" && echo "OK" || echo "NG"; done
```

## 💡 プロのコツ

### 1. 予防的アプローチ
```bash
# 長時間作業前に状態保存
./save-progress.sh

# 2時間タイマーセット（リマインダー）
echo "AI Team 健康チェックの時間です" | at now + 2 hours
```

### 2. dev3特別ケア
```bash
# dev3のみ定期的にリフレッシュ
*/30 * * * * ./send-message.sh dev3 "現在のメモリ使用状況を1行で報告"
```

### 3. 朝のルーティン自動化
```bash
# crontab設定（平日9時）
0 9 * * 1-5 /mnt/d/multiagent-system/morning-check.sh | mail -s "AI Team Morning Report" user@example.com
```

## 🔍 トラブルの早期発見

### 危険信号
- レスポンス時間が通常の3倍以上
- "context too long" エラーの頻発
- 同じ質問に対して異なる回答
- タスクの進捗が不明確

### 対処法の優先順位
1. 個別エージェントの再起動を試す
2. 問題のあるエージェントのみ instructions 再読み込み
3. それでもダメなら完全再起動

## 📈 効率化の実績

実際の運用データ:
- 軽い確認で済むケース: 70%
- 個別再起動で解決: 25%
- 完全再起動が必要: 5%

この手順により、無駄な再起動を避け、
効率的な作業再開が可能になります。