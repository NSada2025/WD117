# システム統合ガイド

## 概要
このドキュメントは、矯正治療分析システムの統合アーキテクチャと使用方法を説明します。

## システムアーキテクチャ

### コンポーネント構成
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│ Integration  │────▶│   Backend   │
│   (React)   │     │     API      │     │  (FastAPI)  │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            ├─────────────────┐
                            ▼                 ▼
                    ┌──────────────┐  ┌──────────────┐
                    │  Occlusion   │  │  Treatment   │
                    │   Analyzer   │  │   Planner    │
                    └──────────────┘  └──────────────┘
```

### ポート構成
- **Frontend**: 3000
- **Integration API**: 8080
- **Backend API**: 8000
- **PostgreSQL**: 5432
- **Nginx**: 80

## 起動方法

### 1. 環境準備
```bash
# .envファイルの作成
cp .env.example .env

# 必要に応じて.envを編集
```

### 2. Docker Composeによる起動
```bash
# システム全体の起動
./docker-start.sh

# または直接Docker Composeを使用
docker-compose up -d
```

### 3. 動作確認
- フロントエンド: http://localhost:3000
- 統合API: http://localhost:8080
- 統合APIドキュメント: http://localhost:8080/docs
- バックエンドAPI: http://localhost:8000
- バックエンドAPIドキュメント: http://localhost:8000/docs

## API使用方法

### 統合分析の実行
```bash
curl -X POST "http://localhost:8080/api/v1/integrated-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "2024-001",
    "age": 25,
    "gender": "女性",
    "chief_complaint": "前歯の突出",
    "measurements": {
      "overjet_mm": 7.0,
      "overbite_mm": 6.0,
      "molar_relationship": "CLASS_II",
      "anb_angle_degrees": 6.0
    },
    "preferences": {
      "aesthetic_priority": true
    }
  }'
```

### レスポンス例
```json
{
  "occlusion_analysis": {
    "total_score": 36.6,
    "severity": "MODERATE",
    "component_scores": {
      "overjet": 45.0,
      "overbite": 30.0,
      "molar_relationship": 60.0,
      "anb_angle": 16.0
    },
    "priority_rankings": ["molar_relationship", "overjet", "overbite"],
    "recommendations": ["矯正治療を強く推奨します"]
  },
  "treatment_plan": {
    "id": "TP-2024-001",
    "appliance_type": "CERAMIC_BRACKET",
    "estimated_duration_months": 24,
    "stages": [...]
  },
  "integration_summary": {
    "severity_level": "MODERATE",
    "treatment_complexity": "中等度",
    "estimated_improvement": "良好（70-90%の改善）",
    "success_probability": 82.0
  }
}
```

## モジュール間連携

### 1. UIとバックエンドの接続
- `BackendConnector`クラスがHTTP通信を管理
- 自動リトライとエラーハンドリング機能
- セッションベースの接続プール

### 2. 咬合分析と治療計画の連携
- `AnalysisConnector`クラスが両エンジンを統合
- 咬合分析結果から自動的に治療目標を生成
- 患者の希望を考慮した治療計画の最適化

### 3. 統合APIの役割
- 全モジュールへの統一インターフェース
- CORS対応でフロントエンドからの直接アクセス可能
- ヘルスチェックとモニタリング機能

## トラブルシューティング

### ポート競合エラー
```bash
# 使用中のポートを確認
netstat -tlnp | grep -E '(3000|8000|8080|5432)'

# 必要に応じてdocker-compose.ymlでポートを変更
```

### データベース接続エラー
```bash
# PostgreSQLの状態確認
docker-compose ps postgres
docker-compose logs postgres

# データベースの再起動
docker-compose restart postgres
```

### モジュールインポートエラー
```bash
# Pythonパスの確認
docker-compose exec integration python -c "import sys; print(sys.path)"

# 依存関係の再インストール
docker-compose exec integration pip install -r requirements.txt
```

## 開発者向け情報

### テストの実行
```bash
# 統合テスト（簡易版）
python3 src/integration/tests/test_integration_simple.py

# 個別モジュールのテスト
python3 src/analysis/test_occlusion_analyzer.py
```

### ログの確認
```bash
# 全サービスのログ
docker-compose logs -f

# 特定サービスのログ
docker-compose logs -f integration
```

### デバッグモード
統合APIはデフォルトでリロードモードで起動します。
コードを変更すると自動的に再起動されます。