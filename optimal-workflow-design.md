# 最適ワークフロー設計

## 🚀 実践的な起動順序

### 1. Windows環境からWSL起動
```bash
# PowerShell
cd d:
wsl
```

### 2. GitHub CLI認証確認
```bash
gh auth status
# ✓ Logged in to github.com as NSada2025
```

### 3. 作業プロジェクト決定
```bash
# リポジトリ一覧確認
gh repo list | grep -E "WD|DN|OT"

# 例: WD108_MultiAgentSystem
# 例: DN001_TF_Analysis
```

### 4. AI Team自動起動
```bash
# 通常起動（同時起動）
./start-system.sh

# 推奨: 段階的起動（API負荷軽減）
./start-system-staggered.sh
```
**ポイント**: instructionsは起動スクリプトで自動読み込み
- 各エージェントが自動的に役割を理解
- 手動での`claude instructions/xxx.md`不要

### 5. 日常作業フロー
```bash
# CEOタブ（PowerShell Tab1）で
./send-message.sh manager "プロジェクト名: WD109_NewFeature - 機能実装開始 - 優先度: 高"
```

### 6. 並行プロジェクト対応（オプション）
```bash
# 新しいWSLタブで
tmux new -s project2
./start-ai-team.sh --session project2
```

## 📋 フロー最適化のポイント

### 自動化された要素
- **instructions読み込み**: 起動時に自動実行
- **役割理解**: 各エージェントが起動時に把握
- **通信準備**: send-message.sh即座に利用可能

### 意識不要になった要素
- instructions/ディレクトリの存在
- 各mdファイルの手動読み込み
- claudeコマンドの個別実行

### 効率化のコツ
1. **エイリアス設定**
   ```bash
   alias ai-team='cd /mnt/d/ && ./start-ai-team.sh'
   alias ai-msg='./send-message.sh'
   ```

2. **プロジェクトテンプレート**
   ```bash
   # 新規プロジェクト開始時
   ./new-project.sh WD110_ProjectName
   # → GitHubリポジトリ作成
   # → ディレクトリ作成
   # → AI Team起動
   ```

3. **ステータス確認**
   ```bash
   # claude-code-monitor併用
   claude-code-monitor
   # 全エージェントの状態を一覧
   ```

## 🎯 理想的な1日の流れ

```
09:00 PowerShell起動 → wsl
09:01 gh auth status（自動ログイン確認）
09:02 今日のプロジェクト選択
09:03 ./start-ai-team.sh（5エージェント自動起動）
09:05 CEOタブで本日のタスク指示
09:10 自動的にタスク分解・実行開始
12:00 進捗確認（必要に応じて追加指示）
15:00 別プロジェクトを並行起動
17:00 完了確認・次回への申し送り
17:30 tmux kill-session -t ai-team
```

## 💡 さらなる最適化案

### 起動スクリプト改良
```bash
#!/bin/bash
# start-ai-team.sh v2

# GitHub認証自動確認
if ! gh auth status &>/dev/null; then
    echo "GitHub CLI未認証。ログインしてください。"
    gh auth login
fi

# プロジェクト選択UI
echo "作業プロジェクトを選択:"
select PROJECT in $(ls -d /mnt/d/WD* /mnt/d/DN* 2>/dev/null); do
    cd "$PROJECT"
    break
done

# tmux起動
tmux new-session -d -s ai-team
# ... 既存の起動処理

# instructions自動読み込み（各ペインで）
tmux send-keys -t ai-team:ceo "claude instructions/ceo.md" C-m
tmux send-keys -t ai-team:manager "claude instructions/manager.md" C-m
# ...

echo "AI Team起動完了！"
echo "CEOタブで指示を開始してください。"
```

これにより、**instructionsを意識することなく**、
効率的なAI Team運用が可能になります。