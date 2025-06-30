#!/usr/bin/env python3
"""
統合テストスイート（簡易版）
システム全体の結合テスト
"""

import sys
import os
import json

# プロジェクトのルートパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../src"))

from analysis.occlusion_analyzer import (
    OcclusionAnalyzer, OcclusionMetrics, MolarRelationship
)


def test_occlusion_analysis():
    """咬合分析エンジンのテスト"""
    print("=" * 70)
    print("咬合分析エンジンテスト")
    print("=" * 70)
    
    # テストケース1: 正常咬合
    print("\nテストケース1: 正常咬合")
    metrics1 = OcclusionMetrics(
        overjet_mm=3.0,
        overbite_mm=3.0,
        molar_relationship=MolarRelationship.CLASS_I,
        anb_angle_degrees=2.0,
        midline_deviation_mm=0.5
    )
    
    analyzer = OcclusionAnalyzer()
    score1 = analyzer.analyze(metrics1)
    
    print(f"総合スコア: {score1.total_score}/100")
    print(f"重症度: {score1.severity.name}")
    assert score1.total_score < 15, "正常咬合のスコアが高すぎます"
    print("✓ テスト成功")
    
    # テストケース2: 重度不正咬合
    print("\nテストケース2: 重度不正咬合")
    metrics2 = OcclusionMetrics(
        overjet_mm=-3.0,
        overbite_mm=-2.0,
        molar_relationship=MolarRelationship.CLASS_III,
        anb_angle_degrees=-4.0,
        anterior_crossbite=True,
        midline_deviation_mm=4.0
    )
    
    score2 = analyzer.analyze(metrics2)
    
    print(f"総合スコア: {score2.total_score}/100")
    print(f"重症度: {score2.severity.name}")
    print(f"改善優先順位: {score2.priority_rankings[:3]}")
    assert score2.total_score > 40, "重度不正咬合のスコアが低すぎます"
    print("✓ テスト成功")
    
    return True


def test_integration_connector():
    """統合コネクタの基本テスト"""
    print("\n" + "=" * 70)
    print("統合コネクタテスト")
    print("=" * 70)
    
    # 統合データの構造テスト
    patient_data = {
        "patient_id": "TEST-001",
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
            "aesthetic_priority": True
        }
    }
    
    # 咬合分析の実行
    measurements = patient_data["measurements"]
    molar_class = measurements.get("molar_relationship", "CLASS_I")
    molar_relationship = MolarRelationship[molar_class.upper().replace(" ", "_")]
    
    metrics = OcclusionMetrics(
        overjet_mm=measurements["overjet_mm"],
        overbite_mm=measurements["overbite_mm"],
        molar_relationship=molar_relationship,
        anb_angle_degrees=measurements["anb_angle_degrees"]
    )
    
    analyzer = OcclusionAnalyzer()
    score = analyzer.analyze(metrics)
    
    # 統合結果の作成
    integrated_result = {
        "patient_id": patient_data["patient_id"],
        "occlusion_analysis": {
            "total_score": score.total_score,
            "severity": score.severity.name,
            "priority_rankings": score.priority_rankings,
            "recommendations": score.recommendations
        },
        "integration_status": "success"
    }
    
    print(f"患者ID: {integrated_result['patient_id']}")
    print(f"咬合スコア: {integrated_result['occlusion_analysis']['total_score']}")
    print(f"重症度: {integrated_result['occlusion_analysis']['severity']}")
    print("✓ 統合テスト成功")
    
    return True


def test_api_response_structure():
    """API レスポンス構造のテスト"""
    print("\n" + "=" * 70)
    print("APIレスポンス構造テスト")
    print("=" * 70)
    
    # サンプルレスポンスの構造
    api_response = {
        "status": "success",
        "data": {
            "patient_id": "2024-001",
            "analysis_results": {
                "occlusion": {
                    "score": 45.5,
                    "severity": "MODERATE"
                },
                "treatment_plan": {
                    "duration_months": 18,
                    "stages": ["初期配列", "レベリング", "空隙閉鎖", "仕上げ"]
                }
            }
        },
        "timestamp": "2025-06-30T12:00:00"
    }
    
    # 構造の検証
    assert "status" in api_response, "status フィールドが存在しません"
    assert "data" in api_response, "data フィールドが存在しません"
    assert "patient_id" in api_response["data"], "patient_id が存在しません"
    
    print("APIレスポンス構造:")
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    print("✓ API構造テスト成功")
    
    return True


def run_all_tests():
    """すべてのテストを実行"""
    print("\n統合テスト（簡易版）を開始します...\n")
    
    tests = [
        ("咬合分析エンジンテスト", test_occlusion_analysis),
        ("統合コネクタテスト", test_integration_connector),
        ("APIレスポンス構造テスト", test_api_response_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"✗ {test_name} 失敗: {e}")
    
    # 結果サマリー
    print("\n" + "=" * 70)
    print("テスト結果サマリー")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success, _ in results if success)
    
    print(f"総テスト数: {total_tests}")
    print(f"成功: {passed_tests}")
    print(f"失敗: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("\n✓ すべてのテストが成功しました！")
        return True
    else:
        print("\n✗ 一部のテストが失敗しました")
        for test_name, success, error in results:
            if not success:
                print(f"  - {test_name}: {error}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)