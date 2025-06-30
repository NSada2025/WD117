#!/usr/bin/env python3
"""
咬合分析エンジンのテストスイート
"""

import unittest
from occlusion_analyzer import (
    OcclusionAnalyzer, OcclusionMetrics, OcclusionSeverity, 
    MolarRelationship
)


class TestOcclusionAnalyzer(unittest.TestCase):
    """咬合分析エンジンのテストクラス"""
    
    def setUp(self):
        """テストの初期化"""
        self.analyzer = OcclusionAnalyzer()
    
    def test_normal_occlusion(self):
        """正常咬合のテスト"""
        metrics = OcclusionMetrics(
            overjet_mm=3.0,
            overbite_mm=3.0,
            molar_relationship=MolarRelationship.CLASS_I,
            anb_angle_degrees=2.0,
            midline_deviation_mm=0.5
        )
        
        score = self.analyzer.analyze(metrics)
        
        # 正常咬合は低スコアであるべき
        self.assertLess(score.total_score, 15)
        self.assertEqual(score.severity, OcclusionSeverity.NORMAL)
        self.assertEqual(len(score.priority_rankings), 0)
    
    def test_mild_class_ii(self):
        """軽度Class II不正咬合のテスト"""
        metrics = OcclusionMetrics(
            overjet_mm=6.0,
            overbite_mm=5.0,
            molar_relationship=MolarRelationship.CLASS_II,
            anb_angle_degrees=6.0,
            midline_deviation_mm=2.0
        )
        
        score = self.analyzer.analyze(metrics)
        
        # 軽度〜中等度の範囲
        self.assertGreater(score.total_score, 15)
        self.assertLess(score.total_score, 50)
        self.assertIn(score.severity, [OcclusionSeverity.MILD, OcclusionSeverity.MODERATE])
        
        # 大臼歯関係が優先順位に含まれるべき
        self.assertIn('molar_relationship', score.priority_rankings)
    
    def test_severe_class_iii(self):
        """重度Class III不正咬合のテスト"""
        metrics = OcclusionMetrics(
            overjet_mm=-3.0,  # 反対咬合
            overbite_mm=-2.0,  # 開咬
            molar_relationship=MolarRelationship.CLASS_III,
            anb_angle_degrees=-4.0,
            anterior_crossbite=True,
            posterior_crossbite=True,
            midline_deviation_mm=5.0
        )
        
        score = self.analyzer.analyze(metrics)
        
        # 重度〜最重度
        self.assertGreater(score.total_score, 50)
        self.assertIn(score.severity, [OcclusionSeverity.SEVERE, OcclusionSeverity.VERY_SEVERE])
        
        # 複数の問題が優先順位に含まれる
        self.assertGreater(len(score.priority_rankings), 3)
        
        # 推奨事項が含まれる
        self.assertGreater(len(score.recommendations), 2)
        self.assertTrue(any("矯正治療" in rec for rec in score.recommendations))
    
    def test_deep_bite(self):
        """過蓋咬合のテスト"""
        metrics = OcclusionMetrics(
            overjet_mm=3.0,
            overbite_mm=7.0,  # 深い咬合
            molar_relationship=MolarRelationship.CLASS_I,
            anb_angle_degrees=2.5,
            deep_bite=True
        )
        
        score = self.analyzer.analyze(metrics)
        
        # オーバーバイトが優先順位の上位に
        self.assertIn('overbite', score.priority_rankings[:2])
        self.assertGreater(score.component_scores['overbite'], 30)
    
    def test_open_bite(self):
        """開咬のテスト"""
        metrics = OcclusionMetrics(
            overjet_mm=4.0,
            overbite_mm=-3.0,  # 開咬
            molar_relationship=MolarRelationship.CLASS_I,
            anb_angle_degrees=3.0,
            open_bite=True
        )
        
        score = self.analyzer.analyze(metrics)
        
        # 開咬は高スコア
        self.assertGreater(score.component_scores['overbite'], 60)
        self.assertIn('overbite', score.priority_rankings[0])
    
    def test_crossbite(self):
        """交叉咬合のテスト"""
        metrics = OcclusionMetrics(
            overjet_mm=2.5,
            overbite_mm=3.0,
            molar_relationship=MolarRelationship.CLASS_I,
            anb_angle_degrees=2.0,
            anterior_crossbite=True,
            posterior_crossbite=True
        )
        
        score = self.analyzer.analyze(metrics)
        
        # 交叉咬合は高スコア
        self.assertEqual(score.component_scores['crossbite'], 100.0)
        self.assertIn('crossbite', score.priority_rankings[:2])
    
    def test_scoring_boundaries(self):
        """スコアリングの境界値テスト"""
        # 正常範囲の境界
        metrics = OcclusionMetrics(
            overjet_mm=2.0,  # 正常下限
            overbite_mm=4.0,  # 正常上限
            molar_relationship=MolarRelationship.CLASS_I,
            anb_angle_degrees=0.0,  # 正常下限
            midline_deviation_mm=2.0  # 正常上限
        )
        
        score = self.analyzer.analyze(metrics)
        
        # すべて正常範囲内
        self.assertEqual(score.component_scores['overjet'], 0.0)
        self.assertEqual(score.component_scores['overbite'], 0.0)
        self.assertEqual(score.component_scores['anb_angle'], 0.0)
        self.assertEqual(score.component_scores['midline'], 0.0)
    
    def test_extreme_values(self):
        """極端な値のテスト"""
        metrics = OcclusionMetrics(
            overjet_mm=15.0,  # 極度の上顎前突
            overbite_mm=10.0,  # 極度の過蓋咬合
            molar_relationship=MolarRelationship.CLASS_II,
            anb_angle_degrees=12.0,  # 極度の骨格性II級
            midline_deviation_mm=8.0  # 大きな正中のずれ
        )
        
        score = self.analyzer.analyze(metrics)
        
        # 最重度と判定されるべき
        self.assertEqual(score.severity, OcclusionSeverity.VERY_SEVERE)
        self.assertGreater(score.total_score, 70)
    
    def test_priority_ranking_order(self):
        """優先順位の順序テスト"""
        metrics = OcclusionMetrics(
            overjet_mm=8.0,    # 中等度の問題
            overbite_mm=-4.0,  # 重度の問題
            molar_relationship=MolarRelationship.CLASS_II,
            anb_angle_degrees=7.0,
            anterior_crossbite=True  # 重度の問題
        )
        
        score = self.analyzer.analyze(metrics)
        
        # スコアの高い順に並んでいることを確認
        priorities = score.priority_rankings
        for i in range(len(priorities) - 1):
            current_score = score.component_scores[priorities[i]]
            next_score = score.component_scores[priorities[i + 1]]
            self.assertGreaterEqual(current_score, next_score)
    
    def test_detailed_report_generation(self):
        """詳細レポート生成のテスト"""
        metrics = OcclusionMetrics(
            overjet_mm=5.0,
            overbite_mm=5.0,
            molar_relationship=MolarRelationship.CLASS_II,
            anb_angle_degrees=5.0
        )
        
        score = self.analyzer.analyze(metrics)
        report = self.analyzer.get_detailed_report()
        
        # レポートに必要な情報が含まれているか
        self.assertIn("咬合分析レポート", report)
        self.assertIn(f"総合スコア: {score.total_score}", report)
        self.assertIn("重症度:", report)
        self.assertIn("測定値", report)
        self.assertIn("各指標スコア", report)
        self.assertIn("改善優先順位", report)
        self.assertIn("推奨事項", report)


def run_comprehensive_test():
    """包括的なテストを実行"""
    print("咬合分析エンジンの包括的テストを開始します...\n")
    
    # ユニットテストの実行
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n追加の実例テスト:")
    print("=" * 50)
    
    analyzer = OcclusionAnalyzer()
    
    # 実例1: 典型的なClass II症例
    print("\n実例1: 典型的なClass II症例")
    metrics = OcclusionMetrics(
        overjet_mm=7.0,
        overbite_mm=6.0,
        molar_relationship=MolarRelationship.CLASS_II,
        anb_angle_degrees=7.0,
        midline_deviation_mm=3.0
    )
    score = analyzer.analyze(metrics)
    print(f"総合スコア: {score.total_score}")
    print(f"重症度: {score.severity.name}")
    print(f"最優先改善項目: {score.priority_rankings[0] if score.priority_rankings else 'なし'}")
    
    # 実例2: 外科的矯正が必要な可能性のある症例
    print("\n実例2: 外科的矯正検討症例")
    metrics = OcclusionMetrics(
        overjet_mm=-5.0,
        overbite_mm=-3.0,
        molar_relationship=MolarRelationship.CLASS_III,
        anb_angle_degrees=-6.0,
        anterior_crossbite=True,
        posterior_crossbite=True,
        midline_deviation_mm=5.0
    )
    score = analyzer.analyze(metrics)
    print(f"総合スコア: {score.total_score}")
    print(f"重症度: {score.severity.name}")
    print("推奨事項:")
    for rec in score.recommendations:
        print(f"  - {rec}")


if __name__ == "__main__":
    run_comprehensive_test()