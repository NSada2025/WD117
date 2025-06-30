# システム再起動チェックリスト

## 1. 再起動前確認事項 ✅
- [x] 進捗状況バックアップ (SYSTEM_STATUS_BACKUP.md)
- [x] 重要コードバックアップ (CRITICAL_CODE_BACKUP.js)
- [x] 設計ドキュメント保存完了
- [x] ファイル構造記録完了

## 2. 再起動後の初期確認

### A. 環境確認
```bash
# 作業ディレクトリ確認
pwd
cd /mnt/d/multiagent-system

# ファイル確認
ls -la
ls -la src/core/
ls -la src/mobile/
```

### B. 依存関係確認
```bash
# package.json確認
cat package.json

# 必要に応じてインストール
npm install
```

### C. コード整合性確認
```bash
# 主要ファイル存在確認
test -f src/main.js && echo "✓ main.js exists"
test -f src/core/CEOManagerProtocol.js && echo "✓ Protocol exists"
test -f src/core/RoleAwareOptimizer.js && echo "✓ RoleOptimizer exists"
```

## 3. システム起動手順

### Step 1: 基本起動
```bash
node src/main.js
```

### Step 2: 機能確認
- CEO-Manager通信: "CEO-Manager communication channels established"
- 安定性監視: "🛡️ 安定性監視システム初期化"
- auto-compact予防: "✅ Auto-compact予防機能を有効化"

### Step 3: デモ実行確認
- プロジェクト作成指示
- データ分析指示
- 緊急対応指示

## 4. 重要な継続タスク

### 高優先度
1. **DN001_TF連携**
   - 実験データとの統合
   - MEDxデータ分析機能

2. **実環境テスト**
   - 実際のdev1/dev2/dev3タスク割当
   - 出力量予測の精度検証

3. **WebSocket実装**
   - リアルタイム通信
   - 双方向データフロー

### 中優先度
1. データベース統合
2. ログ管理システム
3. パフォーマンス最適化

## 5. 既知の問題と対策

### dev3高出力問題
- 解決済み: RoleAwareOptimizer実装
- 監視継続: 実データでの検証必要

### コンテキストサイズ管理
- 解決済み: StabilityManager実装
- 45KB制限で自動圧縮

### モバイル安定性
- 解決済み: 自動再接続・オフライン対応
- パフォーマンス監視継続

## 6. 連絡事項

**Dドライブ直下運用の利点活用**
- DN001_TF等への直接アクセス
- プロジェクト間の自由な移動
- 大容量データの効率的処理

**次回作業の推奨事項**
1. 実データでのテスト実行
2. WebSocket通信の実装
3. データベース設計・統合

---

チェックリスト作成: 2024-12-30
システム再起動準備完了