#!/usr/bin/env python3
"""
歯牙移動計算エンジンの拡張検証テスト
物理学的妥当性と計算精度の詳細確認
"""

from tooth_movement_calculator import (
    ToothMovementCalculator, MovementType, AnchorageType, ForceLevel,
    create_api_interface
)
import time


def test_physical_consistency():
    """物理学的一貫性の詳細検証"""
    print("=== 物理学的一貫性の詳細検証 ===\n")
    
    calculator = ToothMovementCalculator()
    
    # 1. 歯根表面積と力の関係
    print("1. 歯根表面積と必要な力の関係検証")
    test_cases = [
        ("11", "上顎中切歯", 230),  # 小さい歯根
        ("13", "上顎犬歯", 270),    # 中程度の歯根
        ("16", "上顎第一大臼歯", 430)  # 大きい歯根
    ]
    
    for tooth_id, name, expected_area in test_cases:
        actual_area = calculator.root_surface_areas[tooth_id]
        result = calculator.calculate_tooth_movement_vector(
            tooth_id, MovementType.BODILY, 3.0
        )
        
        # 表面積と力の比例関係を確認
        pressure = (result.force_required * 10) / actual_area
        
        print(f"   {name} ({tooth_id}): 表面積{actual_area}mm², 力{result.force_required}g, 圧力{pressure:.1f}g/cm²")
        
        assert actual_area == expected_area, f"表面積が期待値と異なる: {actual_area} != {expected_area}"
        assert 10 <= pressure <= 35, f"圧力が適正範囲外: {pressure}"
    
    print("   ✓ 歯根表面積に応じた適切な力設定を確認")
    
    # 2. 移動タイプと必要な力の関係
    print("\n2. 移動タイプと必要な力の関係検証")
    tooth_id = "11"
    magnitude = 3.0
    
    movement_forces = {}
    for movement_type in [MovementType.TIPPING, MovementType.BODILY, MovementType.INTRUSION]:
        result = calculator.calculate_tooth_movement_vector(tooth_id, movement_type, magnitude)
        movement_forces[movement_type] = result.force_required
        print(f"   {movement_type.value}: {result.force_required}g")
    
    # 傾斜移動 < 歯体移動 の関係を確認
    assert movement_forces[MovementType.TIPPING] < movement_forces[MovementType.BODILY], \
        "傾斜移動の方が歯体移動より力が必要になっています"
    
    # 圧下は軽い力
    assert movement_forces[MovementType.INTRUSION] < movement_forces[MovementType.BODILY], \
        "圧下の力が歯体移動より大きくなっています"
    
    print("   ✓ 移動タイプに応じた適切な力設定を確認")
    
    # 3. 移動量と期間の線形関係
    print("\n3. 移動量と期間の線形関係検証")
    magnitudes = [1.0, 2.0, 4.0, 6.0]
    durations = []
    
    for magnitude in magnitudes:
        result = calculator.calculate_tooth_movement_vector(
            "11", MovementType.BODILY, magnitude
        )
        durations.append(result.estimated_duration_weeks)
        print(f"   移動量{magnitude}mm → 期間{result.estimated_duration_weeks}週")
    
    # 線形関係の確認（誤差±20%以内）
    for i in range(1, len(magnitudes)):
        expected_ratio = magnitudes[i] / magnitudes[0]
        actual_ratio = durations[i] / durations[0]
        error = abs(expected_ratio - actual_ratio) / expected_ratio
        assert error < 0.2, f"移動量と期間の比例関係が崩れています: {error:.2%}"
    
    print("   ✓ 移動量と期間の線形関係を確認")


def test_calculation_precision():
    """計算精度の詳細確認"""
    print("\n=== 計算精度の詳細確認 ===\n")
    
    calculator = ToothMovementCalculator()
    
    # 1. 基本移動計算の精度
    print("1. 基本移動計算の精度検証")
    test_cases = [
        (3.0, 0.0, "正常範囲"),      # 正常
        (5.0, 3.0, "軽度不正咬合"),  # 軽度
        (8.0, 7.0, "重度不正咬合"),  # 重度
    ]
    
    for overjet, crowding, description in test_cases:
        result = calculator.calculate_basic_movement(overjet, crowding)
        
        print(f"   {description}: オーバージェット{overjet}mm, 叢生{crowding}mm")
        print(f"     → 前歯後退{result['anterior_mm']}mm, 拡大{result['expansion_mm']}mm")
        print(f"     → 抜歯要否: {result['extraction_required']}, 期間: {result['estimated_duration_months']}ヶ月")
        
        # 論理的な結果の確認
        if overjet <= 4.0:
            assert result['anterior_mm'] == 0.0, "正常範囲では前歯後退は不要"
        else:
            assert result['anterior_mm'] > 0.0, "過大なオーバージェットでは前歯後退が必要"
        
        if crowding <= 4.0 and crowding > 0:
            assert result['expansion_mm'] > 0.0, "軽度叢生では拡大が必要"
    
    print("   ✓ 基本移動計算の論理的一貫性を確認")
    
    # 2. スペース閉鎖の精度
    print("\n2. スペース閉鎖計算の精度検証")
    
    for space_mm in [3.0, 5.0, 7.0, 10.0]:
        result = calculator.estimate_closure_time(space_mm, "moderate")
        
        # 合理的な期間（1mm/月を基準）
        expected_months = space_mm / result['movement_rate_mm_per_month']
        actual_months = result['estimated_months']
        error = abs(expected_months - actual_months) / expected_months if expected_months > 0 else 0
        
        print(f"   {space_mm}mmスペース: 推定{actual_months}ヶ月 (効率{result['efficiency_factor']:.1%})")
        assert error < 0.3, f"期間推定の誤差が大きすぎます: {error:.2%}"
    
    print("   ✓ スペース閉鎖期間の推定精度を確認")
    
    # 3. 固定源分配の精度
    print("\n3. 固定源分配の精度検証")
    
    for anchorage_type in [AnchorageType.MINIMUM, AnchorageType.MODERATE, AnchorageType.MAXIMUM]:
        simulation = calculator.simulate_space_closure(7.0, "14", anchorage_type)
        total_movement = simulation.anterior_retraction_mm + simulation.posterior_protraction_mm
        
        print(f"   {anchorage_type.value}: 前歯{simulation.anterior_retraction_mm}mm + 臼歯{simulation.posterior_protraction_mm}mm = {total_movement}mm")
        
        # 総移動量がスペース量と一致（誤差±0.1mm以内）
        assert abs(total_movement - 7.0) < 0.1, f"総移動量が一致しません: {total_movement}"
    
    print("   ✓ 固定源分配の精度を確認")


def test_edge_cases():
    """エッジケースのテスト"""
    print("\n=== エッジケースのテスト ===\n")
    
    calculator = ToothMovementCalculator()
    
    # 1. 極端な値のテスト
    print("1. 極端な値のテスト")
    
    edge_cases = [
        (0.0, 0.0, "ゼロ値"),
        (15.0, 15.0, "極大値"),
        (2.5, 0.5, "境界値"),
    ]
    
    for overjet, crowding, description in edge_cases:
        try:
            result = calculator.calculate_basic_movement(overjet, crowding)
            print(f"   {description}: 計算成功 - 前歯後退{result['anterior_mm']}mm")
            
            # 結果の妥当性確認
            assert result['anterior_mm'] >= 0, "前歯後退量が負値"
            assert result['expansion_mm'] >= 0, "拡大量が負値"
            assert result['estimated_duration_months'] >= 0, "期間が負値"
            
        except Exception as e:
            print(f"   {description}: エラー発生 - {e}")
            raise
    
    print("   ✓ 極端な値でも安定動作を確認")
    
    # 2. 存在しない歯牙のテスト
    print("\n2. 存在しない歯牙のテスト")
    
    try:
        # 存在しない歯牙番号でもデフォルト値で動作
        result = calculator.calculate_tooth_movement_vector(
            "99", MovementType.BODILY, 3.0
        )
        print(f"   存在しない歯牙: 計算成功 - 力{result.force_required}g")
        assert result.force_required > 0, "力が計算されていない"
        
    except Exception as e:
        print(f"   存在しない歯牙: エラー発生 - {e}")
        raise
    
    print("   ✓ 存在しない歯牙でもデフォルト値で安定動作")
    
    # 3. 異常な固定源タイプのテスト
    print("\n3. 固定源要求度の境界テスト")
    
    boundary_types = ["alignment", "space_closure", "distalization", "unknown_type"]
    
    for movement_type in boundary_types:
        result = calculator.calculate_anchorage_requirement(movement_type)
        print(f"   {movement_type}: スコア{result['score']}")
        
        assert 0 <= result['score'] <= 100, f"スコアが範囲外: {result['score']}"
        assert 'type' in result, "固定源タイプが設定されていない"
        assert 'recommendations' in result, "推奨事項が設定されていない"
    
    print("   ✓ 全ての移動タイプで適切なスコア算出")


def test_api_integration():
    """API統合テストの詳細実行"""
    print("\n=== API統合テストの詳細実行 ===\n")
    
    api_function = create_api_interface()
    
    # 1. 複数症例でのテスト
    test_cases = [
        {
            "name": "軽度叢生症例",
            "data": {
                "occlusion": {"overjet": 4.5, "overbite": 3.5},
                "crowding": {"upper": 3.0, "lower": 2.0},
                "extraction_plan": None
            }
        },
        {
            "name": "Class II抜歯症例",
            "data": {
                "occlusion": {"overjet": 8.0, "overbite": 5.0},
                "crowding": {"upper": 6.0, "lower": 4.0},
                "extraction_plan": {"required": True, "teeth": ["14", "24"]}
            }
        },
        {
            "name": "Class III症例",
            "data": {
                "occlusion": {"overjet": -2.0, "overbite": 1.0},
                "crowding": {"upper": 2.0, "lower": 3.0},
                "extraction_plan": None
            }
        }
    ]
    
    for case in test_cases:
        print(f"   {case['name']}のテスト:")
        result = api_function(case['data'])
        
        # 必須フィールドの確認
        required_fields = ["basic_movement", "anchorage_plan", "tooth_movements", "total_duration_estimate"]
        for field in required_fields:
            assert field in result, f"{field}が結果に含まれていない"
        
        # 妥当な期間の確認
        duration = result["total_duration_estimate"]["months"]
        assert 6 <= duration <= 36, f"治療期間が非現実的: {duration}ヶ月"
        
        print(f"     期間: {duration}ヶ月, 前歯後退: {result['basic_movement']['anterior_mm']}mm")
        print(f"     抜歯要否: {result['basic_movement']['extraction_required']}")
    
    print("   ✓ 全症例で適切なAPI応答を確認")


def test_performance():
    """パフォーマンステスト"""
    print("\n=== パフォーマンステスト ===\n")
    
    calculator = ToothMovementCalculator()
    
    # 1. 大量計算のテスト
    print("1. 大量計算のパフォーマンステスト")
    
    start_time = time.time()
    
    # 100回の基本移動計算
    for i in range(100):
        overjet = 3.0 + (i % 10) * 0.5
        crowding = (i % 8) * 0.5
        calculator.calculate_basic_movement(overjet, crowding)
    
    basic_time = time.time() - start_time
    print(f"   基本移動計算×100回: {basic_time:.3f}秒")
    
    # 100回の歯牙移動計算
    start_time = time.time()
    
    for i in range(100):
        tooth_id = ["11", "12", "13", "16"][i % 4]
        movement_type = [MovementType.BODILY, MovementType.TIPPING][i % 2]
        magnitude = 1.0 + (i % 5)
        calculator.calculate_tooth_movement_vector(tooth_id, movement_type, magnitude)
    
    tooth_time = time.time() - start_time
    print(f"   歯牙移動計算×100回: {tooth_time:.3f}秒")
    
    # パフォーマンス基準（各計算1秒以内）
    assert basic_time < 1.0, f"基本移動計算が遅すぎます: {basic_time:.3f}秒"
    assert tooth_time < 1.0, f"歯牙移動計算が遅すぎます: {tooth_time:.3f}秒"
    
    print("   ✓ 全ての計算が1秒以内で完了")
    
    # 2. メモリ使用量のテスト
    print("\n2. メモリ効率のテスト")
    
    # 複数のインスタンス作成
    calculators = []
    for i in range(10):
        calc = ToothMovementCalculator()
        calculators.append(calc)
    
    # 各インスタンスで計算実行
    for calc in calculators:
        calc.calculate_basic_movement(5.0, 3.0)
    
    print("   ✓ 複数インスタンスの同時実行が成功")


def run_extended_validation():
    """拡張検証テストの実行"""
    print("歯牙移動計算エンジンの拡張検証テストを開始します...\n")
    
    try:
        test_physical_consistency()
        print("\n" + "="*70)
        
        test_calculation_precision()
        print("\n" + "="*70)
        
        test_edge_cases()
        print("\n" + "="*70)
        
        test_api_integration()
        print("\n" + "="*70)
        
        test_performance()
        print("\n" + "="*70)
        
        print("\n🎉 全ての拡張検証テストが成功しました！")
        return True
        
    except Exception as e:
        print(f"\n❌ 拡張検証テストでエラー発生: {e}")
        return False


if __name__ == "__main__":
    success = run_extended_validation()
    exit(0 if success else 1)