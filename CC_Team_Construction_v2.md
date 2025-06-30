# Claude Code AI Team 実践ガイド v2.0

## 🚀 クイックスタート（4つの基本パターン）

<table style="background: #f0f8ff; border: 2px solid #4169e1; border-radius: 10px; padding: 20px; margin-bottom: 30px;">
<tr>
<td>

### 1️⃣ 朝の起動
```bash
cd d: && wsl
gh auth status
./start-system-staggered.sh
./send-message.sh manager "本日開始"
```

### 2️⃣ 休憩後の再開
```bash
# 短時間（☕）
./send-message.sh manager "進捗確認"

# 長時間（🍽️）
./morning-check.sh
```

</td>
<td>

### 3️⃣ 終業時の締め
```bash
./send-message.sh manager "進捗要約"
./save-progress.sh
# セッション維持OK
```

### 4️⃣ 困った時
| 症状 | 対処 |
|------|------|
| API Error | `./send-message-with-retry.sh` |
| 画面暴走 | dev3に出力抑制指示 |
| 反応なし | 個別再起動 |

</td>
</tr>
</table>

**詳細が必要な場合は以下を参照 ↓**

---

## 🏗️ システム基盤（変更不可）

### コア構成
- **5エージェント体制**: CEO + Manager + Dev1-3
- **tmux構造**: `ceo`セッション（単独） + `team`セッション（4分割）
- **通信方式**: `send-message.sh`による統一的メッセージング
- **基本原則**:
  - CEO: 委任専念（直接作業禁止）
  - Manager: 自動判断・タスク分解
  - Developer: 完了報告必須

1. **起動ディレクトリ**: `/mnt/d/` 推奨（全プロジェクトアクセス）
2. **GitHubワークフロー**: gh CLI連携、リポジトリ管理
3. **プロジェクト管理**: 複数プロジェクトの切り替え手法
4. **auto-compact対策**: 出力抑制、要約機能、事前保存
5. **スマホ操作準備**: Termux/Blink Shell対応

---

## 📂 環境設定例（推奨構成）

### 🗂️ プロジェクト管理体系

**作業ディレクトリ構成**
```
/mnt/d/                    # Dドライブ直下を基点
├── multiagent-system/     # AIチームシステム
├── WD001_ProjectName/     # 開発プロジェクト
├── DN001_ExperimentName/  # データ分析プロジェクト
└── OT001_OtherProject/    # その他プロジェクト
```

**命名規則（WD108準拠）**
- **WD**: Work Development（開発系）
- **DN**: Data aNalysis（分析系）
- **OT**: OTher（その他）
- 番号: 001-999（連番管理）

### 🔄 GitHubとの連動
```bash
# プロジェクトコードとリポジトリ名を一致
gh repo create WD108_MultiAgentSystem
gh repo create DN001_TF_Analysis

# 作業開始時
cd /mnt/d/WD108_MultiAgentSystem
./start-system.sh
```

**メリット**
- 全プロジェクトへの統一的アクセス
- コード体系による整理された管理
- GitHubリポジトリとの1:1対応

---

## 🚀 詳細ワークフロー（参考情報）

<details>
<summary>🔽 起動オプションと詳細説明（クリックで展開）</summary>

<table>
<tr>
<td width="50%">

### 通常起動 vs 段階起動
```bash
# 通常（同時起動）
./start-system.sh

# 推奨（API負荷軽減）
./start-system-staggered.sh
```

### 2セッション構成
- `ceo`: CEO単独画面
- `team`: 4分割(Manager, Dev1-3)

### PowerShell 2タブ接続
```bash
./connect-tab1.sh  # CEO
./connect-tab2.sh  # Team
```

</td>
<td width="50%">

### 起動時の内部処理

1. tmuxセッション作成
2. instructions自動読み込み
3. 各エージェントが役割理解
4. send-message.sh準備完了

staggered起動の場合:
- CEO → 5秒待機
- Manager → 4秒待機
- Dev1 → 3秒待機
- Dev2 → 3秒待機
- Dev3 → 最後に起動

</td>
</tr>
</table>

</details>

---

## 📋 補足情報

<details>
<summary>🔽 プロジェクト管理・日常運用の詳細（クリックで展開）</summary>

### プロジェクト切替
```bash
gh repo list
cd /mnt/d/WD109_ProjectName
./send-message.sh manager "新プロジェクト: [名前]"
```

### よくある場面

**「dev2がもう解析終わってる！」**
Managerタブを見ると、dev2からの完了報告。
思ったより早い。dev1の設計が的確だったようだ。

**「あれ、dev3の画面が...」**
激しく上下動するdev3の画面。auto-compactの兆候。
大量のテスト出力が原因だ。

**昼休みの確認（将来）**
スマホでTermux起動。簡単なコマンドで進捗確認。

</details>

---

## 🔧 トラブルシューティング（詳細）

<details>
<summary>🔽 トラブル対処の詳細情報（クリックで展開）</summary>

### auto-compact対策
- 症状: dev3画面の激動
- 原因: 品質管理役の大量出力
- 対策: 出力抑制指示、自動要約機能

### APIエラー対策
- 段階的起動で負荷分散
- 自動リトライ機能使用
- エラー監視強化

### アクセス権限問題
- Dドライブ直下運用で解決
- 全プロジェクトへのアクセス可能

</details>

---

## 🔄 休憩後の再開手順（詳細）

<details>
<summary>🔽 時間別の詳細手順（クリックで展開）</summary>

### 時間経過とリスク
- 1時間: リスク低（そのまま継続可能）
- 2-3時間: リスク中（軽い確認推奨）
- 4時間以上: リスク高（全体確認必須）
- 翌日: リスク最高（ウォームアップ必須）

### エージェント別注意度
- CEO: ★☆☆☆☆（最も安定）
- Manager: ★★☆☆☆（比較的安定）
- Dev1-2: ★★★☆☆（中程度）
- Dev3: ★★★★★（要注意！）

</details>

---

## 🎓 上級テクニック

### スマートフォン操作（実装予定）
```bash
# Termux/Blink Shell経由
ssh user@home-pc
tmux attach -t ai-team
./send-message.sh ceo "進捗確認"
```

### 複数チーム並行運用
```bash
# チーム1: 機械学習プロジェクト
tmux new -s ml-team
./start-ai-team.sh --profile ml

# チーム2: Web開発プロジェクト  
tmux new -s web-team
./start-ai-team.sh --profile web

# モニター統合表示
claude-code-monitor --all-teams
```

---

## 📁 instructions/ - AIエージェントの頭脳

<table style="background: #f5f5f5; border-radius: 8px; padding: 10px;">
<tr>
<td width="50%">

### 🧠 ディレクトリ概要
```
instructions/
├── ceo.md       # 戦略決定者
├── manager.md   # 自律的管理者
└── developer.md # 実行者（共通）
```

各ファイルがエージェントの「性格」と「行動原則」を定義。
起動時に読み込まれ、それぞれの役割を理解する。

### 📋 各ファイルの要点

**ceo.md - 委任の達人**
- ❌ 直接作業は絶対禁止
- ✅ 必ずmanagerに委任
- 戦略決定と最終承認のみ
- `./send-message.sh manager "プロジェクト名:..."`

**manager.md - 自動化の要**
- 自律的なタスク分解
- 依存関係の自動管理
- 完了報告→次タスク自動実行
- 並列/順次実行の判断

</td>
<td width="50%">

**developer.md - 実行のプロ**
- 役割は動的に割り当て
  - dev1: UI/UX・フロントエンド
  - dev2: バックエンド・データ分析
  - dev3: 品質管理・テスト
- 【完了報告】での報告必須
- managerの指示を確実に実行

### 🔧 カスタマイズのヒント
```bash
# 役割を変更したい場合
vi instructions/developer.md
# dev3の出力量警告追加など
```

### ⚠️ トラブル時の確認ポイント
1. **CEOが直接作業してる？**
   → ceo.mdの「禁止事項」確認
2. **タスクが進まない？**
   → manager.mdの自動実行設定
3. **完了報告が来ない？**
   → developer.mdの報告指示
4. **プロジェクトが見つからない？**
   → /mnt/d/直下、WD/DN/OT形式確認

**「指示書が行動を決める」** - この原則を忘れずに！

</td>
</tr>
</table>

---

## 🛠️ 技術仕様（トラブルシューティング用）

```json
{
  "system_structure": {
    "tmux_sessions": [
      {
        "name": "ceo",
        "type": "single",
        "claude_command": "claude instructions/ceo.md"
      },
      {
        "name": "team", 
        "type": "4-split",
        "panes": ["Manager", "Dev1", "Dev2", "Dev3"],
        "claude_command": "claude instructions/{role}.md"
      }
    ],
    "working_directory": "/mnt/d/multiagent-system",
    "agent_specs": {
      "CEO": {"役割": "委任必須", "制約": "実装禁止"},
      "Manager": {"役割": "自動判断", "特徴": "タスク分解"},
      "Dev1": {"役割": "設計", "出力": "中"},
      "Dev2": {"役割": "実装", "出力": "少"},
      "Dev3": {"役割": "品質", "出力": "最大", "注意": "auto-compact頻発"}
    },
    "communication": {
      "method": "send-message.sh",
      "format": "./send-message.sh [target] \"message\"",
      "targets": ["ceo", "manager", "dev1", "dev2", "dev3"],
      "log_location": "./logs/"
    }
  },
  "known_issues": {
    "auto_compact": {
      "影響": "dev3に集中",
      "対策": ["出力要約", "段階実行", "事前保存"]
    },
    "access_restriction": {
      "問題": "multiagent-system制限",
      "解決": "Dドライブ直下運用"
    }
  },
  "requirements": {
    "WSL": "必須",
    "tmux": "必須", 
    "gh": "GitHub CLI必須",
    "claude-code": "各エージェント用"
  }
}
```

---

## 🔨 基盤システムセットアップ

### 必要環境（全環境共通）
- Windows + WSL2
- tmux (`sudo apt install tmux`)
- GitHub CLI (`gh auth login`)
- Claude Code (5ライセンス)

### 基本セットアップ手順
```bash
# 1. 基盤システムのクローン
git clone https://github.com/your-repo/ai-team-base.git
cd ai-team-base

# 2. instructionsディレクトリ確認
ls instructions/
# ceo.md, manager.md, developer.md

# 3. 通信システム設定
chmod +x send-message.sh
chmod +x start-system.sh

# 4. 起動
./start-system.sh
```

### カスタマイズ例
```bash
# 起動ディレクトリ変更（推奨）
vi start-system.sh
# cd $(pwd) → cd /mnt/d/ に変更

# プロジェクトコード体系導入
mkdir /mnt/d/WD109_NewProject
cd /mnt/d/WD109_NewProject
./start-system.sh

# 役割定義調整
vi instructions/developer.md
# dev3にauto-compact警告追加
```

---

**「CEOに聞けば全部わかる」** - この安心感がAI Team最大の価値です。