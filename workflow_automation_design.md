# ユーザーワークフロー自動化システム設計書

## 📋 プロジェクト概要

### 目的
GitHub CLI → tmux → リポジトリ選択 → チーム作業の完全自動化

### ターゲットワークフロー
```
gh → tmux 5 agents → repository select → team work → Opus4 check → parallel teams
```

## 🔍 既存システム分析結果

### 現在の環境
- ✅ GitHub CLI インストール済み (`/usr/bin/gh`)
- ✅ 現在のリポジトリ: `NSada2025/multiagent-neuroscience-system`
- ✅ 5エージェントtmuxシステム動作中 (CEO + Manager + Dev1,2,3)
- ✅ エージェント間通信システム (`send-message.sh`)
- ✅ 10+ GitHubリポジトリアクセス可能

### 利用可能なリポジトリ例
1. `multiagent-neuroscience-system` - 神経科学データ解析
2. `claude-code-monitor` - トークン使用量監視システム
3. `WD114_tmux-multiagent-system` - tmuxマルチエージェント協調
4. `WD115_GitHubReviewMastery` - GitHub PRレビュー技術
5. その他研究プロジェクト

## 🎯 優先実装項目

### 1. tmuxセッション管理の自動化スクリプト
**目標**: 複数プロジェクト並行実行の効率化

**技術要件**:
- tmuxセッション一覧管理
- プロジェクト固有セッション作成
- セッション間切り替え高速化
- セッション状態保存/復元

**実装コンポーネント**:
```bash
├── tmux-session-manager.sh
├── project-session-template.sh
├── session-state-backup.sh
└── quick-session-switch.sh
```

### 2. リポジトリ選択効率化ツール
**目標**: GitHub CLIを使った直感的リポジトリ選択

**機能要件**:
- `gh repo list` 結果のフィルタリング
- プロジェクト種別による分類表示
- 最近使用したリポジトリ優先表示
- インタラクティブ選択インターフェース

**実装コンポーネント**:
```bash
├── repo-selector.py
├── repo-filter-engine.py
├── recent-projects-cache.json
└── project-categorizer.py
```

### 3. claude-code-monitor連携強化
**目標**: Opus4トークン使用量リアルタイム監視

**連携機能**:
- プロジェクト開始時の監視自動起動
- エージェント別トークン使用量追跡
- 閾値到達時の警告システム
- 使用量レポート自動生成

**実装コンポーネント**:
```bash
├── monitor-integration.py
├── token-usage-tracker.py
├── usage-alert-system.py
└── monitor-dashboard.sh
```

### 4. 複数チーム並行運用サポート
**目標**: 複数プロジェクトでの5エージェントチーム同時実行

**アーキテクチャ**:
```
Project A: tmux session "team-a" (CEO, Manager, Dev1-3)
Project B: tmux session "team-b" (CEO, Manager, Dev1-3)  
Project C: tmux session "team-c" (CEO, Manager, Dev1-3)
```

**管理機能**:
- チーム間通信分離
- リソース使用量制御
- プロジェクト進捗統合表示
- チーム負荷バランシング

### 5. プロジェクト切り替え高速化システム
**目標**: 秒単位でのプロジェクト環境切り替え

**高速化手法**:
- セッション事前準備
- 環境設定キャッシュ
- インクリメンタル状態復元
- ホットスワップ機能

## 🏗️ システムアーキテクチャ

### メインコンポーネント

```
workflow-automation/
├── main-launcher.sh              # 統合起動スクリプト
├── repo-management/
│   ├── gh-repo-selector.py       # GitHub CLI リポジトリ選択
│   ├── project-categorizer.py    # プロジェクト分類エンジン
│   └── recent-cache.json         # 最近使用プロジェクト
├── tmux-management/
│   ├── session-manager.py        # tmuxセッション管理
│   ├── multi-team-orchestrator.py # 複数チーム調整
│   └── session-templates/        # セッション設定テンプレート
├── monitor-integration/
│   ├── claude-monitor-bridge.py  # claude-code-monitor連携
│   ├── token-tracker.py         # トークン使用量追跡
│   └── usage-alerts.py          # 使用量警告システム
├── state-management/
│   ├── project-state-saver.py   # プロジェクト状態保存
│   ├── quick-restore.py         # 高速復元システム
│   └── backup-manager.py        # バックアップ管理
└── ui/
    ├── interactive-selector.py   # インタラクティブUI
    ├── dashboard.py             # 統合ダッシュボード
    └── notification-system.py   # 通知システム
```

### データフロー

```
1. [User Input] → gh repo list
2. [Filter/Select] → Project categorization
3. [Session Setup] → tmux multi-team creation
4. [Monitor Start] → claude-code-monitor activation
5. [Team Launch] → 5-agent system startup
6. [State Save] → Project state persistence
7. [Switch Ready] → Quick project switching
```

## 🚀 想定ワークフロー詳細

### シナリオ1: 新規プロジェクト開始
```bash
$ ./workflow-launcher.sh

🔍 Available Repositories:
[1] multiagent-neuroscience-system (Data Analysis)
[2] claude-code-monitor (Monitoring)
[3] WD114_tmux-multiagent-system (Infrastructure)
[4] WD115_GitHubReviewMastery (Training)

Select repository [1-4]: 1

🚀 Starting Project: multiagent-neuroscience-system
✓ Creating tmux session: neuroscience-team
✓ Launching claude-code-monitor
✓ Starting 5-agent system (CEO, Manager, Dev1-3)  
✓ Loading project state from backup
✓ Ready for development!

Active Sessions:
- neuroscience-team (5 agents)
- monitor-dashboard (token tracking)
```

### シナリオ2: 複数プロジェクト並行実行
```bash
$ ./workflow-launcher.sh --parallel

Current Active Projects:
[A] neuroscience-team (5 agents) - Token usage: 2.1M
[B] review-mastery-team (5 agents) - Token usage: 1.8M
[C] monitor-dev-team (3 agents) - Token usage: 0.9M

Launch new project? [y/N]: y

🔍 Quick Project Selection:
[1] tmux-multiagent-system (Infrastructure) 
[2] academic-website (Web Development)

Select [1-2]: 1

🚀 Starting Project: tmux-multiagent-system
✓ Creating session: tmux-infra-team
✓ Resource check: OK (4 teams max capacity)
✓ Starting 5-agent system
✓ Cross-team communication isolated

Active Sessions:
[A] neuroscience-team (5 agents)
[B] review-mastery-team (5 agents)  
[C] monitor-dev-team (3 agents)
[D] tmux-infra-team (5 agents) <- NEW
```

### シナリオ3: プロジェクト高速切り替え
```bash
$ ./quick-switch.sh neuroscience-team

🔄 Switching to: neuroscience-team
✓ Saving current state: monitor-dev-team
✓ Loading cached environment: neuroscience-team
✓ Restoring 5-agent states
✓ Reactivating claude-code-monitor
✓ Switch completed in 2.3 seconds

Current Focus: neuroscience-team
- CEO: Ready for new directives
- Manager: Coordinating data analysis pipeline
- Dev1: Working on timing correction verification
- Dev2: Optimizing MATLAB visualization  
- Dev3: Quality assurance and testing
```

## 📊 パフォーマンス要件

### 速度目標
- リポジトリ選択: < 3秒
- 新規プロジェクト起動: < 10秒
- プロジェクト切り替え: < 5秒
- 5エージェント同時起動: < 15秒

### リソース効率
- 最大同時プロジェクト: 4チーム (20エージェント)
- メモリ使用量: プロジェクト当たり < 200MB
- CPU使用率: 平常時 < 30%
- ディスク使用量: 状態保存 < 50MB/プロジェクト

## 🔧 技術実装詳細

### GitHub CLI統合
```python
# repo-selector.py の中核機能
def get_filtered_repositories(filter_type=None, limit=20):
    """GitHub CLIを使用してフィルタリングされたリポジトリ一覧を取得"""
    
    cmd = ["gh", "repo", "list", "--limit", str(limit)]
    if filter_type:
        cmd.extend(["--topic", filter_type])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    repositories = parse_repo_list(result.stdout)
    
    return categorize_repositories(repositories)

def categorize_repositories(repos):
    """リポジトリをプロジェクト種別で分類"""
    categories = {
        "analysis": [],    # データ解析プロジェクト
        "infrastructure": [], # インフラ・システム
        "research": [],    # 研究関連
        "tools": [],       # 開発ツール
        "other": []        # その他
    }
    
    for repo in repos:
        category = classify_by_name_and_description(repo)
        categories[category].append(repo)
    
    return categories
```

### tmuxセッション管理
```bash
# session-manager.py の中核機能
def create_multi_team_session(project_name, team_count=1):
    """複数チーム用tmuxセッションを作成"""
    
    session_name = f"{project_name}-team"
    
    # メインセッション作成
    tmux_cmd = f"tmux new-session -d -s {session_name}"
    run_command(tmux_cmd)
    
    # 5エージェント用ペイン作成 (2x2 + CEO)
    setup_agent_panes(session_name)
    
    # エージェント起動
    start_agents(session_name, project_name)
    
    return session_name

def setup_agent_panes(session_name):
    """5エージェント用のペイン構成を作成"""
    
    # CEOセッション（別セッション）
    tmux_cmd = f"tmux new-session -d -s {session_name}-ceo"
    run_command(tmux_cmd)
    
    # チームセッション（4分割）
    split_commands = [
        f"tmux split-window -h -t {session_name}",
        f"tmux split-window -v -t {session_name}:0.0", 
        f"tmux split-window -v -t {session_name}:0.1"
    ]
    
    for cmd in split_commands:
        run_command(cmd)
```

### claude-code-monitor連携
```python
# monitor-integration.py の中核機能
def start_monitor_for_project(project_name):
    """プロジェクト専用のclaude-code-monitor起動"""
    
    monitor_session = f"{project_name}-monitor"
    
    # モニターセッション作成
    tmux_cmd = f"tmux new-session -d -s {monitor_session}"
    run_command(tmux_cmd)
    
    # claude-code-monitorリポジトリに移動して起動
    monitor_dir = get_monitor_repository_path()
    start_cmd = f"tmux send-keys -t {monitor_session} 'cd {monitor_dir} && python3 claude_code_monitor.py --project {project_name}' C-m"
    run_command(start_cmd)
    
    return monitor_session

def track_agent_token_usage(project_name, agent_name):
    """エージェント別トークン使用量を追跡"""
    
    usage_data = {
        "project": project_name,
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "tokens_used": get_current_token_count(agent_name)
    }
    
    save_usage_data(usage_data)
    check_usage_thresholds(usage_data)
```

## ✅ 実装ロードマップ

### Phase 1: 基盤機能 (1-2日)
- [x] 既存システム分析完了
- [ ] GitHub CLI統合基盤
- [ ] tmuxセッション管理コア
- [ ] リポジトリ選択UI

### Phase 2: 統合機能 (2-3日)  
- [ ] claude-code-monitor連携
- [ ] 複数チーム並行実行
- [ ] 状態保存/復元システム
- [ ] インタラクティブダッシュボード

### Phase 3: 最適化 (1-2日)
- [ ] パフォーマンス最適化
- [ ] エラーハンドリング強化
- [ ] ユーザビリティ向上
- [ ] 統合テスト実施

## 📈 成功指標

### 定量的指標
- プロジェクト起動時間: 現在手動15分 → 自動10秒
- 切り替え時間: 現在手動5分 → 自動5秒  
- 同時プロジェクト数: 現在1個 → 自動4個
- エラー率: < 1% (自動復旧含む)

### 定性的指標
- ユーザー体験の劇的改善
- マルチプロジェクト作業効率向上
- リソース使用量の最適化
- 運用保守性の向上

---

**🎯 Next Steps**: Phase 1の基盤機能実装から開始
**👥 Responsible**: dev3 (品質管理・テスト・運営管理)
**⏰ Deadline**: 緊急度高のため即座に着手