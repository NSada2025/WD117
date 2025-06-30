#!/usr/bin/env python3
"""
治療計画エンジン拡張機能のテストスクリプト
"""

import requests
import json
from datetime import datetime

# APIベースURL
BASE_URL = "http://localhost:8000"


def test_tooth_movements():
    """歯牙移動量計算機能のテスト"""
    print("=== 歯牙移動量計算テスト ===\n")
    
    # テスト患者（II級上顎前突）
    patient_id = "2024-001"
    
    response = requests.get(
        f"{BASE_URL}/patients/{patient_id}/tooth-movements",
        params={"patient_age": 15}
    )
    
    if response.status_code == 200:
        data = response.json()
        movements = data["movements"]
        
        print(f"✓ 歯牙移動量計算成功")
        print(f"  患者ID: {patient_id}")
        print(f"  総移動時間: {movements['total_movement_time']}週間")
        
        print("\n【前歯部後方移動量】")
        for tooth, movement in movements["anterior_retraction"].items():
            print(f"  {tooth}:")
            for key, value in movement.items():
                print(f"    - {key}: {value}")
        
        print("\n【臼歯部移動量】")
        for tooth, movement in movements["molar_movement"].items():
            print(f"  {tooth}:")
            for key, value in movement.items():
                print(f"    - {key}: {value}")
        
        print("\n【3D移動ベクトル】")
        for tooth, vector in movements["tooth_vectors"].items():
            print(f"  {tooth}: {vector} (x, y, z)")
    else:
        print(f"✗ エラー: {response.status_code}")
        print(response.text)


def test_wire_sequence():
    """ワイヤーシークエンス計画機能のテスト"""
    print("\n\n=== ワイヤーシークエンステスト ===\n")
    
    patient_id = "2024-001"
    
    response = requests.get(
        f"{BASE_URL}/patients/{patient_id}/wire-sequence",
        params={"patient_age": 15}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✓ ワイヤーシークエンス生成成功")
        print(f"  患者ID: {patient_id}")
        print(f"  装置タイプ: {data['appliance_type']}")
        print(f"  総期間: {data['total_duration_weeks']}週間")
        
        print("\n【ワイヤーシークエンス】")
        for i, wire in enumerate(data["wire_sequence"], 1):
            print(f"\n{i}. {wire['size']}")
            print(f"   期間: {wire['duration_weeks']}週間")
            print(f"   目的: {wire['purpose']}")
            print(f"   力のレベル: {wire['force_level']}")
            print(f"   開始週: {wire['start_week']}週目")
            print(f"   ステージ: {wire['stage']}")
            
            if wire.get("considerations"):
                print(f"   注意事項:")
                for consideration in wire["considerations"]:
                    print(f"     - {consideration}")
    else:
        print(f"✗ エラー: {response.status_code}")
        print(response.text)


def test_elastic_prescription():
    """顎間ゴム処方機能のテスト"""
    print("\n\n=== 顎間ゴム処方テスト ===\n")
    
    # 複数の症例でテスト
    test_cases = [
        {
            "patient_id": "2024-001",
            "name": "山田太郎",
            "stage": "空隙閉鎖",
            "description": "II級症例"
        },
        {
            "patient_id": "2024-002",
            "name": "鈴木花子",
            "stage": "前歯部改善",
            "description": "III級症例"
        },
        {
            "patient_id": "2024-001",
            "name": "山田太郎",
            "stage": "仕上げ",
            "description": "仕上げ段階"
        }
    ]
    
    for case in test_cases:
        print(f"\n【{case['name']} - {case['description']}】")
        print(f"治療ステージ: {case['stage']}")
        
        # 咬合分析データ（テスト用）
        occlusion_analysis = {
            "midline_deviation": 3.0  # 正中線のズレ
        }
        
        response = requests.post(
            f"{BASE_URL}/patients/{case['patient_id']}/elastic-prescription",
            params={"treatment_stage": case['stage']},
            json=occlusion_analysis
        )
        
        if response.status_code == 200:
            data = response.json()
            prescription = data["prescription"]
            
            print(f"✓ 処方生成成功")
            
            if prescription["elastics"]:
                for elastic in prescription["elastics"]:
                    print(f"\n  ゴムタイプ: {elastic['type']}")
                    print(f"  装着部位:")
                    for location, attachment in elastic['attachment'].items():
                        print(f"    - {location}: {attachment}")
                    print(f"  強度: {elastic['force']}")
                    print(f"  装着時間: {elastic['wear_time']}")
                    print(f"  目的: {elastic['purpose']}")
                
                print(f"\n  推奨期間: {prescription['duration_weeks']}週間")
            else:
                print("  顎間ゴムの使用なし")
        else:
            print(f"✗ エラー: {response.status_code}")


def test_different_appliances():
    """異なる装置タイプでのワイヤーシークエンステスト"""
    print("\n\n=== 装置タイプ別ワイヤーシークエンス ===\n")
    
    # セラミックブラケットのテストケースを作成
    # （実際にはAPIで装置タイプを指定できるように拡張が必要）
    
    print("※ 現在の実装では患者の治療計画に基づいて自動選択されます")
    print("  将来的には装置タイプを指定できるエンドポイントの追加を検討")


def test_comprehensive_analysis():
    """統合的な分析テスト"""
    print("\n\n=== 統合分析テスト ===\n")
    
    patient_id = "2024-001"
    patient_age = 15
    
    print(f"患者ID: {patient_id} (年齢: {patient_age}歳)")
    
    # 1. 基本情報取得
    response = requests.get(f"{BASE_URL}/patients/{patient_id}")
    if response.status_code == 200:
        patient = response.json()
        print(f"\n診断情報:")
        print(f"  - 骨格型: {patient['セファロ分析']['骨格系']['骨格型分類']}")
        print(f"  - 臼歯関係: {patient['咬合関係']['臼歯部']['大臼歯関係']}")
        print(f"  - オーバージェット: {patient['咬合関係']['前歯部']['オーバージェット']}")
        print(f"  - 複雑度: {patient['治療難易度評価']['複雑度スコア']}")
    
    # 2. 治療計画生成
    response = requests.post(
        f"{BASE_URL}/patients/{patient_id}/treatment-plan",
        params={"patient_age": patient_age}
    )
    if response.status_code == 200:
        plan = response.json()
        print(f"\n治療計画:")
        print(f"  - 期間: {plan['total_duration_months']}ヶ月")
        print(f"  - 装置: {plan['primary_appliance']}")
        print(f"  - 抜歯: {'あり' if plan['extraction_plan'] else 'なし'}")
    
    # 3. 歯牙移動量
    response = requests.get(
        f"{BASE_URL}/patients/{patient_id}/tooth-movements",
        params={"patient_age": patient_age}
    )
    if response.status_code == 200:
        movements = response.json()["movements"]
        print(f"\n歯牙移動:")
        print(f"  - 予想期間: {movements['total_movement_time']}週間")
        if movements["anterior_retraction"]:
            print(f"  - 前歯後方移動: 必要")
    
    # 4. 初期ゴム処方
    response = requests.post(
        f"{BASE_URL}/patients/{patient_id}/elastic-prescription",
        params={"treatment_stage": "空隙閉鎖"}
    )
    if response.status_code == 200:
        prescription = response.json()["prescription"]
        if prescription["elastics"]:
            print(f"\n顎間ゴム:")
            print(f"  - タイプ: {prescription['elastics'][0]['type']}")
            print(f"  - 強度: {prescription['elastics'][0]['force']}")


def main():
    """メインテスト実行"""
    print("治療計画エンジン拡張機能テスト")
    print("=" * 60)
    
    try:
        # APIサーバー確認
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print("✗ APIサーバーに接続できません")
            return
        
        print("✓ APIサーバー接続確認")
        
        # 各機能のテスト
        test_tooth_movements()
        test_wire_sequence()
        test_elastic_prescription()
        test_comprehensive_analysis()
        
        print("\n\n" + "=" * 60)
        print("テスト完了")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ エラー: APIサーバーに接続できません")
        print("  start_backend.sh を実行してAPIサーバーを起動してください")
    except Exception as e:
        print(f"\n✗ 予期しないエラー: {e}")


if __name__ == "__main__":
    main()