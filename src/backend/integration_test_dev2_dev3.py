#!/usr/bin/env python3
"""
dev2のtreatment_planner.pyとdev3のtooth_movement_calculator.pyの統合テストスクリプト
API応答とデータ精度を検証
"""

import sys
import os
import requests
import json
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Tuple

# dev3のモジュールをインポート
sys.path.append('/mnt/d/multiagent-system/src/analysis')
from tooth_movement_calculator import ToothMovementCalculator, MovementType, AnchorageType, create_api_interface

# APIベースURL
BASE_URL = "http://localhost:8000"

class IntegrationTester:
    """統合テストクラス"""
    
    def __init__(self):
        self.results = []
        self.dev3_calculator = ToothMovementCalculator()
        self.dev3_api = create_api_interface()
        self.test_patients = [
            {
                "id": "2024-001",
                "name": "山田太郎",
                "age": 15,
                "description": "骨格性II級、上顎前突、中等度叢生",
                "expected_overjet": 6.0,
                "expected_crowding": 5.0
            },
            {
                "id": "2024-002", 
                "name": "鈴木花子",
                "age": 18,
                "description": "骨格性III級、反対咬合",
                "expected_overjet": -2.0,
                "expected_crowding": 2.0
            }
        ]
    
    def test_api_connectivity(self) -> bool:
        """APIサーバー接続確認"""
        print("=== API接続確認 ===")
        try:
            response = requests.get(BASE_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ APIサーバー稼働中 (version: {data.get('version', 'unknown')})")
                return True
            else:
                print(f"✗ API応答エラー: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ API接続失敗: {e}")
            return False
    
    def test_dev2_tooth_movements_api(self, patient_id: str, patient_age: int) -> Dict[str, Any]:
        """dev2の歯牙移動量計算APIテスト"""
        print(f"\n--- dev2 歯牙移動量計算API ({patient_id}) ---")
        
        try:
            response = requests.get(
                f"{BASE_URL}/patients/{patient_id}/tooth-movements",
                params={"patient_age": patient_age}
            )
            
            if response.status_code == 200:
                data = response.json()
                movements = data["movements"]
                
                print(f"✓ API応答成功")
                print(f"  - 総移動時間: {movements['total_movement_time']}週間")
                
                # 前歯部後方移動量の確認
                if movements["anterior_retraction"]:
                    print("  - 前歯部後方移動:")
                    for tooth, movement in movements["anterior_retraction"].items():
                        print(f"    {tooth}: {movement.get('後方移動量', 0)}mm")
                
                # 臼歯移動量の確認
                if movements["molar_movement"]:
                    print("  - 臼歯移動:")
                    for tooth, movement in movements["molar_movement"].items():
                        for key, value in movement.items():
                            print(f"    {tooth} {key}: {value}")
                
                # 3D移動ベクトルの確認
                if movements["tooth_vectors"]:
                    print("  - 3D移動ベクトル確認:")
                    for tooth, vector in movements["tooth_vectors"].items():
                        print(f"    {tooth}: {vector}")
                
                return data
            else:
                print(f"✗ API応答エラー: {response.status_code}")
                return {}
        except Exception as e:
            print(f"✗ API呼び出し失敗: {e}")
            return {}
    
    def test_dev3_calculations(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """dev3の計算エンジン直接テスト"""
        print(f"\n--- dev3 歯牙移動計算エンジン ---")
        
        try:
            # 治療計画データを構築
            treatment_data = {
                "occlusion": {
                    "overjet": patient_data.get("expected_overjet", 4.0),
                    "overbite": 4.0
                },
                "crowding": {
                    "upper": patient_data.get("expected_crowding", 3.0),
                    "lower": 2.0
                },
                "extraction_plan": {
                    "required": True,
                    "teeth": ["14", "24"]
                } if patient_data.get("expected_crowding", 0) > 4 else None
            }
            
            # dev3のAPI関数を使用
            result = self.dev3_api(treatment_data)
            
            print(f"✓ dev3計算完了")
            print(f"  - 前歯後退量: {result['basic_movement']['anterior_mm']}mm")
            print(f"  - 抜歯必要性: {result['basic_movement']['extraction_required']}")
            print(f"  - 推定期間: {result['basic_movement']['estimated_duration_months']}ヶ月")
            print(f"  - 固定源スコア: {result['anchorage_plan']['score']}/100")
            
            if result["space_closure"]:
                space_closure = result["space_closure"]
                print(f"  - スペース閉鎖:")
                print(f"    前歯後退: {space_closure.anterior_retraction_mm}mm")
                print(f"    臼歯前進: {space_closure.posterior_protraction_mm}mm")
                print(f"    閉鎖方法: {space_closure.closure_method}")
            
            return result
            
        except Exception as e:
            print(f"✗ dev3計算失敗: {e}")
            return {}
    
    def compare_calculation_accuracy(self, dev2_data: Dict[str, Any], dev3_data: Dict[str, Any], patient_info: Dict[str, Any]) -> Dict[str, Any]:
        """dev2とdev3の計算精度比較"""
        print(f"\n--- 計算精度比較分析 ---")
        
        comparison = {
            "patient_id": patient_info["id"],
            "accuracy_checks": [],
            "discrepancies": [],
            "recommendations": []
        }
        
        try:
            # 1. 前歯後方移動量の比較
            dev2_movements = dev2_data.get("movements", {})
            dev2_anterior = dev2_movements.get("anterior_retraction", {})
            dev3_anterior = dev3_data.get("basic_movement", {}).get("anterior_mm", 0)
            
            if dev2_anterior and dev3_anterior > 0:
                # dev2の上顎中切歯後方移動量を取得
                dev2_central_movement = 0
                for tooth, movement in dev2_anterior.items():
                    if "中切歯" in tooth:
                        dev2_central_movement = movement.get("後方移動量", 0)
                        break
                
                if dev2_central_movement > 0:
                    difference = abs(dev2_central_movement - dev3_anterior)
                    accuracy_percentage = max(0, 100 - (difference / dev3_anterior * 100))
                    
                    print(f"前歯後方移動量比較:")
                    print(f"  dev2 (treatment_planner): {dev2_central_movement}mm")
                    print(f"  dev3 (tooth_calculator): {dev3_anterior}mm")
                    print(f"  差異: {difference}mm ({100-accuracy_percentage:.1f}%)")
                    
                    comparison["accuracy_checks"].append({
                        "parameter": "anterior_retraction",
                        "dev2_value": dev2_central_movement,
                        "dev3_value": dev3_anterior,
                        "difference": difference,
                        "accuracy_percentage": accuracy_percentage
                    })
                    
                    if difference > 1.0:  # 1mm以上の差異
                        comparison["discrepancies"].append(
                            f"前歯後方移動量に{difference:.1f}mmの差異（許容範囲: 1mm）"
                        )
            
            # 2. 治療期間の比較
            dev2_time = dev2_movements.get("total_movement_time", 0)  # 週単位
            dev3_time = dev3_data.get("basic_movement", {}).get("estimated_duration_months", 0) * 4.33  # 週単位に変換
            
            if dev2_time > 0 and dev3_time > 0:
                time_difference = abs(dev2_time - dev3_time)
                time_accuracy = max(0, 100 - (time_difference / dev3_time * 100))
                
                print(f"\n治療期間比較:")
                print(f"  dev2: {dev2_time}週間 ({dev2_time/4.33:.1f}ヶ月)")
                print(f"  dev3: {dev3_time:.1f}週間 ({dev3_time/4.33:.1f}ヶ月)")
                print(f"  差異: {time_difference:.1f}週間")
                
                comparison["accuracy_checks"].append({
                    "parameter": "treatment_duration",
                    "dev2_value": dev2_time,
                    "dev3_value": dev3_time,
                    "difference": time_difference,
                    "accuracy_percentage": time_accuracy
                })
                
                if time_difference > 8:  # 8週間以上の差異
                    comparison["discrepancies"].append(
                        f"治療期間に{time_difference:.1f}週間の差異（許容範囲: 8週間）"
                    )
            
            # 3. 物理学的妥当性の検証
            print(f"\n物理学的妥当性検証:")
            
            # 3D移動ベクトルの妥当性
            tooth_vectors = dev2_movements.get("tooth_vectors", {})
            if tooth_vectors:
                for tooth, vector in tooth_vectors.items():
                    magnitude = np.linalg.norm(vector)
                    print(f"  {tooth} 移動量: {magnitude:.2f}mm")
                    
                    if magnitude > 8:  # 8mm以上の移動は要注意
                        comparison["discrepancies"].append(
                            f"{tooth}の移動量が{magnitude:.1f}mmと大きい"
                        )
            
            # 4. 生物学的制約の確認
            print(f"\n生物学的制約確認:")
            
            # 固定源要求度の整合性
            dev3_anchorage = dev3_data.get("anchorage_plan", {}).get("score", 0)
            print(f"  固定源要求度: {dev3_anchorage}/100")
            
            if dev3_anchorage > 80:
                comparison["recommendations"].append("高い固定源要求度のため、TADs使用を検討")
            
            # 抜歯の必要性
            dev3_extraction = dev3_data.get("basic_movement", {}).get("extraction_required", False)
            print(f"  抜歯必要性: {dev3_extraction}")
            
            if dev3_extraction:
                comparison["recommendations"].append("抜歯症例のため、固定源管理が重要")
            
            # 総合評価
            if comparison["accuracy_checks"]:
                avg_accuracy = np.mean([check["accuracy_percentage"] for check in comparison["accuracy_checks"]])
                print(f"\n総合精度: {avg_accuracy:.1f}%")
                
                if avg_accuracy > 85:
                    print("✓ 高精度: 両エンジンの計算結果が良好に一致")
                elif avg_accuracy > 70:
                    print("△ 中精度: 軽微な差異があるが許容範囲")
                else:
                    print("✗ 低精度: 計算結果に大きな差異")
                
                comparison["overall_accuracy"] = avg_accuracy
            
        except Exception as e:
            print(f"✗ 比較分析エラー: {e}")
            comparison["discrepancies"].append(f"比較分析中にエラー: {e}")
        
        return comparison
    
    def test_wire_sequence_integration(self, patient_id: str, patient_age: int) -> Dict[str, Any]:
        """ワイヤーシークエンスとの統合テスト"""
        print(f"\n--- ワイヤーシークエンス統合テスト ---")
        
        try:
            response = requests.get(
                f"{BASE_URL}/patients/{patient_id}/wire-sequence",
                params={"patient_age": patient_age}
            )
            
            if response.status_code == 200:
                data = response.json()
                wire_sequence = data["wire_sequence"]
                
                print(f"✓ ワイヤーシークエンス取得成功")
                print(f"  - 装置タイプ: {data['appliance_type']}")
                print(f"  - 総期間: {data['total_duration_weeks']}週間")
                print(f"  - ワイヤー段階数: {len(wire_sequence)}")
                
                # 各段階の妥当性確認
                total_weeks = 0
                for i, wire in enumerate(wire_sequence):
                    total_weeks += wire["duration_weeks"]
                    print(f"  段階{i+1}: {wire['size']} ({wire['duration_weeks']}週)")
                
                # 期間の整合性確認
                if abs(total_weeks - data['total_duration_weeks']) > 2:
                    print(f"⚠ 期間計算に不整合: 合計{total_weeks}週 vs 表示{data['total_duration_weeks']}週")
                
                return data
            else:
                print(f"✗ ワイヤーシークエンス取得失敗: {response.status_code}")
                return {}
        except Exception as e:
            print(f"✗ ワイヤーシークエンステスト失敗: {e}")
            return {}
    
    def test_elastic_prescription_integration(self, patient_id: str) -> Dict[str, Any]:
        """顎間ゴム処方との統合テスト"""
        print(f"\n--- 顎間ゴム処方統合テスト ---")
        
        test_stages = ["空隙閉鎖", "前歯部改善", "仕上げ"]
        results = {}
        
        for stage in test_stages:
            try:
                occlusion_analysis = {"midline_deviation": 2.5}
                
                response = requests.post(
                    f"{BASE_URL}/patients/{patient_id}/elastic-prescription",
                    params={"treatment_stage": stage},
                    json=occlusion_analysis
                )
                
                if response.status_code == 200:
                    data = response.json()
                    prescription = data["prescription"]
                    
                    print(f"\n  ステージ: {stage}")
                    if prescription["elastics"]:
                        for elastic in prescription["elastics"]:
                            print(f"    - {elastic['type']}: {elastic['force']}")
                            print(f"      装着時間: {elastic['wear_time']}")
                    else:
                        print(f"    - ゴム使用なし")
                    
                    results[stage] = data
                else:
                    print(f"✗ {stage}の処方取得失敗: {response.status_code}")
            except Exception as e:
                print(f"✗ {stage}のテスト失敗: {e}")
        
        return results
    
    def run_comprehensive_integration_test(self) -> Dict[str, Any]:
        """包括的統合テストの実行"""
        print("=" * 70)
        print("dev2-dev3 統合テスト開始")
        print("=" * 70)
        
        test_report = {
            "test_date": datetime.now().isoformat(),
            "api_connectivity": False,
            "patient_tests": [],
            "overall_accuracy": 0,
            "critical_issues": [],
            "recommendations": []
        }
        
        # API接続確認
        if not self.test_api_connectivity():
            test_report["critical_issues"].append("APIサーバーに接続できません")
            return test_report
        
        test_report["api_connectivity"] = True
        
        # 各患者での統合テスト
        total_accuracy = 0
        successful_tests = 0
        
        for patient in self.test_patients:
            print(f"\n{'='*50}")
            print(f"患者テスト: {patient['name']} ({patient['description']})")
            print(f"{'='*50}")
            
            patient_result = {
                "patient_info": patient,
                "dev2_results": {},
                "dev3_results": {},
                "comparison": {},
                "wire_sequence": {},
                "elastic_prescription": {}
            }
            
            # dev2のAPIテスト
            dev2_data = self.test_dev2_tooth_movements_api(patient["id"], patient["age"])
            patient_result["dev2_results"] = dev2_data
            
            # dev3の計算テスト
            dev3_data = self.test_dev3_calculations(patient)
            patient_result["dev3_results"] = dev3_data
            
            # 計算精度比較
            if dev2_data and dev3_data:
                comparison = self.compare_calculation_accuracy(dev2_data, dev3_data, patient)
                patient_result["comparison"] = comparison
                
                if "overall_accuracy" in comparison:
                    total_accuracy += comparison["overall_accuracy"]
                    successful_tests += 1
                
                # 重要な不整合をレポート
                if comparison["discrepancies"]:
                    test_report["critical_issues"].extend(comparison["discrepancies"])
            
            # ワイヤーシークエンステスト
            wire_data = self.test_wire_sequence_integration(patient["id"], patient["age"])
            patient_result["wire_sequence"] = wire_data
            
            # 顎間ゴム処方テスト
            elastic_data = self.test_elastic_prescription_integration(patient["id"])
            patient_result["elastic_prescription"] = elastic_data
            
            test_report["patient_tests"].append(patient_result)
        
        # 総合評価
        if successful_tests > 0:
            test_report["overall_accuracy"] = total_accuracy / successful_tests
        
        # 推奨事項の生成
        if test_report["overall_accuracy"] > 85:
            test_report["recommendations"].append("統合テスト良好: 本番環境への移行可能")
        elif test_report["overall_accuracy"] > 70:
            test_report["recommendations"].append("軽微な調整後、本番環境移行を推奨")
        else:
            test_report["recommendations"].append("重要な問題解決後の再テストが必要")
        
        return test_report
    
    def generate_test_report(self, test_results: Dict[str, Any]) -> str:
        """テストレポートの生成"""
        report = f"""
# dev2-dev3 統合テスト完了報告

## テスト概要
- **実施日時**: {test_results['test_date']}
- **API接続**: {'成功' if test_results['api_connectivity'] else '失敗'}
- **テスト患者数**: {len(test_results['patient_tests'])}
- **総合精度**: {test_results['overall_accuracy']:.1f}%

## 主要結果

### 精度評価
"""
        
        if test_results["overall_accuracy"] > 85:
            report += "✅ **高精度**: dev2とdev3の計算結果が良好に一致\n"
        elif test_results["overall_accuracy"] > 70:
            report += "⚠️ **中精度**: 軽微な差異があるが許容範囲内\n"
        else:
            report += "❌ **低精度**: 計算結果に大きな差異が検出\n"
        
        # 患者別結果
        report += "\n### 患者別結果\n"
        for patient_test in test_results["patient_tests"]:
            patient = patient_test["patient_info"]
            comparison = patient_test["comparison"]
            
            report += f"\n#### {patient['name']} ({patient['description']})\n"
            
            if "overall_accuracy" in comparison:
                report += f"- **精度**: {comparison['overall_accuracy']:.1f}%\n"
            
            if comparison.get("accuracy_checks"):
                for check in comparison["accuracy_checks"]:
                    report += f"- **{check['parameter']}**: dev2={check['dev2_value']}, dev3={check['dev3_value']}, 差異={check['difference']:.2f}\n"
        
        # 重要な問題
        if test_results["critical_issues"]:
            report += "\n### ⚠️ 重要な問題\n"
            for issue in test_results["critical_issues"]:
                report += f"- {issue}\n"
        
        # 推奨事項
        if test_results["recommendations"]:
            report += "\n### 📋 推奨事項\n"
            for rec in test_results["recommendations"]:
                report += f"- {rec}\n"
        
        # API機能確認
        report += "\n### API機能確認\n"
        for patient_test in test_results["patient_tests"]:
            patient = patient_test["patient_info"]
            
            dev2_success = bool(patient_test["dev2_results"])
            wire_success = bool(patient_test["wire_sequence"])
            elastic_success = bool(patient_test["elastic_prescription"])
            
            report += f"- **{patient['name']}**:\n"
            report += f"  - 歯牙移動量計算: {'✅' if dev2_success else '❌'}\n"
            report += f"  - ワイヤーシークエンス: {'✅' if wire_success else '❌'}\n"
            report += f"  - 顎間ゴム処方: {'✅' if elastic_success else '❌'}\n"
        
        # データ精度詳細
        report += "\n### 📊 データ精度詳細\n"
        for patient_test in test_results["patient_tests"]:
            comparison = patient_test["comparison"]
            if comparison.get("accuracy_checks"):
                patient = patient_test["patient_info"]
                report += f"\n**{patient['name']}**:\n"
                for check in comparison["accuracy_checks"]:
                    report += f"- {check['parameter']}: {check['accuracy_percentage']:.1f}%精度\n"
        
        # 結論
        report += "\n## 結論\n"
        if test_results["overall_accuracy"] > 85:
            report += "統合テストは成功しました。dev2とdev3の連携は良好で、本番環境での使用が可能です。\n"
        elif test_results["overall_accuracy"] > 70:
            report += "統合テストは概ね成功しました。軽微な調整を行った後、本番環境移行を推奨します。\n"
        else:
            report += "統合テストで重要な問題が発見されました。計算アルゴリズムの見直しと再テストが必要です。\n"
        
        return report


def main():
    """メイン実行関数"""
    tester = IntegrationTester()
    
    # 包括的統合テストの実行
    test_results = tester.run_comprehensive_integration_test()
    
    # レポート生成
    report = tester.generate_test_report(test_results)
    
    # レポート表示
    print("\n" + "=" * 70)
    print(report)
    
    # レポートファイル保存
    report_file = "/mnt/d/multiagent-system/src/backend/integration_test_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n📄 詳細レポートを保存しました: {report_file}")
    
    # JSON形式でも保存
    json_file = "/mnt/d/multiagent-system/src/backend/integration_test_results.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"📊 テストデータを保存しました: {json_file}")
    
    # 終了コード決定
    if test_results["overall_accuracy"] > 70:
        print(f"\n✅ 統合テスト成功 (精度: {test_results['overall_accuracy']:.1f}%)")
        return 0
    else:
        print(f"\n❌ 統合テスト要改善 (精度: {test_results['overall_accuracy']:.1f}%)")
        return 1


if __name__ == "__main__":
    exit(main())