# 環境固有設定の明確化

## 汎用システムと環境固有設定の区分

### 🏗️ 基盤システム（汎用）
全ての環境で共通の基本構成:
- 5エージェント体制（CEO/Manager/Dev1-3）
- tmux 2セッション構成（ceo + team）
- send-message.shによる通信
- instructionsによる役割定義

### 📂 環境固有設定（推奨例）

この環境の主な特徴:

1. **作業ディレクトリ**
   - Dドライブ直下（/mnt/d/）を基点
   - 全プロジェクトへの統一的アクセス
   - multiagent-system制限からの解放

2. **命名規則（WD108準拠）**
   ```
   WD001_ProjectName     # Work Development
   DN001_ExperimentName  # Data aNalysis
   OT001_OtherProject    # OTher
   ```
   - 3文字プレフィックス + 3桁番号
   - GitHubリポジトリ名と1:1対応

3. **プロジェクト管理**
   ```bash
   # GitHubとの連動例
   gh repo create WD109_NewProject
   cd /mnt/d/WD109_NewProject
   ./start-system.sh
   ```

### 🔄 他環境への適用

他のユーザーは以下を自由にカスタマイズ:
- 作業ディレクトリ（例: ~/projects/）
- 命名規則（例: proj-001、exp-001）
- リポジトリ管理方法

**重要**: 基盤システムは変更せず、環境設定のみ調整

### 📋 ドキュメントでの扱い

CC_Team_Construction_v2.mdでは:
- 基盤システム: 必須要件として明記
- 環境設定: 「推奨構成」として例示
- NSada2025固有: 実績例として参照

これにより、汎用性を保ちつつ、
効果的な運用例を提供する構成になっています。