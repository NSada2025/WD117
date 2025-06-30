#!/usr/bin/env python3
"""
計算機能のユニットテスト
作成者: dev3 (テスト・品質管理担当)
"""

import unittest
import sys


class Calculator:
    """シンプルな計算機能を提供するクラス"""
    
    @staticmethod
    def add(a, b):
        """2つの数値を加算する"""
        return a + b


class TestCalculator(unittest.TestCase):
    """計算機能のテストケース"""
    
    def setUp(self):
        """テストの初期設定"""
        self.calculator = Calculator()
    
    def test_add_one_plus_one(self):
        """1+1=2が正しく動作することを確認"""
        result = self.calculator.add(1, 1)
        self.assertEqual(result, 2, "1+1は2になるべきです")
    
    def test_add_positive_numbers(self):
        """正の数の加算テスト"""
        test_cases = [
            (0, 0, 0),
            (1, 2, 3),
            (10, 20, 30),
            (100, 200, 300)
        ]
        
        for a, b, expected in test_cases:
            with self.subTest(a=a, b=b):
                result = self.calculator.add(a, b)
                self.assertEqual(result, expected, f"{a}+{b}は{expected}になるべきです")
    
    def test_add_negative_numbers(self):
        """負の数の加算テスト"""
        test_cases = [
            (-1, -1, -2),
            (-5, 3, -2),
            (5, -3, 2),
            (-10, -20, -30)
        ]
        
        for a, b, expected in test_cases:
            with self.subTest(a=a, b=b):
                result = self.calculator.add(a, b)
                self.assertEqual(result, expected, f"{a}+{b}は{expected}になるべきです")
    
    def test_add_float_numbers(self):
        """小数の加算テスト"""
        result = self.calculator.add(0.1, 0.2)
        self.assertAlmostEqual(result, 0.3, places=7, msg="0.1+0.2は約0.3になるべきです")


def run_tests():
    """テストを実行してレポートを生成"""
    print("=" * 70)
    print("計算機能テストレポート")
    print("実行者: dev3 (テスト・品質管理担当)")
    print("=" * 70)
    
    # テストスイートを作成
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCalculator)
    
    # テストを実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 結果サマリー
    print("\n" + "=" * 70)
    print("テスト結果サマリー:")
    print(f"実行テスト数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"エラー: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ すべてのテストが成功しました！")
        print("✓ 1+1=2の計算が正しく動作することを確認しました。")
    else:
        print("\n✗ テストに失敗がありました。")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)