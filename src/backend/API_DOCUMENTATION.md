# 矯正治療データ管理基盤 API ドキュメント

## 概要
顔面写真・レントゲン・口腔内写真・模型写真・セファロ分析・模型分析の各種データを統合管理するバックエンドシステム

## エンドポイント一覧

### 基本情報
- **ベースURL**: `http://localhost:8000`
- **APIドキュメント**: `http://localhost:8000/docs`

### 患者管理

#### GET /patients
患者リストを取得

**パラメータ**:
- `skip`: スキップする件数（デフォルト: 0）
- `limit`: 取得する件数（デフォルト: 100）

**レスポンス例**:
```json
{
  "total": 3,
  "patients": [
    {
      "患者ID": "2024-001",
      "患者氏名": "山田太郎",
      "分析日時": "2025-06-30T17:31:39",
      ...
    }
  ]
}
```

#### GET /patients/{patient_id}
特定患者の詳細情報を取得

#### POST /patients
新規患者を登録

#### PUT /patients/{patient_id}
患者情報を更新

#### DELETE /patients/{patient_id}
患者情報を削除

### データアップロード

#### POST /patients/{patient_id}/photos
写真をアップロード

**パラメータ**:
- `photo_type`: 写真タイプ（facial/intraoral/model）
- `file`: アップロードファイル

#### POST /patients/{patient_id}/xrays
レントゲン画像をアップロード

**パラメータ**:
- `xray_type`: レントゲンタイプ（panoramic/cephalometric）
- `file`: アップロードファイル

#### POST /patients/{patient_id}/models
模型データをアップロード

**パラメータ**:
- `model_type`: 模型タイプ（upper/lower/occlusion）
- `file`: アップロードファイル

### 分析機能

#### POST /analyze
データ分析を実行

**リクエストボディ**:
```json
{
  "patient_id": "2024-001",
  "analysis_type": "cephalometric",
  "data": {}
}
```

#### GET /patients/{patient_id}/summary
患者の総合サマリーを取得

### 治療計画

#### POST /patients/{patient_id}/treatment-plan
治療計画を生成

**パラメータ**:
- `patient_age`: 患者の年齢（必須）
- `occlusion_analysis`: 咬合分析結果（オプション）
- `preferences`: 患者の希望（オプション）

**レスポンス例**:
```json
{
  "patient_id": "2024-001",
  "total_duration_months": 24,
  "primary_appliance": "メタルブラケット",
  "stages": [...]
}
```

#### GET /patients/{patient_id}/treatment-plan-report
治療計画レポートを取得（テキスト形式）

**パラメータ**:
- `patient_age`: 患者の年齢（必須）

#### POST /treatment-simulation
複数の治療オプションをシミュレーション

**リクエストボディ**:
```json
{
  "patient_id": "2024-001",
  "patient_age": 15
}
```

### 詳細治療計画

#### GET /patients/{patient_id}/tooth-movements
歯牙移動量を計算

**パラメータ**:
- `patient_age`: 患者の年齢（必須）

**レスポンス例**:
```json
{
  "movements": {
    "anterior_retraction": {
      "上顎中切歯": {
        "後方移動量": 3.5,
        "舌側傾斜": 10.0,
        "圧下量": 0.5
      }
    },
    "molar_movement": {
      "上顎第一大臼歯": {
        "遠心移動": 3.0,
        "回転": -5.0
      }
    },
    "tooth_vectors": {
      "上顎中切歯": [-3.5, 0, -0.5]
    },
    "total_movement_time": 15
  }
}
```

#### GET /patients/{patient_id}/wire-sequence
ワイヤーシークエンスを取得

**パラメータ**:
- `patient_age`: 患者の年齢（必須）

**レスポンス例**:
```json
{
  "wire_sequence": [
    {
      "size": "0.012\" NiTi",
      "duration_weeks": 4,
      "purpose": "初期配列",
      "force_level": "軽度（25-50g）",
      "stage": "初期治療"
    }
  ]
}
```

#### POST /patients/{patient_id}/elastic-prescription
顎間ゴム処方を取得

**パラメータ**:
- `treatment_stage`: 治療ステージ（必須）

**リクエストボディ（オプション）**:
```json
{
  "midline_deviation": 3.0,
  "occlusal_plane_cant": 2.0
}
```

**レスポンス例**:
```json
{
  "prescription": {
    "stage": "空隙閉鎖",
    "elastics": [
      {
        "type": "II級ゴム",
        "attachment": {
          "上顎": "犬歯フック",
          "下顎": "第一大臼歯フック"
        },
        "force": "3.5oz (中等度)",
        "wear_time": "20時間/日（食事時以外）",
        "purpose": "上顎前突の改善・臼歯関係の改善"
      }
    ],
    "duration_weeks": 16,
    "wear_instructions": "詳細な装着指示"
  }
}
```

### 統計情報

#### GET /stats
システム統計情報を取得

## データモデル

### OrthodonticRecord（矯正治療記録）
- 患者基本情報
- 歯列状態
- 咬合関係
- 顎骨位置関係
- セファロ分析
- 治療難易度評価
- 各種画像・分析データ

## 起動方法

```bash
cd /mnt/d/multiagent-system/src/backend
pip install -r requirements.txt
python main.py
```

アプリケーションは `http://localhost:8000` で起動します。
対話的APIドキュメントは `http://localhost:8000/docs` で確認できます。