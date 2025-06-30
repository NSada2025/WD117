# 咬合分析エンジン

## 概要
咬合改善を最優先とした歯科矯正評価システムです。オーバージェット、オーバーバイト、大臼歯関係、ANB角等の指標から咬合状態を総合評価し、改善優先度をスコアリングします。

## 主な機能
- 咬合評価指標の包括的な分析
- 重症度の自動判定（NORMAL〜VERY_SEVERE）
- 改善優先順位の決定
- 治療推奨事項の生成
- 詳細な分析レポートの作成

## 使用方法

```python
from occlusion_analyzer import OcclusionAnalyzer, OcclusionMetrics, MolarRelationship

# 咬合評価指標を設定
metrics = OcclusionMetrics(
    overjet_mm=5.5,                             # オーバージェット
    overbite_mm=3.0,                            # オーバーバイト
    molar_relationship=MolarRelationship.CLASS_I, # 大臼歯関係
    anb_angle_degrees=3.5,                      # ANB角
    anterior_crossbite=False,                   # 前歯部反対咬合
    posterior_crossbite=False,                  # 臼歯部反対咬合
    midline_deviation_mm=1.5                    # 正中線のずれ
)

# 分析実行
analyzer = OcclusionAnalyzer()
score = analyzer.analyze(metrics)

# 結果表示
print(f"総合スコア: {score.total_score}/100")
print(f"重症度: {score.severity.name}")
print(f"改善優先順位: {score.priority_rankings}")
print(analyzer.get_detailed_report())
```

## 評価指標

### 必須指標
- **オーバージェット**: 前歯の水平的被蓋（正常値: 2-4mm）
- **オーバーバイト**: 前歯の垂直的被蓋（正常値: 2-4mm）
- **大臼歯関係**: Angleの分類（Class I/II/III）
- **ANB角**: 上下顎の前後的関係（正常値: 0-4度）

### オプション指標
- 前歯部反対咬合の有無
- 臼歯部反対咬合の有無
- 開咬の有無
- 過蓋咬合の有無
- 正中線のずれ

## スコアリングシステム
- 各指標は0-100のスコアで評価（0が正常）
- 重み付けに基づいて総合スコアを算出
- 咬合機能への影響度を考慮した重み設定

## ファイル構成
- `occlusion_analyzer.py`: メインの分析エンジン
- `test_occlusion_analyzer.py`: テストスイート
- `README.md`: このドキュメント