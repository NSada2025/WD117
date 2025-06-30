# 重要スクリプト一覧 - 再起動後必須ファイル

## 🚨 最重要ファイル（必ず確保）

### 1. ワークフロー自動化コア
```bash
workflow-launcher.sh         # メイン起動スクリプト
repo-selector.py            # GitHubリポジトリ選択
tmux-session-manager.py     # tmuxセッション管理
monitor-integration.py      # claude-code-monitor連携
```

### 2. 安定化・監視システム
```bash
tmux-health-monitor.py      # auto-compact事前検知
output-management-system.py # 出力量管理・要約
progress-state-saver.py     # 進捗自動保存
realtime-status-dashboard.py # リアルタイム監視
```

### 3. 基本システムスクリプト
```bash
start-system.sh            # 5エージェントシステム起動
send-message.sh            # エージェント間通信
initialize-agents.sh       # エージェント初期化
```

## 📝 設定・ドキュメント

### システム設計書
```
workflow_automation_design.md    # ワークフロー自動化設計
auto-compact-detection-system.md # auto-compact対策設計
dev3-optimized-workflow.md       # 最適化ワークフロー
SYSTEM_RESTART_BACKUP.md        # 再起動バックアップ記録
```

### データファイル
```
recent-projects-cache.json      # 最近使用プロジェクト
token-usage-cache.json         # トークン使用量
tmux-health-history.json       # tmux健全性履歴
selected-repository.json       # 選択リポジトリ情報
```

## 🔧 実行権限設定コマンド

```bash
# 全スクリプトに実行権限付与
chmod +x *.sh *.py

# 特に重要なファイル
chmod +x workflow-launcher.sh
chmod +x repo-selector.py
chmod +x tmux-session-manager.py
chmod +x tmux-health-monitor.py
chmod +x output-management-system.py
chmod +x progress-state-saver.py
chmod +x realtime-status-dashboard.py
```

## 📂 必要ディレクトリ構造

```
multiagent-system/
├── managed-outputs/       # 出力管理用
├── output-summaries/      # 要約保存用
├── output-archives/       # アーカイブ用
├── progress-states/       # 進捗保存用
├── session-configs/       # セッション設定
├── session-states/        # セッション状態
├── tmux-backups/         # tmuxバックアップ
├── instructions/         # エージェント指示書
│   ├── ceo.md
│   ├── manager.md
│   └── developer.md
├── organized/            # 整理済みファイル
│   └── scripts/
└── tmp/                  # 一時ファイル
```

## ⚡ クイックスタートコマンド

```bash
# 1. バックアップファイルの展開（Dドライブ直下で実行）
tar -xzf multiagent-system-backup-20250630_122256.tar.gz

# 2. ディレクトリ移動
cd multiagent-system

# 3. 実行権限設定
chmod +x *.sh *.py

# 4. 必要ディレクトリ作成
mkdir -p {managed-outputs,output-summaries,output-archives,progress-states,session-configs,session-states,tmux-backups}

# 5. 健全性監視起動
python3 tmux-health-monitor.py 30 &

# 6. システムテスト
./workflow-launcher.sh help
```

---

**重要**: このファイルは `/mnt/d/CRITICAL_SCRIPTS_LIST.md` にもコピーを保存することを推奨