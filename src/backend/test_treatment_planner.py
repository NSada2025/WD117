import requests
import json
from datetime import datetime

# APIベースURL
BASE_URL = "http://localhost:8000"

def test_treatment_plan_generation():
    """治療計画生成のテスト"""
    print("=== 治療計画生成テスト ===\n")
    
    # テスト用患者ID
    patient_id = "2024-001"  # 山田太郎（骨格性II級、上顎前突）
    
    # 1. 基本的な治療計画生成
    print("1. 基本的な治療計画生成")
    response = requests.post(
        f"{BASE_URL}/patients/{patient_id}/treatment-plan",
        params={"patient_age": 15}
    )
    
    if response.status_code == 200:
        plan = response.json()
        print(f"✓ 治療計画生成成功")
        print(f"  - 総治療期間: {plan['total_duration_months']}ヶ月")
        print(f"  - 主装置: {plan['primary_appliance']}")
        print(f"  - ステージ数: {len(plan['stages'])}")
        print(f"  - 推定費用: {plan['estimated_cost_range'][0]:,}円 〜 {plan['estimated_cost_range'][1]:,}円")
        
        if plan['extraction_plan']:
            print(f"  - 抜歯計画: あり（{', '.join(plan['extraction_plan']['teeth'])}）")
        else:
            print(f"  - 抜歯計画: なし")
    else:
        print(f"✗ エラー: {response.status_code}")
    
    print()
    
    # 2. 審美重視の治療計画
    print("2. 審美重視の治療計画")
    preferences = {
        "aesthetic_priority": True,
        "invisible_priority": False
    }
    
    response = requests.post(
        f"{BASE_URL}/patients/{patient_id}/treatment-plan",
        params={"patient_age": 20},
        json={"preferences": preferences}
    )
    
    if response.status_code == 200:
        plan = response.json()
        print(f"✓ 審美重視計画生成成功")
        print(f"  - 主装置: {plan['primary_appliance']}")
        print(f"  - 推定費用: {plan['estimated_cost_range'][0]:,}円 〜 {plan['estimated_cost_range'][1]:,}円")
    else:
        print(f"✗ エラー: {response.status_code}")
    
    print()
    
    # 3. 治療計画レポート取得
    print("3. 治療計画レポート取得")
    response = requests.get(
        f"{BASE_URL}/patients/{patient_id}/treatment-plan-report",
        params={"patient_age": 15}
    )
    
    if response.status_code == 200:
        report_data = response.json()
        print(f"✓ レポート取得成功")
        print(f"  - 生成日時: {report_data['generated_at']}")
        print("\n--- レポート内容（一部）---")
        lines = report_data['report'].split('\n')[:10]
        for line in lines:
            print(f"  {line}")
        print("  ...")
    else:
        print(f"✗ エラー: {response.status_code}")
    
    print()
    
    # 4. 治療シミュレーション（複数オプション）
    print("4. 治療シミュレーション（複数オプション）")
    simulation_request = {
        "patient_id": patient_id,
        "patient_age": 15
    }
    
    response = requests.post(
        f"{BASE_URL}/treatment-simulation",
        json=simulation_request
    )
    
    if response.status_code == 200:
        simulation = response.json()
        print(f"✓ シミュレーション成功")
        print(f"  - 治療オプション数: {len(simulation['treatment_options'])}")
        
        for option in simulation['treatment_options']:
            plan = option['plan']
            print(f"\n  【{option['option_name']}】")
            print(f"    - 期間: {plan['total_duration_months']}ヶ月")
            print(f"    - 装置: {plan['primary_appliance']}")
            print(f"    - 費用: {plan['estimated_cost_range'][0]:,}円 〜 {plan['estimated_cost_range'][1]:,}円")
            print(f"    - 抜歯: {'あり' if plan['extraction_plan'] else 'なし'}")
    else:
        print(f"✗ エラー: {response.status_code}")
    
    print()


def test_different_cases():
    """異なる症例での治療計画テスト"""
    print("\n=== 異なる症例でのテスト ===\n")
    
    test_cases = [
        {
            "patient_id": "2024-001",
            "name": "山田太郎",
            "description": "骨格性II級、上顎前突",
            "age": 13
        },
        {
            "patient_id": "2024-002",
            "name": "鈴木花子",
            "description": "骨格性III級、反対咬合",
            "age": 16
        },
        {
            "patient_id": "2024-003",
            "name": "佐藤次郎",
            "description": "Angle I級、標準症例",
            "age": 25
        }
    ]
    
    for case in test_cases:
        print(f"患者: {case['name']} - {case['description']}")
        
        response = requests.post(
            f"{BASE_URL}/patients/{case['patient_id']}/treatment-plan",
            params={"patient_age": case['age']}
        )
        
        if response.status_code == 200:
            plan = response.json()
            print(f"  ✓ 計画生成成功")
            print(f"    - 期間: {plan['total_duration_months']}ヶ月")
            print(f"    - 主装置: {plan['primary_appliance']}")
            
            # 特別な配慮事項
            if plan.get('special_considerations'):
                print(f"    - 特別配慮: {plan['special_considerations'][0]}")
        else:
            print(f"  ✗ エラー: {response.status_code}")
        
        print()


def test_api_endpoints():
    """APIエンドポイントの動作確認"""
    print("\n=== APIエンドポイント動作確認 ===\n")
    
    # ルートエンドポイント
    response = requests.get(BASE_URL)
    if response.status_code == 200:
        data = response.json()
        print("✓ APIサーバー稼働中")
        print(f"  - バージョン: {data['version']}")
    else:
        print("✗ APIサーバーに接続できません")
        return
    
    # 患者リスト確認
    response = requests.get(f"{BASE_URL}/patients")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ 患者データ取得成功")
        print(f"  - 総患者数: {data['total']}")
    else:
        print("✗ 患者データ取得失敗")


if __name__ == "__main__":
    print("治療計画生成エンジンテスト開始")
    print("=" * 50)
    
    try:
        test_api_endpoints()
        test_treatment_plan_generation()
        test_different_cases()
        
        print("\n" + "=" * 50)
        print("テスト完了")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ エラー: APIサーバーに接続できません")
        print("  start_backend.sh を実行してAPIサーバーを起動してください")
    except Exception as e:
        print(f"\n✗ エラーが発生しました: {e}")