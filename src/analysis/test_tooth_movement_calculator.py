#!/usr/bin/env python3
"""
歯牙移動計算エンジンのテストスイート
物理学的妥当性の検証
"""

import unittest
from tooth_movement_calculator import (
    ToothMovementCalculator, MovementType, AnchorageType, ForceLevel,
    create_api_interface
)


class TestToothMovementCalculator(unittest.TestCase):
    """歯牙移動計算エンジンのテストクラス"""
    
    def setUp(self):
        """テストの初期化"""
        self.calculator = ToothMovementCalculator()
    
    def test_calculate_basic_movement_normal(self):
        """正常な咬合の基本移動計算テスト"""
        result = self.calculator.calculate_basic_movement(overjet_mm=3.0, crowding_mm=2.0)
        
        # 正常範囲内のオーバージェットは移動不要
        self.assertEqual(result["anterior_mm"], 0.0)
        
        # 軽度の叢生は拡大で対応
        self.assertGreater(result["expansion_mm"], 0)
        self.assertLess(result["expansion_mm"], 2.0)
        
        # 抜歯は不要
        self.assertFalse(result["extraction_required"])
    
    def test_calculate_basic_movement_severe(self):
        """重度の不正咬合の基本移動計算テスト"""
        result = self.calculator.calculate_basic_movement(overjet_mm=8.0, crowding_mm=7.0)
        
        # 大きなオーバージェットの場合、前歯後退が必要
        self.assertGreater(result["anterior_mm"], 4.0)
        self.assertLessEqual(result["anterior_mm"], 8.0)  # 最大値制限
        
        # 重度の叢生と大きな前歯後退で抜歯が必要
        self.assertTrue(result["extraction_required"])
        
        # 治療期間が長くなる
        self.assertGreater(result["estimated_duration_months"], 18)
    
    def test_anchorage_requirement_calculation(self):
        """固定源要求度計算のテスト"""
        # 空隙閉鎖は高い固定源が必要
        result = self.calculator.calculate_anchorage_requirement("space_closure")
        self.assertGreaterEqual(result["score"], 70)
        self.assertEqual(result["type"], "最大固定")
        
        # 配列は最小限の固定源
        result = self.calculator.calculate_anchorage_requirement("alignment")
        self.assertLessEqual(result["score"], 30)
        self.assertEqual(result["type"], "最小固定")
        
        # 圧下は中等度の固定源
        result = self.calculator.calculate_anchorage_requirement("intrusion")
        self.assertGreaterEqual(result["score"], 50)
        self.assertLessEqual(result["score"], 70)
    
    def test_closure_time_estimation(self):
        """スペース閉鎖時間推定のテスト"""
        # 標準的な7mmスペースの閉鎖
        result = self.calculator.estimate_closure_time(space_mm=7.0, force_level="moderate")
        
        # 合理的な期間（6-12ヶ月）
        self.assertGreaterEqual(result["estimated_months"], 6)
        self.assertLessEqual(result["estimated_months"], 12)
        
        # 軽い力は時間がかかる
        light_result = self.calculator.estimate_closure_time(space_mm=7.0, force_level="light")
        moderate_result = self.calculator.estimate_closure_time(space_mm=7.0, force_level="moderate")
        self.assertGreater(light_result["estimated_months"], moderate_result["estimated_months"])
        
        # 大きなスペースは効率が悪い
        large_space = self.calculator.estimate_closure_time(space_mm=10.0, force_level="moderate")
        self.assertLess(large_space["efficiency_factor"], 1.0)
    
    def test_tooth_movement_vector_calculation(self):
        """歯牙移動ベクトル計算のテスト"""
        # 上顎中切歯の歯体移動
        result = self.calculator.calculate_tooth_movement_vector(
            tooth_id="11",
            movement_type=MovementType.BODILY,
            magnitude_mm=4.0
        )
        
        # 物理学的に妥当な力の範囲
        self.assertGreaterEqual(result.force_required, 50)  # 最小力
        self.assertLessEqual(result.force_required, 800)    # 最大力
        
        # 合理的な期間
        self.assertGreaterEqual(result.estimated_duration_weeks, 8)
        self.assertLessEqual(result.estimated_duration_weeks, 24)
        
        # 移動ベクトルの確認
        self.assertIn("x", result.movement_vector)
        self.assertEqual(result.movement_vector["x"], -4.0)  # 後方移動
    
    def test_space_closure_simulation(self):
        """スペース閉鎖シミュレーションのテスト"""
        result = self.calculator.simulate_space_closure(
            space_mm=7.0,
            extraction_site="14",
            anchorage_type=AnchorageType.MAXIMUM
        )
        
        # 最大固定では前歯が多く動く
        self.assertGreater(result.anterior_retraction_mm, result.posterior_protraction_mm)
        
        # 総移動量がスペース量と一致
        total_movement = result.anterior_retraction_mm + result.posterior_protraction_mm
        self.assertAlmostEqual(total_movement, 7.0, places=1)
        
        # 合理的な力系
        self.assertIn("horizontal_force", result.force_system)
        self.assertGreaterEqual(result.force_system["horizontal_force"], 100)
        self.assertLessEqual(result.force_system["horizontal_force"], 300)
    
    def test_physical_validity_force_levels(self):
        """力レベルの物理学的妥当性テスト"""
        # 歯根表面積に基づく力の計算
        tooth_areas = self.calculator.root_surface_areas
        
        for tooth_id, area in tooth_areas.items():
            # 各歯牙で適切な力が計算されることを確認
            result = self.calculator.calculate_tooth_movement_vector(
                tooth_id=tooth_id,
                movement_type=MovementType.BODILY,
                magnitude_mm=2.0
            )
            
            # 圧力（g/cm²）の確認
            pressure = (result.force_required * 10) / area  # cm²に変換
            self.assertGreaterEqual(pressure, 15)  # 最小圧力
            self.assertLessEqual(pressure, 35)     # 最大圧力
    
    def test_movement_rate_consistency(self):
        """移動速度の一貫性テスト"""
        rates = self.calculator.movement_rates
        
        # 物理学的に妥当な移動速度
        self.assertLess(rates[MovementType.ROOT], rates[MovementType.BODILY])
        self.assertLess(rates[MovementType.BODILY], rates[MovementType.TIPPING])
        self.assertLess(rates[MovementType.INTRUSION], rates[MovementType.EXTRUSION])
        
        # 圧下は最も遅い
        self.assertEqual(rates[MovementType.INTRUSION], min(rates.values()))
    
    def test_anchorage_force_distribution(self):
        """固定源の力分配テスト"""
        # 最大固定では前歯に力が集中
        max_dist = self.calculator._calculate_force_distribution(
            AnchorageType.MAXIMUM, "space_closure"
        )
        self.assertGreater(max_dist["anterior"], 80)
        
        # 最小固定では均等分配
        min_dist = self.calculator._calculate_force_distribution(
            AnchorageType.MINIMUM, "space_closure"
        )
        self.assertAlmostEqual(min_dist["anterior"], min_dist["posterior"], delta=10)
    
    def test_side_effects_prediction(self):
        """副作用予測のテスト"""
        # 大きな圧下は副作用リスクが高い
        intrusion_effects = self.calculator._predict_side_effects(
            "11", MovementType.INTRUSION, 3.0
        )
        self.assertGreater(len(intrusion_effects), 0)
        self.assertTrue(any("歯根吸収" in effect for effect in intrusion_effects))
        
        # 過度な歯体移動もリスクがある
        bodily_effects = self.calculator._predict_side_effects(
            "11", MovementType.BODILY, 8.0
        )
        self.assertGreater(len(bodily_effects), 0)


class TestAPIInterface(unittest.TestCase):
    """API連携のテスト"""
    
    def setUp(self):
        """テストの初期化"""
        self.api_function = create_api_interface()
    
    def test_treatment_plan_integration(self):
        """治療計画エンジンとの統合テスト"""
        # サンプル治療計画データ
        treatment_data = {
            "occlusion": {
                "overjet": 7.0,
                "overbite": 4.0
            },
            "crowding": {
                "upper": 5.0,
                "lower": 3.0
            },
            "extraction_plan": {
                "required": True,
                "teeth": ["14", "24"]
            }
        }
        
        result = self.api_function(treatment_data)
        
        # 必要なキーが含まれているか
        self.assertIn("basic_movement", result)
        self.assertIn("anchorage_plan", result)
        self.assertIn("tooth_movements", result)
        self.assertIn("space_closure", result)
        
        # 物理学的に妥当な結果
        self.assertGreater(result["basic_movement"]["anterior_mm"], 0)
        self.assertTrue(result["basic_movement"]["extraction_required"])
        
        # 歯牙移動データが含まれている
        self.assertGreater(len(result["tooth_movements"]), 0)
        
        # スペース閉鎖計画が含まれている
        self.assertIsNotNone(result["space_closure"])
    
    def test_non_extraction_case(self):
        """非抜歯症例のテスト"""
        treatment_data = {
            "occlusion": {
                "overjet": 4.0,
                "overbite": 3.0
            },
            "crowding": {
                "upper": 2.0,
                "lower": 1.0
            },
            "extraction_plan": None
        }
        
        result = self.api_function(treatment_data)
        
        # 非抜歯症例では抜歯不要
        self.assertFalse(result["basic_movement"]["extraction_required"])
        
        # スペース閉鎖計画は不要
        self.assertIsNone(result["space_closure"])
        
        # 期間が短い
        self.assertLess(result["total_duration_estimate"]["months"], 20)


def run_validation_tests():
    """物理学的妥当性の包括的検証"""
    print("歯牙移動計算エンジンの物理学的妥当性検証を開始...\n")
    
    calculator = ToothMovementCalculator()
    
    # 1. 力と圧力の関係検証
    print("1. 力と圧力の関係検証")
    test_cases = [
        ("11", MovementType.BODILY, 3.0),  # 上顎中切歯
        ("16", MovementType.TIPPING, 2.0),  # 上顎第一大臼歯
        ("31", MovementType.INTRUSION, 1.0)  # 下顎中切歯
    ]
    
    for tooth_id, movement_type, magnitude in test_cases:
        result = calculator.calculate_tooth_movement_vector(tooth_id, movement_type, magnitude)
        area = calculator.root_surface_areas.get(tooth_id, 250)
        pressure = (result.force_required * 10) / area
        
        print(f"   歯牙{tooth_id} ({movement_type.value}): {pressure:.1f} g/cm²")
        assert 10 <= pressure <= 35, f"圧力が範囲外: {pressure} g/cm²"
    
    print("   ✓ すべての圧力が生物学的範囲内（10-35 g/cm²）")
    
    # 2. 移動速度の妥当性検証
    print("\n2. 移動速度の妥当性検証")
    rates = calculator.movement_rates
    for movement_type, rate in rates.items():
        if movement_type != MovementType.ROTATION:
            print(f"   {movement_type.value}: {rate} mm/月")
            assert 0.3 <= rate <= 2.0, f"移動速度が範囲外: {rate} mm/月"
    
    print("   ✓ すべての移動速度が文献値の範囲内")
    
    # 3. エネルギー効率の検証
    print("\n3. スペース閉鎖効率の検証")
    space_sizes = [3, 5, 7, 10]
    for space in space_sizes:
        result = calculator.estimate_closure_time(space, "moderate")
        efficiency = result["efficiency_factor"]
        print(f"   {space}mmスペース: 効率{efficiency:.1%}")
        assert 0.7 <= efficiency <= 1.0, f"効率が範囲外: {efficiency}"
    
    print("   ✓ スペースサイズに応じた適切な効率設定")
    
    # 4. 固定源バランスの検証
    print("\n4. 固定源バランスの検証")
    anchorage_types = [AnchorageType.MINIMUM, AnchorageType.MODERATE, AnchorageType.MAXIMUM]
    for anchorage_type in anchorage_types:
        dist = calculator._calculate_force_distribution(anchorage_type, "space_closure")
        total = dist["anterior"] + dist["posterior"]
        print(f"   {anchorage_type.value}: 前歯{dist['anterior']}% / 臼歯{dist['posterior']}%")
        assert abs(total - 100) < 1, f"力の分配が100%でない: {total}%"
    
    print("   ✓ 固定源タイプに応じた適切な力分配")
    
    print("\n=== 物理学的妥当性検証完了 ===")
    print("すべての計算が生物学的・物理学的に妥当な範囲内です。")


def run_comprehensive_tests():
    """包括的テストの実行"""
    print("歯牙移動計算エンジンの包括的テストを開始します...\n")
    
    # ユニットテストの実行
    test_suite = unittest.TestSuite()
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestToothMovementCalculator))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAPIInterface))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 物理学的妥当性の検証
    if result.wasSuccessful():
        print("\n" + "="*70)
        run_validation_tests()
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    if success:
        print("\n🎉 すべてのテストが成功しました！")
    else:
        print("\n❌ 一部のテストが失敗しました。")
    
    exit(0 if success else 1)