#!/usr/bin/env python3
"""
統合テストスイート
システム全体の結合テスト
"""

import unittest
import json
import sys
import os
from unittest.mock import Mock, patch

# プロジェクトのルートパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))

from src.integration.connectors.backend_connector import BackendConnector, ConnectionConfig
from src.integration.connectors.analysis_connector import AnalysisConnector
from src.analysis.occlusion_analyzer import MolarRelationship, OcclusionSeverity


class TestBackendConnector(unittest.TestCase):
    """バックエンドコネクタのテスト"""
    
    def setUp(self):
        """テストの初期化"""
        self.config = ConnectionConfig(backend_url="http://test-backend:8000")
        self.connector = BackendConnector(self.config)
    
    @patch('requests.Session.get')
    def test_get_patients(self, mock_get):
        """患者リスト取得のテスト"""
        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "total": 2,
            "patients": [
                {"患者ID": "2024-001", "患者氏名": "テスト太郎"},
                {"患者ID": "2024-002", "患者氏名": "テスト花子"}
            ]
        }
        mock_get.return_value = mock_response
        
        # テスト実行
        result = self.connector.get_patients()
        
        # 検証
        self.assertEqual(result["total"], 2)
        self.assertEqual(len(result["patients"]), 2)
        mock_get.assert_called_once()
    
    @patch('requests.Session.post')
    def test_create_patient(self, mock_post):
        """患者登録のテスト"""
        # モックレスポンスの設定
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "患者ID": "2024-003",
            "患者氏名": "新規患者"
        }
        mock_post.return_value = mock_response
        
        # テストデータ
        patient_data = {
            "患者氏名": "新規患者",
            "年齢": 25,
            "性別": "女性"
        }
        
        # テスト実行
        result = self.connector.create_patient(patient_data)
        
        # 検証
        self.assertEqual(result["患者ID"], "2024-003")
        mock_post.assert_called_once()
    
    @patch('requests.Session.get')
    def test_health_check(self, mock_get):
        """ヘルスチェックのテスト"""
        # 正常なレスポンス
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        self.assertTrue(self.connector.health_check())
        
        # 異常なレスポンス
        mock_response.status_code = 500
        self.assertFalse(self.connector.health_check())


class TestAnalysisConnector(unittest.TestCase):
    """分析コネクタのテスト"""
    
    def setUp(self):
        """テストの初期化"""
        self.connector = AnalysisConnector()
    
    def test_analyze_and_plan_normal(self):
        """正常な咬合の分析テスト"""
        # テストデータ
        patient_data = {
            "patient_id": "TEST-001",
            "age": 20,
            "gender": "男性",
            "chief_complaint": "歯並びの改善",
            "measurements": {
                "overjet_mm": 3.0,
                "overbite_mm": 3.0,
                "molar_relationship": "CLASS_I",
                "anb_angle_degrees": 2.0,
                "midline_deviation_mm": 0.5
            },
            "preferences": {
                "aesthetic_priority": True
            }
        }
        
        # 分析実行
        result = self.connector.analyze_and_plan(patient_data)
        
        # 検証
        self.assertIn("occlusion_analysis", result)
        self.assertIn("treatment_plan", result)
        self.assertIn("integration_summary", result)
        
        # 正常咬合の確認
        occlusion = result["occlusion_analysis"]
        self.assertLess(occlusion["total_score"], 15)
        self.assertEqual(occlusion["severity"], "NORMAL")
    
    def test_analyze_and_plan_severe(self):
        """重度不正咬合の分析テスト"""
        # テストデータ
        patient_data = {
            "patient_id": "TEST-002",
            "age": 25,
            "gender": "女性",
            "chief_complaint": "反対咬合",
            "measurements": {
                "overjet_mm": -3.0,
                "overbite_mm": -2.0,
                "molar_relationship": "CLASS_III",
                "anb_angle_degrees": -4.0,
                "anterior_crossbite": True,
                "midline_deviation_mm": 4.0
            }
        }
        
        # 分析実行
        result = self.connector.analyze_and_plan(patient_data)
        
        # 検証
        occlusion = result["occlusion_analysis"]
        self.assertGreater(occlusion["total_score"], 50)
        self.assertIn(occlusion["severity"], ["SEVERE", "VERY_SEVERE"])
        
        # 推奨事項の確認
        self.assertGreater(len(occlusion["recommendations"]), 0)
        self.assertTrue(any("矯正治療" in rec for rec in occlusion["recommendations"]))
    
    def test_treatment_complexity_assessment(self):
        """治療複雑性評価のテスト"""
        # 中等度のケース
        patient_data = {
            "patient_id": "TEST-003",
            "age": 30,
            "measurements": {
                "overjet_mm": 6.0,
                "overbite_mm": 5.0,
                "molar_relationship": "CLASS_II",
                "anb_angle_degrees": 5.0
            }
        }
        
        result = self.connector.analyze_and_plan(patient_data)
        summary = result["integration_summary"]
        
        # 複雑性の確認
        self.assertIn(summary["treatment_complexity"], ["中等度", "高度"])
        self.assertGreater(summary["success_probability"], 70.0)
    
    def test_validate_connection(self):
        """接続検証のテスト"""
        status = self.connector.validate_connection()
        
        self.assertTrue(status["occlusion_analyzer"])
        self.assertTrue(status["treatment_planner"])
        self.assertTrue(status["integration_status"])


class TestIntegrationScenarios(unittest.TestCase):
    """統合シナリオテスト"""
    
    def setUp(self):
        """テストの初期化"""
        self.backend_connector = BackendConnector()
        self.analysis_connector = AnalysisConnector()
    
    @patch('requests.Session.post')
    @patch('requests.Session.get')
    def test_full_patient_workflow(self, mock_get, mock_post):
        """患者登録から分析までの完全なワークフロー"""
        # Step 1: 患者登録
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            "患者ID": "2024-100",
            "患者氏名": "統合テスト患者"
        }
        
        patient_data = {
            "患者氏名": "統合テスト患者",
            "年齢": 22,
            "性別": "女性"
        }
        
        create_result = self.backend_connector.create_patient(patient_data)
        self.assertEqual(create_result["患者ID"], "2024-100")
        
        # Step 2: 咬合分析と治療計画
        analysis_data = {
            "patient_id": "2024-100",
            "age": 22,
            "gender": "女性",
            "chief_complaint": "前歯の突出",
            "measurements": {
                "overjet_mm": 7.0,
                "overbite_mm": 6.0,
                "molar_relationship": "CLASS_II",
                "anb_angle_degrees": 6.5
            },
            "preferences": {
                "aesthetic_priority": True,
                "treatment_duration_preference": "fast"
            }
        }
        
        analysis_result = self.analysis_connector.analyze_and_plan(analysis_data)
        
        # 検証
        self.assertIn("occlusion_analysis", analysis_result)
        self.assertIn("treatment_plan", analysis_result)
        
        # 治療計画の確認
        plan = analysis_result["treatment_plan"]
        self.assertGreater(len(plan["stages"]), 0)
        self.assertIn("estimated_duration_months", plan)
    
    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 不正なデータでのテスト
        invalid_data = {
            "patient_id": "INVALID",
            "measurements": {}  # 必要な測定値が不足
        }
        
        result = self.analysis_connector.analyze_and_plan(invalid_data)
        self.assertIn("error", result)


def run_all_tests():
    """すべてのテストを実行"""
    print("統合テストを開始します...\n")
    
    # テストスイートの作成
    test_suite = unittest.TestSuite()
    
    # テストクラスを追加
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestBackendConnector))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAnalysisConnector))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIntegrationScenarios))
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果サマリー
    print("\n" + "="*70)
    print("テスト結果サマリー")
    print("="*70)
    print(f"実行テスト数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)